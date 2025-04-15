#############################################################################
# File Name: data_processor.py
# Date Created: 4/1/2025
# Original Author: Max Bryk
# Description
#   This file contains the main body of code that controls all the high level
#   functions like updating the configuration set whenever the user updates 
#   config parameters in the GUI, grabbing the DAQ values, sending those values
#   to the processing substsytem, and grabbing processed frames and sending
#   them back to the GUI through multiprocessing pipes
#
# Copyright Cover.ai 2025
#############################################################################

import multiprocessing as mp
import collections
import daq_comms as dc
import main_proc_fcns as mpf
import dat_file_fcns as dff
import time
import ipdb

# simple method for moving the docstring above the function declaration
# because having a big docstring underneath the arguments list is annoying
def docstring(docstr):
    def assign_doc(f):
        f.__doc__ = docstr
        return f
    return assign_doc



#############################################################################
#############################################################################


class Profiler:
    num_rng_proc = 0
    num_pix_proc = 0


    def __init__(s):
        pass

    def reset(s):
        s.num_rng_proc = 0
        s.num_pix_proc = 0



#############################################################################
#############################################################################
"""
configuration parameters

normal radar ones


new ones
    data_src
        this is a number (for inter-process space efficiency) that indicates 
        either "file" or "daq" to indicate whether or not the data comes from
        a file or the DAQ.

    frame_style
        a number (for inter-process space efficiency) that indicates what kind
        of method is used to construct frames:
            fixed number of rangelines
            azimuth turnaround
            percentage of frame "filled"
            frame "integration"
                This allows integration of the frame until the user says 
                "stop". This core will send multiple frames but retain the 
                data in each frame to re-calculate the "best" pixel location
                for each rangeline.  So the integration actually occurrs here
                and the GUI remains the place where it is displayed ONLY
            percentage of columns "filled"
                this works better for A-Sample, it can check each column and 
                if there are missing pixels in any column greater than a 
                certain percentage 

    num_frame_rangelines
        fixed number of rangelines per frame for the frame_style(s) calling 
        for such a value

    frame_percent
        frame percentage "filled" with rangelines required prior to generating
        a frame.  Note that "filled" means a rangeline assigned to that pixel
        not necessarily a valid pixel (as that rangeline may have no 
        valid peaks)
       
    daq_addr
        the address used to connect to the DAQ.  Probably always will be 
        "localhost"

    daq_num_rangelines
        number of rangelines to grab from the DAQ at a time

    daq_timeout       
        total amount of time to wait while grabbing "daq_num_rangelines" before
        returning whatever rangelines you found.  This is not related to the
        python socket timout - that's a lower level timeout
        

"""
#############################################################################
#############################################################################



# Main loop that is called by the multiprocessing core.  This contains all the
# input/output variables
@docstring("""
This means I ned to create a config object, a frame object and possibly
additional objects

cfg_obj_pipe
    this is a pipe that you send configuration objects through to reconfigure
    the data processor.  It consists of a dictionary with values in it that 
    need to be updated

    the number of x and y pixels.  It even includes things that change more 
    frequently like threshold and contrast values.  

    this could also contain file names for data files to process so we can 
    pipe the data files through this postprocessing algorithm as well
    
    This config pipe actually should contain tagged data where only new values
    are sent, to minimize the overhead 

data_out_pipe
    frame and auxiliary data (that needs to be synchronous with the frame) 
    comes out here

query_out_pipe
    This is a pipe where if there's some kind of query in the cfg_flags like 
    "is the DAQ connected?" then the response to that query would come on
    this pipe.  Intended for infrequent queries with low data volume, for
    flags within the processor core as well as for debugging

frame_queue
    a queue object that contains an object that contains all relelvent frame
    data
""")
def main_proc_loop(cfg_obj_pipe, error_pipe, data_out_pipe, query_out_pipe, 
                         cfg_dict):

    dbg_prof    = False
    radar       = dc.SimpRadar()
    proc_obj    = mpf.CoverProc()
    proc_prof   = Profiler() # presently unused

    # buffer containing data from most recent fileset

    file_buf = collections.OrderedDict()
    file_buf["initialized"] = False
    file_buf["rangelines"]  = None
    file_buf["elevation"]   = None
    file_buf["azimuth"]     = None
    file_buf["channels"]    = None
    file_buf["fs_post_dec"] = None
    file_buf["fft_flag"]    = None
    file_buf["powcalc_flag"]    = None
    file_buf["dec_val"]     =  None
    file_buf["len_rangeline"]   = None
    file_buf["data_good"]   = None
    profiler_enabled = False

    # setup everything 
    #   DAQ socket and sending that configuration
    #   xml thing.  Abstract away as much as possible
    #
    #   multiprocessing concurrent.futures stuff as desired

    while True:
        new_frame_flag = False
        # do a status check of everything, the DAQ connection in particular
        # but anything that could periodically change asynchronously

        #####################################################################
        #                         SETUP CHANGES STEPS                       #
        #####################################################################
        # check for new confiugration data
        cfg_update = False
        if (cfg_obj_pipe.poll()):
            new_cfg_vals = cfg_obj_pipe.recv()

            # update the configuration
            for keyval in new_cfg_vals.keys():
                if keyval in cfg_dict.keys():
                    cfg_dict[keyval] = new_cfg_vals[keyval]

                cfg_update = True
                # ultimately we'll want to not do an update on any change
                # but for now just always update
                #if keyval in update_keys:
                #    cfg_update = True
                #else:
                #    cfg_update = False
        
            # all new cfg_obj_pipe values have a flags dict
            # and we check the flags to see what we have to do 
            cfg_flags = new_cfg_vals["flags"]
            if "close_process" in cfg_flags:
                radar.disconnect()
                break

            if ("setup_daq" in cfg_flags) or ("update_daq_ch" in cfg_flags):
                ch0_en = cfg_dict["ch0_en"]
                ch1_en = cfg_dict["ch1_en"]

                if not radar.daq_connected:
                    addr   = cfg_dict["daq_addr"]
                    conn_success = radar.setup_comms(addr, ch0_en, ch1_en)
                    if not conn_success:
                        error_pipe.send(["DAQ_CONN_FAILED"])
                else:
                    radar.set_en_channels(ch0_en, ch1_en)

            # easy way to turn on and off profiling of the code
            if "enable_profiler" in cfg_flags:
                profiler_enabled = True

        else: # no updated config values
            cfg_flags = []

        # and finally perform some DAQ checks


        #####################################################################
        #                      DATA GATHERING STEPS                         #
        #####################################################################
        if cfg_dict["data_src"] == "daq":
            if not radar.daq_connected:
                continue

            daq_num_rangelines = cfg_dict["daq_num_rangelines"]
            daq_timeout         = cfg_dict["daq_timeout"]

            # a hysteresis parameter for turnaround
            # Note: nonzero turn_hyst will produce "wobble" at frame edges
            turn_hyst = cfg_dict["turn_hyst"]
            min_az          = cfg_dict["min_az"] + cfg_dict["turn_az_margin"]
            max_az          = cfg_dict["max_az"] - cfg_dict["turn_az_margin"]


            # this directs get_daq_data() to stop looking for rangelines after
            # a turnaround is detected and return immediately
            if cfg_dict["frame_style"] == "azimuth_turnaround":
                turnaround_mode = True
            else:
                turnaround_mode = False

            if profiler_enabled:
                daq_acq_start = time.time()
            # this step actually grabs the rangelines from the DAQ
            (rangelines_array, az_array, 
            el_array, ch_array, num_rangelines, turn_flag, reset_in_array,
            status_flag) = radar.get_daq_data(daq_num_rangelines, 
                                              turnaround_mode, turn_hyst,
                                              min_az, max_az,
                                              daq_timeout)


            # basically indicates the DAQ is not connected, pause a moment 
            # so the processor isn't thrashing around
            if status_flag in ["DAQ_NOT_CONNECTED", "CONN_RESET"]:
                time.sleep(0.1)
                continue

            # can gather a lot of metadata here

            # turnaround_inds not used right now


            if status_flag not in ["OK", "TIMEOUT"]:
                print(status_flag)
                error_pipe.send(["DAQ STATUS FLAG ERROR", status_flag])
                continue 

            # this is required to resize the numpy arrays since those 
            # arrays are pre-allocated
            if num_rangelines != daq_num_rangelines:
                rangelines_array = rangelines_array[:num_rangelines]
                az_array = az_array[:num_rangelines]
                el_array = el_array[:num_rangelines]
                ch_array = ch_array[:num_rangelines]

            if profiler_enabled:
                daq_acq_end = time.time()
                daq_time_ms = (daq_acq_end - daq_acq_start) * 1000
                print(f"    daq acq duration: {daq_time_ms:.4f} ms")
                print(f"        daq rangelines acq: {num_rangelines}")



            if profiler_enabled:
                start_time = time.time()
            (frame_out, aux_data_out, 
             new_frame_flag) = proc_obj.postproc_data(rangelines_array, 
                                             az_array, el_array, ch_array, 
                                             turn_flag, reset_in_array, 
                                             cfg_dict, cfg_flags, dbg_prof)
                                             

            if profiler_enabled:
                end_time = time.time()
                proc_time_ms = (end_time - start_time) * 1000
                print(f"    pixel processing time: {proc_time_ms:.4f}\n") 

        # future work
        #elif cfg_dict["data_src"] == "video_file"

        elif cfg_dict["data_src"] == "disabled":
            pass

        # NOTE DAT FILE DATA SOURCE UNTESTED
        else: # cfg_dict["data_src"] == "dat_file":
            if cfg_update:
                if (("fname_changed" in cfg_flags) or 
                   (file_buf["initialized"] == False)):

                    fs_adc = cfg_dict["fs_adc"]
                    fname_list = cfg_dict["fname_list"]

                    (rangelines, elevation, azimuth, channels, 
                     fs_post_dec, fft_flag, powcalc_flag, dec_val, 
                     len_rangeline, 
                     data_good) = dff.get_rangelines_from_file(fname_list, 
                                                               fs_adc)
            
                    file_buf["initialized"] = True
                    file_buf["rangelines"]  = rangelines
                    file_buf["elevation"]   = elevation
                    file_buf["azimuth"]     = azimuth
                    file_buf["channels"]    = channels
                    file_buf["fs_post_dec"] = fs_post_dec
                    file_buf["fft_flag"]    = fft_flag
                    file_buf["powcalc_flag"]    = powcalc_flag
                    file_buf["dec_val"]     =  dec_val
                    file_buf["len_rangeline"]   = len_rangeline
                    file_buf["data_good"]   = data_good

                else:
                    # grab the stored data of the most recent file and 
                    # re-process it
                    rangelines_array    = file_buf["rangelines"]
                    el_array            = file_buf["elevation"]
                    az_array            = file_buf["azimuth"]
                    ch_array            = file_buf["channels"]
                    fs_post_dec         = file_buf["fs_post_dec"]
                    fft_flag            = file_buf["fft_flag"]
                    powcalc_flag        = file_buf["powcalc_flag"]
                    dec_val             = file_buf["dec_val"]
                    len_rangeline       = file_buf["len_rangeline"]
                    data_good           = file_buf["data_good"]

                    proc_turnaround = False
                    if not data_good:
                        error_pipe.send("FILE_FRAME_DATA_BAD")
                        new_frame_flag = False
                    else:
                        (frame_out, aux_data_out, 
                         new_frame_flag) = proc_obj.postproc_data(
                                             rangelines_array, 
                                             az_array, el_array, ch_array, 
                                             turn_flag, reset_in_array, 
                                             cfg_dict, cfg_flags, dbg_prof)
                                             


        # send frame
        if new_frame_flag:
            data_out_pipe.send([frame_out, aux_data_out])


##############################################################################
##############################################################################
##############################################################################

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
from collections import OrderedDict
import daq_comms as dc
#import OLD__daq_comms as dc
import main_proc_fcns as mpf
import dat_file_fcns as dff
import external_loader as extl
import time
import ipdb
import traceback

# simple method for moving the docstring above the function declaration
# because having a big docstring underneath the arguments list is annoying
def docstring(docstr):
    def assign_doc(f):
        f.__doc__ = docstr
        return f
    return assign_doc

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

    frac_filled_thresh
        frame fraction "filled" with rangelines required prior to generating
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
Function Name: main_proc_loop()
Description: 
    main processing loop that gathers radar pulses from the DAQ or from a 
    file input and processes them down to frames and auxiliary data before 
    transferring the data to the THzVisGUI.  

    This loop is instaitated from THzVisGUI as a child process and uses
    Python's multiprocessing module to improve speed and efficiency

Arguments:
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

    query_in_pipe
        A pipe

    query_out_pipe
        This is a pipe where if there's some kind of query in the cfg_flags like 
        "is the DAQ connected?" then the response to that query would come on
        this pipe.  Intended for infrequent queries with low data volume, for
        flags within the processor core as well as for debugging

""")
def main_proc_loop(cfg_obj_pipe, error_pipe, data_out_pipe, query_in_pipe, 
                   query_out_pipe, cfg_dict):

    dbg_prof    = False
    radar       = dc.SimpRadar()
    proc_obj    = mpf.CoverProc()

    # Frame Buffer for holding frames for later reference
    FRAME_BUF_MAX = 30
    frame_buffer = OrderedDict()

    # buffer containing data from most recent fileset
    file_buf = OrderedDict()
    file_buf["rangelines"]      = None
    file_buf["elevation"]       = None
    file_buf["azimuth"]         = None
    file_buf["channels"]        = None

    file_params                     = OrderedDict()
    file_params["buf_initialized"]  = False
    file_params["fs_post_dec"]      = None
    file_params["fft_flag"]         = None
    file_params["powcalc_flag"]     = None
    file_params["dec_val"]          = None
    file_params["len_rangeline"]    = None
    file_params["data_good"]        = None
    profiler_enabled                = False

    update_id = 0 # temporary
    # setup everything 
    #   DAQ socket and sending that configuration
    #   xml thing.  Abstract away as much as possible
    #
    #   multiprocessing concurrent.futures stuff as desired

    turn_flag = "DISABLED"

    try:
        while True:
            new_frame_flag = False
            #####################################################################
            #                      QUERY HANDLING STEPS                         #
            #####################################################################
            send_status = False
            while query_in_pipe.poll():
                query_in_list = query_in_pipe.recv()
                if "DAQ_STATUS" in query_in_list:
                    send_status = True
                    query_out_dict = OrderedDict()
                    if radar.get_conn_status():
                        query_out_dict["DAQ_STATUS"] = "CONNECTED"
                    else:
                        query_out_dict["DAQ_STATUS"] = "NOT_CONNECTED"
            if send_status:
                query_out_pipe.send(query_out_dict)

            # do a status check of everything, the DAQ connection in particular
            # but anything that could periodically change asynchronously

            ###################################################################
            #                       SETUP CHANGES STEPS                       #
            ###################################################################
            # check for new confiugration data
            cfg_update = False
            if (cfg_obj_pipe.poll()):
                new_cfg_vals = cfg_obj_pipe.recv()
                query_out_dict = OrderedDict()
                # the value at "CFG_ACK" doesn't matter, the presence of the key 
                # is the "ack"
                query_out_dict["CFG_ACK"] = None
                query_out_pipe.send(query_out_dict)

                # update the configuration
                for keyval in new_cfg_vals.keys():
                    cfg_dict[keyval] = new_cfg_vals[keyval]

                    # ultimately we'll want to not do an update on any change
                    # but for now just always update
                    cfg_update = True
            
                # all new cfg_obj_pipe values have a flags dict
                # and we check the flags to see what we have to do 
                cfg_flags = new_cfg_vals["flags"]
                if "close_process" in cfg_flags:
                    radar.disconnect()
                    radar.end_acq_proc()
                    print("data_processor shutting down....")
                    break

                #####################
                # DAQ SETUP STEPS
                #####################
                # only do DAQ operations if the DAQ is the data source
                if cfg_dict["data_src"] == "daq":
                    if ("setup_daq" in cfg_flags) or ("update_daq_ch" in cfg_flags):
                        ch0_en = cfg_dict["ch0_en"]
                        ch1_en = cfg_dict["ch1_en"]

                        if not radar.get_conn_status():
                            addr   = cfg_dict["daq_addr"]
                            conn_success = radar.setup_comms(addr, ch0_en, ch1_en)
                            #if not conn_success:
                            #    error_pipe.send(["DAQ_CONN_FAILED"])
                        else:
                            radar.set_en_channels(ch0_en, ch1_en)

                    if cfg_dict["acq_dbg"] == True:
                        radar.en_acq_dbg(True)
                    else:
                        radar.en_acq_dbg(False)


                # disable the DAQ if it's not in use
                else: 
                    radar.disconnect()

                # easy way to turn on and off profiling of the code
                if "enable_profiler" in cfg_flags:
                    profiler_enabled = True
                    dbg_prof = True
                
                if "disable_profiler" in cfg_flags:
                    profiler_enabled = False
                    dbg_prof = False

            else: # no updated config values
                cfg_flags = []


            # reset the buffer initialization parameter in case we've switched
            # from dat_file to something else so it doesn't think it's 
            # initialized accidentally
            if cfg_dict["data_src"] != "dat_file":
                file_params["buf_initialized"]  = False

            ###################################################################
            #                      DATA GATHERING STEPS                       #
            ###################################################################
            buf_frames_flag = True
            
            # This is essentially the "paused
            if cfg_dict["data_src"] == "use_buffer":
                # only reprocess the frame if something actually changed
                # otherwise throw in a short pause and do nothing
                if "reproc_buf" not in cfg_flags:
                    time.sleep(0.005)
                    continue
 
                #buf_frames_flag = False
                coarse_grid_ovr = True
                turn_flag = "DISABLED"
                reset_in_array = False

                try:
                    # check for empty frame buffer
                    if frame_buffer == {}:
                        time.sleep(0.01)
                    else:
                        buf_frame_id = cfg_dict["curr_frame_id"] 
                        coarse_grid_dict_in = frame_buffer[buf_frame_id]
                        #(frame_out, aux_data_out, new_frame_flag, frame_id_out, 
                        # coarse_grid_dict_out) = proc_obj.postproc_data(
                        #                     rangelines_array, 
                        #                     az_array, el_array, ch_array, 
                        #                     turn_flag, reset_in_array, 
                        #                     cfg_dict, cfg_flags, file_params, 
                        #                     update_id, coarse_grid_dict_in, 
                        #                     coarse_grid_ovr, dbg_prof)

                        (frame_out, aux_data_out, new_frame_flag, frame_id_out, 
                         coarse_grid_dict_out) = proc_obj.postproc_data(
                                             None, None, None, None, 
                                             turn_flag, reset_in_array, 
                                             cfg_dict, cfg_flags, None, 
                                             update_id, coarse_grid_dict_in, 
                                             coarse_grid_ovr, dbg_prof)



                except Exception as e:
                    print(e)
                    print("got to e")
                    ipdb.set_trace()
                    print("")
                    print("")
                    print("")
                    print("")
                    print("")



            elif cfg_dict["data_src"] == "daq":
                if not radar.get_conn_status():
                    time.sleep(0.01)
                    continue

                if profiler_enabled:
                    start_time = time.time()
                    print("****************** Start Point ******************")

                daq_num_rangelines  = cfg_dict["daq_num_rangelines"]
                daq_timeout         = cfg_dict["daq_timeout"]

                # a hysteresis parameter for turnaround
                # Note: nonzero turn_hyst will produce "wobble" at frame edges
                turn_hyst       = cfg_dict["turn_hyst"]
                turn_min_az     = cfg_dict["turn_min_az"]
                turn_max_az     = cfg_dict["turn_max_az"]
                ch0_offset      = cfg_dict["ch0_offset"]
                ch1_offset      = cfg_dict["ch1_offset"]
                daq_debug       = cfg_dict["daq_debug"]
                if type(daq_debug) == str:
                    if daq_debug.strip().lower() == "true":
                        daq_debug = True
                    else:
                        daq_debug = False

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
                                                  turn_min_az, turn_max_az, 
                                                  ch0_offset, ch1_offset, 
                                                  daq_timeout, daq_debug)

                # basically indicates the DAQ is not connected, pause a moment 
                # so the processor isn't thrashing around
                if status_flag in ["DAQ_NOT_CONNECTED", "CONN_RESET"]:
                    time.sleep(0.01)
                    continue

                # can gather a lot of metadata here
                # turnaround_inds not used right now

                if status_flag not in ["OK", "TIMEOUT"]:
                    print(status_flag)
                    error_pipe.send(["DAQ STATUS FLAG ERROR", status_flag])
                    continue 

                if num_rangelines == 0:
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
                    proc_start_time = time.time()
                coarse_grid_ovr = False
                coarse_grid_dict_in = None
                (frame_out, aux_data_out, new_frame_flag, frame_id_out, 
                 coarse_grid_dict_out) = proc_obj.postproc_data(rangelines_array, 
                                         az_array, el_array, ch_array, 
                                         turn_flag, reset_in_array, 
                                         cfg_dict, cfg_flags, None, 
                                         update_id, coarse_grid_dict_in, 
                                         coarse_grid_ovr, dbg_prof)
                                         

                if profiler_enabled:
                    end_time = time.time()
                    proc_time_ms = (end_time - proc_start_time) * 1000
                    print(f"    pixel processing time: {proc_time_ms:.4f}") 
                    tot_time_ms = (end_time - start_time) * 1000
                    if new_frame_flag:
                        print("    frame generated this snippet")
                    else:
                        print("    frame NOT generated this snippet")
                    print(f"Total Frame Snippet Process Time: {tot_time_ms:.4f} ms")
                    print("******************** End Point ********************\n")
                    

            elif cfg_dict["data_src"] == "dat_file":

                if ((cfg_dict["data0_fpath"] == None) and 
                    (cfg_dict["data1_fpath"] == None)):
                    time.sleep(0.01)
                    continue

                # these trigger the file to be parsed
                if (("fname_changed" in cfg_flags) or 
                   (file_params["buf_initialized"] == False) or
                   ("reload_file" in cfg_flags)):

                    query_out_dict = OrderedDict()
                    query_out_dict["FILE_PROCESSING"] = True
                    query_out_pipe.send(query_out_dict)

                    fs_adc = cfg_dict["fs_adc"]
                    fname_list = []
                    if cfg_dict["data0_fpath"] != None:
                        fname_list.append(cfg_dict["data0_fpath"])
                    if cfg_dict["data1_fpath"] != None:
                        fname_list.append(cfg_dict["data1_fpath"])

                    # grab the initial file data
                    # this can produce a massive amount of memory usage
                    (rangelines_array, el_array, az_array, ch_array, 
                     fs_post_dec, fft_flag, powcalc_flag, dec_val, 
                     len_rangeline, 
                     data_good) = dff.get_rangelines_from_file(fname_list, 
                                                               fs_adc)
            
                    file_params["buf_initialized"] = True
                    file_params["fs_post_dec"]   = fs_post_dec
                    file_params["fft_flag"]      = fft_flag
                    file_params["powcalc_flag"]  = powcalc_flag
                    file_params["dec_val"]       = dec_val
                    file_params["len_rangeline"] = len_rangeline
                    file_params["data_good"]     = data_good

                    # process the file directly and store the resulting 
                    # coarse grid in the file buffer
                    try:
                        coarse_grid_ovr = False
                        coarse_grid_dict_in = None
                        reset_in_array = False
                        (frame_out, aux_data_out, new_frame_flag, frame_id_out, 
                         file_coarse_grid_dict) = proc_obj.postproc_data(
                                             rangelines_array, 
                                             az_array, el_array, ch_array, 
                                             turn_flag, reset_in_array, 
                                             cfg_dict, cfg_flags, file_params, 
                                             update_id, coarse_grid_dict_in, 
                                             coarse_grid_ovr, dbg_prof)
                        
                        # delete these objects to minimize memory consumption
                        # when the files are massive 
                        del rangelines_array
                        del el_array
                        del az_array
                        del ch_array

                    except Exception as err_file_postproc:
                        print(err_file_postproc)
                        print("got to err_file_postproc")
                        ipdb.set_trace()
                        print("")
                        print("")
                        print("")
                        print("")
                        print("")




                else:
                    # only reprocess the frame if something actually changed
                    # otherwise throw in a short pause and do nothing
                    if "reproc_buf" not in cfg_flags:
                        time.sleep(0.005)
                        continue

                    # grab the stored data of the most recent file and 
                    # re-process it
                    rangelines_array    = file_buf["rangelines"]
                    el_array            = file_buf["elevation"]
                    az_array            = file_buf["azimuth"]
                    ch_array            = file_buf["channels"]
                    fs_post_dec         = file_params["fs_post_dec"]
                    fft_flag            = file_params["fft_flag"]
                    powcalc_flag        = file_params["powcalc_flag"]
                    dec_val             = file_params["dec_val"]
                    len_rangeline       = file_params["len_rangeline"]
                    data_good           = file_params["data_good"]

                turn_flag = "DISABLED"
                reset_in_array = False
                if not data_good:
                    error_pipe.send("FILE_FRAME_DATA_BAD")
                    new_frame_flag = False
                else:
                    coarse_grid_ovr = True
                    (frame_out, aux_data_out, new_frame_flag, frame_id_out, 
                     coarse_grid_dict_out) = proc_obj.postproc_data(
                                         None, None, None, None, 
                                         turn_flag, reset_in_array, 
                                         cfg_dict, cfg_flags, file_params, 
                                         update_id, file_coarse_grid_dict, 
                                         coarse_grid_ovr, dbg_prof)
                                             
            elif cfg_dict["data_src"] == "external_h5":
                h5_fpath = cfg_dict.get("external_h5_fpath")
                if h5_fpath is None:
                    time.sleep(0.01)
                    continue

                buf_frames_flag = False

                # only (re)load / reprocess when triggered
                if (("fname_changed" in cfg_flags) or
                    ("reproc_buf" in cfg_flags)):

                    query_out_dict = OrderedDict()
                    query_out_dict["FILE_PROCESSING"] = True
                    query_out_pipe.send(query_out_dict)

                    try:
                        power_cube, h5_meta = extl.load_h5_cube(h5_fpath)

                        # send spatial metadata to GUI so it can
                        # set up axis grids correctly
                        x_m = power_cube["x_coords_m"]
                        y_m = power_cube["y_coords_m"]
                        meta_dict = OrderedDict()
                        meta_dict["EXTERNAL_H5_META"] = {
                            "min_az": float(x_m[0])  * 100.0,
                            "max_az": float(x_m[-1]) * 100.0,
                            "min_el": float(y_m[0])  * 100.0,
                            "max_el": float(y_m[-1]) * 100.0,
                        }
                        query_out_pipe.send(meta_dict)

                        (frame_out, aux_data_out,
                         frame_id_out) = proc_obj.process_power_cube(
                                             power_cube, cfg_dict,
                                             update_id, dbg_prof)
                        new_frame_flag = True

                    except Exception as err_h5:
                        print(f"external_h5 load error: {err_h5}")
                        traceback.print_exc()
                        new_frame_flag = False

                else:
                    time.sleep(0.005)
                    continue

            else: #cfg_dict["data_src"] == "disabled":
                pass

            # send frame
            if new_frame_flag:
                data_src_out = cfg_dict["data_src"]
                data_out_pipe.send([frame_out, frame_id_out, data_src_out, 
                                    aux_data_out])

                # this indicates we're getting "new frames" and should buffer them
                if buf_frames_flag:
                    frame_buf_keys = frame_buffer.keys()
                    if len(frame_buf_keys) >= FRAME_BUF_MAX:
                        # remove the oldest frame in the buffer
                        del frame_buffer[list(frame_buf_keys)[0]]

                    frame_buffer[frame_id_out] = coarse_grid_dict_out

    except Exception as e2:
        print("\n\nGot to e2 exception point")
        print(e2)
        traceback.print_stack()
        ipdb.set_trace()
        print("")
        print("")
        print("")
        print("")
        print("")

##############################################################################
##############################################################################
##############################################################################

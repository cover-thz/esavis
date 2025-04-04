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

rsvd_pipe
    currently uncertain what's in here. But it feels like it should exist

frame_queue
    a queue object that contains an object that contains all relelvent frame
    data
""")
def main_processing_loop(cfg_obj_pipe, error_pipe, frame_pipe, 
                         aux_pipe, cfg_dict):


    radar       = dc.SimpRadar()
    daq_connected = False



    # setup everything 
    #   DAQ socket and sending that configuration
    #   xml thing.  Abstract away as much as possible
    #
    #   multiprocessing concurrent.futures stuff as desired

    while True:
        # do a status check of everything, the DAQ connection in particular
        # but anything that could periodically change asynchronously

        #####################################################################
        #                         SETUP CHANGES STEPS                       #
        #####################################################################
        if (cfg_obj_pipe.poll()):
            new_cfg_vals = cfg_obj_pipe.recv()

            # update the configuration
            for keyval in new_cfg_vals.keys():
                if keyval in cfg_dict.keys():
                    cfg_dict[keyval] = new_cfg_vals[keyval]
                if keyval in update_keys:
                    cfg_update = True
                else:
                    cfg_update = False
        
            # all new cfg_obj_pipe values have a flags dict
            # and we check the flags to see what we have to do 
            cfg_flags = new_cfg_vals["flags"]
            if ("setup_daq" in cfg_flags) or ("update_daq_ch" in cfg_flags):
                ch0_en = cfg_dict["ch0_en"]
                ch1_en = cfg_dict["ch1_en"]

                if not radar.daq_connected:
                    addr   = cfg_dict["daq_addr"]
                    conn_success = radar.setup_comms(addr, ch0_en, ch1_en)
                    if conn_success:
                        daq_connected = True
                    else:
                        error_pipe.send(["DAQ_CONN_FAILED"])
                else:
                    radar.set_en_channels(ch0_en, ch1_en)

        else: # no updated config values
            cfg_flags = None



        #####################################################################
        #                      DATA GATHERING STEPS                         #
        #####################################################################
        if cfg_dict["data_src"] == "daq":
            daq_num_rangelines = cfg_dict["daq_num_rangelines"]
            daq_timeout         = cfg_dict["daq_timeout"]
           
           # this step actually grabs the rangelines from the DAQ
           (rangelines_array, az_array, 
            el_array, ch_array, num_rangelines, 
            status_flag) = radar.get_daq_data(daq_num_rangelines, 
                           radar_timeout)

            # currently just trash everything that's not OK
            if status_flag != "OK":
                error_pipe.send(["DAQ STATUS FLAG NOT OK", status_flag])
                continue 

            if num_rangelines != daq_num_rangelines:
                rangelines_array = rangelines_array[:num_rangelines]
                az_array = az_array[:num_rangelines]
                el_array = el_array[:num_rangelines]
                ch_array = ch_array[:num_rangelines]

            (frame_out, aux_data_out, 
             new_frame_flag) = postproc_data(rangelines_array, az_array, 
                                             el_array, ch_array, cfg_dict, 
                                             cfg_flags)


        elif cfg_dict["data_src"] == "video_file"


        else: # cfg_dict["data_src"] == "still_file":
            if cfg_update:
                (frame_out, aux_data_out, new_frame_flag) = postproc_data(None, cfg_dict)


        # send frame
        if new_frame_flag
            frame_pipe.send(frame_out)


           


        # check for configuration / pipe data
        # 
        # check for DAQ or file.  
        # if file:
        #   If there's new config data, then re-process 
        #   the file, if not, then do nothing.
        #
        # if DAQ:
        #   DAQ data and put it in a buffer based on the "frame_style"
        #   parameters
        #
        #   if enough data has been gathered for a frame, process a frame 
        #   and update the appropriate "processed" state variables
        #










def 



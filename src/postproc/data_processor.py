#############################################################################
# File Name: data_processor.py
# Date Created: 4/1/2025
# Original Author: Max Bryk
# Description
#   This file contains the main body of code that grabs data from the radar 
#   DAQ subsystem and processes it into formats usable by the GUI
#
# Copyright Cover.ai 2025
#############################################################################

from tlv import (
    TLV,
    TLVMessage,
    TLVPlotCmd,
    TLVPlotTag,
    TLVTracePCIeHTGZRF80002Tag,
    TLVType,
)


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
    the data processor.  Its a "pile" of data that changes infrequently, like
    the number of x and y pixels.  It even includes things that change more 
    frequently like threshold and contrast values.  

    this could also contain file names for data files to process so we can 
    pipe the data files through this postprocessing algorithm as well
    
    This config pipe actually should contain tagged data where only new values
    are sent, to minimize the overhead 

flags_pipe 
    a lightweight variable that contains flags indicating various things like
    pause and resume.

rsvd_pipe
    currently uncertain what's in here. But it feels like it should exist

frame_queue
    a queue object that contains an object that contains all relelvent frame
    data


""")
def main_loop(cfg_obj_pipe, flags_pipe, rsvd_pipe, frame_queue, 
              aux_data_queue):
        
    # setup everything 
    #   DAQ socket and sending that configuration
    #   xml thing.  Abstract away as much as possible
    #
    #   multiprocessing concurrent.futures stuff as desired

    while True:
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



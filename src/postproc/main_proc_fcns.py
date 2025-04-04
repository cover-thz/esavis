#############################################################################
# File Name: data_proc_fcns.py
# Date Created: 4/1/2025
# Original Author: Max Bryk
# Description
#   contains helper functions for data_processor.py to abstract away as much
#   as possible to keep data_processor clean and understandable 
#
# Copyright Cover.ai 2025
#############################################################################

import ctypes as ct
import numpy as np
import ipdb
import time
import lower_proc_fcns as lpf
import os

            
def docstring(docstr):
    def assign_doc(f):
        f.__doc__ = docstr
        return f
    return assign_doc




class CoverProc:
    # coarse grids
    uninitialized  = True
    ideal_az_array = None
    ideal_el_array = None
    rng_len = None
    def __init__(s):
        s.rangeline_grid_data   = None
        s.rangeline_grid_valids = None


    # rangeline grid is the pre-processed "frame".  In the initial phase
    # of acquisiton we accumulate rangelines until the regridded rangelines
    # make a satisfactory frame (under certain conditions, such as azimuth
    # turnaround, % pixels, % columns, or just time) 
    # we accumulate those in the "rangeline_grid" variable
    def reset_rangeline_grid(s)
        # TODO maybe reset accumulation-related variables as well
        s.rangeline_grid_data   = np.zeros((s.xlen, s.ylen, s.rng_len), 
                                        dtype=np.float64)
        s.rangeline_grid_valids = np.zeros((s.xlen, s.ylen), dtype=bool)
        s.rangeline_grid_az     = np.zeros((s.xlen, s.ylen), dtype=np.float64)
        s.rangeline_grid_el     = np.zeros((s.xlen, s.ylen), dtype=np.float64)

    #def reset_frame(s):
    #    s.curr_frame_data   = np.zeros((s.xlen, s.ylen), dtype=np.float64)
    #    s.curr_frame_valids = np.zeros((s.xlen, s.ylen), dtype=bool)

    def postproc_data(s, rangelines_array, az_array, el_array, 
                      ch_array, cfg_dict, cfg_flags)
        dbg_prof = False # debug variable

        len_rangeline = len(rangelines_array[-1])
                                                 
        reset_proc = False
        if (uninitialized) or ("recalc_coarse_grid" in cfg_flags)):
            reset_proc = True

        elif len_rangeline != s.rng_len:
            s.rng_len       = len_rangeline
            reset_proc   = True


        if cfg_dict["data_src"] == "still_file":
            pass

        elif cfg_dict["data_src"] == "video_file":
            pass
        
        else: # cfg_dict["data_src"] == "daq"


            # if certain parameters are changed, it messes with everything
            # and buffers etc. have to be recalculated and all the 
            # accumulated rangelines get trashed.  This usually occurs when
            # the user makes a significant change to the system like
            # changing the rangeline length or number of pixels. 
            #
            # changing contrast, threshold, etc. should not trigger this, 
            if reset_proc:
                min_el = cfg_dict["min_el"]
                max_el = cfg_dict["max_el"]

                min_az = cfg_dict["min_az"] 
                max_az = cfg_dict["max_az"] 

                xlen = cfg_dict["xlen"]
                ylen = cfg_dict["ylen"]

                (ideal_az_array, 
                 ideal_el_array) = lpf.calc_coarse_grid(min_el, max_el, 
                                                    min_az, max_az, 
                                                    xlen, ylen)

                s.ideal_az_array = ideal_az_array
                s.ideal_el_array = ideal_el_array
                s.xlen           = xlen
                s.ylen           = ylen
                s.data_format_in = cfg_dict["data_format_in"]

                # have to reset the grid when making these adjustments
                s.reset_rangeline_grid()


                elev_side_0_start   = cfg_dict["elev_side_0_start"]
                elev_side_1_start   = cfg_dict["elev_side_1_start"]

                elev_side_0_end     = cfg_dict["elev_side_0_end"]
                elev_side_1_end     = cfg_dict["elev_side_1_end"]

                disable_el_side0    = cfg_dict["disable_el_side0"]
                disable_el_side1    = cfg_dict["disable_el_side1"]

                ch0_en              = cfg_dict["ch0_en"]
                ch1_en              = cfg_dict["ch1_en"]

                ch0_offset          = cfg_dict["ch0_offset"]
                ch1_offset          = cfg_dict["ch1_offset"]



                (coarse_rangelines_grid, coarse_valid_grid, ideal_az_array, 
                 ideal_el_array, real_az_out, 
                 real_el_out) = regrid_rangelines(rangelines_array, el_array, 
                                    az_array, ch_array, elev_side_0_start, 
                                    elev_side_0_end,  elev_side_1_start, 
                                    elev_side_1_end,  disable_el_side0, 
                                    disable_el_side1,  ch0_en, ch1_en, 
                                    ch0_offset, ch1_offset, s.ideal_az_array, 
                                    s.ideal_el_array,  s.xlen, s.ylen, 
                                    dbg_prof)
                                    
                                   
                                   
                                  
                                  
            # this compares the passed rangelines grid azimuth and elvation
            # values and evaluates how "close" they are to the ideal when
            # compared with the current "rangeline_grid_data"
            s.update_grid                                 


            # here we perform the checks to see if we've satisfied 
            # whatever conditions are required to move forward and perform
            # the remainder of the postprocessing


            #if cfg_dict["frame_style"] == "percent_col_filled":










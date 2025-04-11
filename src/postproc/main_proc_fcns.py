#############################################################################
# File Name: main_proc_fcns.py
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
import time
import lower_proc_fcns as lpf
import os
import ipdb
import collections
import plot_fcns as pf
            
def docstring(docstr):
    def assign_doc(f):
        f.__doc__ = docstr
        return f
    return assign_doc


class CoverProc:
    # coarse grids
    uninitialized   = True
    ideal_az_array  = None
    ideal_el_array  = None
    rng_len         = None
    rng_dtype       = None
    def __init__(s):
        s.r_grid_data   = None
        s.r_grid_valids = None
        s.last_az       = None
        s.accum_rangelines = 0

    def reset_coarse_grids(s, coarse_az_1d, coarse_el_1d, 
                    ideal_az_array, ideal_el_array, xlen, ylen, 
                    data_format_in):
        s.coarse_az_1d = coarse_az_1d
        s.coarse_el_1d = coarse_el_1d

        s.ideal_az_array = ideal_az_array
        s.ideal_el_array = ideal_el_array
        s.xlen           = xlen
        s.ylen           = ylen
        s.data_format_in = data_format_in
        s.uninitialized = False

    # rangeline grid is the pre-processed "frame".  In the initial phase
    # of acquisiton we accumulate rangelines until the regridded rangelines
    # make a satisfactory frame (under certain conditions, such as azimuth
    # turnaround, % pixels, % columns, or just time) 
    # we accumulate those in the "rangeline_grid" variable
    def clear_preproc_buffer(s):
        s.accum_rangelines = 0

        if s.rng_dtype == object:
            print_str  = "Warning: rangeline datatype is 'object'"
            print_str += "this may produce unexpected errors"
            print(print_str)

        s.r_grid_data   = np.zeros((s.xlen, s.ylen, s.rng_len), 
                                  dtype=s.rng_dtype)
        s.r_grid_valids = np.zeros((s.xlen, s.ylen), dtype=bool)
        s.r_grid_az     = np.zeros((s.xlen, s.ylen), dtype=np.float64)
        s.r_grid_el     = np.zeros((s.xlen, s.ylen), dtype=np.float64)

    #def reset_frame(s):
    #    s.curr_frame_data   = np.zeros((s.xlen, s.ylen), dtype=np.float64)
    #    s.curr_frame_valids = np.zeros((s.xlen, s.ylen), dtype=bool)

    # Main Workhorse Function
    def postproc_data(s, rangelines_array, az_array, el_array, 
                      ch_array, turn_flag, reset_in_array, cfg_dict, 
                      cfg_flags, dbg_prof=False):

        #################################################################
        #        Grab Some Data and Check for Reset Conditions          #
        #################################################################

        len_rangeline = len(rangelines_array[-1])
        rng_dtype = rangelines_array.dtype
                                                 
        num_rangelines = len(rangelines_array)
        s.accum_rangelines += num_rangelines
        #print(f"accumulated rangelines: {s.accum_rangelines}")
        if dbg_prof:
            #print(f"accumulated rangelines: {s.accum_rangelines}")
            pass

        reset_proc = False
        if ((s.uninitialized) or ("recalc_coarse_grid" in cfg_flags)):
            reset_proc = True

        # if rangeline length changed
        if len_rangeline != s.rng_len:
            s.rng_len       = len_rangeline
            reset_proc   = True


        # if rangeline data type changed
        if s.rng_dtype != rng_dtype:
            s.rng_dtype = rng_dtype
            reset_proc = True


        if cfg_dict["frame_style"] == "azimuth_turnaround":
            if reset_in_array:
                reset_proc = True
            elif turn_flag == "RESET":
                reset_proc = True



        # NOTE TODO DATA IDEALLY SHOULDN'T AFFECT THIS FUNCTION
        # Work on this later
        if cfg_dict["data_src"] == "dat_file":
            pass

        # work on this later
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

                (coarse_az_1d, coarse_el_1d, ideal_az_array, 
                 ideal_el_array) = lpf.calc_coarse_grid(min_el, max_el, 
                                                    min_az, max_az, 
                                                    xlen, ylen)

                data_format_in = cfg_dict["data_format_in"]

                # have to reset the grid when making these adjustments
                s.reset_coarse_grids(coarse_az_1d, coarse_el_1d, 
                    ideal_az_array, ideal_el_array, xlen, ylen, 
                    data_format_in)
                
                # this 
                s.clear_preproc_buffer()

            #################################################################
            #                        Regridding Steps                       #
            #################################################################
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


            (new_rangelines_grid, new_valid_grid, ideal_az_array, 
             ideal_el_array, new_az_out, 
             new_el_out) = lpf.regrid_rangelines(rangelines_array, el_array, 
                                az_array, ch_array, elev_side_0_start, 
                                elev_side_0_end,  elev_side_1_start, 
                                elev_side_1_end,  disable_el_side0, 
                                disable_el_side1,  ch0_en, ch1_en, 
                                ch0_offset, ch1_offset, s.coarse_az_1d, 
                                s.coarse_el_1d,  s.xlen, s.ylen, 
                                dbg_prof)
            
            num_valids = np.sum(new_valid_grid)
            if dbg_prof:
                #print(f"pre update_grid valids: {num_valids}")
                pass

            # this compares the passed rangelines grid azimuth and elvation
            # values and evaluates how "close" they are to the ideal when
            # compared with the current "rangeline_grid_data"
            (r_grid_out, valid_grid_out, grid_az_out, 
             grid_el_out) = lpf.update_grid(new_rangelines_grid, 
                                new_valid_grid, new_az_out, new_el_out, 
                                s.r_grid_data, s.r_grid_valids, s.r_grid_az, 
                                s.r_grid_el, s.ideal_az_array, 
                                s.ideal_el_array)

            num_valids = np.sum(valid_grid_out)
            if dbg_prof:
                #print(f"post update_grid valids: {num_valids}")
                pass

            s.r_grid_data   = r_grid_out
            s.r_grid_valids = valid_grid_out
            s.r_grid_az     = grid_az_out
            s.r_grid_el     = grid_el_out


            # here we perform the checks to see if we've satisfied 
            # whatever conditions are required to move forward and perform
            # the remainder of the postprocessing

            #################################################################
            #             Check if frame should be processed                #
            #################################################################

            process_frame = False
            if cfg_dict["frame_style"] == "percent_col_filled":
                curr_col_percent = lpf.check_col_percent(s.r_grid_valids)
                if curr_col_percent >= cfg_dict["percent_filled_thresh"]:
                    process_frame = True

            elif cfg_dict["frame_style"] == "percent_pix_filled":
                curr_percent = lpf.check_pix_percent(s.r_grid_valids)
                if curr_percent >= cfg_dict["percent_filled_thresh"]:
                    process_frame = True

            elif cfg_dict["frame_style"] == "azimuth_turnaround":
                if turn_flag == "END_FRAME":
                    process_frame = True

            elif cfg_dict["frame_style"] == "accum_rangelines":
                if s.accum_rangelines >= cfg_dict["accum_rangelines_thresh"]:
                    process_frame = True

            elif cfg_dict["frame_style"] == "always":
                process_frame = True


            #################################################################
            #                         Process frame                         #
            #################################################################

            if process_frame:
                # first we perform our spectral conversions
                data_format_in  = cfg_dict["data_format_in"]
                fft_len         = cfg_dict["fft_len"]
                fs_post_dec     = cfg_dict["fs_post_dec"]
                (coarse_power_grid, 
                 freq_lut) = lpf.spectra_conv(s.r_grid_data, 
                                data_format_in, fft_len, fs_post_dec)

                chirp_span      = cfg_dict["chirp_span"]
                chirp_time      = cfg_dict["chirp_time"]
                center_rangeval = cfg_dict["center_rangeval"]
                range_lut_cm    = lpf.calc_range(freq_lut, chirp_span, 
                                    chirp_time, center_rangeval)

                threshold_lin   = cfg_dict["threshold_lin"]
                contrast_lin    = cfg_dict["contrast_lin"]
                half_peak_width = cfg_dict["half_peak_width"]
                peak_selection  = cfg_dict["peak_selection"]
                num_noise_pts   = cfg_dict["num_noise_pts"]
                noise_start_frac    = cfg_dict["noise_start_frac"]
                calc_weighted_sum   = cfg_dict["calc_weighted_sum"]
                min_range       = cfg_dict["min_range"]
                max_range       = cfg_dict["max_range"]
                dead_pix_val    = cfg_dict["dead_pix_val"]

                (pixel_ranges_grid, valid_pixels_grid, 
                 noise_floor_grid) = lpf.extract_peaks_c(coarse_power_grid, 
                                        s.r_grid_valids, s.xlen, s.ylen, 
                                        fft_len, range_lut_cm, 
                                        threshold_lin, contrast_lin, 
                                        half_peak_width, peak_selection, 
                                        num_noise_pts, noise_start_frac, 
                                        calc_weighted_sum, min_range, 
                                        max_range, dead_pix_val, dbg_prof)                   
                if dbg_prof:
                    num_valids = np.sum(valid_pixels_grid)
                    print(f"num_valid_pixels: {num_valids}")
                #pf.plot_pixel_power(coarse_power_grid[10][10].astype(np.float64), range_lut_cm)

                # frame data
                frame_out = collections.OrderedDict()
                frame_out["pixel_ranges_grid"]  = pixel_ranges_grid
                frame_out["valid_pixels_grid"]  = valid_pixels_grid
                frame_out["noise_floor_grid"]   = noise_floor_grid


                # aux data
                aux_x_ind = cfg_dict["aux_x_ind"]
                aux_y_ind = cfg_dict["aux_y_ind"]
                aux_rngline = s.r_grid_data[aux_x_ind][aux_y_ind]


                (aux_peak_ranges, aux_peak_powers_lin, aux_noise_floor, 
                 aux_num_peaks, aux_adj_lin_thresh, aux_adj_lin_contr, 
                 aux_weight_sum_start, 
                 aux_weight_sum_end) = lpf.extract_aux_vals(aux_rngline, 
                    range_lut_cm, threshold_lin, contrast_lin, 
                    half_peak_width, min_range, max_range, 
                    num_noise_pts, noise_start_frac, 
                    calc_weighted_sum)

                aux_data_out = collections.OrderedDict()
                aux_data_out["aux_peak_ranges"] = aux_peak_ranges
                aux_data_out["aux_peak_powers_lin"] = aux_peak_powers_lin
                aux_data_out["aux_noise_floor"]     = aux_noise_floor
                aux_data_out["aux_num_peaks"]       = aux_num_peaks
                aux_data_out["aux_adj_lin_thresh"]  = aux_adj_lin_thresh
                aux_data_out["aux_adj_lin_contr"]   = aux_adj_lin_contr
                aux_data_out["aux_weight_sum_start"] = aux_weight_sum_start
                aux_data_out["aux_weight_sum_end"]  = aux_weight_sum_end

                new_frame_flag = True


                # clear the preprocessed buffer now that we've processed the 
                # frame
                s.clear_preproc_buffer()

            else:
                frame_out       = None
                aux_data_out    = None
                new_frame_flag  = False

            return (frame_out, aux_data_out, new_frame_flag) 



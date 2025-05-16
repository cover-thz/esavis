import collections
import subprocess
import numpy as np
import time
import ipdb
import math
import os


#"""
#if __name__ == '__main__':
#    CWD = os.getcwd() 
#    if os.name == "nt":
#        # remake the makefile
#        c_funcs_dir = CWD + "\\c_funcs"
#        result = subprocess.run(["make"], cwd=c_funcs_dir)
#    elif os.name == "posix":
#        # remake the makefile
#        c_funcs_dir = CWD + "/c_funcs"
#        result = subprocess.run(["make"], cwd=c_funcs_dir)
#    else:
#        raise Exception("Invalid OS Name")
#"""

import main_proc_fcns as mpf
import lower_proc_fcns as lpf
#import OLD__postproc_fcns as OLD
import plot_fcns as pf
import dat_file_fcns as dff


# this tests a different DAQ file with power-spectrum data over a longer
# period of time
if __name__ == "__main__":

    # this is a simple script that tests running the data_processor
    cfg_dict = collections.OrderedDict()

    cfg_dict["ch0_en"]      = True
    cfg_dict["ch1_en"]      = False
    cfg_dict["daq_addr"]    = "localhost"
    cfg_dict["data_src"]    = "daq"

    cfg_dict["daq_num_rangelines"] = 5000
    cfg_dict["daq_timeout"] = 3
    cfg_dict["frame_style"] = "accum_rangelines"
    #cfg_dict["frame_style"] = "always"
    cfg_dict["accum_rangelines_thresh"] = 900000

    fs_adc = 4e9
    dec_val = 4
    cfg_dict["fs_adc"]  = fs_adc
    cfg_dict["dec_val"] = dec_val
    FPATH  = "C:/Users/mbryk/Documents/tracetech/contracts/Cover_ai/"
    FPATH += "Work_Product/sw_dev_and_repos/THzVis/data/"
    cfg_dict["fname_list"] = [FPATH + "20241030_135847_Channel0_0000.dat"]


    cfg_dict["min_el"] = 0
    cfg_dict["max_el"] = 1005

    cfg_dict["min_az"] = -250
    cfg_dict["max_az"] = 250

    cfg_dict["xlen"] = 40
    cfg_dict["ylen"] = 80

    cfg_dict["data_format_in"] = "power_spectrum"

    cfg_dict["el_side_0_start"] = 1860
    cfg_dict["el_side_1_start"] = 1860+8192

    cfg_dict["el_side_0_end"] = 1860+2000
    cfg_dict["el_side_1_end"] = 1860+8192+2000

    cfg_dict["disable_el_side0"] = False
    cfg_dict["disable_el_side1"] = False

    cfg_dict["el_offset0"] = 12
    cfg_dict["el_offset1"] = 0

    cfg_dict["ch0_en"] = True
    cfg_dict["ch1_en"] = False

    cfg_dict["ch0_offset"] = 0
    cfg_dict["ch1_offset"] = 0

    # first we perform our spectral conversions
    cfg_dict["fft_len"] = 256
    cfg_dict["fs_post_dec"] = fs_post_dec = fs_adc/(16*(dec_val))


    cfg_dict["chirp_span"] = 28.8e9
    cfg_dict["chirp_time"] = 4e-6
    cfg_dict["center_rangeval"] = 400

    threshold_db        = 15
    contrast_db         = 1
    # calculate the linear values of threshold and contrast
    threshold_lin   = np.float64(10**(threshold_db/10))
    contrast_lin    = np.float64(10**(contrast_db/10))

    cfg_dict["threshold_lin"]   = threshold_lin
    cfg_dict["contrast_lin"]    = contrast_lin

    cfg_dict["half_peak_width"] = 2
    cfg_dict["peak_selection"] = "back"

    cfg_dict["num_noise_pts"] = 10
    cfg_dict["noise_start_frac"] = 0.0

    cfg_dict["calc_weighted_sum"] = False

    cfg_dict["min_range"] = 250
    cfg_dict["max_range"] = 500
    cfg_dict["dead_pix_val"] = 1000

    # aux data
    cfg_dict["aux_x_ind"] = 7
    cfg_dict["aux_y_ind"] = 21
    cfg_flags = []
    cfg_dict["cfg_flags"] = cfg_flags


    file_params = collections.OrderedDict()



    # calculate the coarse grids here as well
    min_az  = cfg_dict["min_az"]
    max_az  = cfg_dict["max_az"]
    min_el  = cfg_dict["min_el"]
    max_el  = cfg_dict["max_el"]
    xlen    = cfg_dict["xlen"]
    ylen    = cfg_dict["ylen"]
    coarse_az_array = np.linspace(min_az, max_az, xlen)
    coarse_el_array = np.linspace(min_el, max_el, ylen)

    proc_obj = mpf.CoverProc()
    fs_adc     = cfg_dict["fs_adc"]
    fname_list = cfg_dict["fname_list"]


    # now I'm going to parse the file
    (rangelines, elevation, azimuth, channels, 
     fs_post_dec, fft_flag, powcalc_flag, dec_val, 
     len_rangeline, 
     data_good) = dff.get_rangelines_from_file(fname_list, fs_adc)
                                              
    sl_rng_len = cfg_dict["daq_num_rangelines"]
    num_slices = int(math.floor(len(rangelines)/sl_rng_len))

    rangelines_gathered = 0
    for slice_ind in range(num_slices-1):
        rangelines_gathered += sl_rng_len
        start_ind       = slice_ind*sl_rng_len
        stop_ind        = (slice_ind+1)*(sl_rng_len)

        rangelines_array  = rangelines[start_ind:stop_ind]
        az_array        = azimuth[start_ind:stop_ind]
        el_array        = elevation[start_ind:stop_ind]
        ch_array        = channels[start_ind:stop_ind]
        turn_flag       = False
        reset_in_array  = False
        dbg_prof        = False
        #dbg_prof = True
        cfg_flags = cfg_dict["cfg_flags"]
        

        (frame_out, aux_data_out, 
         new_frame_flag, frame_id_out) = proc_obj.postproc_data(
                            rangelines_array, 
                            az_array, el_array, ch_array, 
                            turn_flag, reset_in_array, cfg_dict, 
                            cfg_flags, file_params, dbg_prof)

        #if not new_frame_flag:
            #print(f"rangelines_gathered: {rangelines_gathered}!")
        if new_frame_flag:
            break

    rangelines_array = rangelines[:]
    az_array         = azimuth[:]
    el_array         = elevation[:]
    ch_array         = channels[:]
    turn_flag  = False
    cfg_flags        = cfg_dict["cfg_flags"]

    ########################################################################
    ########################################################################

    pixel_ranges_grid   = frame_out["pixel_ranges_grid"]
    valid_pixels_grid   = frame_out["valid_pixels_grid"]
    noise_floor_grid    = frame_out["noise_floor_grid"]

    ########################################################################
    ########################################################################


    color_min = min(pixel_ranges_grid[valid_pixels_grid])
    color_max = max(pixel_ranges_grid[valid_pixels_grid])
    #color_min = np.min(valid_pixels_grid)
    #color_max = np.max(valid_pixels_grid)

    #pf.plot_img_vals(valid_pixels_grid, coarse_az_array, coarse_el_array, 
    #        color_min, color_max, "Test 1!")
    pf.plot_img_vals(pixel_ranges_grid, coarse_az_array, coarse_el_array, 
            color_min, color_max, "Test 1!")



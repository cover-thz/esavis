

import main_proc_fcns as mpf
import lower_proc_fcns as lpf
import OLD__postproc_fcns as OLD
import collections
import plot_fcns as pf
import dat_file_fcns as dff
import numpy as np
import time
import ipdb
import math


if __name__ == "__main__":
    # this is a simple script that tests running the data_processor
    cfg_dict = collections.OrderedDict()

    cfg_dict["ch0_en"]      = True
    cfg_dict["ch1_en"]      = False
    cfg_dict["daq_addr"]    = "localhost"
    cfg_dict["data_src"]    = "daq"

    cfg_dict["daq_num_rangelines"] = 98000
    cfg_dict["daq_timeout"] = 3
    #cfg_dict["frame_style"] = "accum_rangelines"
    cfg_dict["frame_style"] = "always"
    cfg_dict["accum_rangelines_thresh"] = 98000

    fs_adc = 4e9
    dec_val = 1
    cfg_dict["fs_adc"]  = fs_adc
    cfg_dict["dec_val"] = dec_val
    fs_post_dec = fs_adc/(16*(dec_val))
    cfg_dict["fs_post_dec"] = fs_post_dec

    FPATH  = "C:/Users/mbryk/Documents/tracetech/contracts/Cover_ai/"
    FPATH += "Work_Product/sw_dev_and_repos/THzVis/data/"
    cfg_dict["fname_list"] = [FPATH + "20240930_143346_Channel0_0000.dat"]


    cfg_dict["min_el"] = 0
    cfg_dict["max_el"] = 1108

    cfg_dict["min_az"] = -280
    cfg_dict["max_az"] = 280

    cfg_dict["xlen"] = 40
    cfg_dict["ylen"] = 80

    cfg_dict["data_format_in"] = "time_domain"


    cfg_dict["elev_side_0_start"] = 1790
    cfg_dict["elev_side_1_start"] = 1790+8192

    cfg_dict["elev_side_0_end"] = 1790+2000
    cfg_dict["elev_side_1_end"] = 1790+8192+2000

    cfg_dict["disable_el_side0"] = False
    cfg_dict["disable_el_side1"] = False

    cfg_dict["el_side0_offs"] = 12
    cfg_dict["el_side1_offs"] = 0

    cfg_dict["ch0_en"] = True
    cfg_dict["ch1_en"] = False

    cfg_dict["ch0_offset"] = 0
    cfg_dict["ch1_offset"] = 0

    # first we perform our spectral conversions
    cfg_dict["fft_len"] = 2048


    cfg_dict["chirp_span"] = 28.8e9
    cfg_dict["chirp_time"] = 4e-6
    cfg_dict["center_rangeval"] = 400

    threshold_db        = 15
    contrast_db         = 11
    # calculate the linear values of threshold and contrast
    threshold_lin   = np.float64(10**(threshold_db/10))
    contrast_lin    = np.float64(10**(contrast_db/10))

    cfg_dict["threshold_lin"]   = threshold_lin
    cfg_dict["contrast_lin"]    = contrast_lin

    cfg_dict["half_peak_width"] = 2
    cfg_dict["peak_selection"] = "back"

    cfg_dict["num_noise_pts"] = 101
    cfg_dict["noise_start_frac"] = 0.2

    cfg_dict["calc_weighted_sum"] = False

    cfg_dict["min_range"] = 360
    cfg_dict["max_range"] = 420
    cfg_dict["dead_pix_val"] = 1000

    # aux data
    cfg_dict["aux_x_ind"] = 7
    cfg_dict["aux_y_ind"] = 21
    cfg_flags = []
    cfg_dict["cfg_flags"] = cfg_flags




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
                                              
    #sl_rng_len = cfg_dict["daq_num_rangelines"]
    #num_slices = int(math.floor(len(rangelines)/sl_rng_len))

    #rangelines_gathered = 0
    #for slice_ind in range(num_slices-1):
    #    rangelines_gathered += sl_rng_len
    #    start_ind       = slice_ind*sl_rng_len
    #    stop_ind        = (slice_ind+1)*(sl_rng_len)

    #    rangelines_array  = rangelines[start_ind:stop_ind]
    #    az_array        = azimuth[start_ind:stop_ind]
    #    el_array        = elevation[start_ind:stop_ind]
    #    ch_array        = channels[start_ind:stop_ind]
    #    turnaround_flag = False
    #    dbg_prof = False
    #    cfg_flags = cfg_dict["cfg_flags"]

    #    (frame_out, aux_data_out, 
    #     new_frame_flag) = proc_obj.postproc_data(
    #                        rangelines_array, 
    #                        az_array, el_array, ch_array, 
    #                        turnaround_flag, cfg_dict, 
    #                        cfg_flags, dbg_prof)

    #    if not new_frame_flag:
    #        print(f"rangelines_gathered: {rangelines_gathered}!")
    #    if new_frame_flag:
    #        break

    rangelines_array = rangelines[:]
    az_array         = azimuth[:]
    el_array         = elevation[:]
    ch_array         = channels[:]
    turnaround_flag  = False
    dbg_prof         = False
    cfg_flags        = cfg_dict["cfg_flags"]

    ########################################################################
    ########################################################################
    (coarse_az_1d, coarse_el_1d, ideal_az_array, 
     ideal_el_array) = lpf.calc_coarse_grid(min_el, max_el, 
                                        min_az, max_az, 
                                        xlen, ylen)


    elev_side_0_start = cfg_dict["elev_side_0_start"]
    elev_side_0_end = cfg_dict["elev_side_0_end"]
    elev_side_1_start = cfg_dict["elev_side_1_start"]
    elev_side_1_end = cfg_dict["elev_side_1_end"]
    disable_el_side0 = cfg_dict["disable_el_side0"]
    disable_el_side1 = cfg_dict["disable_el_side1"]
    ch0_en = cfg_dict["ch0_en"]
    ch1_en = cfg_dict["ch1_en"]
    ch0_offset = cfg_dict["ch0_offset"]
    ch1_offset = cfg_dict["ch1_offset"]

    min_el = cfg_dict["min_el"]
    max_el = cfg_dict["max_el"]

    min_az = cfg_dict["min_az"]
    max_az = cfg_dict["max_az"]

    rng_len = len(rangelines_array[0])
    (new_rangelines_grid, new_valid_grid, ideal_az_array, 
     ideal_el_array) = OLD.regrid_rangelines(rangelines_array, el_array, 
                        az_array, ch_array, elev_side_0_start, 
                        elev_side_0_end,  elev_side_1_start, 
                        elev_side_1_end,  disable_el_side0, 
                        disable_el_side1,  ch0_en, ch1_en, 
                        ch0_offset, ch1_offset, min_el, max_el, 
                        min_az, max_az, xlen, ylen, dbg_prof)
                        

    #(new_rangelines_grid, new_valid_grid, ideal_az_array, 
    # ideal_el_array, new_az_out, 
    # new_el_out) = lpf.regrid_rangelines(rangelines_array, el_array, 
    #                    az_array, ch_array, elev_side_0_start, 
    #                    elev_side_0_end,  elev_side_1_start, 
    #                    elev_side_1_end,  disable_el_side0, 
    #                    disable_el_side1,  ch0_en, ch1_en, 
    #                    ch0_offset, ch1_offset, coarse_az_1d, 
    #                    coarse_el_1d,  xlen, ylen, 
    #                    dbg_prof)



    data_format_in  = cfg_dict["data_format_in"]
    fft_len         = cfg_dict["fft_len"] 
    fs_post_dec     = cfg_dict["fs_post_dec"]

    (coarse_power_grid, 
     freq_lut) = lpf.spectra_conv(new_rangelines_grid,
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
                            new_valid_grid, xlen, ylen, 
                            fft_len, range_lut_cm, 
                            threshold_lin, contrast_lin, 
                            half_peak_width, peak_selection, 
                            num_noise_pts, noise_start_frac, 
                            calc_weighted_sum, min_range, 
                            max_range, dead_pix_val, dbg_prof)                   


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



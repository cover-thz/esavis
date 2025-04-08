

import multiprocessing as mp
import data_processor as dp
import collections
import plot_fcns as pf
import numpy as np
import time
import ipdb


if __name__ == "__main__":
    # this is a simple script that tests running the data_processor
    cfg_dict = collections.OrderedDict()

    cfg_dict["ch0_en"]      = True
    cfg_dict["ch1_en"]      = False
    cfg_dict["daq_addr"]    = "localhost"
    cfg_dict["data_src"]    = "daq"

    cfg_dict["daq_num_rangelines"] = 4000
    cfg_dict["daq_timeout"] = 3
    #cfg_dict["frame_style"] = "azimuth_turnaround"
    #cfg_dict["frame_style"] = "always"
    cfg_dict["frame_style"] = "accum_rangelines"
    cfg_dict["accum_rangelines_thresh"] = 96000


    fs_adc = 4e9
    dec_val = 1
    cfg_dict["fs_adc"]  = fs_adc
    cfg_dict["dec_val"] = dec_val
    #cfg_dict["fname_list"]


    cfg_dict["min_el"] = 0
    cfg_dict["max_el"] = 1005

    cfg_dict["min_az"] = -250
    cfg_dict["max_az"] = 250

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
    cfg_dict["fs_post_dec"] = fs_post_dec = fs_adc/(16*(dec_val))


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


    # calculate the coarse grids here as well
    min_az  = cfg_dict["min_az"]
    max_az  = cfg_dict["max_az"]
    min_el  = cfg_dict["min_el"]
    max_el  = cfg_dict["max_el"]
    xlen    = cfg_dict["xlen"]
    ylen    = cfg_dict["ylen"]
    coarse_az_array = np.linspace(min_az, max_az, xlen)
    coarse_el_array = np.linspace(min_el, max_el, ylen)

    (dp_cfg_pipe, main_cfg_pipe)    = mp.Pipe(duplex=False)
    (main_err_pipe, dp_err_pipe)    = mp.Pipe(duplex=False)
    (main_data_pipe, dp_data_pipe)  = mp.Pipe(duplex=False)

    proc = mp.Process(target=dp.main_proc_loop, args=(dp_cfg_pipe, 
        dp_err_pipe, dp_data_pipe, cfg_dict,))
    proc.start()

    i = 0
    daq_setup_flag = False
    while True:   
        if (main_data_pipe.poll()):
            i = 0
            [frame_out, aux_data_out] = main_data_pipe.recv()
            if frame_out != None:
                pixel_ranges_grid   = frame_out["pixel_ranges_grid"]
                valid_pixels_grid   = frame_out["valid_pixels_grid"]
                noise_floor_grid    = frame_out["noise_floor_grid"]
            else:
                print("frame_out is None")

            color_min = min(pixel_ranges_grid[valid_pixels_grid])
            color_max = max(pixel_ranges_grid[valid_pixels_grid])
            #color_min = np.min(valid_pixels_grid)
            #color_max = np.max(valid_pixels_grid)

            pf.plot_img_vals(pixel_ranges_grid, coarse_az_array, coarse_el_array, 
                    color_min, color_max, "Test 1!")
        else:
            i += 1
            if (i >= 50 and (not daq_setup_flag)):
                i = 0
                print("setting up DAQ...")
                cfg_params = collections.OrderedDict()
                cfg_params["flags"] = ["setup_daq"]
                main_cfg_pipe.send(cfg_params)
                daq_setup_flag = True

            if (i >= 200):
                print("closing things down...")
                cfg_params = collections.OrderedDict()
                cfg_params["flags"] = ["close_process"]
                main_cfg_pipe.send(cfg_params)
                break



        time.sleep(0.1)

    proc.join()


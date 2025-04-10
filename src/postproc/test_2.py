

import multiprocessing as mp
import data_processor as dp
import collections
import plot_fcns as pf
import numpy as np
import time
import matplotlib.pyplot as plt
import ipdb


# this tests a different DAQ file with power-spectrum data over a longer
# period of time
if __name__ == "__main__":
    # this is a simple script that tests running the data_processor
    cfg_dict = collections.OrderedDict()

    cfg_dict["ch0_en"]      = True
    cfg_dict["ch1_en"]      = False
    cfg_dict["daq_addr"]    = "localhost"
    cfg_dict["data_src"]    = "daq"

    #cfg_dict["daq_num_rangelines"] = 27100
    cfg_dict["daq_num_rangelines"] = 10000
    cfg_dict["daq_timeout"] = 3
    #cfg_dict["frame_style"] = "azimuth_turnaround"
    #cfg_dict["frame_style"] = "always"
    cfg_dict["frame_style"] = "accum_rangelines"
    cfg_dict["accum_rangelines_thresh"] = 27100


    fs_adc = 4e9
    dec_val = 4
    cfg_dict["fs_adc"]  = fs_adc
    cfg_dict["dec_val"] = dec_val
    #cfg_dict["fname_list"]


    cfg_dict["min_el"] = 0
    cfg_dict["max_el"] = 1005

    cfg_dict["min_az"] = -250
    cfg_dict["max_az"] = 250

    cfg_dict["xlen"] = 40
    cfg_dict["ylen"] = 80

    cfg_dict["data_format_in"] = "power_spectrum"


    cfg_dict["elev_side_0_start"] = 1860
    cfg_dict["elev_side_1_start"] = 1860+8192

    cfg_dict["elev_side_0_end"] = 1860+2000
    cfg_dict["elev_side_1_end"] = 1860+8192+2000

    cfg_dict["disable_el_side0"] = False
    cfg_dict["disable_el_side1"] = False

    cfg_dict["el_side0_offs"] = 12
    cfg_dict["el_side1_offs"] = 0

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
    cfg_dict["noise_start_frac"] = 0.9

    cfg_dict["calc_weighted_sum"] = False

    cfg_dict["min_range"] = 250
    cfg_dict["max_range"] = 500
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

    daq_setup_flag = False

    # construct the image plot:
    az_min = coarse_az_array.min()
    az_max = coarse_az_array.max()

    el_min = coarse_el_array.min()
    el_max = coarse_el_array.max()

    colormap_val = "jet_r"
    fig, ax = plt.subplots()
    
    plt_title = "Plotting some data using the fake DAQ"
    color_min = None
    color_max = None
    thz_image_vals = np.zeros((xlen,ylen))
    img_obj = plt.imshow(thz_image_vals.T, extent=[az_min, az_max, el_min, el_max],
                                    aspect='equal', origin='lower', 
                                    cmap=colormap_val, vmin=color_min, 
                                    vmax=color_max)
    plt.gca().invert_xaxis()  # Reverse x-axis
    plt.gca().invert_yaxis()  # Reverse y-axis
    plt.colorbar(label='range (cm)')
    plt.xlabel('interp. Az encoder vals')
    plt.ylabel('interp. El encoder vals from start')
    plt.title(plt_title)
    fig.set_figheight(6)
    fig.tight_layout()
    fig.canvas.draw()
    plt.show(block=False)
    pause_len = 0.01
    plt.pause(pause_len)
    fig.canvas.draw()


    prev_time = time.time()
    while True:   
        plt.pause(pause_len)
        if (main_data_pipe.poll()):
            [frame_out, aux_data_out] = main_data_pipe.recv()
            if frame_out != None:
                curr_time = time.time()
                time_elapsed_ms = (curr_time - prev_time)*1000
                #print(f"Time elapsed since last frame: {time_elapsed_ms:.4f} ms")
                prev_time = curr_time
                pixel_ranges_grid   = frame_out["pixel_ranges_grid"]
                valid_pixels_grid   = frame_out["valid_pixels_grid"]
                noise_floor_grid    = frame_out["noise_floor_grid"]

                color_min = min(pixel_ranges_grid[valid_pixels_grid])
                color_max = max(pixel_ranges_grid[valid_pixels_grid])
                #color_min = np.min(valid_pixels_grid)
                #color_max = np.max(valid_pixels_grid)

                img_obj.set_data(pixel_ranges_grid.T)
                img_obj.set_clim(vmin=color_min, vmax=color_max)
                fig.canvas.draw()
            else:
                print("frame_out is None")


        else:
            curr_time = time.time()
            time_elapsed_ms = (curr_time - prev_time)*1000
            if ((time_elapsed_ms > 5000) and (not daq_setup_flag)):
                print("setting up DAQ...")
                cfg_params = collections.OrderedDict()
                cfg_params["flags"] = ["setup_daq", "enable_profiler"]
                #cfg_params["flags"] = ["setup_daq"]
                main_cfg_pipe.send(cfg_params)
                daq_setup_flag = True

            if (time_elapsed_ms > 10000):
                print("closing things down...")
                cfg_params = collections.OrderedDict()
                cfg_params["flags"] = ["close_process"]
                main_cfg_pipe.send(cfg_params)
                break

        time.sleep(0.1)
    plt.close(fig)
    proc.join()


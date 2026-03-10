#############################################################################
# File Name: main_proc_fcns.py
# Date Created: 4/1/2025
# Original Author: Max Bryk
# Description
#   Contains the CoverProc class with process_power_cube() which performs
#   peak finding on a PowerCube and returns frame + aux data for the GUI.
#
# Copyright Cover.ai 2025
#############################################################################

import ctypes as ct
import numpy as np
import time
import lower_proc_fcns as lpf
import os
import collections
from power_cube import make_power_cube


class CoverProc:
    def __init__(s):
        s.frame_id = 0

    ###################################################################
    #  Stage B: PowerCube → frame_out + aux_data                      #
    ###################################################################
    def process_power_cube(s, power_cube, cfg_dict, update_id,
                           dbg_prof=False):
        """
        Accepts a PowerCube (see power_cube.py) and runs peak finding /
        integrated-power extraction to produce frame_out and aux_data_out
        suitable for the GUI.

        Parameters
        ----------
        power_cube : OrderedDict  (from make_power_cube)
        cfg_dict   : dict
        update_id  : int
        dbg_prof   : bool

        Returns
        -------
        (frame_out, aux_data_out, frame_id_out)
        """
        coarse_power_grid = power_cube["power_grid"]
        valid_grid        = power_cube["valid_mask"]
        range_lut_cm      = power_cube["range_lut_cm"]

        xlen = coarse_power_grid.shape[0]
        ylen = coarse_power_grid.shape[1]
        fft_len = coarse_power_grid.shape[2]

        threshold_lin     = cfg_dict["threshold_lin"]
        contrast_lin      = cfg_dict["contrast_lin"]
        half_peak_width   = cfg_dict["half_peak_width"]
        peak_selection    = cfg_dict["peak_selection"]
        num_noise_pts     = cfg_dict["num_noise_pts"]
        noise_start_frac  = cfg_dict["noise_start_frac"]
        calc_weighted_sum = cfg_dict["calc_weighted_sum"]
        min_range         = cfg_dict["min_range"]
        max_range         = cfg_dict["max_range"]
        dead_pix_val      = cfg_dict["dead_pix_val"]
        plot_style        = cfg_dict["plot_style"]

        if dbg_prof:
            peak_start = time.time_ns()

        if plot_style == "integ_power_plot":
            (pixel_grid,
             valid_pixels_grid) = lpf.calc_integ_pwr(coarse_power_grid,
                                      valid_grid, range_lut_cm,
                                      dead_pix_val, min_range, max_range)
            noise_floor_grid = np.zeros(pixel_grid.shape)
        else:
            (pixel_grid, valid_pixels_grid,
             noise_floor_grid) = lpf.extract_peaks_c(coarse_power_grid,
                                     valid_grid, xlen, ylen,
                                     fft_len, range_lut_cm,
                                     threshold_lin, contrast_lin,
                                     half_peak_width, peak_selection,
                                     num_noise_pts, noise_start_frac,
                                     calc_weighted_sum, min_range,
                                     max_range, dead_pix_val, dbg_prof)

        if dbg_prof:
            peak_end = time.time_ns()
            dur_ms = (peak_end - peak_start) / 1e6
            print(f"    process_power_cube peak finding: {dur_ms:.4f} ms")
            num_valids = np.sum(valid_pixels_grid)
            print(f"    num_valid_pixels: {num_valids}")

        # frame data
        frame_out = collections.OrderedDict()
        frame_out["pixel_grid"]        = pixel_grid
        frame_out["valid_pixels_grid"] = valid_pixels_grid
        frame_out["noise_floor_grid"]  = noise_floor_grid
        frame_out["update_id"]         = update_id

        # aux data
        aux_x_ind = cfg_dict["aux_x_ind"]
        aux_y_ind = cfg_dict["aux_y_ind"]

        frame_id_out = s.frame_id
        s.frame_id += 1

        try:
            aux_power_spectra = coarse_power_grid[aux_x_ind][aux_y_ind]

            if type(aux_power_spectra) != type(None):
                (aux_peak_ranges, aux_peak_powers_lin, aux_noise_floor,
                 aux_num_peaks, aux_adj_lin_thresh, aux_adj_lin_contr,
                 aux_weight_sum_start,
                 aux_weight_sum_end) = lpf.extract_aux_vals(
                    aux_power_spectra,
                    range_lut_cm, threshold_lin, contrast_lin,
                    half_peak_width, min_range, max_range,
                    num_noise_pts, noise_start_frac,
                    calc_weighted_sum)

            aux_data_out = collections.OrderedDict()
            aux_data_out["data_valid"]      = True
            aux_data_out["x_ind"]           = aux_x_ind
            aux_data_out["y_ind"]           = aux_y_ind
            aux_data_out["aux_az_val"]      = cfg_dict["aux_az_val"]
            aux_data_out["aux_el_val"]      = cfg_dict["aux_el_val"]
            aux_data_out["power_spectra"]   = aux_power_spectra
            aux_data_out["range_lut_cm"]    = range_lut_cm
            aux_data_out["peak_ranges"]     = aux_peak_ranges
            aux_data_out["peak_powers_lin"] = aux_peak_powers_lin
            aux_data_out["noise_floor"]     = aux_noise_floor
            aux_data_out["num_peaks"]       = aux_num_peaks
            aux_data_out["adj_lin_thresh"]  = aux_adj_lin_thresh
            aux_data_out["adj_lin_contr"]   = aux_adj_lin_contr
            aux_data_out["weight_sum_start"] = aux_weight_sum_start
            aux_data_out["weight_sum_end"]  = aux_weight_sum_end
            aux_data_out["min_range"]       = min_range
            aux_data_out["max_range"]       = max_range

            noise_ind_start = int(round(noise_start_frac * fft_len, 2))
            noise_ind_end = noise_ind_start + num_noise_pts - 1
            aux_data_out["noise_ind_start"] = noise_ind_start
            aux_data_out["noise_ind_end"]   = noise_ind_end
            aux_data_out["frame_id"]        = frame_id_out

        except Exception:
            print("invalid aux_power_spectra data")
            aux_data_out = collections.OrderedDict()
            aux_data_out["data_valid"]      = False
            aux_data_out["x_ind"]           = aux_x_ind
            aux_data_out["y_ind"]           = aux_y_ind
            aux_data_out["aux_az_val"]      = cfg_dict["aux_az_val"]
            aux_data_out["aux_el_val"]      = cfg_dict["aux_el_val"]
            aux_data_out["power_spectra"]   = None
            aux_data_out["range_lut_cm"]    = range_lut_cm
            aux_data_out["peak_ranges"]     = None
            aux_data_out["peak_powers_lin"] = None
            aux_data_out["noise_floor"]     = None
            aux_data_out["num_peaks"]       = None
            aux_data_out["adj_lin_thresh"]  = None
            aux_data_out["adj_lin_contr"]   = None
            aux_data_out["weight_sum_start"] = None
            aux_data_out["weight_sum_end"]  = None
            aux_data_out["min_range"]       = None
            aux_data_out["max_range"]       = None
            aux_data_out["noise_ind_start"] = None
            aux_data_out["noise_ind_end"]   = None
            aux_data_out["frame_id"]        = None

        return (frame_out, aux_data_out, frame_id_out)

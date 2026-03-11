#############################################################################
# File Name: lower_proc_fcns.py
# Date Created: 4/1/2025
# Original Author: Max Bryk
# Description
#   contains lower level functions that support main_proc_fcns.py
#   to keep main_prof_fcns clean and readable.  This includes setup and
#   calling of the C peakfinding code
#
# Copyright Cover.ai 2025
#############################################################################

import ctypes as ct
import numpy as np
import time
import os
import copy


# C function imports 
##############################################################################
CFUNCS_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), 
                'c_funcs'))
if os.name == "nt":
    c_peak_fcns_lib = ct.CDLL(CFUNCS_DIR + "\\peak_find_fcns.dll")
elif os.name == "posix":
    c_peak_fcns_lib = ct.CDLL(CFUNCS_DIR + "/peak_find_fcns.so")
else:
    raise Exception("Invalid OS Name")


extract_single_rangeline_peaks  = c_peak_fcns_lib.extract_single_rangeline_peaks
extract_all_rangeline_peaks     = c_peak_fcns_lib.extract_all_rangeline_peaks
extract_aux_data                = c_peak_fcns_lib.extract_aux_data

extract_single_rangeline_peaks.argtypes = [ct.POINTER(ct.c_double), 
    ct.c_int, ct.POINTER(ct.c_double), ct.c_double, ct.c_double, ct.c_int, 
    ct.c_double, ct.c_double, ct.c_int, ct.c_double, ct.POINTER(ct.c_int), 
    ct.c_bool, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), 
    ct.POINTER(ct.c_double), ct.POINTER(ct.c_int)]
extract_single_rangeline_peaks.restype = ct.c_int

extract_all_rangeline_peaks.argtypes = [ct.POINTER(ct.c_double), 
    ct.POINTER(ct.c_bool), ct.c_int, ct.c_int, ct.POINTER(ct.c_double), 
    ct.c_double, ct.c_double, ct.c_int, ct.c_double, ct.c_double, ct.c_int, 
    ct.c_double, ct.c_bool, ct.c_bool, ct.POINTER(ct.c_double), 
    ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_int), 
    ct.POINTER(ct.c_double)]
extract_all_rangeline_peaks.restype = ct.c_int


extract_aux_data.argtypes = [ct.POINTER(ct.c_double), 
    ct.c_int, ct.POINTER(ct.c_double), ct.c_double, ct.c_double, ct.c_int, 
    ct.c_double, ct.c_double, ct.c_int, ct.c_double,  
    ct.c_bool, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), 
    ct.POINTER(ct.c_double), ct.POINTER(ct.c_int), ct.POINTER(ct.c_double),
    ct.POINTER(ct.c_double), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]
extract_aux_data.restype = ct.c_int

##############################################################################
##############################################################################


def calc_integ_pwr(coarse_power_grid, valid_grid, range_lut_cm, dead_pix_val, 
                   min_range, max_range):
    """
    coarse_power_grid.shape = (num_az_pix, num_el_pix, rangeline_len)
    valid_grid.shape = (num_az_pix, num_el_pix)
    range_lut_cm.shape = (rangeline_len)
    
    Inefficiently implemented, but unlikely to be a bottleneck and is
    especially not a bottleneck for real-time processing

    """
    # find the valid indices
    range_mask = (range_lut_cm >= min_range) & (range_lut_cm <= max_range)
    coarse_power_grid_masked = coarse_power_grid[:,:,range_mask]
    integ_power_grid_int1 = 10*np.log10(coarse_power_grid_masked.sum(axis=2))

    # update valid grid based on any weird values experienced here
    valid_grid_out = copy.deepcopy(valid_grid)
    new_invalids = np.where(integ_power_grid_int1 == -np.inf)
    valid_grid_out[new_invalids] = False

    new_invalids = np.where(integ_power_grid_int1 == np.inf)
    valid_grid_out[new_invalids] = False

    new_invalids = np.where(integ_power_grid_int1 == np.nan)
    valid_grid_out[new_invalids] = False
          

    integ_power_grid = np.empty(coarse_power_grid.shape[:-1])
    integ_power_grid.fill(dead_pix_val)
    integ_power_grid[valid_grid_out] = integ_power_grid_int1[valid_grid_out]

    return (integ_power_grid, valid_grid_out)


##############################################################################
##############################################################################

# extracts some data from a single rangeline calculation
def extract_aux_vals(rangeline_power_in, range_lut_cm_in, threshold_lin_in, 
    contrast_lin_in, half_peak_width_in, min_range_in, max_range_in, 
    num_noise_pts_in, noise_start_frac_in, calc_weighted_sum_in):
    """
    what aux values do I want?
        stuff we can get without the C code
            the power spectrum
            time domain (if it exists)
            FFT (if it exists)
            calc_weighted_sum flag
            noise floor value
            noise floor indices

        stuff we need to get from the C dcode
            adjusted linear threshold
            adjusted linear contrast "threshold"
            weighted_sum indices


    """

    # convert the arguments to ctypes objects to pass to the C functions
    #
    rng_len_in = len(rangeline_power_in)
    rangeline_power = rangeline_power_in.flatten()   
    rangeline_power = rangeline_power.ctypes.data_as(ct.POINTER(ct.c_double))
    
    rng_len = ct.c_int(rng_len_in)

    #range_lut_cm_in = np.array(range_lut_cm_in, dtype=np.float64)
    range_lut_cm = range_lut_cm_in.flatten()   
    range_lut_cm = range_lut_cm.ctypes.data_as(ct.POINTER(ct.c_double))

    threshold_lin   = ct.c_double(threshold_lin_in)
    contrast_lin    = ct.c_double(contrast_lin_in)
    half_peak_width = ct.c_int(half_peak_width_in)
    min_range       = ct.c_double(min_range_in)
    max_range       = ct.c_double(max_range_in)
    num_noise_pts   = ct.c_int(num_noise_pts_in)
    noise_start_frac    = ct.c_double(noise_start_frac_in)
    calc_weighted_sum   = ct.c_bool(calc_weighted_sum_in)


    # "return" values
    #
    peak_ranges   = np.empty(rng_len_in)
    peak_ranges   = peak_ranges.ctypes.data_as(ct.POINTER(ct.c_double))

    peak_powers_lin   = np.empty(rng_len_in)
    peak_powers_lin   = peak_powers_lin.ctypes.data_as(ct.POINTER(ct.c_double))

    noise_floor = np.empty(1).ctypes.data_as(ct.POINTER(ct.c_double))

    num_peaks = np.empty(1).ctypes.data_as(ct.POINTER(ct.c_int))

    adj_lin_thresh      = np.empty(1).ctypes.data_as(ct.POINTER(ct.c_double))
    adj_lin_contr       = np.empty(1).ctypes.data_as(ct.POINTER(ct.c_double))
    weight_sum_start    = np.empty(1).ctypes.data_as(ct.POINTER(ct.c_int))
    weight_sum_end      = np.empty(1).ctypes.data_as(ct.POINTER(ct.c_int))


    ##########################################################################
    ##########################################################################
    # call the actual C function
    ret_val = extract_aux_data(rangeline_power, rng_len, range_lut_cm, 
                threshold_lin, contrast_lin, half_peak_width, min_range, 
                max_range, num_noise_pts, noise_start_frac, calc_weighted_sum,
                peak_ranges, peak_powers_lin, noise_floor, num_peaks, 
                adj_lin_thresh, adj_lin_contr, weight_sum_start, 
                weight_sum_end)
    ##########################################################################
    ##########################################################################

    # unpack the output variables
    peak_ranges_py        = np.ctypeslib.as_array(peak_ranges, (rng_len_in,))
    peak_powers_lin_py    = np.ctypeslib.as_array(peak_powers_lin, 
                                (rng_len_in,))
    noise_floor_py        = np.float64(noise_floor.contents)
    num_peaks_py          = np.int32(num_peaks.contents)
    adj_lin_thresh_py     = np.float64(adj_lin_thresh.contents)
    adj_lin_contr_py      = np.float64(adj_lin_contr.contents)
    weight_sum_start_py   = np.int32(weight_sum_start.contents)
    weight_sum_end_py     = np.int32(weight_sum_end.contents)

    return (peak_ranges_py, peak_powers_lin_py, noise_floor_py, num_peaks_py,
            adj_lin_thresh_py, adj_lin_contr_py, weight_sum_start_py, 
            weight_sum_end_py)


##############################################################################
##############################################################################

def extract_peaks_c(coarse_power_grid_in, coarse_valid_grid_in, xlen_in, 
    ylen_in, rng_len_in, range_lut_cm_in, threshold_lin_in, contrast_lin_in, 
    half_peak_width_in, peak_selection, num_noise_pts_in, 
    noise_start_frac_in, calc_weighted_sum_in, min_range_in, max_range_in,
    dead_pix_val, dbg_prof=False):

    # note that rng_len_in here refers to the rangeline POST FFT, so more 
    # accurately the FFT length.  This is an example of some nomenclature 
    # that should be fixed

    if peak_selection.lower() == "back":
        back_peak_bool_in = True
    else:
        back_peak_bool_in = False # indicates front peak

    # convert the arguments to ctypes objects to pass to the C functions
    #
    power_array = coarse_power_grid_in.flatten()   
    power_array = power_array.ctypes.data_as(ct.POINTER(ct.c_double))

    valid_array = coarse_valid_grid_in.flatten()   
    valid_array = valid_array.ctypes.data_as(ct.POINTER(ct.c_bool))
    
    arr_len_in = xlen_in*ylen_in
    arr_len = ct.c_int(arr_len_in)
    rng_len = ct.c_int(rng_len_in)

    #range_lut_cm_in = np.array(range_lut_cm_in, dtype=np.float64)
    range_lut_cm = range_lut_cm_in.flatten()   
    range_lut_cm = range_lut_cm.ctypes.data_as(ct.POINTER(ct.c_double))

    threshold_lin   = ct.c_double(threshold_lin_in)
    contrast_lin    = ct.c_double(contrast_lin_in)
    half_peak_width = ct.c_int(half_peak_width_in)
    min_range       = ct.c_double(min_range_in)
    max_range       = ct.c_double(max_range_in)
    num_noise_pts   = ct.c_int(num_noise_pts_in)
    noise_start_frac    = ct.c_double(noise_start_frac_in)
    calc_weighted_sum   = ct.c_bool(calc_weighted_sum_in)
    back_peak_bool_in   = ct.c_bool(back_peak_bool_in)


    # "return" values
    #
    tot_num_samples_len_in = arr_len_in * rng_len_in
    
    peak_ranges_array   = np.empty(tot_num_samples_len_in)
    peak_ranges_array   = peak_ranges_array.ctypes.data_as(ct.POINTER(ct.c_double))

    peak_powers_lin_array   = np.empty(tot_num_samples_len_in)
    peak_powers_lin_array   = peak_powers_lin_array.ctypes.data_as(ct.POINTER(ct.c_double))

    noise_floor_array   = np.empty(arr_len_in)
    noise_floor_array   = noise_floor_array.ctypes.data_as(ct.POINTER(ct.c_double))

    num_peaks_array   = np.empty(arr_len_in)
    num_peaks_array   = num_peaks_array.ctypes.data_as(ct.POINTER(ct.c_int))

    sel_ranges_array_out   = np.empty(arr_len_in)
    sel_ranges_array_out   = sel_ranges_array_out.ctypes.data_as(ct.POINTER(ct.c_double))


    ###########################################################################
    ###########################################################################
    #if dbg_prof:
    #    cfunc_start = time.time_ns()
    # call the C functions
    ret_val = extract_all_rangeline_peaks(power_array, valid_array, arr_len, 
        rng_len, range_lut_cm, threshold_lin, contrast_lin, half_peak_width, 
        min_range, max_range, num_noise_pts, noise_start_frac, 
        calc_weighted_sum, back_peak_bool_in, peak_ranges_array, 
        peak_powers_lin_array, noise_floor_array, num_peaks_array, 
        sel_ranges_array_out) 
    cfunc_stop = time.time_ns()
    #if dbg_prof:
    #    cfcn_time_ms = float(cfunc_stop - cfunc_start) / 1e6
    #    print(f"        C function only duration: {cfcn_time_ms:.4f} ms")
    ###########################################################################
    ###########################################################################

    # unpack the output variables
    num_peaks_array_py          = np.ctypeslib.as_array(num_peaks_array, 
        (xlen_in, ylen_in,))
    peak_ranges_array_py        = np.ctypeslib.as_array(peak_ranges_array, 
        (xlen_in, ylen_in, rng_len_in))
    peak_powers_lin_array_py    = np.ctypeslib.as_array(peak_powers_lin_array,
        (xlen_in, ylen_in, rng_len_in))
    noise_floor_grid            = np.ctypeslib.as_array(noise_floor_array, 
        (xlen_in, ylen_in,))
    pixel_ranges_grid           = np.ctypeslib.as_array(sel_ranges_array_out, 
        (xlen_in, ylen_in,))

    # this argument will have been changed too
    valid_pixels_grid           = np.ctypeslib.as_array(valid_array, 
        (xlen_in, ylen_in,))

    for i in range(xlen_in):
        for j in range(ylen_in):
            if not valid_pixels_grid[i][j]:
                pixel_ranges_grid[i][j] = dead_pix_val

    return (pixel_ranges_grid, valid_pixels_grid, noise_floor_grid)

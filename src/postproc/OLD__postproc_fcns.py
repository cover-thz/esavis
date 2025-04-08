#############################################################################
# File Name: postproc_fcns.py
# Date Created: 2/5/2025
# Original Author: Max Bryk
# Description
#   This file contains postprocessing functions including "workhorse" 
#   functions, "helper" functions, and fucntions that ultimately link to 
#   compiled C functions that should remain mostly "under the hood" while the 
#   functions in "postproc.py" remain the "user-facing" functions
#
# Copyright Cover.ai 2025
#############################################################################

import ctypes as ct
import numpy as np
import ipdb
import time
import os
import subprocess


# C function imports 
##############################################################################
# remake the makefile
CWD = os.getcwd() 
c_funcs_dir = CWD + "\\c_funcs"
result = subprocess.run(["make"], cwd=c_funcs_dir)

c_peak_fcns_lib = ct.CDLL(CWD + "\\c_funcs\\peak_find_fcns.dll")
extract_single_rangeline_peaks  = c_peak_fcns_lib.extract_single_rangeline_peaks
extract_all_rangeline_peaks     = c_peak_fcns_lib.extract_all_rangeline_peaks

extract_single_rangeline_peaks.argtypes = [ct.POINTER(ct.c_double), 
    ct.c_int, ct.POINTER(ct.c_double), ct.c_double, ct.c_double, ct.c_int, 
    ct.c_double, ct.c_double, ct.c_int, ct.c_double, ct.POINTER(ct.c_int), 
    ct.c_bool, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), 
    ct.POINTER(ct.c_double), ct.POINTER(ct.c_int)]
extract_single_rangeline_peaks.restype = ct.c_int
    
# alternative (that I do not believe would actually work):
#ct_dbl_ptr = ct.POINTER(ct.c_double)
#ct_int = ct.c_int
#ct_dbl = ct.c_double
#ct_int_ptr = ct.POINTER(ct.c_int)
#ct_bool = ct.c_bool
#ct_bool_ptr = ct.POINTER(ct.c_bool)
# 
#extract_single_rangeline_peaks.argtypes = [ct_dbl_ptr, ct_int, ct_dbl_ptr, 
#    ct_dbl, ct_dbl, ct_int_ptr, ct_dbl, ct_dbl, ct_int, ct_dbl, ct_int_ptr, 
#    ct_bool, ct_dbl_ptr, ct_dbl_ptr, ct_dbl_ptr, ct_int_ptr]
#    

extract_all_rangeline_peaks.argtypes = [ct.POINTER(ct.c_double), 
    ct.POINTER(ct.c_bool), ct.c_int, ct.c_int, ct.POINTER(ct.c_double), 
    ct.c_double, ct.c_double, ct.c_int, ct.c_double, ct.c_double, ct.c_int, 
    ct.c_double, ct.c_bool, ct.c_bool, ct.POINTER(ct.c_double), 
    ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_int), 
    ct.POINTER(ct.c_double)]
extract_all_rangeline_peaks.restype = ct.c_int


##############################################################################


def calc_range(freq_lut, chirp_span, chirp_time, center_rangeval):
    """
    calculates range in centimeters

    """
    
    clight_cm = 2.998e10 # cm/s
    #time_diff = 2*range / clight_cm 
    # the factor of 2 is because the distance is from the radar to 
    # the object then back to the radar

    # range = time_diff * clight_cm / 2

    #chirpspan = 28.8e9
    k_chirp = chirp_span / chirp_time # this is frequency change in Hz per 
                                      # second of chirp time

    
    # time_diff = frequency / k_chirp 
    # coefficient to apply to the frequency lut to get the ranges at each
    # frequency is:

    #f2r_coeff = clight / 2 / Kchirp / (len_rangeline/fft_len) / oversamp
    f2r_coeff = clight_cm / (k_chirp * 2)


    # now we apply the coefficient and add the center_rangeval so our
    # focal point is annotated as "center_rangeval" centimeters
    range_lut_cm = np.array((freq_lut * f2r_coeff) + center_rangeval)

    return range_lut_cm



def pulse_az_el_adj(el_val_in, az_val_in, channel_val_in, 
    elev_side_0_start, elev_side_0_end, elev_side_1_start, elev_side_1_end, 
    disable_el_side0, disable_el_side1, ch0_en, ch1_en, ch0_offset, 
    ch1_offset):
    """
    While the raw elevation and azimuth values do provide useful information
    for the location of each radar rangeline, due to various offsets and other 
    idiosyncrasies in the radar, they do not describe the location of each
    radar rangeline in a straightforward manner.  So this function will use
    some parameters along with elevation and azimuth encoder values to create 
    an "adjusted" version of the azimuth and elevation output to make it 
    easier to fit the values to a grid later

    additionally it outputs a "valid_rangeline" variable which indicates if 
    the pulse whould be marked for removal or not due to if it's from a 
    disabled channel, or if the side of the elevation mirror that the 
    rangeline is from is disabled.  
    """

    # starts valid unless invalid properties are found later
    valid_rangeline = True

    # elevation checks and adjustment 
    if ((el_val_in >= elev_side_0_start) and 
        (el_val_in <= elev_side_0_end) and (not disable_el_side0)):
        el_mirror_side = 0
        el_val_out = el_val_in - elev_side_0_start
    elif ((el_val_in >= elev_side_1_start) and 
          (el_val_in <= elev_side_1_end) and (not disable_el_side1)):
        el_mirror_side = 1
        el_val_out = el_val_in - elev_side_1_start
    else: 
        el_mirror_side  = None
        valid_rangeline = False


    # check to see if we keep this rangeline due to mirror side exlusions
    if disable_el_side0 and (el_mirror_side == 0):
        valid_rangeline = False
    elif disable_el_side1 and (el_mirror_side == 1):
        valid_rangeline = False


    # check to see if we keep this rangeline due to channel exclusions
    if (not ch0_en) and (channel_val_in == 0):
        valid_rangeline = False
    elif (not ch1_en) and (channel_val_in == 1):
        valid_rangeline = False


    # azimuth checks and adjustment 
    if channel_val_in == 0:
        az_val_out = az_val_in + ch0_offset
    elif channel_val_in == 1:
        az_val_out = az_val_in + ch1_offset
    else:
        raise Exception("Invalid channel value")

    return (valid_rangeline, el_val_out, el_mirror_side, az_val_out)



def adj_rangelines(rangelines_in, el_array_in, az_array_in, channels_in, 
    elev_side_0_start, elev_side_0_end, elev_side_1_start, elev_side_1_end, 
    disable_el_side0, disable_el_side1, ch0_en, ch1_en, ch0_offset, 
    ch1_offset): 
    """
    this takes the raw rangelines, elevation, and azimuth encoder values in
    and performs the appropriate adjustments based on elevation mirror encoder
    start points and azimuth offsets due to multiple channels and removes
    the appropriate rangelines that are disabled based on mirror side or 
    channel.  

    Then the resulting "trimmed" rangeline set is produced and 
    ready to be re-gridded (in a different function)
    """

    rangelines_out           = []
    el_array_out             = []
    az_array_out             = []
    channels_out             = []
    el_mirror_side_array_out = []

    for i in range(len(rangelines_in)):
        (valid_rangeline, el_val_out, 
            el_mirror_side, az_val_out) = pulse_az_el_adj(el_array_in[i], 
            az_array_in[i], channels_in[i], elev_side_0_start, elev_side_0_end, 
            elev_side_1_start, elev_side_1_end, disable_el_side0, 
            disable_el_side1, ch0_en, ch1_en, ch0_offset, ch1_offset)
    
        if not valid_rangeline:
            continue
        else:
            rangelines_out.append(rangelines_in[i])
            el_array_out.append(el_val_out)
            az_array_out.append(az_val_out)
            channels_out.append(channels_in[i])
            el_mirror_side_array_out.append(el_mirror_side)

    return (rangelines_out, el_array_out, az_array_out, channels_out,
            el_mirror_side_array_out)
    


def calc_coarse_grid(min_elev, max_elev, min_az, max_az, num_x_pixels, 
    num_y_pixels):
    """
    This calculates the elevation and azimuth coarse grid which is used 
    to identify the closest rangeline to each pixel in the dataset then 
    strip away all the other rangelines 

    Arguments
        min_elev
            minimum adjusted elevation value, which should be 0 if the 
            starting elevation should be right at elev_side_x_start where x 
            is 0 or 1 depending upon which side of the mirror we're on

        max_elev
            maximum adjusted elevation value.  Is set by the user to define
            the elevation span desired.  

        min_az
            minimum adjusted azimuth value.  Note that this must take into 
            account the offsets incorporated by using the two pixel system

        max_az
            maximum adjusted azimuth value.  Note that this must take into 
            account the offsets incorporated by using the two pixel system

        num_x_pixels
            number of pixels in the x direction (number of columns)

        num_y_pixels
            number of pixels in the y direction (number of rows)

    """

    coarse_az_array = np.linspace(min_az, max_az, num_x_pixels)
    coarse_el_array = np.linspace(min_elev, max_elev, num_y_pixels)

    return (coarse_az_array, coarse_el_array)
   

def calc_coarse_rangelines_grid(coarse_az_array, coarse_el_array, 
        el_array_adj, az_array_adj, rangelines_adj, 
        coarse_valid_grid, coarse_rangelines_grid, npts_az, npts_el):

    min_coarse_az = min(coarse_az_array)
    max_coarse_az = max(coarse_az_array)

    min_coarse_el = min(coarse_el_array)
    max_coarse_el = max(coarse_el_array)

    el_ind_coeff = (npts_el-1) / (max_coarse_el - min_coarse_el)
    az_ind_coeff = (npts_az-1) / (max_coarse_az - min_coarse_az)

    # need to create large array of "nearby values"
    # assume it's 10 times the "average" oversampling rate
    # this shouldn't be a problem
    max_loc_pts = int(len(rangelines_adj) / (npts_az * npts_el) * 10)
    local_rngln_inds = np.zeros((npts_az, npts_el, max_loc_pts), dtype=int)
    local_az_vals    = np.zeros((npts_az, npts_el, max_loc_pts), dtype=int)
    local_el_vals    = np.zeros((npts_az, npts_el, max_loc_pts), dtype=int)

    # this holds how many points are in each "local_rangeline_inds_matrix" 
    # location as the length of that array is not the number actually filled
    num_local_pts_matrix = np.zeros((npts_az, npts_el), dtype=int)


    # iterate through each rangeline
    for i in range(len(el_array_adj)):
        elev = el_array_adj[i]
        azi  = az_array_adj[i]

        # nearest indices
        n_az_ind = int(round(((azi- min_coarse_az) * az_ind_coeff)))
        n_el_ind = int(round(((elev - min_coarse_el) * el_ind_coeff)))


        # number of points also doubles as the next empty index
        next_ind = num_local_pts_matrix[n_az_ind][n_el_ind]

        # assign the value and increment the number of local points there
        local_rngln_inds[n_az_ind][n_el_ind][next_ind] = i
        local_az_vals[n_az_ind][n_el_ind][next_ind] = azi
        local_el_vals[n_az_ind][n_el_ind][next_ind] = elev

        num_local_pts_matrix[n_az_ind][n_el_ind] += 1


    # iterate through each pixel and find the nearest rangeline
    for i in range(len(coarse_az_array)):
        for j in range(len(coarse_el_array)):
            num_loc_pts = num_local_pts_matrix[i][j]
            el_array_loc = local_el_vals[i][j][:num_loc_pts]
            az_array_loc = local_az_vals[i][j][:num_loc_pts]

            dist_arr = (el_array_loc-coarse_el_array[j])**2 + \
                       (az_array_loc-coarse_az_array[i])**2 

            # closest index in local arrays
            if len(dist_arr) > 0:
                ind_n = np.argmin(dist_arr)

                # rangeline index
                rng_ind = local_rngln_inds[i][j][ind_n]
                nearest_rangeline = rangelines_adj[rng_ind]

                coarse_rangelines_grid[i][j] = nearest_rangeline
                coarse_valid_grid[i][j] = True

            else:
                coarse_valid_grid[i][j] = False

    return (coarse_rangelines_grid, coarse_valid_grid)







# NOTE TODO fill out the docstring
def regrid_rangelines(rangelines_in, el_array_in, az_array_in, channels_in, 
    elev_side_0_start, elev_side_0_end, elev_side_1_start, elev_side_1_end, 
    disable_el_side0, disable_el_side1, ch0_en, ch1_en, ch0_offset, ch1_offset, 
    min_elev, max_elev, min_az, max_az,
    num_x_pixels, num_y_pixels, dbg_prof=False):

    """
    While the raw elevation and azimuth values do provide useful information
    for the location of each radar rangeline, due to various offsets and other 
    idiosyncrasies in the radar, they do not describe the location of each
    radar rangeline in a straightforward manner.  So this function will use
    some parameters along with elevation and azimuth encoder values to create 
    an "adjusted" version of the azimuth and elevation output to make it 
    easier to fit the values to a grid later


    NOTE TODO 
    NOTE TODO 
    NOTE TODO 
    
    I need to fix this so it properly describes all forms of trimming, both 
    el and az out of range trimming as well as regridding trimming
    Also I need to finish putting the body of the first for loop in another 
    function

    NOTE TODO 
    NOTE TODO 
    NOTE TODO 

    """
    #manual_el_limits = True
    #manual_az_limits = True
    manual_el_limits = False
    manual_az_limits = False


    if dbg_prof:
        regrid_start = time.time()

    # first make initial adjustments to the rangelines el and az 
    # encoder values etc.
    (rangelines_adj, el_array_adj, az_array_adj, channels_adj, 
        el_mirror_side_array_adj) = adj_rangelines(rangelines_in, el_array_in, 
        az_array_in, channels_in, elev_side_0_start, elev_side_0_end, 
        elev_side_1_start, elev_side_1_end, disable_el_side0, 
        disable_el_side1, ch0_en, ch1_en, ch0_offset, ch1_offset)

    # now generate the coarse grid
    if not manual_el_limits:
        min_elev = min(el_array_adj)
        max_elev = max(el_array_adj)

    if not manual_az_limits:
        min_az = min(az_array_adj)
        max_az = max(az_array_adj)
    
    (coarse_az_array, coarse_el_array) = calc_coarse_grid(min_elev, max_elev, 
        min_az, max_az, num_x_pixels, num_y_pixels)


    # Each rangeline must be the same size 
    coarse_rangelines_grid = np.zeros((coarse_az_array.shape[0], 
                            coarse_el_array.shape[0], rangelines_adj[0].shape[0]),
                            dtype=type(rangelines_adj[0][0]))

    # this will flag any data that is not present.  This allows us to avoid
    # certain problems associated with using NaNs to flag "empty" pixels
    coarse_valid_grid = np.zeros((coarse_az_array.shape[0], 
                            coarse_el_array.shape[0]), dtype=bool)

    if dbg_prof:
        time_1 = time.time()
        print(f"    regrid functions set 1 duration: {time_1-regrid_start:.4f}")


    #old_code = True
    old_code = False
    if old_code:
        # iterate through each pixel and find the nearest rangeline
        for i in range(len(coarse_az_array)):
            for j in range(len(coarse_el_array)):
                dist_arr = (el_array_adj-coarse_el_array[j])**2 + \
                           (az_array_adj-coarse_az_array[i])**2 
                coarse_rangelines_grid[i][j] = rangelines_adj[np.argmin(dist_arr)]
                coarse_valid_grid[i][j] = True
                #ipdb.set_trace()
    else:
        npts_az = len(coarse_az_array)
        npts_el = len(coarse_el_array)
        (coarse_rangelines_grid, 
            coarse_valid_grid) = calc_coarse_rangelines_grid(coarse_az_array, 
            coarse_el_array, el_array_adj, az_array_adj, rangelines_adj, 
            coarse_valid_grid, coarse_rangelines_grid, npts_az, npts_el)
    
    if dbg_prof:
        time_2 = time.time()
        print(f"    regrid functions set 2 duration: {time_2-time_1:.4f}")

    return (coarse_rangelines_grid, coarse_valid_grid, 
            coarse_az_array, coarse_el_array)

            


###############################################################################
###############################################################################
###############################################################################

# here's the FFT and power spectrum calculations.  Rather straightforward

def spectra_conv(coarse_rangelines_grid, data_format_in, fft_len, fs_post_dec):
    # TODO I think this will work with the shape of 'coarse_rangelines_grid'
    if data_format_in.lower() == "time_domain":
        coarse_power_grid = np.square(np.abs(np.fft.fft(
            coarse_rangelines_grid, fft_len)))
        #coarse_power_grid = np.flip(coarse_power_grid, 2)

    elif data_format_in.lower() == "fft":
        coarse_power_grid = np.square(np.abs(coarse_rangelines_grid))
        coarse_power_grid = np.flip(coarse_power_grid, 2)

    else: # data_format_in.lower() == "power_spectrum"
        # need to flip the axis for ranges to be correct
        coarse_power_grid = np.flip(coarse_rangelines_grid, 2)

    # frequency vector, contains the frequency bins for each FFT (they're all
    # the same for each pulse, so it's just one vector.  Units are Hz.
    # Conversion to range does not occur in this function
    freq_lut = np.fft.fftfreq(coarse_power_grid.shape[-1], d=1/fs_post_dec)

    # the format of coarse_power_grid is that each element is addressed with
    # x and y values corresponding to the pixel index

    # also, reorder the freq_lut (and compare them with the notebook values
    # to see if they match)
    coarse_power_grid = np.fft.fftshift(coarse_power_grid, 2)
    freq_lut = np.fft.fftshift(freq_lut)

    return (coarse_power_grid, freq_lut)


###############################################################################
###############################################################################
###############################################################################


# see py_postproc_fcns.py for the python version


def extract_peaks_c(coarse_power_grid_in, coarse_valid_grid_in, xlen_in, 
    ylen_in, rng_len_in, range_lut_cm_in, threshold_lin_in, contrast_lin_in, 
    half_peak_width_in, peak_selection, num_noise_pts_in, 
    noise_start_frac_in, calc_weighted_sum_in, min_range_in, max_range_in,
    dead_pix_val, dbg_prof=False):

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
    if dbg_prof:
        cfunc_start = time.time()
    # call the C function
    ret_val = extract_all_rangeline_peaks(power_array, valid_array, arr_len, 
        rng_len, range_lut_cm, threshold_lin, contrast_lin, half_peak_width, 
        min_range, max_range, num_noise_pts, noise_start_frac, 
        calc_weighted_sum, back_peak_bool_in, peak_ranges_array, 
        peak_powers_lin_array, noise_floor_array, num_peaks_array, 
        sel_ranges_array_out) 
    cfunc_stop = time.time()
    if dbg_prof:
        cfcn_time_ms = (cfunc_stop - cfunc_start) * 1000
        print(f"*******C function only duration: {cfcn_time_ms:.4f} ms")
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

    # argument will have been changed
    valid_pixels_grid           = np.ctypeslib.as_array(valid_array, 
        (xlen_in, ylen_in,))

    for i in range(xlen_in):
        for j in range(ylen_in):
            if not valid_pixels_grid[i][j]:
                pixel_ranges_grid[i][j] = dead_pix_val

    return (pixel_ranges_grid, valid_pixels_grid, noise_floor_grid)
    




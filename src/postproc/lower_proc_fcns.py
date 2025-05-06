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
import ipdb
import time
import os
import ipdb
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


extract_aux_data.argtypes = [ct.POINTER(ct.c_double), 
    ct.c_int, ct.POINTER(ct.c_double), ct.c_double, ct.c_double, ct.c_int, 
    ct.c_double, ct.c_double, ct.c_int, ct.c_double,  
    ct.c_bool, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), 
    ct.POINTER(ct.c_double), ct.POINTER(ct.c_int), ct.POINTER(ct.c_double),
    ct.POINTER(ct.c_double), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]
extract_aux_data.restype = ct.c_int



##############################################################################

def docstring(docstr):
    def assign_doc(f):
        f.__doc__ = docstr
        return f
    return assign_doc

##############################################################################
##############################################################################

@docstring("""
    Function Name: calc_coarse_rangelines_grid()
""")
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
    max_loc_pts = max(int(len(rangelines_adj) / (npts_az * npts_el) * 10), 100)
    local_rngln_inds = np.zeros((npts_az, npts_el, max_loc_pts), dtype=int)
    local_az_vals    = np.zeros((npts_az, npts_el, max_loc_pts), dtype=int)
    local_el_vals    = np.zeros((npts_az, npts_el, max_loc_pts), dtype=int)

    # this holds how many points are in each "local_rangeline_inds_matrix" 
    # location as the length of that array is not the number actually filled
    num_local_pts_matrix = np.zeros((npts_az, npts_el), dtype=int)

    # we also want to retain the elevation and azimuth encoder values
    # so we can check for later regridded rangelines to select the best
    coarse_az_out = np.zeros(coarse_valid_grid.shape, dtype=np.float64)
    coarse_el_out = np.zeros(coarse_valid_grid.shape, dtype=np.float64)


    # iterate through each rangeline
    for i in range(len(el_array_adj)):
        elev = el_array_adj[i]
        azi  = az_array_adj[i]

        # nearest indices
        n_az_ind = int(round(((azi- min_coarse_az) * az_ind_coeff)))

        if n_az_ind > (npts_az-1):
            continue

        n_el_ind = int(round(((elev - min_coarse_el) * el_ind_coeff)))

        if n_el_ind > (npts_el-1):
            continue


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
                coarse_az_out[i][j] = local_az_vals[i][j][ind_n]
                coarse_el_out[i][j] = local_el_vals[i][j][ind_n]

            else:
                coarse_valid_grid[i][j] = False

    return (coarse_rangelines_grid, coarse_valid_grid, coarse_az_out, 
            coarse_el_out)


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

##############################################################################
##############################################################################

def pulse_az_el_adj(el_val_in, az_val_in, channel_val_in, 
    elev_side_0_start, elev_side_0_end, elev_side_1_start, elev_side_1_end, 
    disable_el_side0, disable_el_side1, ch0_en, ch1_en, ch0_offset, 
    ch1_offset, el_offset0, el_offset1):
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
        el_val_out = el_val_in - elev_side_0_start + el_offset0
    elif ((el_val_in >= elev_side_1_start) and 
          (el_val_in <= elev_side_1_end) and (not disable_el_side1)):
        el_mirror_side = 1
        el_val_out = el_val_in - elev_side_1_start + el_offset1
    else: 
        el_mirror_side  = None
        el_val_out = el_val_in
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

##############################################################################
##############################################################################

def adj_rangelines(rangelines_in, el_array_in, az_array_in, channels_in, 
    elev_side_0_start, elev_side_0_end, elev_side_1_start, elev_side_1_end, 
    disable_el_side0, disable_el_side1, ch0_en, ch1_en, ch0_offset, 
    ch1_offset, el_offset0, el_offset1): 
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
            disable_el_side1, ch0_en, ch1_en, ch0_offset, ch1_offset, 
            el_offset0, el_offset1)
    
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
    
##############################################################################
##############################################################################

@docstring("""
    This calculates the elevation and azimuth coarse grid which is used 
    to identify the closest rangeline to each pixel in the dataset then 
    strip away all the other rangelines 

    Arguments
        min_el
            minimum adjusted elevation value, which should be 0 if the 
            starting elevation should be right at elev_side_x_start where x 
            is 0 or 1 depending upon which side of the mirror we're on

        max_el
            maximum adjusted elevation value.  Is set by the user to define
            the elevation span desired.  

        min_az
            minimum adjusted azimuth value.  Note that this must take into 
            account the offsets incorporated by using the two pixel system

        max_az
            maximum adjusted azimuth value.  Note that this must take into 
            account the offsets incorporated by using the two pixel system

        xlen
            number of pixels in the x direction (number of columns)

        ylen
            number of pixels in the y direction (number of rows)

""")
def calc_coarse_grid(min_el, max_el, min_az, max_az, xlen, 
    ylen):
    coarse_az_1d = np.linspace(min_az, max_az, xlen)
    coarse_el_1d = np.linspace(min_el, max_el, ylen)

    ideal_az_array = np.tile(coarse_az_1d, ylen).reshape((xlen,ylen))
    ideal_el_array = (np.tile(coarse_el_1d, xlen).reshape((ylen,xlen))).T

    return (coarse_az_1d, coarse_el_1d, ideal_az_array, ideal_el_array)
   

##############################################################################
##############################################################################


# NOTE TODO fill out the docstring
def regrid_rangelines(rangelines_in, el_array_in, az_array_in, channels_in, 
    elev_side_0_start, elev_side_0_end, elev_side_1_start, elev_side_1_end, 
    disable_el_side0, disable_el_side1, ch0_en, ch1_en, ch0_offset, ch1_offset, 
    el_offset0, el_offset1, ideal_az_array, ideal_el_array, xlen, ylen, 
    dbg_prof=False):
    

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
    
    NOTE TODO 
    NOTE TODO 
    NOTE TODO 

    """
    if dbg_prof:
        regrid_start = time.time_ns()

    # first make initial adjustments to the rangelines el and az 
    # encoder values etc.
    (rangelines_adj, el_array_adj, az_array_adj, channels_adj, 
        el_mirror_side_array_adj) = adj_rangelines(rangelines_in, el_array_in, 
        az_array_in, channels_in, elev_side_0_start, elev_side_0_end, 
        elev_side_1_start, elev_side_1_end, disable_el_side0, 
        disable_el_side1, ch0_en, ch1_en, ch0_offset, ch1_offset, 
        el_offset0, el_offset1)


    # Each rangeline must be the same size 
    coarse_rangelines_grid = np.zeros((ideal_az_array.shape[0], 
                            ideal_el_array.shape[0], rangelines_adj[0].shape[0]),
                            dtype=type(rangelines_adj[0][0]))

    # this will flag any data that is not present.  This allows us to avoid
    # certain problems associated with using NaNs to flag "empty" pixels
    coarse_valid_grid = np.zeros((ideal_az_array.shape[0], 
                            ideal_el_array.shape[0]), dtype=bool)

    if dbg_prof:
        time_1 = time.time_ns()
        dur_ms = float(time_1-regrid_start) / 1e6
        print(f"    regrid functions set 1 duration: {dur_ms:.4f} ms")

    npts_az = len(ideal_az_array)
    npts_el = len(ideal_el_array)

    (coarse_rangelines_grid, coarse_valid_grid, real_az_out, 
        real_el_out) = calc_coarse_rangelines_grid(ideal_az_array, 
        ideal_el_array, el_array_adj, az_array_adj, rangelines_adj, 
        coarse_valid_grid, coarse_rangelines_grid, npts_az, npts_el)
    
    if dbg_prof:
        time_2 = time.time_ns()
        dur_ms = float(time_2-time_1) / 1e6
        print(f"    regrid functions set 2 duration: {dur_ms:.4f} ms")

    return (coarse_rangelines_grid, coarse_valid_grid, 
            ideal_az_array, ideal_el_array, real_az_out, real_el_out)
            
###############################################################################
###############################################################################


def update_grid(rangelines_grid_a, valid_grid_a, grid_az_a, grid_el_a, 
                rangelines_grid_b, valid_grid_b, grid_az_b, grid_el_b, 
                ideal_az_grid, ideal_el_grid):
                """
                compares the two grids of rangelines, checks the distance
                of each rangeline from the ideal and selects the better one
                """
                rangelines_grid_out = np.zeros(rangelines_grid_a.shape, 
                                        dtype=rangelines_grid_a.dtype)
                grid_el_out = np.zeros(grid_el_a.shape)
                grid_az_out = np.zeros(grid_az_a.shape)
                dist_arr_a  = (np.square(grid_az_a-ideal_az_grid) + 
                              np.square(grid_el_a-ideal_el_grid))
                max_a = np.max(dist_arr_a)
                
                dist_arr_b  = (np.square(grid_az_b-ideal_az_grid) + 
                              np.square(grid_el_b-ideal_el_grid))
                max_b = np.max(dist_arr_b)
                max_val = np.max([max_a, max_b])

                # now effectively get rid of the invalid indices
                dist_arr_a[~valid_grid_a] = max_val + 1
                dist_arr_b[~valid_grid_b] = max_val + 1

                #old_code = True
                old_code = False 
                if old_code:
                    # this is inefficient, but there are speedups available 
                    # if it becomes necessary
                    for i in range(dist_arr_a.shape[0]):
                        for j in range(dist_arr_a.shape[1]):
                            if dist_arr_a[i][j] <= dist_arr_b[i][j]:
                                rangelines_grid_out[i][j] = rangelines_grid_a[i][j]
                                grid_el_out[i][j] = grid_el_a[i][j]
                                grid_az_out[i][j] = grid_az_a[i][j]
                            else:
                                rangelines_grid_out[i][j] = rangelines_grid_b[i][j]
                                grid_el_out[i][j] = grid_el_b[i][j]
                                grid_az_out[i][j] = grid_az_b[i][j]
                
                else: 
                    # a
                    a_inds = np.where(dist_arr_a <= dist_arr_b)
                    rangelines_grid_out[a_inds] = rangelines_grid_a[a_inds]
                    grid_el_out[a_inds] = grid_el_a[a_inds]
                    grid_az_out[a_inds] = grid_az_a[a_inds]

                    # b 
                    b_inds = np.where(dist_arr_a > dist_arr_b)
                    rangelines_grid_out[b_inds] = rangelines_grid_b[b_inds]
                    grid_el_out[b_inds] = grid_el_b[b_inds]
                    grid_az_out[b_inds] = grid_az_b[b_inds]

                valid_grid_out = valid_grid_a + valid_grid_b
                return (rangelines_grid_out, valid_grid_out, grid_az_out, 
                        grid_el_out)

###############################################################################
###############################################################################


def check_col_fraction(r_grid_valids):
    """
    checks the number of "almost full" columns are in the passed frame of 
    valids.  "almost full" in this case is defined by the magic number 
    FULL_FRAC
    """
    # going to do this the slow way
    (xlen, ylen) = r_grid_valids.shape
    num_full_cols = 0
    for col in r_grid_valids:
        if col.sum()/ylen >= 0.9:
            num_full_cols += 1

    frac_full = num_full_cols / xlen
    return frac_full

    

def check_pix_fraction(r_grid_valids):
    """
    To be written
    """
    frac_full = r_grid_valids.sum() / r_grid_valids.size
    return frac_full


            
###############################################################################
###############################################################################

# here's the FFT and power spectrum calculations.  Rather straightforward

def spectra_conv(coarse_rangelines_grid, data_format_in, fft_len, fs_post_dec,
                 invert_range=False):
    if data_format_in.lower() == "time_domain":
        coarse_power_grid = np.square(np.abs(np.fft.fft(
            coarse_rangelines_grid, fft_len)))

        if not invert_range:
            coarse_power_grid = np.flip(coarse_power_grid, 2)
        fft_len_out = fft_len

    elif data_format_in.lower() == "fft":
        coarse_power_grid = np.square(np.abs(coarse_rangelines_grid))

        if not invert_range:
            coarse_power_grid = np.flip(coarse_power_grid, 2)
        fft_len_out = coarse_power_grid.shape[2]

    else: # data_format_in.lower() == "power_spectrum"
        # need to convert to float64
        # and flip the axis for ranges to be correct
        #coarse_power_grid = 
        coarse_power_grid = coarse_rangelines_grid.astype(np.float64)

        if not invert_range:
            coarse_power_grid = np.flip(coarse_power_grid, 2)
        fft_len_out = coarse_power_grid.shape[2]

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

    return (coarse_power_grid, freq_lut, fft_len_out)

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
    if dbg_prof:
        cfunc_start = time.time_ns()
    # call the C functions
    ret_val = extract_all_rangeline_peaks(power_array, valid_array, arr_len, 
        rng_len, range_lut_cm, threshold_lin, contrast_lin, half_peak_width, 
        min_range, max_range, num_noise_pts, noise_start_frac, 
        calc_weighted_sum, back_peak_bool_in, peak_ranges_array, 
        peak_powers_lin_array, noise_floor_array, num_peaks_array, 
        sel_ranges_array_out) 
    cfunc_stop = time.time_ns()
    if dbg_prof:
        cfcn_time_ms = float(cfunc_stop - cfunc_start) / 1e6
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

    # this argument will have been changed too
    valid_pixels_grid           = np.ctypeslib.as_array(valid_array, 
        (xlen_in, ylen_in,))

    for i in range(xlen_in):
        for j in range(ylen_in):
            if not valid_pixels_grid[i][j]:
                pixel_ranges_grid[i][j] = dead_pix_val

    return (pixel_ranges_grid, valid_pixels_grid, noise_floor_grid)




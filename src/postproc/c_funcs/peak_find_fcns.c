/*****************************************************************************
This is the C code that performs peak-finding


*****************************************************************************/


#include<stdio.h>
#include<stdlib.h>
#include<stdbool.h>
#include<math.h>

//#include<complex.h>

/*
int add_nums (int a, int b) {
    int c = 0;

    c = a + b;
    return c;
};
*/

//struct


/*****************************************************************************
Function: get_min_double()
Description:
    This function just gets the minimum of a double* array passed to it and
    returns the minimum value as a double

Arguments:
    (double*) dbl_arr
        one dimensional array of doubles of length "arr_len" of which this
        function will find the minimum value.

    (int) arr_len
        length of power_arr

Return Value:
    (double) min_val
        The minimum value of dbl_arr
*****************************************************************************/
double get_min_double(double *dbl_arr, int arr_len) {
    double min_val = *dbl_arr;
    double curr_val;

    for (int i=0; i<arr_len; i++) {
        curr_val = dbl_arr[i];
        if (curr_val < min_val) {
            min_val = curr_val;
        }
    }

    return min_val;
}


/*****************************************************************************
Function: get_weighted_sum_limits()
Description:
    This function applies the weighted sum from SimplePeak2() legacy code to
    create adjusted start and stop indices for finding peaks

Arguments:
    (double*) power_arr
        one dimensional array of length "arr_len" that contains the power
        spectrum of the passed rangeline
    (int) arr_len
        length of power_arr

Return Values (returned through pointers in arguments):
    (int*) start_ind
        The start index produced by the weighted sum

    (int*) stop_ind
        The stop index produced by the weighted sum

Function Return Value
    Returns 0 if successful
*****************************************************************************/
int get_weighted_sum_limits(double *power_arr, int arr_len, int *start_ind,
    int *stop_ind) {

    double arr_min;
    double weighted_sum = 0;
    double simple_sum = 0;
    double arr_len_dbl = arr_len;
    int ctrpt, interm_1;


    // First get the minimum value of the array
    // This isn't the absolute most efficient way to do it, but it is a bit
    // cleaner, we'll start with this
    arr_min = get_min_double(power_arr, arr_len);

    // now calculate the two sums
    for (int i=0; i<arr_len; i++) {
        weighted_sum += (i+1) * (power_arr[i] - arr_min);
        simple_sum += power_arr[i] - arr_min;
    }


    if (simple_sum == 0) {
        *start_ind = 0;
        *stop_ind  = arr_len-1;
    } else {
        // this will hopefully recast properly
        ctrpt = (int) round(weighted_sum / simple_sum);

        interm_1 = (int) round((arr_len_dbl)/10);
        *start_ind = ctrpt - interm_1;
        *stop_ind = ctrpt + interm_1;
    }


    if (*start_ind < 0) {
        *start_ind = 0;
    }

    if (*stop_ind > arr_len) {
        *stop_ind = arr_len;
    }

    return 0;
}


/*****************************************************************************
Function: calc_noise_floor()
Description:
    This calculates the approximate noise floor value based on the average
    of a set of points starting at a specified location in the waveform
    that is intended to have no peaks

Arguments:
    (double*) rangeline_power
        one dimensional array of doubles of length "arr_len" which represents
        the rangeline's power spectrum

    (int) num_noise_pts
        number of points at the start of the array to average and set as the
        "noise floor"

    (double) noise_start_frac
        fraction of "rng_len" from the start of the "rangeline_power"
        at which to begin sampling points for calculating the noise floor

    (int) rng_len
        number of samples in the rangeline


Return Value
    (double*) noise_floor

*****************************************************************************/

double calc_noise_floor(double *rangeline_power, int num_noise_pts,
                          double noise_start_frac, int rng_len) {

    int start_ind;
    double noise_floor;
    start_ind = (int) round(noise_start_frac * ((double)rng_len));
    noise_floor = 0;
    for (int i=start_ind; i<(start_ind+num_noise_pts); i++){
        noise_floor += rangeline_power[i];
    }

    // get the average power of the noise floor
    start_ind = start_ind+1;
    noise_floor = noise_floor / ((double)num_noise_pts);
    start_ind = start_ind+1;
    return noise_floor;
}



/*****************************************************************************
Function: extract_single_rangeline_peaks()
Description:
    Extracts all the peaks from rangeline_power that satisfy the
    half_peak_width, weighted sum, min_range, max_range, threshold and
    contrast "trimming" values {MAYBE EXPLAIN THIS BETTER LATER}

Arguments:
    (double*) rangeline_power
        one dimensional array of length "rng_len" which
        represents the rangeline's power spectrum

    (int) rng_len
        number of samples in "rangeline_power" and "range_lut_cm"

    (double*) range_lut_cm
        one dimensional array of length "rng_len" which
        represents the ranges in centimeters of each "'rangeline_power"
        power spectrum sample

    (double) threshold_lin
        used in combination with the calculated noise floor of the rangeline
        to calculate "adj_thresh_lin" which is a linear power
        level.  Peaks below "adj_thresh_lin" are ignored

    (double) contrast_lin
        used in combination with the maximum detected peak power in the
        rangeline to exclude peaks that are below the value:
            "max_peak_power" / "contrast_lin"

    (int) half_peak_width
        half the number of points to look around the peak to search for higher
        "nearby" peaks.
        e.g. if this is 2, that means the code will search 2 samples before the
        peak and 2 samples after each peak to see if there's a sample with a
        power value greater than the peak being examined.  If there is a power
        value in those 4 samples around the peak that is greater than the
        power value of the peak being examined, then the peak being examined
        is excluded.  Otherwise, the peak being examined is included

    (double) min_range
        minimum range to search for peaks. Used to be index 0 of "rangecut"

    (double) max_range
        maximum range to search for peaks. Used to be index 1 of "rangecut"

    (int) num_noise_pts
        number of points at the start of the array to average and set as the
        "noise floor"

    (double) noise_start_frac
        fraction of "rng_len" from the start of the "rangeline_power"
        at which to begin sampling points for calculating the noise floor


    (int*) interm_peak_inds
        This is a block of memory to be used as an array of integers to
        temporarily store the number of peak indices prior to reducing them
        down using "half_peak_width" and "contrast_lin".  Because it's a
        relatively large amount of memory, I allocate it in the parent function
        and re-use it every time I call this extract_single_rangeline_peaks()
        function to improve efficiency as we don't have to initialize or
        reset the values to use it properly.

    (bool) calc_weighted_sum
        a switch to turn on or off the weighted sum calculation as it adds
        additional processing time


Return Values (returned through pointers in arguments):
    (double*) peak_ranges
        an array of the peak ranges, in the order they were found by going
        incrementally through "rangeline_power"

    (double*) peak_powers_lin
        an array of the peak powers in linear units, corresponding to the peak
        ranges in "peak_ranges"

    (double*) noise_floor
        a single value that contains the calculated noise floor of this
        rangeline in linear units

    (int*) num_peaks
        number of peaks found.  This also serves as the length of both the
        "peak_ranges" and "peak_powers_lin" arrays


Function Return Value
    Returns 0 if successful
*****************************************************************************/

int extract_single_rangeline_peaks(double *rangeline_power, int rng_len,
    double *range_lut_cm, double threshold_lin,
    double contrast_lin, int half_peak_width, double min_range,
    double max_range, int num_noise_pts, double noise_start_frac,
    int *interm_peak_inds, bool calc_weighted_sum, double *peak_ranges,
    double *peak_powers_lin, double *noise_floor, int *num_peaks) {

    //////////////////////////////// VARIABLES ///////////////////////////////
    int start_ind;
    int stop_ind;
    double power_val, power_val_next, power_val_prev;
    double adj_thresh_lin;

    // interm_ind points to the address after the last filled address in
    // interm_peak_inds
    int interm_ind;
    double max_peak_power;
    int peak_ind;
    double peak_power;
    double contr_thresh;
    double interm_peak_power;

    // pointer to the indices of the final peak ranges and powers output values
    int peak_ind_out;
    bool keep_peak;

    ////////////////////////////// END VARIABLES /////////////////////////////


    // do weighted sum to trim limits
    if (calc_weighted_sum) {
        get_weighted_sum_limits(rangeline_power, rng_len, &start_ind,
                                &stop_ind);
    } else {
        start_ind = 0;
        stop_ind = rng_len;
    }

    // calculate the noise floor
    *noise_floor = calc_noise_floor(rangeline_power, num_noise_pts,
                                   noise_start_frac, rng_len);


    // calc adjusted linear power threshold
    adj_thresh_lin = *(noise_floor) * (threshold_lin);


    // adjust start and stop indices to account for half peak width edge
    // conditions
    if (half_peak_width > start_ind) {
        start_ind = half_peak_width;
    }

    if ((rng_len-half_peak_width-2) < stop_ind) {
        stop_ind = (rng_len-half_peak_width-2);
    }


    // main "for" loop that searches for peaks
    //
    max_peak_power = power_val;
    interm_ind = 0;
    // NOTE: because the number of true peaks is usually sparse, we're going 
    // to make each loop a little more expensive to allow for an initial 
    // check at the start to see if the power value is above the noise floor 
    // or not so we can remove as many samples as possible as quickly as 
    // possible
    for (int i=1; i<(stop_ind-1); i++) {
        power_val       = rangeline_power[i];
        // A few checks to see if we're even in a state where we should be
        // looking at things at all
        //
        // this first check should immediately eliminate most samples
        if (power_val < adj_thresh_lin) {
            continue;
        }

        // get rid of the start edge so we don't run into edge problems when
        // searching around each peak later
        if (i <= start_ind) {
            continue;
        }

        if (range_lut_cm[i] < min_range) {
            continue;
        }

        if (range_lut_cm[i] > max_range) {
            break; // or continue?
        }

        // extract previous and next power values
        power_val_next  = rangeline_power[i + 1];
        power_val_prev  = rangeline_power[i - 1];

        // conditions pointing to a peak at i
        // will interpret a transition from "flat" to lower value as a peak
        // but will not interpret a transition from lower region to a "flat" 
        // value as a peak (to avoid many peaks from long flat regions)
        // we may want to revisit this later, though it likely won't matter 
        // much
        if ((power_val >= power_val_prev) && (power_val > power_val_next)) {
            // add the peak power and peak value to their respective arrays

            // So you need to store peak index in an array.  Not the peak
            // values, not yet.

            // store the index
            interm_peak_inds[interm_ind] = i;
            interm_ind += 1;

            // update the maximum power peak value
            if (power_val > max_peak_power) {
                max_peak_power = power_val;
            }
        }

    }

    // First for loop found all the peaks, but because we need the maximum
    // value to apply the contrast parameter we need to go through the peaks
    // a second time.  Also doing the peak width checks with this reduced
    // set of peaks is more efficient than doing it on the raw
    // "rangeline_power" array

    // computes threshold for contrast exclusions
    contr_thresh = max_peak_power / contrast_lin;

    // "outer" peak loop.
    peak_ind_out = 0;
    for (int i=0; i<interm_ind; i++) {
        peak_ind    = interm_peak_inds[i];
        peak_power  = rangeline_power[peak_ind];

        // first ignore any peaks that are below the contrast threshold
        if (peak_power < contr_thresh) {
            continue;
        }

        keep_peak = true;
        for (int j=-half_peak_width; j<half_peak_width+1; j++) {
            interm_peak_power = rangeline_power[peak_ind+j];

            // indicates the peak should be removed
            if (interm_peak_power > peak_power) {
                keep_peak = false;
                break;
            }
        }

        if (keep_peak) {
            // if we made it through without peaks getting removed, then
            peak_ranges[peak_ind_out] = range_lut_cm[peak_ind];
            peak_powers_lin[peak_ind_out] = rangeline_power[peak_ind];
            peak_ind_out += 1;
        }
    }

    *num_peaks = peak_ind_out;
    return 0;
}



// NOTE TODO: you should send back the entire set of peaks as well as the
// front and back to allow the higher level function to simply grab the front
// or back peak as desired.  We can change this later but it makes things
// fastest while still alowing for additional peakfinding algorithm changes

/*****************************************************************************
Function: extract_all_rangeline_peaks()
Description:
    Extracts all the peaks from rangeline_power that satisfy the
    half_peak_width, weighted sum, min_range, max_range, threshold and
    contrast "trimming" values [MAYBE EXPLAIN THIS BETTER LATER]

Arguments:
    (double*) power_array
        Array of rangeline power spectra for each rangeline in.  Stored in
        python as a 2D array, but now it's a 1D array.  So that means that the
        way to address each rangeline is:

        sample(i,j) = power_array[(rng_len*arr_len)*i + j]
            sample j, of power spectrum of rangeline i

    (double*) valid_array
        a 1D array of booleans indicating whether or not the rangeline
        indicated at each point is "valid".  It is generally used as a
        C-compatible replacement for "NaN" values, however here it is useful
        for reducing the processing load by eliminating invalid rangelines
        from processing.  Consists of a 1D array of length arr_len.

        This argument also serves as the "output" valid_array.  So any
        rangelines that are found to be invalid will trigger an update of
        the corresponding value in this array so that once the function is
        finished, this array will contain an updated set of valid values


    (int) arr_len
        number of rangelines in power_array

    (int) rng_len
        length of each rangeline in power_array

    (double*) range_lut_cm
        one dimensional array of length "rng_len" which
        represents the ranges in centimeters of each "'rangeline_power"
        power spectrum sample

    (double) threshold_lin
        used in combination with the calculated noise floor of the rangeline
        to calculate "adj_thresh_lin" which is a linear power
        level.  Peaks below "adj_thresh_lin" are ignored

    (double) contrast_lin
        used in combination with the maximum detected peak power in the
        rangeline to exclude peaks that are below the value:
            "max_peak_power" / "contrast_lin"

    (int) half_peak_width
        half the number of points to look around the peak to search for higher
        "nearby" peaks.
        e.g. if this is 2, that means the code will search 2 samples before the
        peak and 2 samples after each peak to see if there's a sample with a
        power value greater than the peak being examined.  If there is a power
        value in those 4 samples around the peak that is greater than the
        power value of the peak being examined, then the peak being examined
        is excluded.  Otherwise, the peak being examined is included

    (double) min_range
        minimum range to search for peaks. Used to be index 0 of "rangecut"

    (double) max_range
        maximum range to search for peaks. Used to be index 1 of "rangecut"

    (int) num_noise_pts
        number of points at the start of the array to average and set as the
        "noise floor"

    (double) noise_start_frac
        fraction of "rng_len" from the start of the "rangeline_power"
        at which to begin sampling points for calculating the noise floor

    (bool) calc_weighted_sum
        a switch to turn on or off the weighted sum calculation as it adds
        additional processing time

    (bool) back_peak_bool_in
        a switch to have the function return back or front peak rangees
        in the variable "sel_ranges_array_out"



Return Values (returned through pointers in arguments):
    (double*) peak_ranges_array
        an array that contains peak ranges for each rangeline in the order
        they were found by going incrementally through "rangeline_power".

        Addressing works like this:
            peak range "j" of rangeline i, where i is the index from the
            original "power_array"
            peak_range(i,j)
                = peak_ranges_array[rng_len*i + j]

            "rng_len" is used here because it represents the maximum number of
            peak ranges that you can store for each rangeline.  There aren't
            actually "rng_len" peak ranges in each rangeline, it's just for
            memory sizing.  The number of peaks in each rangeline is stored in
            "num_peaks_array"


    (double*) peak_powers_lin_array
        an array that contains the peak powers in linear units for each
        rangeline, corresponding to the peak ranges in "peak_ranges_array".
        addressing works similarly as with "peak_ranges_array"


    (double*) noise_floor_array
        an array that contains the noise floor value for each rangeline
        in linear units.

        Addressing works like this:
            rangeline i, where i is array index
            noise_floor(i) = noise_floor_array[i]

    (int*) num_peaks_array
        number of peaks found for each rangeline.  Addressing works the same as
        for "noise_floor_array"

    (double*) sel_ranges_array_out
        this is an array of "selected" peaks based on "back_peak_bool_in".
        when "back_peak_bool_in" is "True", then this contains an array
        of the "last" peaks for each rangeline (indicating the back peaks for
        each rangeline).  When "back_peak_bool_in" is "False", then this
        contains an array of the "first" peaks in each rangeline (indicating
        the front peaks for each rangeline).


Function Return Value
    Returns 0 if successful
*****************************************************************************/

int extract_all_rangeline_peaks(double *power_array, bool *valid_array,
    int arr_len, int rng_len, double *range_lut_cm,
    double threshold_lin, double contrast_lin, int half_peak_width,
    double min_range, double max_range, int num_noise_pts,
    double noise_start_frac, bool calc_weighted_sum, bool back_peak_bool_in,
    double *peak_ranges_array, double *peak_powers_lin_array,
    double *noise_floor_array, int *num_peaks_array,
    double *sel_ranges_array_out) {

    // create the interim buffer
    int *interm_peak_inds   = malloc(rng_len*sizeof(int));
    double *rangeline_power;
    bool valid_rangeline;

    // "inner" function output variables
    double *peak_ranges, *peak_powers_lin;
    double *noise_floor;
    int *num_peaks;


    // the "rangeline_power" pointer can just be an address in
    // power_array there's no need to copy the array

    // maximum number of peak ranges is the length of the rangeline.
    // maybe length of the rangeline divided by 2, I'll have to revisit that
    // later, but really it shouldn't be a big deal unless we start running
    // out of memory
    
    /*********************************************************************/
    /*********************************************************************/
    /*********************************************************************/
    // TEMP DEBUG: showing all the passed variales
    /*
    int tot_len;
    tot_len = arr_len * rng_len;

    printf("starting function!\n");
    printf("arr_len = %d\n", arr_len);
    printf("rng_len = %d\n", rng_len);
    

    for (int i=0; i<rng_len; i++) {
        printf("range_lut_cm[%d] = %f\n", i, range_lut_cm[i]);
    }


    
    //for (int i=0; i<tot_len; i++) {
    //    printf("")

    //}

    */


    /*********************************************************************/
    /*********************************************************************/
    /*********************************************************************/


    for (int i=0; i<arr_len; i++) {
        // invalid rangelines are ignored
        valid_rangeline = valid_array[i];
        if (!valid_rangeline) {
            continue;
        }

        rangeline_power = &power_array[rng_len*i];

        // we don't have to copy the arrays we simply have to provide
        // the correct pointer values
        peak_ranges         = &peak_ranges_array[rng_len*i];
        peak_powers_lin     = &peak_powers_lin_array[rng_len*i];
        noise_floor         = &noise_floor_array[i];
        num_peaks           = &num_peaks_array[i];

        extract_single_rangeline_peaks(rangeline_power, rng_len, range_lut_cm,
            threshold_lin, contrast_lin, half_peak_width, min_range,
            max_range, num_noise_pts, noise_start_frac, interm_peak_inds,
            calc_weighted_sum, peak_ranges, peak_powers_lin, noise_floor,
            num_peaks);

        if (*num_peaks == 0) {
            valid_array[i] = false;
        } else {
            if (back_peak_bool_in) {
                sel_ranges_array_out[i] = peak_ranges[(*num_peaks)-1];
                //printf("range_out[%d] = %f\n", i, sel_ranges_array_out[i]);
            } else {
                sel_ranges_array_out[i] = peak_ranges[0];
            }
        }
    }

    // free memory
    free(interm_peak_inds);
    //printf("function complete!\n");
    return 0;
}



#ifndef PEAK_FIND_FCNS_H
#define PEAK_FIND_FCNS_H


#include<stdbool.h>

double get_min_double(double *dbl_arr, int arr_len);


int get_weighted_sum_limits(double *power_arr, int arr_len, int *start_ind, 
    int *stop_ind);


double calc_noise_floor(double *rangeline_power, int num_noise_pts, 
                        double noise_start_frac, int rng_len);
                          

int extract_aux_data(double *rangeline_power, int rng_len,
    double *range_lut_cm, double threshold_lin,
    double contrast_lin, int half_peak_width, double min_range,
    double max_range, int num_noise_pts, double noise_start_frac,
    int *interm_peak_inds, bool calc_weighted_sum, double *peak_ranges,
    double *peak_powers_lin, double *noise_floor, int *num_peaks, 
    double *adj_lin_thresh, double *adj_lin_contr, int *weight_sum_start,  
    int *weight_sum_end);


int extract_single_rangeline_peaks(double *rangeline_power, int rng_len, 
    double *range_lut_cm, double threshold_lin, 
    double contrast_lin, int half_peak_width, double min_range, 
    double max_range, int num_noise_pts, double noise_start_frac, 
    int *interm_peak_inds, bool calc_weighted_sum, double *peak_ranges, 
    double *peak_powers_lin, double *noise_floor, int *num_peaks);


int extract_all_rangeline_peaks(double *power_array, bool *valid_array, 
    int arr_len, int rng_len, double *range_lut_cm, 
    double threshold_lin, double contrast_lin, int half_peak_width, 
    double min_range, double max_range, int num_noise_pts, 
    double noise_start_frac, bool calc_weighted_sum, bool back_peak_bool_in, 
    double *peak_ranges_array, double *peak_powers_lin_array, 
    double *noise_floor_array, int *num_peaks_array, 
    double *sel_peak_array_out);


#endif

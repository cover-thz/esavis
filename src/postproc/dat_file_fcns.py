import numpy as np
import file_parser as fp

def extract_rdat(rdat, fs_adc):
    # preallocate header data parameters 
    num_rangelines  = len(rdat.rangelines)
    len_rangeline   = len(rdat.rangelines[0])

    elevation       = np.zeros(num_rangelines)
    azimuth         = np.zeros(num_rangelines)
    rangelines_out  = np.zeros((num_rangelines, len_rangeline), 
                        dtype=type(rdat.rangelines[0][0]))
    channels        = np.zeros(num_rangelines)
    j = 0
    for i, hdr in enumerate(rdat.headers):
        # In some files/runs, there are erroneous elevation counter values 
        # that seem to be perfectly correlated with occurrences of erroneous 
        # BRI values of 2**32-1. So we will use the bri array as a filter 
        # for this and strip off all time corresponding time steps from each 
        # of the arrays.
        if (hdr.bri_ctr >= 2**32-1):
            continue

        elevation[j]        = np.float64(hdr.el_pos) 
        azimuth[j]          = np.float64(hdr.az_pos) 
        #rangelines_out[j]   = rdat.rangelines[i][::-1]
        rangelines_out[j]   = rdat.rangelines[i]
        channels[j]         = hdr.channel_id

        # decimation values, FFT values, and power values  for each header 
        # must be identical for the post-processing to work, if they're not 
        # it means a setting was changed, so the data should be flagged as 
        # unusuable
        data_good = True
        dec_en_temp = bool(hdr.rx_cfg_ssdec)
        dec_temp = hdr.decimation # probably unnecessary 
        fft_temp = np.int8(hdr.rx_cfg_fft) 
        powcalc_temp = np.int8(hdr.rx_cfg_powcalc) 
        if j == 0:
            dec_en       = dec_en_temp
            dec_val      = dec_temp
            fft_flag     = fft_temp
            powcalc_flag = powcalc_temp
        else:
            if (dec_en != dec_en_temp):
                data_good = False

            elif (dec_val != dec_temp):
                data_good = False # decimation value changed during 
                                  # data gathering
                break
            elif (fft_flag != fft_temp):
                data_good = False # FFT value changed during data gathering
                break
            elif (powcalc_flag != powcalc_temp):
                data_good = False # power calc value changed during 
                                  # data gathering
                break

        # increment the output index if a sample was processed
        j += 1

    # need to remove the unused elements from each array
    elevation       = elevation[:j]
    azimuth         = azimuth[:j]
    rangelines_out  = rangelines_out[:j]
    channels        = channels[:j]

    # decimation value is only valid if decimation is enabled
    # and true decimation value is one more than the register value
    if dec_en:
        dec_val = dec_val + 1
    else:
        dec_val = 1

    # sampling frequency after decimation
    fs_post_dec = fs_adc/(16*(dec_val))

    # a little clunkier than casting with bool() but I suspect I'll run into
    # weird problems if I cast with bool()
    if fft_flag == 1:
        fft_flag = True
    else:
        fft_flag = False

    if powcalc_flag == 1:
        powcalc_flag = True
    else:
        powcalc_flag = False

    return (rangelines_out, elevation, azimuth, channels, fs_post_dec, fft_flag, 
            powcalc_flag, dec_val, len_rangeline, data_good)




def get_rangelines_from_file(fname_list, fs_adc):
    if type(fname_list) == str:
        fname_list = [fname_list]
    elif type(fname_list) == list:
        pass
    else:
        raise Exception("fname_list must be a string with one file name or \
        a list of file names")

    # parse_data performs the low-level parsing from binary file to 
    # python-accessible objects.  
    rdat_list = []
    for fname in fname_list:
        rdat = fp.parse_data([fname])
        rdat_list.append(rdat)

    rangelines_list = []
    elevation_list  = []
    azimuth_list    = []
    channels_list   = []
    for i,rdat in enumerate(rdat_list):
        (rangelines_in, elevation_in, azimuth_in, channels_in, fs_post_dec_in, 
            fft_flag_in, powcalc_flag_in, dec_val_in, len_rangeline_in, 
            data_good_in) = extract_rdat(rdat, fs_adc) 

        rangelines_list.append(rangelines_in)
        elevation_list.append(elevation_in)
        azimuth_list.append(azimuth_in)
        channels_list.append(channels_in)

        # these values must be identical for the rdat objects to be 
        # combine-able 
        if i == 0:
            fs_post_dec     = fs_post_dec_in
            fft_flag        = fft_flag_in
            powcalc_flag    = powcalc_flag_in
            dec_val         = dec_val_in
            len_rangeline   = len_rangeline_in
            data_good       = data_good_in

        else:
            if fs_post_dec != fs_post_dec_in:
                data_good = False
            if fft_flag != fft_flag_in:
                data_good = False
            if powcalc_flag != powcalc_flag_in:
                data_good = False
            if dec_val != dec_val_in:
                data_good = False
            if len_rangeline != len_rangeline_in:
                data_good = False
            if not data_good_in:
                data_good = False

    rangelines      = np.concatenate(rangelines_list)
    elevation       = np.concatenate(elevation_list)
    azimuth         = np.concatenate(azimuth_list)
    channels        = np.concatenate(channels_list)

    return (rangelines, elevation, azimuth, channels, fs_post_dec, fft_flag, 
            powcalc_flag, dec_val, len_rangeline, data_good)
            








from src.data_parser import HeaderStruct, parse_data
import tkinter
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
import src.jpl_data_util as jdu
import src.signal_util as su
import src.image_processor as ip
import matplotlib as mpl
from scipy import constants
from scipy.signal import find_peaks
from scipy.signal.windows import tukey, hann
from skimage.filters import window
import sys
import os.path

def get_last_modified_file(dir_val, extension, channel=None):
    """
    returns the filename of the most recently modified file in dir_val with
    the passed 'extension'.  Note that 'extension' should not include the '.'
    """
    fnames = []
    path_prefix = f"{dir_val}/"
    for val in os.listdir(dir_val):
        if os.path.isfile(path_prefix+val):
           fnames.append(val)

    best_last_mod_time = 0
    for fname in fnames:
        curr_ext = fname.split(".")[-1]
        if curr_ext == extension:
            if channel == 0:
                # check specific portion of file to see if it matches the string
                # associated with channel 0 files 
                if fname[-17:-9] != "Channel0":
                    continue

            elif channel == 1:
                # check specific portion of file to see if it matches the string
                # associated with channel 0 files 
                if fname[-17:-9] != "Channel1":
                    continue

            last_mod_time = os.stat(path_prefix+fname).st_mtime
            if last_mod_time > best_last_mod_time:
                best_last_mod_time = last_mod_time
                last_mod_fname = fname

    return last_mod_fname



def create_cal_file(dat_fpath, dflt_out_fname, cal_dir):
    print("target source file with path:", dat_fpath)
    source_file_wo_ext = os.path.splitext(os.path.basename(dat_fpath))[0]
    assert os.path.isfile(dat_fpath), f"source file {dat_fpath} doesn't exist"

    fidlist = [dat_fpath]
    rdat = parse_data(fidlist)
    use_all_rangelines = True

    if use_all_rangelines:
        # average across all data collected
        cal_wf = np.mean(rdat.rangelines, axis = 0)
    else:
        cal_wf = rdat.rangelines[0]

    # pre-normalize it (uncertain if this step is necessary)
    cal_wf /= np.abs(cal_wf).max()
    zero_inds = np.where(cal_wf == 0)
    cal_wf = 1/cal_wf
    # zero out start and end values
    cal_wf[0:20] = 0
    cal_wf[-20:-1] = 0

    # apply hann window
    cal_wf *= hann(len(cal_wf))
    # cast as a complex double
    cal_wf = cal_wf.astype(np.complex128)

    # actually normalize here
    cal_wf /= np.abs(cal_wf).max()
    cal_wf[zero_inds] = 1 # get rid of undefined values

    dest_file = cal_dir + source_file_wo_ext + "_cal.bin"
    default_out_fpath = cal_dir + dflt_out_fname

    # write to properly dated name
    cal_wf.tofile(dest_file)
    print("destination file with path: ", dest_file)

    # write to default file name
    cal_wf.tofile(default_out_fpath)

    print("default destination file with path: ", default_out_fpath)
    print("")
    plt.figure()
    plt.plot(np.real(cal_wf))
    plt.plot(np.imag(cal_wf))
    plt.show(block=False)





mpl.use('TkAgg')
source_dir = '/tmp'
cal_dir = '/home/wsr/Dev/GUI/arenaUserApps/deployments/thz/'
#source_dir = './local-data/wsr-sdr-data/'
#cal_dir = source_dir

#assert len(sys.argv) == 2, "must pass data file name to generate cal"
#source_file = sys.argv[1]
#source_file_w_path = filedialog.askopenfilename(title="select a cal source file", 
#                        filetypes=[("All files", "*.*")])
#print(source_file_w_path)
#source_file_w_path = source_dir + source_file


# channel 0
ch0_fname = get_last_modified_file(source_dir, "dat", channel=0)
ch0_fpath = source_dir + "/" + ch0_fname
dflt_out_fname0 = "default_cal_file_pix0_cal.bin"
create_cal_file(ch0_fpath, dflt_out_fname0, cal_dir)

ch1_fname = get_last_modified_file(source_dir, "dat", channel=1)
ch1_fpath = source_dir + "/" + ch1_fname
dflt_out_fname1 = "default_cal_file_pix1_cal.bin"
create_cal_file(ch1_fpath, dflt_out_fname1, cal_dir)


#print("target source file with path:", source_file_w_path)
#source_file_wo_ext = os.path.splitext(os.path.basename(source_file_w_path))[0]

#assert os.path.isfile(source_file_w_path), "source file doesn't exist"

#fidlist = [source_file_w_path]
#rdat = parse_data(fidlist)

# average across all data collected
#cal_wf = np.mean(rdat.rangelines, axis = 0)
# normalize it
#cal_wf /= np.abs(cal_wf).max()
#cal_wf = 1/cal_wf
# zero out start and end values
#cal_wf[0:20] = 0
#cal_wf[-20:-1] = 0

# apply hann window
#cal_wf *= hann(len(cal_wf))
# cast as a complex double
#cal_wf = cal_wf.astype(np.complex128)


#dest_file = cal_dir + source_file_wo_ext + "_cal.bin"
#print("destination file with path: ", dest_file)
#cal_wf.tofile(dest_file)
#plt.figure()
#plt.plot(np.real(cal_wf))
#plt.plot(np.imag(cal_wf))


_ = input("Press Enter to exit")




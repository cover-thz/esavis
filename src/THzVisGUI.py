#
# This contains the main code for the THz Visualizer GUI
# heavily modified from the StillViewerGUI
# The purpose of this file is to set up the main GUI widgets and instantiate 
# the processing core.  
# 
# There are two main paramters sets: one set that goes into the processing 
# and makes up the processing's "cfg_dict" which includes the flags 
# "cfg_flags".  
#
# And a second parameter set that contains visualization 
# settings like color scaling, color mapping, etc.
#   
#
#
#
# ADD COLOR SCHEME DROPDOWN MENU
#



from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, QTimer
import os
import sys
import json
#from math import nan
import signal
import numpy as np
import pyqtgraph as pg
import multiprocessing as mp
from collections import OrderedDict
import copy
import subprocess
import time

# compile the C functions
if __name__ == '__main__':
    CWD = os.getcwd() 
    if os.name == "nt":
        c_funcs_dir = CWD + "\\postproc\\c_funcs"
        #result = subprocess.run(["make"], cwd=c_funcs_dir)
    elif os.name == "posix":
        c_funcs_dir = CWD + "/postproc/c_funcs"
        #result = subprocess.run(["make"], cwd=c_funcs_dir)
    else:
        raise Exception("Invalid OS Name")

#from dataclasses import dataclass, field
from THzImageTab import THzImageTab
from SingPixTab import SingPixTab

# crude but effective way of getting the postprocessing directory in here
# without playing maddening namespace games with the modules in the that
# directory
PROC_DIR    = os.path.abspath(os.path.join(os.getcwd(), 'postproc'))
sys.path.append(PROC_DIR)
import data_processor as dp


from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGridLayout,
    QTabWidget,
    QWidget,
    QSizePolicy,
)


# this is just a class to contain the processing core related functions so
# they can be packaged nicely into one object to pass around the program
class ProcPipes:
    def __init__(s, cfg_pipe, err_pipe, data_pipe, 
                    query_pipe_in, query_pipe_out):
        s.cfg_pipe = cfg_pipe
        s.err_pipe   = err_pipe
        s.data_pipe    = data_pipe
        s.query_pipe_in   = query_pipe_in
        s.query_pipe_out  = query_pipe_out


# quit the app on Ctrl + C from console
def sigint_handler(*_):
    print("HIT CTRL-C")
    QtGui.QGuiApplication.quit()

##############################################################################
# DEFAULT CONFIG SET
##############################################################################


def get_default_cfgs():
    DFLT_CFG_DICT = OrderedDict()
    DFLT_CFG_DICT["el_side_0_start"] = 0
    DFLT_CFG_DICT["el_side_0_end"] = 0
    DFLT_CFG_DICT["el_side_1_start"] = 0
    DFLT_CFG_DICT["el_side_1_end"] = 0

    DFLT_CFG_DICT["ylen"] = 1 
    DFLT_CFG_DICT["xlen"] = 1

    DFLT_CFG_DICT["fft_len"] = 1
    DFLT_CFG_DICT["num_noise_pts"] = 1
    DFLT_CFG_DICT["noise_start_frac"] = 0.
    DFLT_CFG_DICT["chirp_span"] = 0.
    DFLT_CFG_DICT["chirp_time"] = 0.

    DFLT_CFG_DICT["dead_pix_val"] = 0.
    DFLT_CFG_DICT["fs_adc"] = 0.

    DFLT_CFG_DICT["el_offset0"] = 0.
    DFLT_CFG_DICT["el_offset1"] = 0.

    DFLT_CFG_DICT["center_rangeval"] = 0.
    DFLT_CFG_DICT["dec_val"] = 1
    DFLT_CFG_DICT["ch0_offset"] = 0.
    DFLT_CFG_DICT["ch1_offset"] = 0.

    DFLT_CFG_DICT["disable_el_side0"] = 0.
    DFLT_CFG_DICT["disable_el_side1"] = 0.

    DFLT_CFG_DICT["calc_weighted_sum"] = True
    DFLT_CFG_DICT["ch0_en"] = True
    DFLT_CFG_DICT["ch1_en"] = True

    DFLT_CFG_DICT["data_format_in"] = "power_spectrum"

    DFLT_CFG_DICT["save_image_desc"] = "NONE"

    DFLT_CFG_DICT["threshold_db"] = 0.
    DFLT_CFG_DICT["contrast_db"] = 0.
    DFLT_CFG_DICT["half_peak_width"] = 1

    DFLT_CFG_DICT["min_range"] = 0.
    DFLT_CFG_DICT["max_range"] = 7000.

    DFLT_CFG_DICT["autoscale_color"] = True
    DFLT_CFG_DICT["color_scale_min"] = 0.
    DFLT_CFG_DICT["color_scale_max"] = 7000.

    DFLT_CFG_DICT["min_az"] = 0.
    DFLT_CFG_DICT["max_az"] = 1.
    DFLT_CFG_DICT["min_el"] = 0.
    DFLT_CFG_DICT["max_el"] = 1.

    DFLT_CFG_DICT["colormap"]        = "jet"
    DFLT_CFG_DICT["data_src"]        = "disabled"
    DFLT_CFG_DICT["plot_style"]      = "front_peak_range"
    DFLT_CFG_DICT["peak_selection"]  = "front"
    DFLT_CFG_DICT["paused"]     = False
    DFLT_CFG_DICT["invert_range"] = False

    DFLT_CFG_DICT["aux_x_ind"] = 10
    DFLT_CFG_DICT["aux_y_ind"] = 10
    DFLT_CFG_DICT["aux_az_val"] = -1
    DFLT_CFG_DICT["aux_el_val"] = -1

    DFLT_CFG_DICT["external_h5_fpath"] = None


    # These values do not appear in the GUI yet
    # so they are "hard-coded"
    DFLT_CFG_DICT["el_encoder_to_cm"]  = 16/500
    DFLT_CFG_DICT["az_encoder_to_cm"]  = 16/500

    DFLT_CFG_DICT["flags"] = []


    # NOTE Debug dictionary objects for use with the debug tab
    DFLT_CFG_DICT["dbg_0"] = False
    DFLT_CFG_DICT["dbg_1"] = False
    DFLT_CFG_DICT["dbg_2"] = False
    DFLT_CFG_DICT["profiler"] = False
    DFLT_CFG_DICT["frame_update_dbg"] = False
    return DFLT_CFG_DICT


##############################################################################
# Main Window Class
##############################################################################
class MainWindow(QMainWindow):
    """
    Toplevel window initiates the tab widgets and distributes data to them
    and doesn't do much else.  The bulk of the widget-related code is in 
    the respective tab widget 
    """
    cfg_dict    =   None

    powspec_matrix  = None
    coarse_azi_lut  = None
    coarse_elev_lut = None
    freq_lut        = None

    # tier 2 postprocessing data values
    peak_indices_matrix = None
    peak_ranges_matrix  = None
    peak_powers_matrix  = None
    num_peaks_matrix    = None
    noise_floor_matrix  = None

    cur_proc_data_file_0 = None
    cur_proc_data_file_1 = None
    proc_pipes = None


    def __init__(s, DFLT_DATA_DIR, CFG_DFLT_PATH, CONFIG_DIR, proc_pipes):
        super().__init__()

        # going with a single configuration file rather than two
        s.CFG_DFLT_PATH     = CFG_DFLT_PATH
        s.CONFIG_DIR        = CONFIG_DIR
        s.proc_pipes        = proc_pipes
        s.pre_first_update  = True
        s.last_update_time  = None
        s.lock_pipes = False

        # hard-coded default configs
        # used to construct the cfg_dict prior to loading the default file
        # and to override defaults in any loaded config file that need 
        # overriding
        s.DFLT_CFG_DICT = get_default_cfgs()

        # Config data transfer handshaking flags
        s.cfg_pipe_count    = 0
        s.cfg_pipe_maxcount = 1
        s.update_cfg_flag   = False

        s.SLOW_UPDATES  = 3.0
        s.FAST_UPDATES  = 0.1

        # maximum length of time without a real frame coming through 
        # before pushing an empty or "null" frame through the GUI to 
        # update all the objects
        s.max_null_frame_update_period     = s.SLOW_UPDATES

        # maximum length of time without a frame update when data source is 
        # dat_file or use_buffer before forcing a frame update so we can 
        # properly update all the GUI objects.
        # NOTE TODO HERE 5/22/2025!!!! 
        #s.max_buf_frame_update_period = 0.1
        #s.last_buf_frame_update = time.time()

        # used for seeing the frame-to-frame "rate"
        s.prev_frame_time = None

        # store last received frame/aux data so we can replay on tab switch
        s.last_frame_data = None
        s.last_aux_data   = None

        # sets ths title and default size of the window
        s.setWindowTitle('THz Vizualizer GUI')
        #s.setGeometry(100, 100, 400, 300)
        s.setGeometry(100, 100, 1000, 700)

        # central widget needs to be defined
        s.central_widget = QWidget()
        s.setCentralWidget(s.central_widget)
        s.layout = QVBoxLayout(s.central_widget)

        # Construct the default configuration dictionary
        s.cfg_dict = copy.deepcopy(s.DFLT_CFG_DICT)
        s.cfg_dict["default_data_dir"] = DFLT_DATA_DIR
        s.cfg_dict["flags"] = []

        # keys that indicate that a reprocessing is needed:
        s.reproc_buf_keys = ["ylen","xlen","fft_len",
            "num_noise_pts","noise_start_frac",
            "dead_pix_val",
            "calc_weighted_sum",
            "threshold_db",
            "contrast_db","half_peak_width","min_range","max_range",
            "min_az","max_az","min_el","max_el","plot_style",
            "peak_selection","aux_x_ind","aux_y_ind"]


        # config keys that if changed indicate that a file should be reloaded
        s.reload_file_keys = ["ylen","xlen","fft_len",
            "min_az","max_az","min_el","max_el"]
            
            
        # these are the keys that are excluded from being saved to 
        # config files and when loading config files
        s.excluded_keys = ["external_h5_fpath"]

        # create the tab widget which contains pretty much the remainder of
        # the GUI objects
        s.tab_widget = QTabWidget()

        s.sing_pix_tab = SingPixTab(CFG_DFLT_PATH, CONFIG_DIR, 
                                        s.update_config, s.cfg_dict)

        s.main_thz_tab = THzImageTab(CFG_DFLT_PATH, CONFIG_DIR, 
                                        s.update_config, s.cfg_dict, 
                                        s.sing_pix_tab) 

        # add the tabs to the tab widget 
        s.tab_widget.addTab(s.main_thz_tab, "Main THz Image")
        s.tab_widget.addTab(s.sing_pix_tab, "Single Pixel")

        s.layout.addWidget(s.tab_widget)


        s.tab_index_dict = {}
        s.tab_index_dict[0] = "Main THz Image"
        s.tab_index_dict[1] = "Single Pixel"
        s.tab_widget.setCurrentIndex(0)
        s.tab_widget.currentChanged.connect(s.tab_switch_callback)


        # check for default postprocessing config and execute configuration 
        # sequence if there is a default postprocessing config
        if os.path.isfile(CFG_DFLT_PATH):
            s.load_config(CFG_DFLT_PATH)
        else:
            new_cfg_dict = OrderedDict()
            new_cfg_dict["data_src"] = "disabled"
            s.update_config(new_cfg_dict)

        # finally setup the timer
        s.timer = QTimer()
        s.timer.timeout.connect(s.timer_handler)
        s.cfg_dict["flags"] = []

        # setting timer to update 10 times a second)
        s.timer.start(100)


    def tab_switch_callback(s, index):
        tab_name = s.tab_index_dict.get(index)
        if tab_name == "Single Pixel":
            if s.last_frame_data is not None:
                s.sing_pix_tab.update_image(s.last_frame_data, True)
            if s.last_aux_data is not None:
                s.sing_pix_tab.aux_update(s.last_aux_data, True)
        elif tab_name == "Main THz Image":
            if s.last_frame_data is not None:
                s.main_thz_tab.update_image(s.last_frame_data, True)



    def closeEvent(s, event):
        s.timer.stop()
        s.lock_pipes = True
        time.sleep(0.1)

        # NOTE the following 2 lines does not appear to work, but this is 
        # cleanup, we can defer this problem indefinitely 
        s.cfg_dict["data_src"] = "disabled"
        s.proc_pipes.cfg_pipe.send(s.cfg_dict)

        cfg_pipe    = s.proc_pipes.cfg_pipe
        err_pipe    = s.proc_pipes.err_pipe
        data_pipe   = s.proc_pipes.data_pipe
        query_pipe_in  = s.proc_pipes.query_pipe_in
        query_pipe_out  = s.proc_pipes.query_pipe_out

        # empty the pipes quickly
        while err_pipe.poll():
            _ = err_pipe.recv()

        while data_pipe.poll():
            _ = data_pipe.recv()

        while query_pipe_in.poll():
            _ = query_pipe_in.recv()

        close_dict = OrderedDict()
        close_dict["flags"] = "close_process"
        cfg_pipe.send(close_dict)
        event.accept()


    # central function that loads files into our config dict
    def load_config(s, fpath):
        """
        loads a config file creating a config dictionary
        """
        ret_val = False
        try:
            with open(fpath, "r", encoding="utf-8") as file:
                cfg_dict_in = json.load(file, object_pairs_hook=OrderedDict)

            # exclude the excluded keys
            cfg_dict_out = OrderedDict()
            for key in cfg_dict_in.keys():
                if key not in s.excluded_keys:
                    cfg_dict_out[key] = cfg_dict_in[key]
                else:
                    cfg_dict_out[key] = s.DFLT_CFG_DICT[key]
            s.update_config(cfg_dict_out)

        except:
            print("load_config failed")
            ret_val = True

        # pass the config to the various functions that set the appropriate 
        # GUI objects
        if s.cfg_dict != None:
            s.main_thz_tab.set_gui_config_params(s.cfg_dict)
        return ret_val



    # central function that saves our config dict to a file
    def save_config(s, fpath):
        """
        saves a config file with the current configuration dictionary
        excluding the excluded keys
        """
        # exclude the excluded keys
        cfg_dict_out = OrderedDict()
        for key in s.cfg_dict.keys():
            if key not in s.excluded_keys:
                cfg_dict_out[key] = s.cfg_dict[key]
            else:
                cfg_dict_out[key] = s.DFLT_CFG_DICT[key]

        with open(fpath, 'w') as file:
            json.dump(cfg_dict_out, file)


    @staticmethod
    def append_if_absent(cfg_flags, new_flag):
        if new_flag not in cfg_flags:
            cfg_flags.append(new_flag)
        return cfg_flags


    # NOTE NOTE NOTE: ACTUALLY WRITE THIS FUNCTION!
    # NOTE so we need a few more functions to to "centralize" the configuration
    # and flag generation for the processing core (which is interacted 
    # with here)
    def update_config(s, cfg_dict_in, cfg_flags_in=None):
        """
        This function is called by lower level objects (the tabs) to "update"
        the configuraiton dictionary and trigger the main window to send
        an updated version of the configuraiton to the processing core.
        
        We don't want other objects in the GUI changing cfg_dict directly, so
        while cfg_dict is sent pretty much everywhere, it is only ever changed
        HERE.  

        Additionally, some GUI object changes will trigger many calls to 
        update_config() over a short period of time (like moving a slider).  
        This has the potential to overwhelm the processing core as it would
        require processing each change.  Thus here changes are accumulated 
        and less frequent updates are sent to the processing core (in the 
        timer_handler).  If an update needs to take effect ASAP, then the 
        "force_update" flag can be sent through cfg_flags_in.  

        note that cfg_dict_in is not a complete cfg_dict, it only contains 
        keys that have been changed.   same with cfg_flags_in

        The central object of the GUI "cfg_dict" is updated every time this 
        function is called, however the updated "cfg_dict" is not sent to 
        the processing core.  That happens less frequently in the timer 
        event handler.  This is to minimize overwhelming the processing 
        core's pipe whenever the user makes a small change to the system by 
        typing values in a textbox it's all to keep the processing system 
        moving quickly.  
        """
        #if (cfg_dict_in != None) and (cfg_dict_in != {}):
        #    cfg_flags_none = (cfg_flags_in == None) or (cfg_flags_in != [])
        #    just_curr_frame_id = ((len(cfg_dict_in.keys()) == 1) and 
        #                         ("curr_frame_id" in cfg_dict_in.keys()))

        #    if ((not cfg_flags_none) or (not just_curr_frame_id)):
        #        print("--------------------")
        #        print("UPDATE CONFIG (apart from just curr_frame_id)!:")
        #        print(cfg_dict_in)
        #        print(cfg_flags_in)
        #        print("--------------------\n")


        #else:
        #    print("--------------------")
        #    print("UPDATE CONFIG (apart from just curr_frame_id)!:")
        #    print(cfg_dict_in)
        #    print(cfg_flags_in)
        #    print("--------------------\n")


        cfg_dict = s.cfg_dict
        cfg_flags = []
        if (cfg_dict_in != None) and (cfg_dict_in != {}):
            # construct an old dictionary
            old_cfg_dict = copy.deepcopy(cfg_dict)

            # HERE is where the global cfg_dict object that contains the 
            # configuration for the entire system is updated
            for key in cfg_dict_in.keys():
                cfg_dict[key] = cfg_dict_in[key]

            # flag checks
            if cfg_dict["external_h5_fpath"] != old_cfg_dict.get("external_h5_fpath"):
                s.append_if_absent(cfg_flags, "fname_changed")


            # check to see if anything changed that requires a reprocessing 
            # of the file buffer
            for rf_key in s.reproc_buf_keys:
                if rf_key in cfg_dict_in.keys():
                    s.append_if_absent(cfg_flags, "reproc_buf")

            # check to see if something significant enough chagned that the 
            # regridded rangelines of the file won't work anymore and the 
            # file needs to be reloaded
            for rf_key in s.reload_file_keys:
                if rf_key in cfg_dict_in.keys():
                    s.append_if_absent(cfg_flags, "reload_file")


            # check to see if the pixel grid size/shape has changed
            # which triggers a flag to notify the processor to recalculate
            # those grids
            if cfg_dict["min_az"] != old_cfg_dict["min_az"]:
                cfg_flags = s.append_if_absent(cfg_flags, "recalc_coarse_grid")
            elif cfg_dict["max_az"] != old_cfg_dict["max_az"]:
                cfg_flags = s.append_if_absent(cfg_flags, "recalc_coarse_grid")
            elif cfg_dict["min_el"] != old_cfg_dict["min_el"]:
                cfg_flags = s.append_if_absent(cfg_flags, "recalc_coarse_grid")
            elif cfg_dict["max_el"] != old_cfg_dict["max_el"]:
                cfg_flags = s.append_if_absent(cfg_flags, "recalc_coarse_grid")
            elif cfg_dict["xlen"] != old_cfg_dict["xlen"]:
                cfg_flags = s.append_if_absent(cfg_flags, "recalc_coarse_grid")
            elif cfg_dict["ylen"] != old_cfg_dict["ylen"]:
                cfg_flags = s.append_if_absent(cfg_flags, "recalc_coarse_grid")



        # calculate fs_post_dec
        fs_adc = cfg_dict["fs_adc"]
        dec_val = cfg_dict["dec_val"]
        cfg_dict["fs_post_dec"] = fs_adc/(16*(dec_val))

        # calculate the linear versions of threshold and contrast
        try:
            cfg_dict["threshold_lin"]   = 10**(cfg_dict["threshold_db"]/10)
            cfg_dict["contrast_lin"]    = 10**(cfg_dict["contrast_db"]/10)
        except OverflowError:
            print("warning - threshold or contrast too high")
            cfg_dict["threshold_lin"]   = 1000.0
            cfg_dict["contrast_lin"]    = 100.0




        if cfg_dict["profiler"] == True:
            cfg_flags = s.append_if_absent(cfg_flags, "enable_profiler")
        else:
            cfg_flags = s.append_if_absent(cfg_flags, "disable_profiler")

        # now the stuffing of the flags
        if ((cfg_flags_in != None) and (cfg_flags_in != [])):
            for flag in cfg_flags_in:
                cfg_flags = s.append_if_absent(cfg_flags, flag)

        for flag in cfg_dict["flags"]:
            cfg_flags = s.append_if_absent(cfg_flags, flag)
            
        cfg_dict["flags"] = cfg_flags





        update = False
        if s.pre_first_update:
            s.pre_first_update = False
            update = True

        elif s.last_update_time == None:
            update = True

        elif "force_update" in cfg_dict["flags"]:
            update = True

        # instead of actually sending the updated cfg_dict to the processing 
        # core  here we "mark" it for update by the timer handler which will 
        # perform the actual update and clear the flags from the dict.  
        # 
        # we do this to minimize the number of updates sent to the processing
        # core to keep the system from slowing down too much
        if update:
            s.update_cfg_flag = True



    def frame_update(s, frame_in, frame_id, data_src_in, new_frame_flag):
        """
        this updates all the appropriate THz image objects when a new frame 
        comes in
        """
        if new_frame_flag:
            cfg_dict_update = OrderedDict()
            #if s.cfg_dict["data_src"] != "use_buffer":
            cfg_dict_update["curr_frame_id"] = frame_id
            s.update_config(cfg_dict_update)



        # TODO change the updates based on which tabs are visible to make
        # the GUI look less sluggish
        if new_frame_flag and s.cfg_dict["frame_update_dbg"]:
            if s.prev_frame_time == None:
                s.prev_frame_time = time.time_ns()

            else:
                curr_time = time.time_ns()
                frame_period_ns = curr_time - s.prev_frame_time
                frame_period_ms = frame_period_ns / 1e6
                print(f"frame_period_ms = {frame_period_ms:.4f}")
                s.prev_frame_time = curr_time
        
        if new_frame_flag and frame_in is not None:
            s.last_frame_data = frame_in
            s.main_thz_tab.update_image(frame_in, new_frame_flag)
            s.sing_pix_tab.update_image(frame_in, new_frame_flag)
        else:
            if s.tab_index_dict[s.tab_widget.currentIndex()] == "Main THz Image":
                s.main_thz_tab.update_image(frame_in, new_frame_flag)
            elif s.tab_index_dict[s.tab_widget.currentIndex()] == "Single Pixel":
                s.sing_pix_tab.update_image(frame_in, new_frame_flag)


    def aux_update(s, aux_data_in, new_frame_flag):
        """
        this updates all the appropriate auxilary plot objects when a new 
        frame ( + auxiliary data) comes in
        """
        if new_frame_flag and aux_data_in is not None:
            s.last_aux_data = aux_data_in
        if s.tab_index_dict[s.tab_widget.currentIndex()] == "Single Pixel":
            s.sing_pix_tab.aux_update(aux_data_in, new_frame_flag)

    
    def timer_handler(s):
        """
        timer event handler, handles most of the transfer of data between
        the GUI and the data_processor
        """
        if s.cfg_dict["dbg_0"]:
            _dbg = True
        else:
            _dbg = False
        #if s.dbg_i > 100:
        #    s.dbg_i = 0
        #    _dbg = True
        #    print("entered timer_handler")
        cfg_pipe    = s.proc_pipes.cfg_pipe
        err_pipe    = s.proc_pipes.err_pipe
        data_pipe   = s.proc_pipes.data_pipe
        query_pipe_in  = s.proc_pipes.query_pipe_in
        query_pipe_out  = s.proc_pipes.query_pipe_out
        
        # Error handling first
        if err_pipe.poll():
            err_val = err_pipe.recv()

            # do stuff with the err_val
            print(err_val) # just this for now

        if _dbg:
            print("finished error pipe handling")

        # Main frame data comes in here
        if data_pipe.poll():
            data_in     = data_pipe.recv()
            frame_in    = data_in[0]
            frame_id    = data_in[1]
            data_src_in = data_in[2]
            aux_data_in = data_in[3]
            
            pre = time.time_ns() # NOTE TODO DEBUG REMOVE
            s.frame_update(frame_in, frame_id, data_src_in, True)
            post = time.time_ns() # NOTE TODO DEBUG REMOVE
            if s.cfg_dict["frame_update_dbg"]:
                print(f"frame_update duration: {((post-pre)/1e6):.4f} ms\n")

            s.aux_update(aux_data_in, True)
            if s.cfg_dict["data_src"] == "external_h5":
                if data_src_in == "external_h5":
                    stat_id = "FILE_PROC"
                    s.main_thz_tab.update_data_src_status(stat_id)

        if _dbg:
            print("finished data pipe handling")

        # check the input queries
        while query_pipe_in.poll():
            query_in_dict = query_pipe_in.recv()
            if "CFG_ACK" in query_in_dict.keys():
                s.cfg_pipe_count -= 1
                if s.cfg_pipe_count < 0:
                    s.cfg_pipe_count  = 0
                    print("Warning: config count went negative")

            elif "FILE_PROCESSING" in query_in_dict.keys():
                if s.cfg_dict["data_src"] == "external_h5":
                    stat_id = "PROC_FILE"
                    s.main_thz_tab.update_data_src_status(stat_id)

            elif "EXTERNAL_H5_META" in query_in_dict.keys():
                meta = query_in_dict["EXTERNAL_H5_META"]
                s.cfg_dict["min_az"] = meta["min_az"]
                s.cfg_dict["max_az"] = meta["max_az"]
                s.cfg_dict["min_el"] = meta["min_el"]
                s.cfg_dict["max_el"] = meta["max_el"]
                s.cfg_dict["az_encoder_to_cm"] = 1.0
                s.cfg_dict["el_encoder_to_cm"] = 1.0

            else:
                print(f"Warning: invalid query keys: {query_in_dict.keys()}")

        # set the update period based on the data_src
        if s.cfg_dict["data_src"] == "external_h5":
            s.max_null_frame_update_period = s.FAST_UPDATES
        else: # "disabled" or others
            s.max_null_frame_update_period = s.SLOW_UPDATES


        if _dbg:
            print("finished query_pipe_in handling")

        if _dbg:
            print("finished query_pipe_out handling")

        # NOTE Placeholder
        # otherwise just trash whatever comes out of the query for now

        # here we perform the actual configuration update and handshaking
        # 
        # first check if it's been a while
        if s.last_update_time != None:
            if ((time.time() - s.last_update_time) > s.max_null_frame_update_period):
                s.update_cfg_flag = True
                s.frame_update(None, None, None, False)

        if _dbg:
            print("finished check of min update period handling")
            print(f"(time.time() - s.last_update_time) = {(time.time() - s.last_update_time)}")


        if s.update_cfg_flag and (not s.lock_pipes):
            # check to see if the data_processor has acklowledged receipt of
            # the last configuration packet
            if s.cfg_pipe_count < s.cfg_pipe_maxcount:
                s.proc_pipes.cfg_pipe.send(s.cfg_dict)
                s.last_update_time = time.time()
                s.cfg_dict["flags"] = []
                s.cfg_pipe_count += 1
                s.update_cfg_flag = False


        if _dbg:
            print("end of event handler\n")


if __name__ == '__main__':
    CWD = os.getcwd() 
    if os.name == "nt":
        CONFIG_DIR  = CWD + "\\config\\"
        DFLT_DATA_DIR  =   os.path.dirname(os.getcwd()) + "\\data\\"
    elif os.name == "posix":
        CONFIG_DIR  = CWD + "/config/"
        DFLT_DATA_DIR = "/tmp/"
    else:
        raise Exception("Invalid OS Name")

    CFG_DFLT_FNAME  = "default_cfg.json"
    #PLOT_SETTINGS_DFLT_FNAME    = "plot_settings_default.json"
    #POSTPROC_CFG_DFLT_FNAME     = "postproc_default_cfg.json"
    #PLOT_SETTINGS_DFLT_PATH     = CONFIG_DIR + PLOT_SETTINGS_DFLT_FNAME
    #POSTPROC_DFLT_CFG_PATH      = CONFIG_DIR + POSTPROC_CFG_DFLT_FNAME
    CFG_DFLT_PATH   = CONFIG_DIR + CFG_DFLT_FNAME

    # this is supposed to allow quitting the app from CTRL-C on console
    signal.signal(signal.SIGINT, sigint_handler)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("THz Visualizer")
    app.setApplicationVersion("0.0.1")

    # Icon Do I need one? We should get one later
    #icon = QtGui.QIcon("Cover_Symbol_RGB_Black.svg")
    #app.setWindowIcon(icon)

    import argparse
    ap = argparse.ArgumentParser(description="THz Visualizer")
    ap.add_argument("h5file", nargs="?", default="",
                    help="HDF5 data cube file path to load on startup")
    args, _qt_remaining = ap.parse_known_args()
    h5_file_arg = args.h5file

    # this should be all we need for the initial configuration dictionary
    cfg_dict = OrderedDict()
    cfg_dict["data_src"] = "disabled"
    cfg_dict["default_data_dir"] = DFLT_DATA_DIR

    # construct the multiprocessing system
    mp.set_start_method("spawn")
    (proc_cfg_pipe, cfg_pipe)      = mp.Pipe(duplex=False)
    (err_pipe, proc_err_pipe)      = mp.Pipe(duplex=False)
    (data_pipe, proc_data_pipe)    = mp.Pipe(duplex=False)
    (proc_query_pipe_in, query_pipe_out)  = mp.Pipe(duplex=False)
    (query_pipe_in, proc_query_pipe_out)  = mp.Pipe(duplex=False)

    proc = mp.Process(target=dp.main_proc_loop, args=(proc_cfg_pipe, 
        proc_err_pipe, proc_data_pipe, proc_query_pipe_in, proc_query_pipe_out,
        cfg_dict,))
    proc.start()
    proc_pipes = ProcPipes(cfg_pipe, err_pipe, data_pipe, query_pipe_in, 
                           query_pipe_out)

    # Defining and showing the main window
    window = MainWindow(DFLT_DATA_DIR, CFG_DFLT_PATH, CONFIG_DIR, proc_pipes)
                
    window.show()

    # If an HDF5 file was passed via command line, load it
    if h5_file_arg:
        h5_path = os.path.abspath(h5_file_arg)
        if os.path.isfile(h5_path):
            h5_path = h5_path.replace("\\", "/")
            cfg_update = OrderedDict()
            cfg_update["external_h5_fpath"] = h5_path
            cfg_update["data_src"] = "external_h5"
            window.main_thz_tab.curr_h5_val_ledit.setText(h5_path)
            window.update_config(cfg_update, ["fname_changed"])
        else:
            print(f"Warning: HDF5 file not found: {h5_path}")
    sys.exit(app.exec())

    # NOTE the following line of code doesn't actually work properly 
    # because we never actually get here even after X-ing out the window
    proc.join()


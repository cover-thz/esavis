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
import ipdb # NOTE REMOVE
import json
#from math import nan
import signal
import numpy as np
import pyqtgraph as pg
import multiprocessing as mp
from collections import OrderedDict
import copy
import subprocess


if __name__ == '__main__':
    CWD = os.getcwd() 
    if os.name == "nt":
        # remake the makefile
        c_funcs_dir = CWD + "\\postproc\\c_funcs"
        result = subprocess.run(["make"], cwd=c_funcs_dir)
    elif os.name == "posix":
        # remake the makefile
        c_funcs_dir = CWD + "/postproc/c_funcs"
        result = subprocess.run(["make"], cwd=c_funcs_dir)
    else:
        raise Exception("Invalid OS Name")

#from dataclasses import dataclass, field
from ConfigTab import ConfigTab
from THzImageTab import THzImageTab
from DebugTab import DebugTab
from CameraTab import CameraTab
import time

# crude but effective way of getting the postprocessing directory in here
# without playing maddening namespace games with the modules in the that
#directory
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
##############################################################################
# DEFAULT CONFIG SET
##############################################################################

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

DFLT_CFG_DICT["data_format_in"] = "time_domain"

DFLT_CFG_DICT["turn_hyst"]  = 0.
DFLT_CFG_DICT["turn_az_margin"]  = 0.
DFLT_CFG_DICT["daq_num_rangelines"]  = 0
DFLT_CFG_DICT["fraction_filled_thresh"]  = 0.1
DFLT_CFG_DICT["save_image_desc"] = "NONE"

DFLT_CFG_DICT["threshold_db"] = 0.
DFLT_CFG_DICT["contrast_db"] = 0.
DFLT_CFG_DICT["half_peak_width"] = 1

DFLT_CFG_DICT["min_range"] = 0.
DFLT_CFG_DICT["max_range"] = 7000.

DFLT_CFG_DICT["autoscale_color"] = False
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
DFLT_CFG_DICT["fname_list"]  = None
DFLT_CFG_DICT["paused"]     = False
    
# These values do not appear in the GUI yet
# so they are "hard-coded"
DFLT_CFG_DICT["daq_timeout"]  = 2.
DFLT_CFG_DICT["el_encoder_to_cm"]  = 16/500
DFLT_CFG_DICT["az_encoder_to_cm"]  = 16/500
DFLT_CFG_DICT["daq_addr"]  = "localhost"


# These are currently hard-coded but need to be propagated to the single-pixel
# GUI
DFLT_CFG_DICT["aux_x_ind"] = 10
DFLT_CFG_DICT["aux_y_ind"] = 10
DFLT_CFG_DICT["flags"] = []


# NOTE Debug dictionary objects for use with the debug tab
DFLT_CFG_DICT["dbg_0"] = False
DFLT_CFG_DICT["dbg_1"] = False
DFLT_CFG_DICT["dbg_2"] = False
DFLT_CFG_DICT["profiler"] = False


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
    daq_connected = False


    def __init__(s, DFLT_DATA_DIR, CFG_DFLT_PATH, CONFIG_DIR, proc_pipes):
        super().__init__()

        # going with a single configuration file rather than two
        s.CFG_DFLT_PATH     = CFG_DFLT_PATH
        s.CONFIG_DIR        = CONFIG_DIR
        s.proc_pipes        = proc_pipes
        s.pre_first_update  = True
        s.last_update_time  = None
        s.lock_pipes = False

        # Config data transfer handshaking flags
        s.cfg_pipe_count   = 0
        s.cfg_pipe_maxcount = 3
        s.update_cfg_flag  = False

        # starts out at 2 seconds when the daq is not connected, changes t
        s.NO_DAQ_PERIOD = 1.0
        s.DAQ_CONNECTED_PERIOD = 0.25
        s.min_update_period    = s.NO_DAQ_PERIOD

        # this is used to mark time for how often we're querying the processing
        # core to see if the DAQ is connected
        s.last_daq_query_time   = None
        s.daq_query_period      = 1

        # sets ths title and default size of the window
        s.setWindowTitle('THz Vizualizer GUI')
        #s.setGeometry(100, 100, 400, 300)
        s.setGeometry(100, 100, 500, 700)

        # central widget needs to be defined
        s.central_widget = QWidget()
        s.setCentralWidget(s.central_widget)
        s.layout = QVBoxLayout(s.central_widget)

        # Construct the default configuration dictionary
        s.cfg_dict = copy.deepcopy(DFLT_CFG_DICT)
        s.cfg_dict["default_data_dir"] = DFLT_DATA_DIR
        s.cfg_dict["flags"] = []

        # keys that indicate that a file should be reprocessed:
        s.reproc_file_keys = ["el_side_0_start","el_side_0_end",
            "el_side_1_start","el_side_1_end","ylen","xlen","fft_len",
            "num_noise_pts","noise_start_frac","chirp_span","chirp_time",
            "dead_pix_val","fs_adc","el_offset0","el_offset1",
            "center_rangeval","dec_val","ch0_offset","ch1_offset",
            "disable_el_side0","disable_el_side1","calc_weighted_sum",
            "ch0_en","ch1_en","data_format_in","turn_hyst","turn_az_margin",
            "daq_num_rangelines","fraction_filled_thresh","threshold_db",
            "contrast_db","half_peak_width","min_range","max_range",
            "min_az","max_az","min_el","max_el","plot_style",
            "peak_selection","aux_x_ind","aux_y_ind"]


        # create the tab widget which contains pretty much the remainder of
        # the GUI objects
        s.tab_widget = QTabWidget()
        s.cfg_tab    = ConfigTab(CFG_DFLT_PATH, CONFIG_DIR, 
                                    s.load_config, 
                                    s.save_config, s.update_config,
                                    s.cfg_dict)


        s.camera_tab   = CameraTab(CFG_DFLT_PATH, CONFIG_DIR, 
                                        s.update_config, 
                                        s.cfg_dict)

        # unfortunately I needed to give the camera tab's thz image object
        # to this main tab so the reset plot camera button would work
        s.main_thz_tab = THzImageTab(CFG_DFLT_PATH, CONFIG_DIR, 
                                        s.update_config, 
                                        s.cfg_dict, 
                                        s.camera_tab) 




        s.single_pix_tab  = QWidget() # TODO Placeholder 

        s.debug_tab = DebugTab(CFG_DFLT_PATH, CONFIG_DIR, 
                                        s.update_config, 
                                        s.cfg_dict)

        # add the tabs to the tab widget 
        s.tab_widget.addTab(s.cfg_tab, "Config")
        s.tab_widget.addTab(s.main_thz_tab, "Main THz Image")
        #s.tab_widget.addTab(s.camera_tab, "Camera Overlay")
        s.tab_widget.addTab(s.camera_tab, "Large Viewer")
        s.tab_widget.addTab(s.single_pix_tab, "Single Pixel")
        s.tab_widget.addTab(s.debug_tab, "Debug")

        s.layout.addWidget(s.tab_widget)

        s.init_single_pix_tab()  # TODO Placeholder

        # set the GUI to view the config tab
        s.tab_widget.setCurrentIndex(0)

        #s.tab_widget.currentChanged.connect(s.tab_switch_callback)


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
        # Main THz image
        if index == 1:
            thz_image_obj = s.main_thz_tab.thz_image_obj
            s.camera_tab.remove_thz_image(thz_image_obj)
            s.main_thz_tab.add_thz_image(thz_image_obj)
        elif index == 2:
            thz_image_obj = s.main_thz_tab.thz_image_obj
            s.main_thz_tab.remove_thz_image(thz_image_obj)
            s.camera_tab.add_thz_image(thz_image_obj)

        # Large Viewer / CameraTab



    def closeEvent(s, event):
        s.lock_pipes = True
        s.timer.stop()

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

    def init_camera_tab(s):
        """
        This is just a placeholder for Tab 3 until I actually create GUI 
        content for the camera overlay
        """
        layout = QVBoxLayout(s.camera_tab)
        label = QLabel("Camera Overlay goes here")
        layout.addWidget(label)


    def init_single_pix_tab(s):
        """
        This is just a placeholder for Tab 4 until I actually create GUI 
        content for the single pixel tab
        """
        layout = QVBoxLayout(s.single_pix_tab)
        label = QLabel("Single Pixel goes here")
        layout.addWidget(label)


    # central function that loads files into our config dict
    def load_config(s, fpath):
        """
        loads a config file creating a config dictionary
        """
        ret_val = False
        try:
            with open(fpath, "r", encoding="utf-8") as file:
                cfg_dict = json.load(file, object_pairs_hook=OrderedDict)
            s.update_config(cfg_dict)
        except:
            print("load_config failed")
            ret_val = True

        # pass the config to the various functions that set the appropriate 
        # GUI objects
        if s.cfg_dict != None:
            s.cfg_tab.set_gui_config_params(s.cfg_dict)
            s.main_thz_tab.set_gui_config_params(s.cfg_dict)
        return ret_val




    # central function that saves our config dict to a file
    def save_config(s, fpath):
        """
        saves a config file with the current configuration dictionary
        """
        with open(fpath, 'w') as file:
            json.dump(s.cfg_dict, file)

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

        note that cfg_dict_in is not a complete cfg_dict, it only contains 
        keys that have been changed.   same with cfg_flags_in
        """
        
        # here we check the input dict to see if there are any changes that
        # trigger a flag change

        # then here we append the cfg_flags_in, which is really just an 
        # opportunity for hte lower level tab to force-trigger a flag 
        # condition
    
        # NOTE we need to have some sort of buffering/throttling system so that
        # we only send something line 3-4 updates per second maximum and if 
        # there are more updates than that sent, then we combine them into a 
        # single update with prefeerence to later update values.
        #
        # I can imagine changing the contrast slider repeatedly causing many
        # contrast updates occuring in sort sequence, but only the last one 
        # is actually propagated
        #
        # Alternatively we could have an "ACK" signal of some kind come back
        # from the processor core along an new pipe to indicate the config
        # has been recieved and is being processed so we could properly combine
        # and buffer the requests 
        #
        #

        # NOTE  you need to calculate fs_post_dec from fs_adc and dec_val
        # whenever either of them change

        # NOTE construct some sort of buffering of changes when you have 
        # tabs that don't have THz images visible so you don't hammer the
        # processing
        cfg_dict = s.cfg_dict
        cfg_flags = []
        if (cfg_dict_in != None) and (cfg_dict_in != {}):
            # construct an old dictionary
            old_cfg_dict = copy.deepcopy(cfg_dict)

            # update the dictionary
            for key in cfg_dict_in.keys():
                cfg_dict[key] = cfg_dict_in[key]

            # flag checks
            if cfg_dict["fname_list"] != old_cfg_dict["fname_list"]:
                s.append_if_absent(cfg_flags, "fname_changed")

            for rf_key in s.reproc_file_keys:
                if rf_key in cfg_dict_in.keys():
                    s.append_if_absent(cfg_flags, "reproc_file")


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


            if cfg_dict["data_src"] == "daq":
                if cfg_dict["ch0_en"] != old_cfg_dict["ch0_en"]:
                    cfg_flags = s.append_if_absent(cfg_flags, "update_daq_ch")
                elif cfg_dict["ch1_en"] != old_cfg_dict["ch1_en"]:
                    cfg_flags = s.append_if_absent(cfg_flags, "update_daq_ch")


        # calculate fs_post_dec
        fs_adc = cfg_dict["fs_adc"]
        dec_val = cfg_dict["dec_val"]
        cfg_dict["fs_post_dec"] = fs_adc/(16*(dec_val))

        # calculate the linear versions of threshold and contrast
        cfg_dict["threshold_lin"]   = 10**(cfg_dict["threshold_db"]/10)
        cfg_dict["contrast_lin"]    = 10**(cfg_dict["contrast_db"]/10)

        # always send the "setup_daq" flag if daq is data source
        if cfg_dict["data_src"] == "daq":
            cfg_flags = s.append_if_absent(cfg_flags, "setup_daq")

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


        # flag that data is currently being reprocessed
        # only a small lie
        if s.cfg_dict["data_src"] == "dat_file":
            if "reproc_file" in cfg_flags:
                stat_id = "PROC_FILE"
                s.main_thz_tab.update_data_src_status(stat_id)


        update = False
        if s.pre_first_update:
            s.pre_first_update = False
            update = True

        elif s.last_update_time == None:
            update = True

        elif "force_update" in cfg_dict["flags"]:
            update = True

        else:
            if ((time.time() - s.last_update_time) > s.min_update_period):
                update = True

        # instead of actually performing the update here we "mark" it for
        # update by the timer handler which will perform the actual update
        # and clear the flags from the dict
        if update:
            s.update_cfg_flag = True




    def frame_update(s, frame_in, new_frame_flag):
        """
        this updates all the appropriate THz image objects when a new frame 
        comes in
        """
        s.main_thz_tab.update_image(frame_in, new_frame_flag)
        s.camera_tab.update_image(frame_in, new_frame_flag)


    def aux_update(s, aux_data_in):
        """
        this updates all the appropriate auxilary plto objects when a new 
        frame ( + auxiliary data) comes in
        """
        pass

    
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
            aux_data_in = data_in[1]
            
            s.frame_update(frame_in, True)
            s.aux_update(aux_data_in)
            if s.cfg_dict["data_src"] == "dat_file":
                stat_id = "FILE_PROC"
                s.main_thz_tab.update_data_src_status(stat_id)

        if _dbg:
            print("finished data pipe handling")

        # check the input queries
        if query_pipe_in.poll():
            query_in_dict = query_pipe_in.recv()
            if "DAQ_STATUS" in query_in_dict.keys():
                s.last_daq_query_time = time.time()
                if query_in_dict["DAQ_STATUS"] == "CONNECTED":
                    stat_id = "CONNECTED"
                    if not s.daq_connected:
                        print(f"stat_id = {stat_id}")
                    s.daq_connected = True
                    s.min_update_period = s.DAQ_CONNECTED_PERIOD
                    s.main_thz_tab.update_data_src_status(stat_id)
                else:
                    stat_id = "NOT_CONNECTED"
                    if s.daq_connected:
                        print(f"stat_id = {stat_id}")
                    s.daq_connected = False
                    s.min_update_period = s.NO_DAQ_PERIOD
                    s.main_thz_tab.update_data_src_status(stat_id)
            elif "CFG_ACK" in query_in_dict.keys():
                s.cfg_pipe_count -= 1
                if s.cfg_pipe_count < 0:
                    s.cfg_pipe_count  = 0
                    print("Warning: config count went negative")

            elif "FILE_PROCESSING" in query_in_dict.keys():
                if s.cfg_dict["data_src"] == "dat_file":
                    stat_id = "PROC_FILE"
                    s.main_thz_tab.update_data_src_status(stat_id)

            else:
                print(f"Warning: invalid query keys: {query_in_dict.keys()}")
                       
        if _dbg:
            print("finished query_pipe_in handling")

        # check for DAQ connected
        if s.cfg_dict["data_src"] == "daq":
            if s.last_daq_query_time == None:
                query_pipe_out.send(["DAQ_STATUS"])
                s.last_daq_query_time = time.time()
            elif (time.time() - s.last_daq_query_time) > s.daq_query_period:
                query_pipe_out.send(["DAQ_STATUS"])
                s.last_daq_query_time = time.time()

        if _dbg:
            print("finished query_pipe_out handling")

        # NOTE Placeholder
        # otherwise just trash whatever comes out of the query for now

        # here we perform the actual configuration update and handshaking
        # 
        # first check if it's been a while
        if s.last_update_time != None:
            if ((time.time() - s.last_update_time) > s.min_update_period):
                s.update_cfg_flag = True
                s.update_config(None)
                s.frame_update(None, False)

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

    # disabling command-line parsing options for now because nobody will 
    # actually use them
    parser = QtCore.QCommandLineParser()
    parser.addHelpOption()
    parser.addVersionOption()

    #config_file_option = QtCore.QCommandLineOption(
    #    ["c", "config"], "Config file path to load", "file")
    #parser.addOption(config_file_option)
    parser.process(app)
    #config_file = parser.value(config_file_option)

    # this should be all we need for the initial configuration dictionary
    cfg_dict = OrderedDict()
    cfg_dict["data_src"] = "disabled"
    cfg_dict["default_data_dir"] = DFLT_DATA_DIR

    # construct the multiprocessing system
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
    #window = MainWindow(config_file)
    window = MainWindow(DFLT_DATA_DIR, CFG_DFLT_PATH, CONFIG_DIR, proc_pipes)
                
    window.show()
    sys.exit(app.exec())

    # NOTE the following line of code doesn't actually work properly 
    # because we never actually get here even after X-ing out the window
    proc.join()


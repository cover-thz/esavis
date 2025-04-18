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
import subprocess
#from dataclasses import dataclass, field
from ConfigTab import ConfigTab
from THzImageTab import THzImageTab

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
                    query_pipe):
        s.cfg_pipe = cfg_pipe
        s.err_pipe   = err_pipe
        s.data_pipe    = data_pipe
        s.query_pipe   = query_pipe


# quit the app on Ctrl + C from console
def sigint_handler(*_):
    print("HIT CTRL-C")
    QtGui.QGuiApplication.quit()


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


    def __init__(self, CFG_DFLT_PATH, CONFIG_DIR, DFLT_DATA_DIR, proc_pipes):
        super().__init__()

        # going with a single configuration file rather than two
        self.CFG_DFLT_PATH      = CFG_DFLT_PATH
        self.CONFIG_DIR         = CONFIG_DIR
        self.DFLT_DATA_DIR      = DFLT_DATA_DIR
        self.proc_pipes         = proc_pipes

        # sets ths title and default size of the window
        self.setWindowTitle('THz Vizualizer GUI')
        #self.setGeometry(100, 100, 400, 300)
        self.setGeometry(100, 100, 500, 700)

        # central widget needs to be defined
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # create the tab widget which contains pretty much the remainder of
        # the GUI objects
        self.tab_widget = QTabWidget()
        self.cfg_tab    = ConfigTab(CFG_DFLT_PATH, CONFIG_DIR, 
                                    DFLT_DATA_DIR, self.load_config, 
                                    self.save_config, self.update_config)
                                    
                                    
        self.main_thz_tab = THzImageTab(self, CFG_DFLT_PATH, CONFIG_DIR, 
                                    DFLT_DATA_DIR, self.update_config)
        self.camera_tab   = QWidget() # TODO Placeholder until 
                                      # I get the camera working

        self.single_pix_tab  = QWidget() # TODO Placeholder 



        # add the tabs to the tab widget 
        self.tab_widget.addTab(self.cfg_tab, "Config")
        self.tab_widget.addTab(self.main_thz_tab, "Main THz Image")
        self.tab_widget.addTab(self.camera_tab, "Camera Overlay")
        self.tab_widget.addTab(self.single_pix_tab, "Single Pixel")

        self.layout.addWidget(self.tab_widget)

        self.init_camera_tab() # TODO Placeholder
        self.init_single_pix_tab() # TODO Placeholder

        # set the GUI to view the config tab
        self.tab_widget.setCurrentIndex(0)

        # check for default postprocessing config and execute configuration 
        # sequence if there is a default postprocessing config
        if os.path.isfile(CFG_DFLT_PATH):
            self.load_config(CFG_DFLT_PATH)
        else:
            new_cfg_dict = OrderedDict()
            new_cfg_dict["data_src"] = "disabled"
            self.update_config(new_cfg_dict)

        # finally setup the timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_handler)

        # setting timer to update 10 times a second)
        self.timer.start(100)



    def init_camera_tab(self):
        """
        This is just a placeholder for Tab 3 until I actually create GUI 
        content for the camera overlay
        """
        layout = QVBoxLayout(self.camera_tab)
        label = QLabel("Camera Overlay goes here")
        layout.addWidget(label)


    def init_single_pix_tab(self):
        """
        This is just a placeholder for Tab 4 until I actually create GUI 
        content for the single pixel tab
        """
        layout = QVBoxLayout(self.single_pix_tab)
        label = QLabel("Single Pixel goes here")
        layout.addWidget(label)


    # central function that loads files into our config dict
    def load_config(self, fpath):
        """
        loads a config file creating a config dictionary
        """
        with open(fpath, "r", encoding="utf-8") as file:
            cfg_dict = json.load(file, opbject_pairs_hook=OrderedDict)
        self.update_config(cfg_dict)


    # central function that saves our config dict to a file
    def save_config(self, fpath):
        """
        saves a config file with the current configuration dictionary
        """
        with open(fpath, 'w') as file:
            json.dump(self.cfg_dict, file)


    # NOTE NOTE NOTE: ACTUALLY WRITE THIS FUNCTION!
    # NOTE so we need a few more functions to to "centralize" the configuration
    # and flag generation for the processing core (which is interacted 
    # with here)
    def update_config(self, cfg_dict_in, cfg_flags_in=None):
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

        print(cfg_dict_in)

        pass
        


    def frame_update(self, frame_in):
        """
        this updates all the appropriate THz image objects when a new frame 
        comes in
        """
        pass



    def aux_update(self, aux_data_in):
        """
        this updates all the appropriate auxilary plto objects when a new 
        frame ( + auxiliary data) comes in
        """
        pass


    
    def timer_handler(self):
        """
        timer event handler
        """
        cfg_pipe    = self.proc_pipes.cfg_pipe
        err_pipe    = self.proc_pipes.err_pipe
        data_pipe   = self.proc_pipes.data_pipe
        query_pipe  = self.proc_pipes.query_pipe
        
        # Error handling first
        if err_pipe.poll():
            err_val = err_pipe.recv()

            # do stuff with the err_val
            print(err_val) # just this for now


        # Main frame data comes in here
        if data_pipe.poll():
            data_in     = data_pipe.recv()
            frame_in    = data_in[0]
            aux_data_in = data_in[1]
            
            self.frame_update(frame_in)
            self.aux_update(aux_data_in)


        # query pipe is presently unused
        if query_pipe.poll():
            pass







if __name__ == '__main__':

    CWD = os.getcwd() 
    if os.name == "nt":
        # remake the makefile
        c_funcs_dir = CWD + "\\postproc\\c_funcs"
        result = subprocess.run(["make"], cwd=c_funcs_dir)

        CONFIG_DIR  = CWD + "\\config\\"
        DFLT_DATA_DIR  =   os.getcwd() + "\\data\\"
    elif os.name == 'posix':
        # remake the makefile
        c_funcs_dir = CWD + "/postproc/c_funcs"
        result = subprocess.run(["make"], cwd=c_funcs_dir)

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

    # construct the multiprocessing system
    (proc_cfg_pipe, cfg_pipe)      = mp.Pipe(duplex=False)
    (err_pipe, proc_err_pipe)      = mp.Pipe(duplex=False)
    (data_pipe, proc_data_pipe)    = mp.Pipe(duplex=False)
    (query_pipe, proc_query_pipe)  = mp.Pipe(duplex=False)

    proc = mp.Process(target=dp.main_proc_loop, args=(proc_cfg_pipe, 
        proc_err_pipe, proc_data_pipe, proc_query_pipe, cfg_dict,))
    proc.start()
    proc_pipes = ProcPipes(cfg_pipe, err_pipe, data_pipe, query_pipe)

    # Defining and showing the main window
    #window = MainWindow(config_file)
    window = MainWindow(CFG_DFLT_PATH, CONFIG_DIR, DFLT_DATA_DIR, proc_pipes)
                
    window.show()
    sys.exit(app.exec())

    # NOTE the following line of code doesn't actually work properly 
    # because we never actually get here even after X-ing out the window
    proc.join()


# this contains the ConfigTab() class


from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
import os
import ipdb # NOTE REMOVE
import json
#from math import nan
#import sys
#import signal
import numpy as np
import build_config_tab as bct
#import pyqtgraph as pg
#from dataclasses import dataclass, field

import time

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
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QScrollArea,
)


##############################################################################
# Simple Helper Functions
##############################################################################

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


def fix_data_path(data_path_in):
    """
    This function just changes a data path that uses windows backslashes to 
    use unix forward slashees
    """
    data_path_out = ""
    for char in data_path_in:
        if char == "\\":
            data_path_out += "/"
        else:
            data_path_out += char
    return data_path_out



##############################################################################
# Simple Dialog Box Class
##############################################################################

class SimpDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Confirm Default Config Change Dialog")

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        msg_str  = "Are you sure you want to change "
        msg_str += "the default configuration file?"
        message = QLabel(msg_str)
        self.layout.addWidget(message)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)



##############################################################################
# Main Class
##############################################################################

class ConfigTab(QScrollArea):
    """
    This is the default tab visible and contains all the main configuration 
    data for the image processing.  

    """
    # data file paths for channels 0 and 1
    data0_fpath = None
    data1_fpath = None

    def __init__(self, mainwin_obj, RADAR_DFLT_CFG_PATH, 
                 POSTPROC_DFLT_CFG_PATH, CONFIG_DIR, DFLT_DATA_DIR):
        super().__init__()

        self.mainwin_obj = mainwin_obj
        self.RADAR_DFLT_CFG_PATH      = RADAR_DFLT_CFG_PATH
        self.POSTPROC_DFLT_CFG_PATH   = POSTPROC_DFLT_CFG_PATH
        self.CONFIG_DIR               = CONFIG_DIR
        self.DFLT_DATA_DIR            = DFLT_DATA_DIR

        # builds up all the widgets and layout adds them to self
        bct.build_config_tab(self, mainwin_obj)

        ####################################################################
        # Signals/Slots stuff
        #
        # config related callbacks
        self.load_cfg_btn.clicked.connect(self.load_cfg_btn_clicked)
        self.save_cfg_btn.clicked.connect(self.save_cfg_btn_clicked)
        self.save_dflt_cfg_btn.clicked.connect(self.save_dflt_cfg_btn_clicked)
        self.load_dflt_cfg_btn.clicked.connect(self.load_dflt_cfg_btn_clicked)


        # radar data related callbacks
        self.load_ch0_btn.clicked.connect(lambda: 
                self.load_dat_btn_clicked(0))
        self.load_latest_ch0_btn.clicked.connect(lambda: 
                self.load_latest_dat_btn_clicked(0))

        self.load_ch1_btn.clicked.connect(lambda: 
                self.load_dat_btn_clicked(1))
        self.load_latest_ch1_btn.clicked.connect(lambda: 
                self.load_latest_dat_btn_clicked(1))

        self.process_data_btn.clicked.connect(self.process_data_btn_clicked)
        self.autoload_btn.clicked.connect(self.autoload_btn_clicked)

        ####################################################################
        # Activities that signal that the processing has become stale
        #
        self.el_s0_strt_ledit.textChanged.connect(self.make_stale)
        self.el_s0_end_ledit.textChanged.connect(self.make_stale)
        self.el_s1_strt_ledit.textChanged.connect(self.make_stale)
        self.el_s1_end_ledit.textChanged.connect(self.make_stale)
        self.process_side0_chkb.stateChanged.connect(self.make_stale)
        self.process_side1_chkb.stateChanged.connect(self.make_stale)
        self.num_elev_pix_ledit.textChanged.connect(self.make_stale)
        self.num_azi_pix_ledit.textChanged.connect(self.make_stale)
        self.fft_len_ledit.textChanged.connect(self.make_stale)
        self.num_noise_pts_ledit.textChanged.connect(self.make_stale)

        self.max_avgs_ledit.textChanged.connect(self.make_stale)
        self.fft_avg_rbut.toggled.connect(self.make_stale)
        self.pwr_avg_rbut.toggled.connect(self.make_stale)

        self.fsamp_freq_ledit.textChanged.connect(self.make_stale)
        self.chirp_time_us_ledit.textChanged.connect(self.make_stale)
        self.enable_ch0_chkb.stateChanged.connect(self.make_stale)
        self.enable_ch1_chkb.stateChanged.connect(self.make_stale)
        self.rough_pwr_thresh_ledit.textChanged.connect(self.make_stale)
        self.half_peak_width_ledit.textChanged.connect(self.make_stale)
        self.center_rangeval_ledit.textChanged.connect(self.make_stale)
        self.ch0_offset_ledit.textChanged.connect(self.make_stale)
        self.ch1_offset_ledit.textChanged.connect(self.make_stale)



    def get_gui_config_params(self):
        """
        grabs the current set of configuration parameters entered into the 
        various GUI textboxes and checkboxes etc. and converts them to a 
        config dictionary which is returned
        """
        radar_config_dict = {}
        radar_config_dict["el_side_0_start"]    = self.el_s0_strt_ledit.text()
        radar_config_dict["el_side_0_end"]      = self.el_s0_end_ledit.text()
        radar_config_dict["el_side_1_start"]    = self.el_s1_strt_ledit.text()
        radar_config_dict["el_side_1_end"]      = self.el_s1_end_ledit.text()

        side0_state = not self.process_side0_chkb.isChecked()
        side1_state = not self.process_side1_chkb.isChecked()
        radar_config_dict["disable_el_side0"]  = side0_state
        radar_config_dict["disable_el_side1"]  = side1_state

        radar_config_dict["npts_el"]        = self.num_elev_pix_ledit.text()
        radar_config_dict["npts_az"]        = self.num_azi_pix_ledit.text()
        radar_config_dict["fft_len"]        = self.fft_len_ledit.text()
        radar_config_dict["num_noise_pts"]  = self.num_noise_pts_ledit.text()
        radar_config_dict["max_num_avgs"]   = self.max_avgs_ledit.text()

        if self.fft_avg_rbut.isChecked():
            radar_config_dict["avg_style"]      = "fft"

        elif self.pwr_avg_rbut.isChecked():
            radar_config_dict["avg_style"]      = "power"

        else:
            radar_config_dict["avg_style"]      = "none"

        radar_config_dict["fs_adc_msps"]    = self.fsamp_freq_ledit.text()
        radar_config_dict["chirp_time_us"]  = self.chirp_time_us_ledit.text()

        ch0_en = self.enable_ch0_chkb.isChecked()
        ch1_en = self.enable_ch1_chkb.isChecked()
        radar_config_dict["channel_0_en"]  = ch0_en
        radar_config_dict["channel_1_en"]  = ch1_en
        radar_config_dict["rough_pwr_thresh"]  = self.rough_pwr_thresh_ledit.text()
        radar_config_dict["half_peak_width"]  = self.half_peak_width_ledit.text()
        radar_config_dict["center_rangeval"]  = self.center_rangeval_ledit.text()

        radar_config_dict["ch0_offset"]  = self.ch0_offset_ledit.text()
        radar_config_dict["ch1_offset"]  = self.ch1_offset_ledit.text()
        return radar_config_dict
        


    def set_gui_config_params(self, radar_config_dict):
        """
        takes the passed radar config dictionary and distributes the values 
        to the relevent GUI objects (the inverse of get_gui_config_params)
        """
        self.el_s0_strt_ledit.setText(str(radar_config_dict["el_side_0_start"]))
        self.el_s0_end_ledit.setText(str(radar_config_dict["el_side_0_end"]))
        self.el_s1_strt_ledit.setText(str(radar_config_dict["el_side_1_start"]))
        self.el_s1_end_ledit.setText(str(radar_config_dict["el_side_1_end"]))

        side0_state = not bool(radar_config_dict["disable_el_side0"])
        side1_state = not bool(radar_config_dict["disable_el_side1"])
        self.process_side0_chkb.setChecked(side0_state)
        self.process_side1_chkb.setChecked(side1_state)

        self.num_elev_pix_ledit.setText(str(radar_config_dict["npts_el"]))
        self.num_azi_pix_ledit.setText(str(radar_config_dict["npts_az"]))
       
        self.fft_len_ledit.setText(str(radar_config_dict["fft_len"]))
        self.num_noise_pts_ledit.setText(str(radar_config_dict["num_noise_pts"]))

        self.max_avgs_ledit.setText(str(radar_config_dict["max_num_avgs"])) 

        self.fft_avg_rbut.setChecked(False)
        self.pwr_avg_rbut.setChecked(False)

        if radar_config_dict["avg_style"] == "fft":
            self.fft_avg_rbut.setChecked(True)

        elif radar_config_dict["avg_style"] == "power":
            self.pwr_avg_rbut.setChecked(True)

        self.fsamp_freq_ledit.setText(str(radar_config_dict["fs_adc_msps"]))
        self.chirp_time_us_ledit.setText(str(radar_config_dict["chirp_time_us"]))

        ch0_en = bool(radar_config_dict["channel_0_en"])
        ch1_en = bool(radar_config_dict["channel_1_en"])
        self.enable_ch0_chkb.setChecked(ch0_en)
        self.enable_ch1_chkb.setChecked(ch1_en)

        self.rough_pwr_thresh_ledit.setText(str(radar_config_dict["rough_pwr_thresh"]))
        self.half_peak_width_ledit.setText(str(radar_config_dict["half_peak_width"]))
        self.center_rangeval_ledit.setText(str(radar_config_dict["center_rangeval"]))

        self.ch0_offset_ledit.setText(str(radar_config_dict["ch0_offset"]))
        self.ch1_offset_ledit.setText(str(radar_config_dict["ch1_offset"]))

        # set data processing status to "STALE" as things have been changed
        self.make_stale()


    
    def update_radar_config(self, radar_config_dict):
        """
        this formally sets the radar_config_dict object in the main window
        function.  I put it seperately in a function so that it's easier to
        track all instances in which this variable is changed in this file
        """
        self.mainwin_obj.radar_config_dict = radar_config_dict



    def load_config_file(self, cfg_path):
        """
        This loads the config data into a dictionary.  It's a rather simple
        function, and may not be necessary to even exist, but in case things
        change I would like the abstraction

        note that this works for both radar configuration files and postproc 
        configuration files

        """
        with open(cfg_path, "r", encoding="utf-8") as file:
            cfg_dict = json.load(file)

        return cfg_dict



    def save_config_file(self, cfg_dict, cfg_path):
        """
        this saves a dictionary as a json file.  similar to "load_config_file" 
        it is likely an unnecessary function, but the abstraction might be 
        helpful

        """
        with open(cfg_path, 'w') as file:
            json.dump(cfg_dict, file)



    def set_proc_status(self, flag):
        """
        simple function that sets the processing status label to useful and 
        easy to interpret colors / texts
        """
        if flag == "STALE":
            style_options = "background-color: orange; color: black"
            self.curr_dat_proc_lbl.setStyleSheet(style_options)
            text_str = "Processing Status:    STALE       "
            self.curr_dat_proc_lbl.setText(text_str)
        elif flag == "COMPLETE":
            style_options = "background-color: green; color: white"
            self.curr_dat_proc_lbl.setStyleSheet(style_options)
            text_str = "Processing Status:    COMPLETE    "
            self.curr_dat_proc_lbl.setText(text_str)
        elif flag == "IN PROGRESS":
            style_options = "background-color: yellow; color: black"
            self.curr_dat_proc_lbl.setStyleSheet(style_options)
            text_str = "Processing Status:   IN PROGRESS  "
            self.curr_dat_proc_lbl.setText(text_str)
        else:
            raise Exception("Invalid processing status flag")



    ##################### CALLBACK FUNCTIONS #####################

    def make_stale(self):
        """
        make processing stale because something changed
        """
        # set data processing status to "STALE"
        self.set_proc_status("STALE")



    def load_cfg_btn_clicked(self):
        """
        clicking the load config button will load the config file
        """
        fpath, ok = QFileDialog.getOpenFileName(
            self,
            "Select a Radar Configuration File", 
            self.CONFIG_DIR,
            ""
        )
        if fpath:
            # update the textbox showing the current config file name
            self.curr_cfg_val_ledit.setText(str(fpath))

            # load the file
            radar_config_dict = self.load_config_file(fpath)

            # set the GUI values per the loaded file
            self.set_gui_config_params(radar_config_dict)

            # update the toplevel configuration variable
            self.update_radar_config(radar_config_dict)

            # set data processing status to "STALE"
            self.make_stale()



    def save_cfg_btn_clicked(self):
        """
        clicking the save config button will save the current configuration 
        to a file
        """
        radar_config_dict = self.get_gui_config_params()
        fpath, ok = QFileDialog.getSaveFileName(
            self,
            "Save a Radar Configuration File", 
            self.CONFIG_DIR,
            ""
        )
        if fpath:
            #os.path.isfile(fpath):
            #path = Path(fpath)
            self.save_config_file(radar_config_dict, fpath)
            self.curr_cfg_val_ledit.setText(str(fpath))



    def save_dflt_cfg_btn_clicked(self):
        """
        clicking the save config button will save the current configuration 
        to a file.  Will generate a popup asking if you're sure 
        """
        # dialog popup to confirm the user intended to click this button
        dlg = SimpDialog()
        proceed = bool(dlg.exec_())
        if proceed:
            radar_config_dict = self.get_gui_config_params()
            fpath = self.RADAR_DFLT_CFG_PATH 

            try:
                self.save_config_file(radar_config_dict, fpath)
                self.curr_cfg_val_ledit.setText(str(fpath))
            except Exception as except_val:
                print(except_val)
                print_str = "You may need to add a 'config' directory in "
                print_str += "the same directory as 'StillViewerGUI.py'"
                print(print_str)
                    


    def load_dflt_cfg_btn_clicked(self):
        """
        clicking the load default config button will load the default config
        file
        """
        fpath = self.RADAR_DFLT_CFG_PATH 

        try:
            # update the textbox showing the current config file name
            self.curr_cfg_val_ledit.setText(str(fpath))

            # load the file
            radar_config_dict = self.load_config_file(fpath)

            # set the GUI values per the loaded file
            self.set_gui_config_params(radar_config_dict)

            # update the toplevel configuration variable
            self.update_radar_config(radar_config_dict)

            # set data processing status to "STALE"
            self.make_stale()

        except Exception as except_val:
            print(except_val)
            print_str = "Default config file may not exist"
            print(print_str)



    def load_dat_btn_clicked(self, channel):
        """
        clicking the load data button will load the data
        """
        fpath, ok = QFileDialog.getOpenFileName(
            self,
            "Select a Radar Data File", 
            self.DFLT_DATA_DIR,
            ""
        )
        if fpath:
            # this is all the "loading" actually is
            if channel==0:
                self.data0_fpath = fpath
                self.curr_loaded0_val_ledit.setText(str(fpath))
            elif channel==1:
                self.data1_fpath = fpath
                self.curr_loaded1_val_ledit.setText(str(fpath))
            else:
                raise Exception("Invalid Channel")

            # set data processing status to "STALE"
            self.make_stale()



    def load_latest_dat_btn_clicked(self, channel):
        """
        clicking this button will load the last modified data file from the 
        default data directory
        """
        # grab the last modified file from the default data dir
        try: 
            data_dir = self.DFLT_DATA_DIR
            extension = "dat"
            last_mod_fname = get_last_modified_file(data_dir, extension, channel)
            fpath = data_dir + last_mod_fname

            if fpath:
                if channel==0:
                    self.data0_fpath = fpath
                    self.curr_loaded0_val_ledit.setText(str(fpath))
                elif channel==1:
                    self.data1_fpath = fpath
                    self.curr_loaded1_val_ledit.setText(str(fpath))
                else:
                    raise Exception("Invalid Channel")

            else:
                except_str = "Invalid or non-existent default"
                except_str += "configuration directory"
                raise Exception(except_str)

        except:
            except_str = "Invalid or non-existent default"
            except_str += "configuration directory"
            raise Exception(except_str)

        # set data processing status to "STALE"
        self.make_stale()




    def process_data_btn_clicked(self):
        """
        callback for when process_data_btn is clicked.  It will process
        the data file assuming one is loaded
        """
        self.process_data_files()



    def autoload_btn_clicked(self):
        """
        callback for when autoload button is clicked.  It will process
        the data files for the enabled channels (if the corresponding files 
        are also loaded
        """
        radar_config_dict = self.get_gui_config_params()
        if (radar_config_dict["channel_0_en"]):
            self.load_latest_dat_btn_clicked(0)
        if (radar_config_dict["channel_1_en"]):
            self.load_latest_dat_btn_clicked(1)
        self.process_data_files()


    ##################### Central Processing Function #####################

    def process_data_files(self):
        """
        This performs tier 1 and 2 post-processing on the data file with the 
        configuration settings as they are in the GUI
        
        This will also update the radar configuration toplevel dictionary
        """
        print("TBD")

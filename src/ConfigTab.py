# this contains the ConfigTab() class


from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
import os
import ipdb # NOTE REMOVE
import json
import collections
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

    def __init__(self, CFG_DFLT_PATH, CONFIG_DIR, DFLT_DATA_DIR, 
                 load_config, save_config, update_config):
                                    
        super().__init__()

        self.load_config = load_config
        self.save_config = save_config
        self.update_config = update_config

        self.CFG_DFLT_PATH            = CFG_DFLT_PATH
        self.CONFIG_DIR               = CONFIG_DIR
        self.DFLT_DATA_DIR            = DFLT_DATA_DIR

        # builds up all the widgets and layout adds them to self
        bct.build_config_tab(self)

        # This sets up all the callback functions that detect when
        # something has changed so that the configuration update is called
        # with the appropriate dictionary parameter
        bct.setup_config_callbacks(self, update_config)

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

        self.autoload_btn.clicked.connect(self.autoload_btn_clicked)

        ####################################################################
        # Activities that require an update to the cfg_dict
        #
        #self.el_s0_strt_ledit.textChanged.connect(self.make_stale)
        #self.el_s0_end_ledit.textChanged.connect(self.make_stale)
        #self.el_s1_strt_ledit.textChanged.connect(self.make_stale)
        #self.el_s1_end_ledit.textChanged.connect(self.make_stale)
        #self.process_side0_chkb.stateChanged.connect(self.make_stale)
        #self.process_side1_chkb.stateChanged.connect(self.make_stale)
        #self.num_elev_pix_ledit.textChanged.connect(self.make_stale)
        #self.num_azi_pix_ledit.textChanged.connect(self.make_stale)
        #self.fft_len_ledit.textChanged.connect(self.make_stale)
        #self.num_noise_pts_ledit.textChanged.connect(self.make_stale)


        #self.fsamp_freq_ledit.textChanged.connect(self.make_stale)
        #self.chirp_time_us_ledit.textChanged.connect(self.make_stale)
        #self.enable_ch0_chkb.stateChanged.connect(self.make_stale)
        #self.enable_ch1_chkb.stateChanged.connect(self.make_stale)
        #self.el_offset0_ledit.textChanged.connect(self.make_stale)
        #self.el_offset1_ledit.textChanged.connect(self.make_stale)
        #self.center_rangeval_ledit.textChanged.connect(self.make_stale)
        #self.ch0_offset_ledit.textChanged.connect(self.make_stale)
        #self.ch1_offset_ledit.textChanged.connect(self.make_stale)


        # New stuff
        #self.noise_frac_ledit.textChanged.connect(self.make_stale)
        #self.df_time_domain_rbut.toggled.connect(self.make_stale)
        #self.df_freq_domain_rbut.toggled.connect(self.make_stale)
        #self.df_power_domain_rbut.toggled.connect(self.make_stale)
        #self.chirp_span_ledit.textChanged.connect(self.make_stale)
        #self.calc_wt_sum_chkb.stateChanged.connect(self.make_stale)
        #self.dead_pix_ledit.textChanged.connect(self.make_stale)




    ###########################################################################
    #         Central function that grabs GUI configuration parameters        #
    ###########################################################################
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



        radar_config_dict["fs_adc_msps"]    = self.fsamp_freq_ledit.text()
        radar_config_dict["chirp_time_us"]  = self.chirp_time_us_ledit.text()

        ch0_en = self.enable_ch0_chkb.isChecked()
        ch1_en = self.enable_ch1_chkb.isChecked()
        radar_config_dict["channel_0_en"]  = ch0_en
        radar_config_dict["channel_1_en"]  = ch1_en
        radar_config_dict["el_offset0"]  = self.el_offset0_ledit.text()
        radar_config_dict["el_offset1"]  = self.el_offset1_ledit.text()
        radar_config_dict["center_rangeval"]  = self.center_rangeval_ledit.text()

        radar_config_dict["ch0_offset"]  = self.ch0_offset_ledit.text()
        radar_config_dict["ch1_offset"]  = self.ch1_offset_ledit.text()
        return radar_config_dict
        


    ###########################################################################
    #         Central function that sets GUI configuration parameters         #
    ###########################################################################
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



        self.fsamp_freq_ledit.setText(str(radar_config_dict["fs_adc_msps"]))
        self.chirp_time_us_ledit.setText(str(radar_config_dict["chirp_time_us"]))

        ch0_en = bool(radar_config_dict["channel_0_en"])
        ch1_en = bool(radar_config_dict["channel_1_en"])
        self.enable_ch0_chkb.setChecked(ch0_en)
        self.enable_ch1_chkb.setChecked(ch1_en)

        self.el_offset0_ledit.setText(str(radar_config_dict["el_offset0"]))
        self.el_offset1_ledit.setText(str(radar_config_dict["el_offset1"]))
        self.center_rangeval_ledit.setText(str(radar_config_dict["center_rangeval"]))

        self.ch0_offset_ledit.setText(str(radar_config_dict["ch0_offset"]))
        self.ch1_offset_ledit.setText(str(radar_config_dict["ch1_offset"]))

        # set data processing status to "STALE" as things have been changed
        self.make_stale()


    

    ##################### CALLBACK FUNCTIONS #####################

    def make_stale(self):
        """
        make processing stale because something changed
        """
        # set data processing status to "STALE"
        #self.set_proc_status("STALE")
        pass



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
            self.load_config(fpath)
            self.curr_cfg_val_ledit.setText(str(fpath))


    def save_cfg_btn_clicked(self):
        """
        clicking the save config button will save the current configuration 
        to a file
        """
        fpath, ok = QFileDialog.getSaveFileName(
            self,
            "Save a Radar Configuration File", 
            self.CONFIG_DIR,
            ""
        )
        if fpath:
            self.save_config(fpath)
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
            fpath = self.CFG_DFLT_PATH

            if fpath:
                self.save_config(fpath)
                self.curr_cfg_val_ledit.setText(str(fpath))
            else:
                print_str = "You may need to add a 'config' directory in "
                print_str += "the same directory as 'THzVisGUI.py'"
                print(print_str)
                    


    def load_dflt_cfg_btn_clicked(self):
        """
        clicking the load default config button will load the default config
        file
        """
        fpath = self.CFG_DFLT_PATH 

        if fpath:
            self.load_config(fpath)
            self.curr_cfg_val_ledit.setText(str(fpath))

        else:
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
            cfg_dict_updates = collections.OrderedDict()

            if channel==0:
                cfg_dict_updates["data0_fpath"] = fpath
                self.curr_loaded0_val_ledit.setText(str(fpath))
            elif channel==1:
                cfg_dict_updates["data1_fpath"] = fpath
                self.curr_loaded1_val_ledit.setText(str(fpath))
            else:
                raise Exception("Invalid Channel")

            # update the configuration
            self.update_config(cfg_dict_updates)



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
                cfg_dict_updates = collections.OrderedDict()
                if channel==0:
                    cfg_dict_updates["data0_fpath"] = fpath
                    self.curr_loaded0_val_ledit.setText(str(fpath))
                elif channel==1:
                    cfg_dict_updates["data1_fpath"] = fpath
                    self.curr_loaded1_val_ledit.setText(str(fpath))
                else:
                    raise Exception("Invalid Channel")

                # update the configuration
                self.update_config(cfg_dict_updates)


            else:
                except_str = "Invalid or non-existent default "
                except_str += "configuration directory"
                raise Exception(except_str)

        except:
            except_str = "Invalid or non-existent default "
            except_str += "configuration directory"
            raise Exception(except_str)


    def autoload_btn_clicked(self):
        """
        callback for when autoload button is clicked.  It will process
        the data files for the enabled channels (if the corresponding files 
        are also loaded
        """
        if (self.cfg_dict["channel_0_en"]):
            self.load_latest_dat_btn_clicked(0)
        if (self.cfg_dict["channel_1_en"]):
            self.load_latest_dat_btn_clicked(1)



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
    def __init__(s):
        super().__init__()

        s.setWindowTitle("Confirm Default Config Change Dialog")

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        s.button_box = QDialogButtonBox(buttons)
        s.button_box.accepted.connect(s.accept)
        s.button_box.rejected.connect(s.reject)

        s.layout = QVBoxLayout()
        msg_str  = "Are you sure you want to change "
        msg_str += "the default configuration file?"
        message = QLabel(msg_str)
        s.layout.addWidget(message)
        s.layout.addWidget(s.button_box)
        s.setLayout(s.layout)


##############################################################################
# Main Class
##############################################################################
class ConfigTab(QScrollArea):
    """
    This is the default tab visible and contains all the main configuration 
    data for the image processing.  
    """

    # NOTE: cfg_dict is the global configuration dictionary, it is
    # not to be modified outside of the MainWindow, it is only provided
    # to be read
    def __init__(s, CFG_DFLT_PATH, CONFIG_DIR, 
                 load_config, save_config, update_config, cfg_dict):
                                    
        super().__init__()

        s.load_config = load_config
        s.save_config = save_config
        s.update_config = update_config

        s.CFG_DFLT_PATH            = CFG_DFLT_PATH
        s.CONFIG_DIR               = CONFIG_DIR
        s.cfg_dict                 = cfg_dict

        # builds up all the widgets and layout adds them to s
        bct.build_config_tab(s)

        # This sets up all the callback functions that detect when
        # something has changed so that the configuration update is called
        # with the appropriate dictionary parameter
        bct.setup_config_callbacks(s, update_config)

        ####################################################################
        # Signals/Slots stuff
        #
        # config related callbacks
        s.load_cfg_btn.clicked.connect(s.load_cfg_btn_clicked)
        s.save_cfg_btn.clicked.connect(s.save_cfg_btn_clicked)
        s.save_dflt_cfg_btn.clicked.connect(s.save_dflt_cfg_btn_clicked)
        s.load_dflt_cfg_btn.clicked.connect(s.load_dflt_cfg_btn_clicked)


        # radar data related callbacks
        s.load_ch0_btn.clicked.connect(lambda: 
            s.load_dat_btn_clicked(0))
        s.load_latest_ch0_btn.clicked.connect(lambda: 
            s.load_latest_dat_btn_clicked(0))

        s.load_ch1_btn.clicked.connect(lambda: 
            s.load_dat_btn_clicked(1))
        s.load_latest_ch1_btn.clicked.connect(lambda: 
            s.load_latest_dat_btn_clicked(1))

        s.autoload_btn.clicked.connect(s.autoload_btn_clicked)

        # external HDF5 load
        s.load_h5_btn.clicked.connect(s.load_h5_btn_clicked)

    ###########################################################################
    #         Central function that sets GUI configuration parameters         #
    ###########################################################################
    def set_gui_config_params(s, cfg_dict):
        """
        takes the passed radar config dictionary and distributes the values 
        to the relevent GUI objects 
        """
        s.el_s0_strt_ledit.setText(str(cfg_dict["el_side_0_start"]))
        s.el_s0_end_ledit.setText(str(cfg_dict["el_side_0_end"]))
        s.el_s1_strt_ledit.setText(str(cfg_dict["el_side_1_start"]))
        s.el_s1_end_ledit.setText(str(cfg_dict["el_side_1_end"]))

        s.num_elev_pix_ledit.setText(str(cfg_dict["ylen"]))
        s.num_azi_pix_ledit.setText(str(cfg_dict["xlen"]))

        s.fft_len_ledit.setText(str(cfg_dict["fft_len"]))
        s.num_noise_pts_ledit.setText(str(cfg_dict["num_noise_pts"]))
        s.noise_frac_ledit.setText(str(cfg_dict["noise_start_frac"]))
        s.chirp_span_ledit.setText(str(cfg_dict["chirp_span"]/1e9))
        s.chirp_time_us_ledit.setText(str(cfg_dict["chirp_time"]*1e6))

        s.dead_pix_ledit.setText(str(cfg_dict["dead_pix_val"]))
        s.fsamp_freq_ledit.setText(str(cfg_dict["fs_adc"]/1e6))

        s.el_offset0_ledit.setText(str(cfg_dict["el_offset0"]))
        s.el_offset1_ledit.setText(str(cfg_dict["el_offset1"]))

        s.center_rangeval_ledit.setText(str(cfg_dict["center_rangeval"]))
        s.dec_val_ledit.setText(str(cfg_dict["dec_val"]))
        s.ch0_offset_ledit.setText(str(cfg_dict["ch0_offset"]))
        s.ch1_offset_ledit.setText(str(cfg_dict["ch1_offset"]))

        side0_state = not cfg_dict["disable_el_side0"]
        side1_state = not cfg_dict["disable_el_side1"]
        s.process_side0_chkb.setChecked(side0_state)
        s.process_side1_chkb.setChecked(side1_state)

        s.calc_wt_sum_chkb.setChecked(cfg_dict["calc_weighted_sum"])
        s.enable_ch0_chkb.setChecked(cfg_dict["ch0_en"])
        s.enable_ch1_chkb.setChecked(cfg_dict["ch1_en"])
        
        s.df_time_domin_rbut.setChecked(False)
        s.df_freq_domin_rbut.setChecked(False)
        s.df_power_domin_rbut.setChecked(False)


        if cfg_dict["data_format_in"] == "time_domain":
            s.df_time_domin_rbut.setChecked(True)
            
        elif cfg_dict["data_format_in"] == "fft":
            s.df_freq_domin_rbut.setChecked(True)

        elif cfg_dict["data_format_in"] == "power_spectrum":
            s.df_power_domin_rbut.setChecked(True)


    

    ##################### CALLBACK FUNCTIONS #####################

    def load_cfg_btn_clicked(s):
        """
        clicking the load config button will load the config file
        """
        fpath, ok = QFileDialog.getOpenFileName(
            s,
            "Select a Radar Configuration File", 
            s.CONFIG_DIR,
            ""
        )
        if fpath:
            s.load_config(fpath)
            s.curr_cfg_val_ledit.setText(str(fpath))


    def save_cfg_btn_clicked(s):
        """
        clicking the save config button will save the current configuration 
        to a file
        """
        fpath, ok = QFileDialog.getSaveFileName(
            s,
            "Save a Radar Configuration File", 
            s.CONFIG_DIR,
            ""
        )
        if fpath:
            s.save_config(fpath)
            s.curr_cfg_val_ledit.setText(str(fpath))



    def save_dflt_cfg_btn_clicked(s):
        """
        clicking the save config button will save the current configuration 
        to a file.  Will generate a popup asking if you're sure 
        """
        # dialog popup to confirm the user intended to click this button
        dlg = SimpDialog()
        proceed = bool(dlg.exec_())
        if proceed:
            fpath = s.CFG_DFLT_PATH

            if fpath:
                s.save_config(fpath)
                s.curr_cfg_val_ledit.setText(str(fpath))
            else:
                print_str = "You may need to add a 'config' directory in "
                print_str += "the same directory as 'THzVisGUI.py'"
                print(print_str)
                    


    def load_dflt_cfg_btn_clicked(s):
        """
        clicking the load default config button will load the default config
        file
        """
        fpath = s.CFG_DFLT_PATH 

        if fpath:
            s.load_config(fpath)
            s.curr_cfg_val_ledit.setText(str(fpath))

        else:
            print_str = "Default config file may not exist"
            print(print_str)



    def load_dat_btn_clicked(s, channel):
        """
        clicking the load data button will load the data
        """
        fpath, ok = QFileDialog.getOpenFileName(
            s,
            "Select a Radar Data File", 
            s.cfg_dict["default_data_dir"],
            ""
        )
        if fpath:
            fpath = fix_data_path(fpath)
            cfg_dict_updates = collections.OrderedDict()
            if channel==0:
                cfg_dict_updates["data0_fpath"] = fpath
                s.curr_loaded0_val_ledit.setText(str(fpath))
            elif channel==1:
                cfg_dict_updates["data1_fpath"] = fpath
                s.curr_loaded1_val_ledit.setText(str(fpath))
            else:
                raise Exception("Invalid Channel")

            # update the configuration
            s.update_config(cfg_dict_updates, ["fname_changed"])



    def load_latest_dat_btn_clicked(s, channel):
        """
        clicking this button will load the last modified data file from the 
        default data directory
        """
        # grab the last modified file from the default data dir
        try: 
            data_dir = s.cfg_dict["default_data_dir"]
            extension = "dat"
            last_mod_fname = get_last_modified_file(data_dir, extension, channel)
            fpath = data_dir + last_mod_fname

            if fpath:
                fpath = fix_data_path(fpath)
                cfg_dict_updates = collections.OrderedDict()
                if channel==0:
                    cfg_dict_updates["data0_fpath"] = fpath
                    s.curr_loaded0_val_ledit.setText(str(fpath))
                elif channel==1:
                    cfg_dict_updates["data1_fpath"] = fpath
                    s.curr_loaded1_val_ledit.setText(str(fpath))
                else:
                    raise Exception("Invalid Channel")

                # update the configuration
                s.update_config(cfg_dict_updates, ["fname_changed"])


            else:
                except_str = "Invalid or non-existent default "
                except_str += "data directory"
                raise Exception(except_str)

        except:
            except_str = "Invalid or non-existent default "
            except_str += "data directory"
            raise Exception(except_str)


    def load_h5_btn_clicked(s):
        """
        Load an external HDF5 data cube for visualization.
        """
        fpath, ok = QFileDialog.getOpenFileName(
            s,
            "Select an HDF5 Data Cube",
            s.cfg_dict["default_data_dir"],
            "HDF5 Files (*.h5 *.hdf5);;All Files (*)"
        )
        if fpath:
            fpath = fix_data_path(fpath)
            cfg_dict_updates = collections.OrderedDict()
            cfg_dict_updates["external_h5_fpath"] = fpath
            cfg_dict_updates["data_src"] = "external_h5"
            s.curr_h5_val_ledit.setText(str(fpath))
            s.update_config(cfg_dict_updates, ["fname_changed"])


    def autoload_btn_clicked(s):
        """
        callback for when autoload button is clicked.  It will process
        the data files for the enabled channels (if the corresponding files 
        are also loaded
        """
        if (s.cfg_dict["ch0_en"]):
            s.load_latest_dat_btn_clicked(0)
        if (s.cfg_dict["ch1_en"]):
            s.load_latest_dat_btn_clicked(1)



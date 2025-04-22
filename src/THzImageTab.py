
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
import os
import ipdb # NOTE REMOVE
import json
from math import nan
#import sys
#import signal
import copy
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from collections import OrderedDict
import THzImageObj as tio
import build_thz_image_tab as bti
#from dataclasses import dataclass, field

#import proc.postproc_fcns_t3 as pft3

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
    QMessageBox,
    QDialog,
    QDialogButtonBox,
)


def conv_fpath_to_unix(fpath):
    fpath_out = ""
    for char in fpath:
        if char == "\\":
            fpath_out += "/"
        else:
            fpath_out += char

    return fpath_out



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
class THzImageTab(QWidget):
    """
    This is the first sort of "raw" THz image tab.  It's really for viewing 
    minimially processed data
    """
    set_trace_val = False

    # NOTE: cfg_dict is the global configuration dictionary, it is
    # not to be modified outside of the MainWindow, it is only provided
    # to be read
    def __init__(s, CFG_DFLT_PATH, CONFIG_DIR, 
                 update_config, cfg_dict):
        super().__init__()

        
        s.CFG_DFLT_PATH  = CFG_DFLT_PATH
        s.CONFIG_DIR     = CONFIG_DIR
        s.cfg_dict       = cfg_dict

        # builds up all the widgets and layout adds them to s
        bti.build_thz_image_tab(s)

        # This sets up all the callback functions that detect when
        # something has changed so that the configuration update is called
        # with the appropriate dictionary parameter
        bti.setup_thz_tab_callbacks(s, update_config)

        ####################################################################
        # signals/slots for connecting line edit textboxes to sliders
        #
        # Connect the lineEdit(textbox) and slider together
        s.thresh_slider.valueChanged.connect(s.update_thresh_ledit)
        s.thresh_ledit.editingFinished.connect(s.update_thresh_slider)

        # Connect the lineEdit(textbox) and slider together
        s.contr_slider.valueChanged.connect(s.update_contr_ledit)
        s.contr_ledit.editingFinished.connect(s.update_contr_slider)

        # Connect the lineEdit(textbox) and slider together
        s.pkwdth_slider.valueChanged.connect(s.update_pkwdth_ledit)
        s.pkwdth_ledit.textChanged.connect(s.update_pkwdth_slider)

        # Connect the lineEdits(textboxes) and sliders together
        s.rc_slider_min.valueChanged.connect(s.update_rc_min_ledit)
        s.rc_ledit_min.editingFinished.connect(s.update_rc_min_slider)

        s.rc_slider_max.valueChanged.connect(s.update_rc_max_ledit)
        s.rc_ledit_max.editingFinished.connect(s.update_rc_max_slider)

        # Connect the lineEdits(textboxes) and sliders together
        s.cs_slider_min.valueChanged.connect(s.update_cs_min_ledit)
        s.cs_ledit_min.editingFinished.connect(s.update_cs_min_slider)

        s.cs_slider_max.valueChanged.connect(s.update_cs_max_ledit)
        s.cs_ledit_max.editingFinished.connect(s.update_cs_max_slider)


        ####################################################################
        # assign some callbacks
        #
        #s.load_cfg_btn.clicked.connect(s.load_cfg_btn_clicked)
        #s.save_cfg_btn.clicked.connect(s.save_cfg_btn_clicked)
        #s.save_dflt_cfg_btn.clicked.connect(s.save_dflt_cfg_btn_clicked)
        #s.load_dflt_cfg_btn.clicked.connect(s.load_dflt_cfg_btn_clicked)

        # Button callbacks
        s.ld_save_image_save_btn.clicked.connect(
            s.ld_save_image_save_btn_clicked)

        s.ld_save_image_autosave_btn.clicked.connect(
            s.ld_save_image_autosave_btn_clicked)

        s.ld_save_image_chng_dir_btn.clicked.connect(
            s.ld_save_image_chng_dir_btn_clicked)


        s.reset_camera_btn.clicked.connect(
            s.reset_camera_btn_clicked)




    def get_gui_config_params(s):
        """
        grabs the current set of configuration parameters on the GUI and 
        converts them to a config dictionary which is returned
        """
        cfg_dict = {}
        
        cfg_dict["threshold_db"]    = s.thresh_ledit.text()
        cfg_dict["contrast_db"]     = s.contr_ledit.text()
        cfg_dict["half_peak_width"] = s.pkwdth_ledit.text()
        cfg_dict["rangecut_min"]    = s.rc_ledit_min.text()
        cfg_dict["rangecut_max"]    = s.rc_ledit_max.text()

        cfg_dict["autoscale_color"] = s.cs_autoscale_chkb.isChecked()

        cfg_dict["color_scale_min"] = s.cs_ledit_min.text()
        cfg_dict["color_scale_max"] = s.cs_ledit_max.text()

        cfg_dict["colormap"] = s.cmap_cbox.currentText()

        if s.front_peak_rbut.isChecked():
            cfg_dict["plot_style"]      = "front_peak_range"
        elif s.back_peak_rbut.isChecked():
            cfg_dict["plot_style"]      = "back_peak_range"
        elif s.front_surface_plot_rbut.isChecked():
            cfg_dict["plot_style"]      = "front_surface_plot"
        elif s.back_surface_plot_rbut.isChecked():
            cfg_dict["plot_style"]      = "back_surface_plot"
        elif s.num_oversamp_rbut.isChecked():
            cfg_dict["plot_style"]      = "num_oversamp_plot"
        elif s.integ_pwr_rbut.isChecked():
            cfg_dict["plot_style"]      = "integ_power_plot"
        elif s.point_cloud_rbut.isChecked():
            cfg_dict["plot_style"]      = "point_cloud_plot"
        else:
            except_str = "I admit defeat, I have no idea how this error happened"
            raise Exception(except_str)

        return cfg_dict



    def set_gui_config_params(s, cfg_dict):
        """
        takes the passed postprocessing config dictionary and distributes 
        the values  to the relevent GUI objects
        """
        s.azi_hyst_fs_ledit.setText(str(cfg_dict["turn_hyst"])) 
        s.azi_marg_fs_ledit.setText(str(cfg_dict["turn_az_margin"])) 
        s.num_rng_fs_ledit.setText(str(cfg_dict["daq_num_rangelines"])) 
        s.tot_frac_fs_ledit.setText(str(cfg_dict["fraction_filled_thresh"])) 
        s.ld_save_image_desc_ledit.setText(str(cfg_dict["save_image_desc"])) 

        s.thresh_ledit.setText(str(cfg_dict["threshold_db"])) 
        s.contr_ledit.setText(str(cfg_dict["contrast_db"]) )
        s.pkwdth_ledit.setText(str(cfg_dict["half_peak_width"]))

        s.rc_ledit_min.setText(str(cfg_dict["min_range"]))
        s.rc_ledit_max.setText(str(cfg_dict["max_range"]))

        s.cs_autoscale_chkb.setChecked(bool(cfg_dict["autoscale_color"]))
        s.cs_ledit_min.setText(str(cfg_dict["color_scale_min"]))
        s.cs_ledit_max.setText(str(cfg_dict["color_scale_max"]))

        s.az_min_lim_ledit.setText(str(cfg_dict["min_az"]))
        s.az_max_lim_ledit.setText(str(cfg_dict["max_az"]))
        s.el_min_lim_ledit.setText(str(cfg_dict["min_el"]))
        s.el_max_lim_ledit.setText(str(cfg_dict["max_el"]))

        colormap_str = cfg_dict["colormap"] 
        colormap_ind = s.colormaps.index(colormap_str)
        s.cmap_cbox.setCurrentIndex(colormap_ind)


        s.file_src_rbut.setChecked(False)
        s.daq_src_rbut.setChecked(False)

        s.front_peak_rbut.setChecked(False)
        s.back_peak_rbut.setChecked(False)
        s.front_surface_plot_rbut.setChecked(False)
        s.back_surface_plot_rbut.setChecked(False)
        s.num_oversamp_rbut.setChecked(False)
        s.integ_pwr_rbut.setChecked(False)
        s.point_cloud_rbut.setChecked(False)

        s.azi_turn_fs_rbut.setChecked(False)
        s.num_rng_fs_rbut.setChecked(False)
        s.col_frac_fs_rbut.setChecked(False)
        s.pix_frac_fs_rbut.setChecked(False)


        if cfg_dict["data_src"] == "dat_file":
            s.file_src_rbut.setChecked(True)
            
        elif cfg_dict["data_src"] == "daq":
            s.daq_src_rbut.setChecked(True)
            
        if cfg_dict["plot_style"] == "front_peak":
            s.front_peak_rbut.setChecked(True)
            
        elif cfg_dict["plot_style"] == "back_peak":
            s.back_peak_rbut.setChecked(True)
            
        elif cfg_dict["plot_style"] == "front_surface":
            s.front_surface_plot_rbut.setChecked(True)
            
        elif cfg_dict["plot_style"] == "back_surface":
            s.back_surface_plot_rbut.setChecked(True)

        elif cfg_dict["plot_style"] == "num_oversamp_plot":
            s.num_oversamp_rbut.setChecked(True)

        elif cfg_dict["plot_style"] == "integ_power_plot":
            s.integ_pwr_rbut.setChecked(True)
            
        elif cfg_dict["plot_style"] == "point_cloud_plot":
            s.point_cloud_rbut.setChecked(True)

        # need to update these because the proper signals won't be generated 
        # with automatic editing

        s.update_thresh_slider()
        s.update_contr_slider()
        s.update_rc_min_slider()
        s.update_rc_max_slider()
        s.update_cs_min_slider()
        s.update_cs_max_slider()

        s.update_image(None, False)



    def load_config_file(s, cfg_path):
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



    def save_config_file(s, cfg_dict, cfg_path):
        """
        this saves a dictionary as a json file.  similar to "load_config_file" 
        it is likely an unnecessary function, but the abstraction might be helpful

        """
        with open(cfg_path, 'w') as file:
            json.dump(cfg_dict, file)


    #def update_thresh_slider(s):
    #def update_contr_slider(s):
    #def update_rc_min_slider(s):
    #def update_rc_max_slider(s):
    #def update_cs_min_slider(s):
    #def update_cs_max_slider(s):

    ############## CALLBACK FUNCTIONS ##############


    #########################################################################
    ################### SLIDER-RELATED CALLBACK FUNCTIONS ###################
    #########################################################################

    def update_thresh_ledit(s, value):
        s.thresh_ledit.clear()
        s.thresh_ledit.insert(str(value))
    
    def update_thresh_slider(s):
        value = float(s.thresh_ledit.text())
        if value != "":
            s.thresh_slider.setValue(value)

    def update_contr_ledit(s, value):
        s.contr_ledit.clear()
        s.contr_ledit.insert(str(value))
    
    def update_contr_slider(s):
        value = float(s.contr_ledit.text())
        if value != "":
            s.contr_slider.setValue(value)

    def update_pkwdth_ledit(s, value):
        s.pkwdth_ledit.clear()
        s.pkwdth_ledit.insert(str(value))
    
    def update_pkwdth_slider(s, value):
        if value != "":
            s.pkwdth_slider.setValue(int(value))

    def update_rc_min_ledit(s, value):
        s.rc_ledit_min.clear()
        s.rc_ledit_min.insert(str(value))
    
    def update_rc_min_slider(s):
        value = int(float(s.rc_ledit_min.text()))
        if value != "":
            s.rc_slider_min.setValue(int(value))

    def update_rc_max_ledit(s, value):
        s.rc_ledit_max.clear()
        s.rc_ledit_max.insert(str(value))
    
    def update_rc_max_slider(s):
        value = int(float(s.rc_ledit_max.text()))
        if value != "":
            s.rc_slider_max.setValue(int(value))

    def update_cs_min_ledit(s, value):
        s.cs_ledit_min.clear()
        s.cs_ledit_min.insert(str(value))
    
    def update_cs_min_slider(s):
        value = int(float(s.cs_ledit_min.text()))
        if value != "":
            s.cs_slider_min.setValue(value)

    def update_cs_max_ledit(s, value):
        s.cs_ledit_max.clear()
        s.cs_ledit_max.insert(str(value))
    
    def update_cs_max_slider(s):
        value = int(float(s.cs_ledit_max.text()))
        if value != "":
            s.cs_slider_max.setValue(value)


    #########################################################################
    ################# END SLIDER-RELATED CALLBACK FUNCTIONS #################
    #########################################################################

    def ld_save_image_save_btn_clicked(s):
        fpath, ok = QFileDialog.getSaveFileName(
            s,
            "Save an Image File", 
            s.cfg_dict["default_data_dir"],
            "png")
        if fpath:
            fpath = conv_fpath_to_unix(fpath)
            fname = fpath.split("/")[-1]
            s.thz_image_obj.save_cur_image(fpath, fname)


    # NOTE TODO need to add saving of surface plots functionality
    # NOTE TODO THIS NEEDS MAJOR WORK NOW THAT WE HAVE DAQ CAPABILITIES 
    def ld_save_image_autosave_btn_clicked(s):
        #frame_style = s.cfg_dict["frame_style"]
        plot_style = s.cfg_dict["plot_style"]
        data_fpath_0 = s.cfg_dict["data_fpath_0"]
        data_fpath_1 = s.cfg_dict["data_fpath_1"]

        # use the pixel 0 filename to generate the image file if pixel 0 is 
        # in the dataset
        if data_fpath_0 != None:
            data_fpath = conv_fpath_to_unix(data_fpath_0)

        # use the pixel 1 filename to generate the image file if pixel 0 is 
        # not in the dataset
        elif data_fpath_1 != None:
            data_fpath = conv_fpath_to_unix(data_fpath_1)
        fname = data_fpath.split("/")[-1]
        fprefix = fname[0:16]
        DFLT_DATA_DIR_unix = conv_fpath_to_unix(s.cfg_dict["default_data_dir"]) 
        fpath = DFLT_DATA_DIR_unix + fprefix + plot_style + ".png"
        s.thz_image_obj.save_cur_image(fpath, fprefix)

        msgbox = QMessageBox()
        msgbox.setText("The Image has been Saved!")
        msgbox.exec()
        

    def ld_save_image_chng_dir_btn_clicked(s):
        (fpath, ok) = QFileDialog.getExistingDirectory(
            s, "Select Directory to Autosave Images", 
            s.cfg_dict["default_data_dir"])
        if fpath:
            fpath = conv_fpath_to_unix(fpath)
            new_cfg_dict = OrderedDict()
            new_cfg_dict["default_data_dir"] = fpath
            s.update_config(new_cfg_dict)


    def reset_camera_btn_clicked(s):
        """
        Resets the camera position for the 3D plots
        """
        s.update_image(None, False,reset_camera=True)

    #########################################################################
    ###################### MAIN IMAGE UPDATE FUNCTION #######################
    #########################################################################
    def update_image(s, frame_data, new_frame_flag, reset_camera_flag=False):
        """
        This is called whenver a new frame comes in and properly distributes 
        it to the THzImageObj widgets 
        """
        s.thz_image_obj.update_image(frame_data, new_frame_flag, 
            reset_camera_flag)


    #########################################################################
    ###################### COLOR SCALE UPDATE FUNCTION ######################
    #########################################################################
    def update_autocolors(s, color_min, color_max):
        """
        this is an update function that comes from the THzImageObj class that
        sends the minimum and maximum colors that it detects while updating
        the plot so that the GUI can adjust the color textboxes and sliders
        appropriately
        """
        s.cs_ledit_min.setText(str(color_min))
        s.cs_ledit_max.setText(str(color_max))




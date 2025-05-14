# This is the "single pixel" view tab

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
import os
import ipdb # NOTE REMOVE
import json
from collections import OrderedDict
#from math import nan
#import sys
#import signal
import numpy as np
#import build_singpix_tab as bst
#import pyqtgraph as pg
#from dataclasses import dataclass, field
import AuxPlotObj as apo
import THzImageObj as tio

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
# Main Class
##############################################################################
class SingPixTab(QWidget):
    """
    This is the tab that shows the spectrum of a single pixel you click on
    so you can examine where the peaks are and what it's actually finding
    """

    # NOTE: cfg_dict is the global configuration dictionary, it is
    # not to be modified outside of the MainWindow, it is only provided
    # to be read
    def __init__(s, CFG_DFLT_PATH, CONFIG_DIR, update_config, cfg_dict):
        super().__init__()
        s.update_config         = update_config
        s.CFG_DFLT_PATH         = CFG_DFLT_PATH
        s.CONFIG_DIR            = CONFIG_DIR
        s.cfg_dict              = cfg_dict

        # In the future if this file gets too cluttered we'll move some of 
        # the code to build_singlepix_tab
        #bst.build_singlepix_tab(s)
        ######################################################################
        # Layout-related stuff                        
        #
        s.main_layout  = QVBoxLayout() 
        s.upper_layout = QHBoxLayout()

        # doing this because it's the minimum effort
        #s.aux_layout   = QHBoxLayout() 
        s.lower_layout = QHBoxLayout()

        s.thz_image_obj = tio.THzImageObj(s, s.cfg_dict, sing_pix_flag=True)

        # this is where the pixel is plotted
        s.aux_plot_obj = apo.AuxPlotObj()
        #s.aux_layout.addWidget(s.aux_plot_obj)

        # layout of the two images
        s.upper_layout.addLayout(s.thz_image_obj)
        s.upper_layout.addWidget(s.aux_plot_obj)
        s.upper_layout.setStretch(0,1)
        s.upper_layout.setStretch(1,1)

        ######################################################################
        # control box 
        s.ctrl_box_layout = QGridLayout()
        s.legend_chkb  = QCheckBox()
        s.legend_chkb.setText("Legend Visible")
        s.legend_chkb.setChecked(True)

        s.noise_limits_chkb = QCheckBox()
        s.noise_limits_chkb.setText("Noise Delimiters")
        s.noise_limits_chkb.setChecked(True)

        s.noise_floor_chkb = QCheckBox()
        s.noise_floor_chkb.setText("Noise Floor")
        s.noise_floor_chkb.setChecked(True)

        s.thresh_chkb = QCheckBox()
        s.thresh_chkb.setText("Threshold")
        s.thresh_chkb.setChecked(True)

        s.contr_chkb = QCheckBox()
        s.contr_chkb.setText("Contrast")
        s.contr_chkb.setChecked(True)

        s.front_peak_chkb = QCheckBox()
        s.front_peak_chkb.setText("Front Peak Marker")
        s.front_peak_chkb.setChecked(True)

        s.back_peak_chkb = QCheckBox()
        s.back_peak_chkb.setText("Back Peak Marker")
        s.back_peak_chkb.setChecked(True)

        s.range_cuts_chkb = QCheckBox()
        s.range_cuts_chkb.setText("Range Cuts")
        s.range_cuts_chkb.setChecked(True)

        s.weight_sum_chkb = QCheckBox()
        s.weight_sum_chkb.setText("Weighted Sum")
        s.weight_sum_chkb.setChecked(False)

        s.ctrl_box_layout.addWidget(s.legend_chkb,       0, 0, 1, 1)
        s.ctrl_box_layout.addWidget(s.noise_limits_chkb, 1, 0, 1, 1)
        s.ctrl_box_layout.addWidget(s.noise_floor_chkb,  2, 0, 1, 1)
        s.ctrl_box_layout.addWidget(s.thresh_chkb,       3, 0, 1, 1)

        s.ctrl_box_layout.addWidget(s.contr_chkb,        0, 1, 1, 1)
        s.ctrl_box_layout.addWidget(s.front_peak_chkb,   1, 1, 1, 1)
        s.ctrl_box_layout.addWidget(s.back_peak_chkb,    2, 1, 1, 1)
        s.ctrl_box_layout.addWidget(s.range_cuts_chkb,   3, 1, 1, 1)
        s.ctrl_box_layout.addWidget(s.weight_sum_chkb,   0, 2, 1, 1)


        #s.upper_layout.addLayout(s.aux_layout)
        s.main_layout.addLayout(s.upper_layout)
        s.main_layout.addLayout(s.ctrl_box_layout)
        s.setLayout(s.main_layout)


        ####################################################################
        # Signals/Slots stuff
        #
        # config related callbacks
        s.thz_image_obj.new_pix_clicked.connect(s.new_pix_clicked)


    def update_image(s, frame_data, new_frame_flag, reset_camera=False):
        """
        This is called whenever a new frame comes in and properly distributes 
        it to the THzImageObj widgets 
        """
        s.thz_image_obj.update_image(frame_data, new_frame_flag, 
            reset_camera)


    def aux_update(s, aux_data_in, new_frame_flag):
        """
        this updates all the appropriate auxilary plot objects when a new 
        frame ( + auxiliary data) comes in
        """
        local_cfg_params = OrderedDict()
        local_cfg_params["legend_en"] = bool(s.legend_chkb.isChecked())
        local_cfg_params["noise_delim_en"] = bool(s.noise_limits_chkb.isChecked())
        local_cfg_params["noise_floor_en"] = bool(s.noise_floor_chkb.isChecked())
        local_cfg_params["thresh_en"] = bool(s.thresh_chkb.isChecked())
        local_cfg_params["contr_en"] = bool(s.contr_chkb.isChecked())
        local_cfg_params["front_peak_en"] = bool(s.front_peak_chkb.isChecked())
        local_cfg_params["back_peak_en"] = bool(s.back_peak_chkb.isChecked())
        local_cfg_params["range_cuts_en"] = bool(s.range_cuts_chkb.isChecked())
        local_cfg_params["weight_sum_en"] = bool(s.weight_sum_chkb.isChecked())
        s.aux_plot_obj.aux_update(aux_data_in, new_frame_flag, 
            local_cfg_params)



    def new_pix_clicked(s, position, az_ind, el_ind):
        x_click = position.x()
        y_click = position.y()
        print(f"clicked at data coords: x={x_click:.2f}, y={y_click:.2f}")
        print(f"az_ind = {az_ind}, el_ind = {el_ind}")
        new_cfg_dict = OrderedDict()
        new_cfg_dict["aux_x_ind"] = int(az_ind)
        new_cfg_dict["aux_y_ind"] = int(el_ind)

        new_cfg_dict["aux_az_val"] = x_click
        new_cfg_dict["aux_el_val"] = y_click

        # update the pixel being viewed
        s.update_config(new_cfg_dict)



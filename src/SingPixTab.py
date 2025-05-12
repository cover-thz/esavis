# This is the "single pixel" view tab

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

        s.thz_image_obj = tio.THzImageObj(s, s.cfg_dict)

        # this is where the pixel is plotted
        s.aux_plot_obj = apo.AuxPlotObj()
        #s.aux_layout.addWidget(s.aux_plot_obj)

        # layout of the two images
        s.upper_layout.addLayout(s.thz_image_obj)
        s.upper_layout.addWidget(s.aux_plot_obj)
        s.upper_layout.setStretch(0,1)
        s.upper_layout.setStretch(1,1)

        #s.upper_layout.addLayout(s.aux_layout)

        # NOTE test plot
        s.aux_plot_obj.plt_axes.plot([0,1,2,3,4],[10,1,20,3,40], color="r")

        s.main_layout.addLayout(s.upper_layout)
        s.setLayout(s.main_layout)


        ####################################################################
        # Signals/Slots stuff
        #
        # config related callbacks



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
        s.aux_plot_obj.aux_update(aux_data_in, new_frame_flag)


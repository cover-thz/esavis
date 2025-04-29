
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
class CameraTab(QWidget):
    """
    This ideally holds the camera and THz image together.  Right now its
    just going to have a larger duplicate of the THz image tab
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
        s.update_config  = update_config
        s.cfg_dict       = cfg_dict

        # only has to do one thing
        s.main_layout = QHBoxLayout()

        #s.thz_image_obj = tio.THzImageObj
        s.thz_image_obj = tio.THzImageObj(s, s.cfg_dict)
            
        s.main_layout.addLayout(s.thz_image_obj) 
        s.setLayout(s.main_layout)


    def update_image(s, frame_data, new_frame_flag, reset_camera=False):
        """
        This is called whenver a new frame comes in and properly distributes 
        it to the THzImageObj widgets 
        """
        s.thz_image_obj.update_image(frame_data, new_frame_flag, 
            reset_camera)






from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, QRectF
#from PySide6.QtGui import QColor, QPalette
from PySide6.QtGui import QTransform
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
import CameraItem as ca
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
    QGraphicsScene,
    QGraphicsView,
    QGraphicsProxyWidget,
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
        #
        # This sets the CameraTab's main layout
        s.main_layout = QVBoxLayout(s)

        ######################################################################
        #                        IMAGE WIDGET SETUP                          #
        ######################################################################
        # the main plotwidget that contains both the THz image and the 
        # visible-light camera 
        s.image_widget = pg.PlotWidget()

        # THz Image Setup
        # If I'm correct I should be able to just grab the mesh and use that
        s.thz_image_obj = tio.THzImageObj(s, s.cfg_dict)
        s.thz_mesh_plot = s.thz_image_obj.thz_mesh_obj.color_mesh
        s.image_widget.addItem(s.thz_mesh_plot)

        # Camera Object Setup
        s.camera_item = ca.CameraItem()
        s.image_widget.addItem(s.camera_item)

        s.image_plot_item = s.image_widget.getPlotItem()
        s.image_plot_item.invertX(False)
        s.image_plot_item.invertY(True)

        # This keeps the aspect ratio equal to 1 so the image doesn't get 
        # distorted when you resize the display
        s.image_plot_item.setAspectLocked(lock=True, ratio=1)

        # camera configuration
        x       = cfg_dict["camera_x"]
        y       = cfg_dict["camera_y"]
        h_scale = cfg_dict["camera_h_scale"]
        v_scale = cfg_dict["camera_v_scale"]
        opacity = cfg_dict["camera_opacity"]

        s.camera_item.setOpacity(opacity)
        s.camera_item.make_transform(x, y, h_scale, v_scale)


        ######################################################################
        #                         POSITIONING TOOLS                          #
        ######################################################################
        s.pos_tools_layout  = QHBoxLayout()

        # Buttons
        s.button_box_layout = QGridLayout()
        s.up_btn            = QPushButton("UP")
        s.left_btn          = QPushButton("LEFT")
        s.right_btn         = QPushButton("RIGHT")
        s.down_btn          = QPushButton("DOWN")

        #s.button_box_layout.addWidget(up_btn, 0, 1, 1, 1, 
        #    alignment=Qt.AlignmentFlag.AlignCenter)
        s.button_box_layout.addWidget(s.up_btn, 0, 1, 1, 1)
        s.button_box_layout.addWidget(s.left_btn, 1, 0, 1, 1)
        s.button_box_layout.addWidget(s.right_btn, 1, 2, 1, 1)
        s.button_box_layout.addWidget(s.down_btn, 2, 1, 1, 1)

        # line edits (text boxes)
        s.text_controls_layout = QGridLayout()
        s.xpos_label = QLabel("X Position")
        s.xpos_ledit = QLineEdit()
        s.ypos_label = QLabel("Y Position")
        s.ypos_ledit = QLineEdit()

        s.hscale_label = QLabel("Horiz. Scale")
        s.hscale_ledit = QLineEdit()
        s.vscale_label = QLabel("Vert. Scale")
        s.vscale_ledit = QLineEdit()

        s.step_int_label = QLabel("Step Int.")
        s.step_int_ledit = QLineEdit() 

        s.opacity_label = QLabel("Opacity")
        s.opacity_ledit = QLineEdit() 

        s.text_controls_layout.addWidget(s.xpos_label, 0, 0)
        s.text_controls_layout.addWidget(s.xpos_ledit, 0, 1)
        s.text_controls_layout.addWidget(s.hscale_label, 0, 2)
        s.text_controls_layout.addWidget(s.hscale_ledit, 0, 3)

        s.text_controls_layout.addWidget(s.ypos_label, 1, 0)
        s.text_controls_layout.addWidget(s.ypos_ledit, 1, 1)
        s.text_controls_layout.addWidget(s.vscale_label, 1, 2)
        s.text_controls_layout.addWidget(s.vscale_ledit, 1, 3)

        s.text_controls_layout.addWidget(s.step_int_label, 2, 0)
        s.text_controls_layout.addWidget(s.step_int_ledit, 2, 1)
        s.text_controls_layout.addWidget(s.opacity_label, 2, 2)
        s.text_controls_layout.addWidget(s.opacity_ledit, 2, 3)

        s.pos_tools_layout.addLayout(s.button_box_layout)
        s.pos_tools_layout.addLayout(s.text_controls_layout)


        ######################################################################
        #                           FINAL LAYOUT                             #
        ######################################################################
        # combined image widget goes on top
        s.main_layout.addWidget(s.image_widget)
        s.main_layout.addLayout(s.pos_tools_layout)

        # this starts the camera up, 
        s.camera_item.set_index(0)
        s.camera_item.check_and_start_capture()
        s.camera_item.capture_and_display()



        ######################################################################
        #                      CALLBACK FUNCTIONS SETUP                      #
        ######################################################################

        # buttons
        s.up_btn.clicked.connect(s.up_btn_clicked)
        s.left_btn.clicked.connect(s.left_btn_clicked)
        s.right_btn.clicked.connect(s.right_btn_clicked)
        s.down_btn.clicked.connect(s.down_btn_clicked)


        # textboxes (linedits)
        s.xpos_ledit.editingFinished.connect(
            lambda: s.ledit_update(s.xpos_ledit, "camera_x", float))
            
        s.hscale_ledit.editingFinished.connect(
            lambda: s.ledit_update(s.hscale_ledit, "camera_h_scale", float))

        s.ypos_ledit.editingFinished.connect(
            lambda: s.ledit_update(s.ypos_ledit, "camera_y", float))

        s.vscale_ledit.editingFinished.connect(
            lambda: s.ledit_update(s.vscale_ledit, "camera_v_scale", float))

        s.step_int_ledit.editingFinished.connect(
            lambda: s.ledit_update(s.step_int_ledit, "camera_step_int", float))

        s.opacity_ledit.editingFinished.connect(
            lambda: s.ledit_update(s.opacity_ledit, "camera_opacity", float))



    ######################################################################
    #                      MAIN IMAGE UPDATE FUNCTION
    ######################################################################
    def update_image(s, frame_data, new_frame_flag, reset_camera=False):
        """
        This is called whenver a new frame comes in and properly distributes 
        it to the THzImageObj widgets 
        """
        s.thz_image_obj.update_image(frame_data, new_frame_flag, 
            reset_camera)

        # update the camera as well
        s.camera_item.capture_and_display()


    ######################################################################
    #                     GUI OBJECTS UPDATE FUNCTIONS                   #
    ######################################################################
    
    def set_gui_config_params(s, cfg_dict):
        """
        Sets the GUI parameters based off the passed configuration dictionary
        """
        x       = cfg_dict["camera_x"]
        y       = cfg_dict["camera_y"]
        h_scale = cfg_dict["camera_h_scale"]
        v_scale = cfg_dict["camera_v_scale"]
        opacity = cfg_dict["camera_opacity"]
    
        # change the textbox values
        s.xpos_ledit.setText(str(cfg_dict["camera_x"]))
        s.hscale_ledit.setText(str(cfg_dict["camera_h_scale"]))

        s.ypos_ledit.setText(str(cfg_dict["camera_y"]))
        s.vscale_ledit.setText(str(cfg_dict["camera_v_scale"]))

        s.step_int_ledit.setText(str(cfg_dict["camera_step_int"]))
        s.opacity_ledit.setText(str(cfg_dict["camera_opacity"]))

        # Change the actual image settings
        s.camera_item.setOpacity(opacity)
        s.camera_item.make_transform(x, y, h_scale, v_scale)


    ######################################################################
    #                 TEXT CONTROLS CALLBACK FUNCTIONS                   #
    ######################################################################
    def up_btn_clicked(s):
        new_cfg_dict = OrderedDict()
        new_y = s.cfg_dict["camera_y"] + s.cfg_dict["camera_step_int"]
        new_cfg_dict["camera_y"] = new_y
        s.update_config(new_cfg_dict)

        # now update the GUI to reflect the change
        s.set_gui_config_params(s.cfg_dict)


    def left_btn_clicked(s):
        new_cfg_dict = OrderedDict()
        new_x = s.cfg_dict["camera_x"] - s.cfg_dict["camera_step_int"]
        new_cfg_dict["camera_x"] = new_x
        s.update_config(new_cfg_dict)

        # now update the GUI to reflect the change
        s.set_gui_config_params(s.cfg_dict)


    def right_btn_clicked(s):
        new_cfg_dict = OrderedDict()
        new_x = s.cfg_dict["camera_x"] + s.cfg_dict["camera_step_int"]
        new_cfg_dict["camera_x"] = new_x
        s.update_config(new_cfg_dict)

        # now update the GUI to reflect the change
        s.set_gui_config_params(s.cfg_dict)


    def down_btn_clicked(s):
        new_cfg_dict = OrderedDict()
        new_y = s.cfg_dict["camera_y"] - s.cfg_dict["camera_step_int"]
        new_cfg_dict["camera_y"] = new_y
        s.update_config(new_cfg_dict)

        # now update the GUI to reflect the change
        s.set_gui_config_params(s.cfg_dict)



    def ledit_update(s, ledit_obj, key, dtype=float, mult=None):
        ignore_update = False
        try:
            if mult == None:
                val = dtype(ledit_obj.text()) 
            else:
                val = dtype(dtype(ledit_obj.text()) * mult)
        except ValueError:
            ignore_update = True

        if not ignore_update:
            new_cfg_dict = OrderedDict()
            new_cfg_dict[key] = val
            s.update_config(new_cfg_dict)
            s.set_gui_config_params(s.cfg_dict)





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
class THzImageTab(QWidget):
    """
    This is the first sort of "raw" THz image tab.  It's really for viewing 
    minimially processed data
    """
    set_trace_val = False
    prev_postproc_config_dict = None

    def __init__(self, mainwin_obj, RADAR_DFLT_CFG_PATH, 
                 POSTPROC_DFLT_CFG_PATH, CONFIG_DIR, DFLT_DATA_DIR):
        super().__init__()

        self.RADAR_DFLT_CFG_PATH      = RADAR_DFLT_CFG_PATH
        self.POSTPROC_DFLT_CFG_PATH   = POSTPROC_DFLT_CFG_PATH
        self.CONFIG_DIR = CONFIG_DIR
        self.DFLT_DATA_DIR = DFLT_DATA_DIR
        self.mainwin_obj = mainwin_obj

        # builds up all the widgets and layout adds them to self
        bti.build_thz_image_tab(self)

        ####################################################################
        # signals/slots for connecting line edit textboxes to sliders
        #
        # Connect the lineEdit(textbox) and slider together
        self.thresh_slider.valueChanged.connect(self.update_thresh_ledit)
        self.thresh_ledit.editingFinished.connect(self.update_thresh_slider)

        # Connect the lineEdit(textbox) and slider together
        self.contr_slider.valueChanged.connect(self.update_contr_ledit)
        self.contr_ledit.editingFinished.connect(self.update_contr_slider)

        # [REMOVED FOR NOW] Connect the lineEdit(textbox) and slider together
        #pkwdth_slider.valueChanged.connect(self.update_pkwdth_ledit)
        #pkwdth_ledit.textChanged.connect(self.update_pkwdth_slider)

        # Connect the lineEdits(textboxes) and sliders together
        self.rc_slider_min.valueChanged.connect(self.update_rc_min_ledit)
        self.rc_ledit_min.editingFinished.connect(self.update_rc_min_slider)

        self.rc_slider_max.valueChanged.connect(self.update_rc_max_ledit)
        self.rc_ledit_max.editingFinished.connect(self.update_rc_max_slider)

        # Connect the lineEdits(textboxes) and sliders together
        self.cs_slider_min.valueChanged.connect(self.update_cs_min_ledit)
        self.cs_ledit_min.editingFinished.connect(self.update_cs_min_slider)

        self.cs_slider_max.valueChanged.connect(self.update_cs_max_ledit)
        self.cs_ledit_max.editingFinished.connect(self.update_cs_max_slider)


        ####################################################################
        # assign some callbacks
        #
        #update_btn.clicked.connect(self.update_image)
        self.update_btn.clicked.connect(self.update_btn_clicked)
        self.load_cfg_btn.clicked.connect(self.load_cfg_btn_clicked)
        self.save_cfg_btn.clicked.connect(self.save_cfg_btn_clicked)
        self.save_dflt_cfg_btn.clicked.connect(self.save_dflt_cfg_btn_clicked)
        self.load_dflt_cfg_btn.clicked.connect(self.load_dflt_cfg_btn_clicked)

        # objects that need to update the image when interacted with 
        self.front_peak_rbut.toggled.connect(self.update_image)
        self.back_peak_rbut.toggled.connect(self.update_image)
        self.front_surface_plot_rbut.toggled.connect(self.update_image)
        self.back_surface_plot_rbut.toggled.connect(self.update_image)
        self.num_avgs_rbut.toggled.connect(self.update_image)
        self.integ_pwr_rbut.toggled.connect(self.update_image)

        self.cs_autoscale_chkb.stateChanged.connect(self.update_image)
        self.cmap_cbox.currentIndexChanged.connect(self.cmap_box_index_changed)

        self.image_save_btn.clicked.connect(self.image_save_btn_clicked)
        self.image_autosave_btn.clicked.connect(self.image_autosave_btn_clicked)
        self.reset_camera_btn.clicked.connect(self.reset_camera_btn_clicked)



    def get_gui_config_params(self):
        """
        grabs the current set of configuration parameters on the GUI and 
        converts them to a config dictionary which is returned
        """
        postproc_config_dict = {}
        
        postproc_config_dict["threshold_db"]    = self.thresh_ledit.text()
        postproc_config_dict["contrast_db"]     = self.contr_ledit.text()
        #postproc_config_dict["peak_width"]      = 
        postproc_config_dict["rangecut_min"]    = self.rc_ledit_min.text()
        postproc_config_dict["rangecut_max"]    = self.rc_ledit_max.text()

        postproc_config_dict["autoscale_color"] = self.cs_autoscale_chkb.isChecked()

        postproc_config_dict["color_scale_min"] = self.cs_ledit_min.text()
        postproc_config_dict["color_scale_max"] = self.cs_ledit_max.text()

        postproc_config_dict["colormap"] = self.cmap_cbox.currentText()


        if self.front_peak_rbut.isChecked():
            postproc_config_dict["plot_style"]      = "front_peak_range"
        elif self.back_peak_rbut.isChecked():
            postproc_config_dict["plot_style"]      = "back_peak_range"
        elif self.front_surface_plot_rbut.isChecked():
            postproc_config_dict["plot_style"]      = "front_surface_plot"
        elif self.back_surface_plot_rbut.isChecked():
            postproc_config_dict["plot_style"]      = "back_surface_plot"
        elif self.num_avgs_rbut.isChecked():
            postproc_config_dict["plot_style"]      = "num_avgs_plot"
        elif self.integ_pwr_rbut.isChecked():
            postproc_config_dict["plot_style"]      = "integ_power_plot"
        elif self.point_cloud_rbut.isChecked():
            postproc_config_dict["plot_style"]      = "point_cloud_plot"
        else:
            except_str = "I admit defeat, I have no idea how this error happened"
            raise Exception(except_str)

        return postproc_config_dict



    def set_gui_config_params(self, postproc_config_dict):
        """
        takes the passed postprocessing config dictionary and distributes 
        the values  to the relevent GUI objects
        """

        self.thresh_ledit.setText(str(postproc_config_dict["threshold_db"])) 
        self.contr_ledit.setText(str(postproc_config_dict["contrast_db"]) )
        #postproc_config_dict["peak_width"] 
        self.rc_ledit_min.setText(str(postproc_config_dict["rangecut_min"]))
        self.rc_ledit_max.setText(str(postproc_config_dict["rangecut_max"]))

        self.cs_autoscale_chkb.setChecked(bool(postproc_config_dict["autoscale_color"]))
        self.cs_ledit_min.setText(postproc_config_dict["color_scale_min"])
        self.cs_ledit_max.setText(postproc_config_dict["color_scale_max"])

        colormap_str = postproc_config_dict["colormap"] 
        colormap_ind = self.colormaps.index(colormap_str)
        self.cmap_cbox.setCurrentIndex(colormap_ind)

        self.front_peak_rbut.setChecked(False)
        self.back_peak_rbut.setChecked(False)
        self.front_surface_plot_rbut.setChecked(False)
        self.back_surface_plot_rbut.setChecked(False)
        self.num_avgs_rbut.setChecked(False)
        self.integ_pwr_rbut.setChecked(False)
        self.point_cloud_rbut.setChecked(False)

        if postproc_config_dict["plot_style"] == "front_peak_range":
            self.front_peak_rbut.setChecked(True)
            
        elif postproc_config_dict["plot_style"] == "back_peak_range":
            self.back_peak_rbut.setChecked(True)
            
        elif postproc_config_dict["plot_style"] == "front_surface_plot":
            self.front_surface_plot_rbut.setChecked(True)
            
        elif postproc_config_dict["plot_style"] == "back_surface_plot":
            self.back_surface_plot_rbut.setChecked(True)
            
        elif postproc_config_dict["plot_style"] == "num_avgs_plot":
            self.num_avgs_rbut.setChecked(True)

        elif postproc_config_dict["plot_style"] == "integ_power_plot":
            self.integ_pwr_rbut.setChecked(True)
            
        elif postproc_config_dict["plot_style"] == "point_cloud_plot":
            self.point_cloud_rbut.setChecked(True)

        #else:
        #    except_str = "I admit defeat, I have no idea how this error happened"
        #    raise Exception(except_str)

        # need to update these because the proper signals won't be generated 
        # with automatic editing

        self.update_thresh_slider()
        self.update_contr_slider()
        self.update_rc_min_slider()
        self.update_rc_max_slider()
        self.update_cs_min_slider()
        self.update_cs_max_slider()

        self.update_image()



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
        it is likely an unnecessary function, but the abstraction might be helpful

        """
        with open(cfg_path, 'w') as file:
            json.dump(cfg_dict, file)



    def update_postproc_config(self, postproc_config_dict):
        """
        this formally sets the postproc_config_dict object in the main window
        function.  I put it seperately in a function so that it's easier to
        track all instances in which this variable is changed in this file
        """
        self.mainwin_obj.postproc_config_dict = postproc_config_dict




    #def update_thresh_slider(self):
    #def update_contr_slider(self):
    #def update_rc_min_slider(self):
    #def update_rc_max_slider(self):
    #def update_cs_min_slider(self):
    #def update_cs_max_slider(self):

    ############## CALLBACK FUNCTIONS ##############

    def update_thresh_ledit(self, value):
        self.thresh_ledit.clear()
        self.thresh_ledit.insert(str(value))
        self.update_image()

    
    def update_thresh_slider(self):
        value = int(float(self.thresh_ledit.text()))
        if value != "":
            self.thresh_slider.setValue(int(value))
            self.update_image()


    def update_contr_ledit(self, value):
        self.contr_ledit.clear()
        self.contr_ledit.insert(str(value))
        self.update_image()

    
    def update_contr_slider(self):
        value = int(float(self.contr_ledit.text()))
        if value != "":
            self.contr_slider.setValue(int(value))
            self.update_image()


    #def update_pkwdth_ledit(self, value):
    #    self.pkwdth_ledit.clear()
    #    self.pkwdth_ledit.insert(str(value))
    #    self.update_image()

    
    #def update_pkwdth_slider(self, value):
    #    if value != "":
    #        self.pkwdth_slider.setValue(int(value))
    #        self.update_image()


    def update_rc_min_ledit(self, value):
        self.rc_ledit_min.clear()
        self.rc_ledit_min.insert(str(value))
        self.update_image()

    
    def update_rc_min_slider(self):
        value = int(float(self.rc_ledit_min.text()))
        if value != "":
            self.rc_slider_min.setValue(int(value))
            self.update_image()


    def update_rc_max_ledit(self, value):
        self.rc_ledit_max.clear()
        self.rc_ledit_max.insert(str(value))
        self.update_image()

    
    def update_rc_max_slider(self):
        value = int(float(self.rc_ledit_max.text()))
        if value != "":
            self.rc_slider_max.setValue(int(value))
            self.update_image()


    def update_cs_min_ledit(self, value):
        self.cs_ledit_min.clear()
        self.cs_ledit_min.insert(str(value))

        # no need to update the image if autscale colors are checked, it 
        # will do that enough on its own
        if not self.cs_autoscale_chkb.isChecked():
            self.update_image()

    
    def update_cs_min_slider(self):
        value = int(float(self.cs_ledit_min.text()))
        if value != "":
            self.cs_slider_min.setValue(value)
            # no need to update the image if autscale colors are checked, it 
            # will do that enough on its own
            if not self.cs_autoscale_chkb.isChecked():
                self.update_image()


    def update_cs_max_ledit(self, value):
        self.cs_ledit_max.clear()
        self.cs_ledit_max.insert(str(value))
        # no need to update the image if autscale colors are checked, it 
        # will do that enough on its own
        if not self.cs_autoscale_chkb.isChecked():
            self.update_image()

    
    def update_cs_max_slider(self):
        value = int(float(self.cs_ledit_max.text()))
        if value != "":
            self.cs_slider_max.setValue(value)
            # no need to update the image if autscale colors are checked, it 
            # will do that enough on its own
            if not self.cs_autoscale_chkb.isChecked():
                self.update_image()


    def load_cfg_btn_clicked(self):
        """
        clicking the load config button will load the config file
        """
        fpath, ok = QFileDialog.getOpenFileName(
            self,
            "Select a Postprocessing Configuration File", 
            self.CONFIG_DIR,
            ""
        )
        if fpath:
            # load the file
            postproc_config_dict = self.load_config_file(fpath)

            # set the GUI values per the loaded file
            self.set_gui_config_params(postproc_config_dict)

            # update the toplevel configuration variable
            self.update_postproc_config(postproc_config_dict)
        self.update_image()


    def save_cfg_btn_clicked(self):
        """
        clicking the save config button will save the current configuration 
        to a file
        """
        postproc_config_dict = self.get_gui_config_params()
        fpath, ok = QFileDialog.getSaveFileName(
            self,
            "Save a Postprocessing Configuration File", 
            self.CONFIG_DIR,
            ""
        )
        if fpath:
            #os.path.isfile(fpath):
            #path = Path(fpath)
            self.save_config_file(postproc_config_dict, fpath)


    def save_dflt_cfg_btn_clicked(self):
        """
        clicking the save config button will save the current configuration 
        to a file
        """
        # dialog popup to confirm the user intended to click this button
        dlg = SimpDialog()
        proceed = bool(dlg.exec_())
        if proceed:
            postproc_config_dict = self.get_gui_config_params()
            fpath = self.POSTPROC_DFLT_CFG_PATH 

            try:
                self.save_config_file(postproc_config_dict, fpath)
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
        fpath = self.POSTPROC_DFLT_CFG_PATH 

        #try:
        # load the file
        postproc_config_dict = self.load_config_file(fpath)

        # set the GUI values per the loaded file
        self.set_gui_config_params(postproc_config_dict)

        # update the toplevel configuration variable
        self.update_postproc_config(postproc_config_dict)

        self.update_image()

        #except Exception as except_val:
        #    print(except_val)
        #    print_str = "Default config file may not exist"
        #    print(print_str)


    # NOTE Sort of a debug button
    def update_btn_clicked(self):
        """
        triggered when the update button is clicked.  Both updates the 
        interface and toggles a debug variable that indicates to debug code
        whether a debug trace should engage
        """
        if self.set_trace_val:
            self.set_trace_val = False

        else:
            self.set_trace_val = True
        self.update_image(force_update=True)


    def cmap_box_index_changed(self):
        self.update_image(force_update=True)


    def image_save_btn_clicked(self):
        postproc_config_dict = self.get_gui_config_params()
        fpath, ok = QFileDialog.getSaveFileName(
            self,
            "Save an Image File", 
            self.DFLT_DATA_DIR,
            "png"
        )
        if fpath:

            fpath = conv_fpath_to_unix(fpath)
            fname = fpath.split("/")[-1]
            self.thz_image_obj.save_cur_image(fpath, fname)

    # NOTE TODO need to add saving of surface plots functionality
    def image_autosave_btn_clicked(self):
        postproc_config_dict = self.get_gui_config_params()
        plot_style = postproc_config_dict["plot_style"]

        # gotta grab the data file's name from the ConfigTab
        # NOTE PIXUPDATE!

        data_fpath_0 = self.mainwin_obj.cur_proc_data_file_0 
        data_fpath_1 = self.mainwin_obj.cur_proc_data_file_1 

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
        DFLT_DATA_DIR_unix = conv_fpath_to_unix(self.DFLT_DATA_DIR) 
        fpath = DFLT_DATA_DIR_unix + fprefix + plot_style + ".png"
        self.thz_image_obj.save_cur_image(fpath, fprefix)

        msgbox = QMessageBox()
        msgbox.setText("The Image has been Saved!")
        msgbox.exec()
        

    def reset_camera_btn_clicked(self):
        """
        Resets the camera position for the 3D plots
        """
        self.update_image(force_update=True,reset_camera=True)



    def update_image(self, force_update=False, reset_camera=False):
        """
        this is called whenever something in this tab changes (also should
        be called when the tab is switched over) and updates the image
        with the new set of values

        """
        pass

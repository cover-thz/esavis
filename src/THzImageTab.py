
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
import os
import collections
import math
from collections import OrderedDict
import build_thz_image_tab as bti

from PySide6.QtWidgets import (
    QWidget,
    QFileDialog,
    QMessageBox,
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
# Main Class
##############################################################################
class THzImageTab(QWidget):
    """
    This is the first sort of "raw" THz image tab.  It's really for viewing 
    minimially processed data
    """

    # NOTE: cfg_dict is the global configuration dictionary, it is
    # not to be modified outside of the MainWindow, it is only provided
    # to be read
    def __init__(s, update_config, cfg_dict):
        super().__init__()

        s.update_config  = update_config
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
        s.cs_slider_min.valueChanged.connect(s.update_cs_min_ledit)
        s.cs_ledit_min.editingFinished.connect(s.update_cs_min_slider)

        s.cs_slider_max.valueChanged.connect(s.update_cs_max_ledit)
        s.cs_ledit_max.editingFinished.connect(s.update_cs_max_slider)


        ####################################################################
        # assign some callbacks
        #
        # Button callbacks
        s.load_h5_btn.clicked.connect(
            s.load_h5_btn_clicked)

        s.ld_save_image_save_btn.clicked.connect(
            s.ld_save_image_save_btn_clicked)

        s.ld_save_image_autosave_btn.clicked.connect(
            s.ld_save_image_autosave_btn_clicked)

        s.ld_save_image_chng_dir_btn.clicked.connect(
            s.ld_save_image_chng_dir_btn_clicked)

        # pixel click signal from the image
        s.thz_image_obj.new_pix_clicked.connect(s.new_pix_clicked)

        # aux checkbox changes should immediately redraw the aux plot
        s.last_aux_data = None
        for chkb in [s.legend_chkb, s.noise_limits_chkb, s.noise_floor_chkb,
                      s.thresh_chkb, s.contr_chkb, s.front_peak_chkb,
                      s.back_peak_chkb, s.weight_sum_chkb,
                      s.pt_mrkrs_chkb]:
            chkb.stateChanged.connect(s._on_aux_checkbox_changed)

        ####################################################################
        # set the default save image path
        #
        s.ld_save_image_curr_dir_ledit.setText(s.cfg_dict["default_data_dir"])


    def set_gui_config_params(s, cfg_dict):
        """
        takes the passed postprocessing config dictionary and distributes 
        the values  to the relevent GUI objects
        """
        s.ld_save_image_desc_ledit.setText(str(cfg_dict["save_image_desc"])) 

        s.thresh_ledit.setText(str(cfg_dict["threshold_db"])) 
        s.contr_ledit.setText(str(cfg_dict["contrast_db"]) )
        s.pkwdth_ledit.setText(str(cfg_dict["half_peak_width"]))

        s.cs_autoscale_chkb.setChecked(bool(cfg_dict["autoscale_color"]))
        s.cs_ledit_min.setText(str(cfg_dict["color_scale_min"]))
        s.cs_ledit_max.setText(str(cfg_dict["color_scale_max"]))

        colormap_str = cfg_dict["colormap"]
        colormap_ind = s.colormaps.index(colormap_str) if colormap_str in s.colormaps else 0
        s.cmap_cbox.setCurrentIndex(colormap_ind)


        s.front_peak_rbut.setChecked(False)
        s.back_peak_rbut.setChecked(False)
        s.front_surface_plot_rbut.setChecked(False)
        s.back_surface_plot_rbut.setChecked(False)
        s.integ_pwr_rbut.setChecked(False)


        if cfg_dict["plot_style"] == "front_peak_range":
            s.front_peak_rbut.setChecked(True)
        elif cfg_dict["plot_style"] == "back_peak_range":
            s.back_peak_rbut.setChecked(True)
        elif cfg_dict["plot_style"] == "front_surface_range":
            s.front_surface_plot_rbut.setChecked(True)
        elif cfg_dict["plot_style"] == "back_surface_range":
            s.back_surface_plot_rbut.setChecked(True)
        elif cfg_dict["plot_style"] == "integ_power_plot":
            s.integ_pwr_rbut.setChecked(True)


        # need to update these because the proper signals won't be generated 
        # with automatic editing

        s.update_thresh_slider()
        s.update_contr_slider()
        s.update_cs_min_slider()
        s.update_cs_max_slider()

        s.update_image(None, False)





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

    def update_cs_min_ledit(s, value):
        s.cs_ledit_min.clear()
        s.cs_ledit_min.insert(str(value))
    
    def update_cs_min_slider(s):
        value = s.cs_ledit_min.text()
        if value != "":
            value = float(value)
            if not math.isnan(value):
                value = int(value)
                s.cs_slider_min.setValue(value)

    def update_cs_max_ledit(s, value):
        s.cs_ledit_max.clear()
        s.cs_ledit_max.insert(str(value))
    
    def update_cs_max_slider(s):
        value = s.cs_ledit_max.text()
        if value != "":
            value = float(value)
            if not math.isnan(value):
                value = int(value)
                s.cs_slider_max.setValue(value)


    #########################################################################
    ################# END SLIDER-RELATED CALLBACK FUNCTIONS #################
    #########################################################################

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
            fpath = conv_fpath_to_unix(fpath)
            cfg_dict_updates = collections.OrderedDict()
            cfg_dict_updates["external_h5_fpath"] = fpath
            cfg_dict_updates["data_src"] = "external_h5"
            s.window().setWindowTitle('THz Visualizer — ' + fpath)
            s.update_config(cfg_dict_updates, ["fname_changed"])


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
        plot_style = s.cfg_dict["plot_style"]
        image_desc = s.ld_save_image_desc_ledit.text()
        DFLT_DATA_DIR_unix = conv_fpath_to_unix(s.cfg_dict["default_data_dir"]) 
        fpath = DFLT_DATA_DIR_unix + image_desc + "_" + plot_style + ".png"
        s.thz_image_obj.save_cur_image(fpath, image_desc)

        msgbox = QMessageBox()
        msgbox.setText("The Image has been Saved!")
        msgbox.exec()



    def ld_save_image_chng_dir_btn_clicked(s):
        fpath = QFileDialog.getExistingDirectory(
            s, "Select Directory to Autosave Images", 
            s.cfg_dict["default_data_dir"])
        if fpath:
            fpath = conv_fpath_to_unix(fpath) + "/"
            new_cfg_dict = OrderedDict()
            new_cfg_dict["default_data_dir"] = fpath
            s.update_config(new_cfg_dict)
            s.ld_save_image_curr_dir_ledit.setText(s.cfg_dict["default_data_dir"])




    #########################################################################
    ###################### MAIN IMAGE UPDATE FUNCTION #######################
    #########################################################################
    def update_image(s, frame_data, new_frame_flag, reset_camera=False):
        """
        This is called whenver a new frame comes in and properly distributes 
        it to the THzImageObj widgets 
        """
        s.thz_image_obj.update_image(frame_data, new_frame_flag, 
            reset_camera)


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

        s.update_cs_min_slider()
        s.update_cs_max_slider()



    def aux_update(s, aux_data_in, new_frame_flag):
        """
        Updates the auxiliary spectrum plot when new frame data arrives.
        Reads checkbox states and passes them to AuxPlotObj.
        """
        if new_frame_flag and aux_data_in is not None:
            s.last_aux_data = aux_data_in
        loc_cfg_params = OrderedDict()
        loc_cfg_params["legend_en"] = bool(s.legend_chkb.isChecked())
        loc_cfg_params["noise_delim_en"] = bool(s.noise_limits_chkb.isChecked())
        loc_cfg_params["noise_floor_en"] = bool(s.noise_floor_chkb.isChecked())
        loc_cfg_params["thresh_en"] = bool(s.thresh_chkb.isChecked())
        loc_cfg_params["contr_en"] = bool(s.contr_chkb.isChecked())
        loc_cfg_params["front_peak_en"] = bool(s.front_peak_chkb.isChecked())
        loc_cfg_params["back_peak_en"] = bool(s.back_peak_chkb.isChecked())
        loc_cfg_params["weight_sum_en"] = bool(s.weight_sum_chkb.isChecked())
        loc_cfg_params["pt_mrkrs_en"] = bool(s.pt_mrkrs_chkb.isChecked())

        s.aux_plot_obj.aux_update(aux_data_in, new_frame_flag,
            loc_cfg_params)


    def _on_aux_checkbox_changed(s):
        if s.last_aux_data is not None:
            s.aux_update(s.last_aux_data, True)


    def new_pix_clicked(s, position, x_ind, y_ind):
        x_click = position.x()
        y_click = position.y()
        print(f"clicked at data coords: x={x_click:.2f}, y={y_click:.2f}")
        print(f"X_in = {x_ind}, Y_in = {y_ind}")
        new_cfg_dict = OrderedDict()
        new_cfg_dict["aux_x_ind"] = int(x_ind)
        new_cfg_dict["aux_y_ind"] = int(y_ind)

        new_cfg_dict["aux_x_val"] = x_click
        new_cfg_dict["aux_y_val"] = y_click

        cfg_flags = ["force_update"]
        s.update_config(new_cfg_dict, cfg_flags)


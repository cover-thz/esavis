# This file only contains widget generation and layout along with some parameter 
# settings of widgets (e.g. read-only for a QLineEdit widget) for the 
# THzImageTab
# 
# Signals and slots should not be assigned here.  The purpose of this file is 
# to make the THzImageTab file much cleaner and more concise
#

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from esavis import THzImageObj as tio
from esavis import AuxPlotObj as apo
from collections import OrderedDict

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
)


def build_thz_image_tab(thz_img_tab):
    """
    builds up the initial set of GUI objects and the layout of the GUI for 
    the THzImageTab along with some default parameters and adds them to the 
    thz_img_tab object
    """

    # NOTE consider setting the verticalScrollBarPolicy of the QScrollArea
    # to "ScrollBarAsNeeded"

    ####################################################################
    # setup layouts
    #
    right_layout    = QVBoxLayout()

    ####################################################################
    # Left side widgets
    ####################################################################

    ####################################################################
    # This is the main upper left widget that is the THz image plot
    # that takes up a significant portion of the screen.  
    # 
    # The processing config stuff below is the lower left 
    # portion of the screen
    # 
    # NOTE: Giving the cfg_dict to THzImageObj but again it does NOT alter it
    # only reads from it
    thz_img_tab.thz_image_obj = tio.THzImageObj(thz_img_tab, 
        thz_img_tab.cfg_dict, sing_pix_flag=True, main_image=True)

    # Aux spectrum plot for single pixel view
    thz_img_tab.aux_plot_obj = apo.AuxPlotObj()

    
    ####################################################################
    # Load HDF5 button — goes at top of right column
    #
    load_h5_btn = QPushButton("Load HDF5 Cube")
    thz_img_tab.load_h5_btn = load_h5_btn


    ####################################################################
    # Plot Style radio buttons — will go below main image
    #
    front_peak_rbut     = QRadioButton("Front Peak Range")
    back_peak_rbut      = QRadioButton("Back Peak Range")
    front_surface_plot_rbut = QRadioButton("Front Surface Plot")
    back_surface_plot_rbut  = QRadioButton("Back Surface Plot")
    integ_pwr_rbut      = QRadioButton("Integrated Power")

    thz_img_tab.front_peak_rbut         = front_peak_rbut
    thz_img_tab.back_peak_rbut          = back_peak_rbut
    thz_img_tab.front_surface_plot_rbut = front_surface_plot_rbut
    thz_img_tab.back_surface_plot_rbut  = back_surface_plot_rbut
    thz_img_tab.integ_pwr_rbut          = integ_pwr_rbut


    ####################################################################
    # "Load/Save Image" widgets — will go at bottom of right column
    #
    ld_save_image_sublayout_row1  = QHBoxLayout()
    ld_save_image_autosave_btn  = QPushButton("Autosave\nImage")
    ld_save_image_chng_dir_btn  = QPushButton("Change Save\nDirectory")
    ld_save_image_save_btn      = QPushButton("Save\nImage")
    ld_save_image_sublayout_row1.addWidget(ld_save_image_autosave_btn)
    ld_save_image_sublayout_row1.addWidget(ld_save_image_chng_dir_btn)
    ld_save_image_sublayout_row1.addWidget(ld_save_image_save_btn)

    ld_save_image_sublayout_row2 = QHBoxLayout()
    ld_save_image_curr_dir_lbl    = QLabel("Current Save Dir:")
    ld_save_image_curr_dir_ledit  = QLineEdit()
    ld_save_image_curr_dir_ledit.setReadOnly(True)
    ld_save_image_sublayout_row2.addWidget(ld_save_image_curr_dir_lbl)
    ld_save_image_sublayout_row2.addWidget(ld_save_image_curr_dir_ledit)

    ld_save_image_sublayout_row3 = QHBoxLayout()
    ld_save_image_desc_lbl    = QLabel("Image Description:")
    ld_save_image_desc_ledit  = QLineEdit()
    ld_save_image_sublayout_row3.addWidget(ld_save_image_desc_lbl)
    ld_save_image_sublayout_row3.addWidget(ld_save_image_desc_ledit)

    thz_img_tab.ld_save_image_autosave_btn = ld_save_image_autosave_btn
    thz_img_tab.ld_save_image_chng_dir_btn = ld_save_image_chng_dir_btn
    thz_img_tab.ld_save_image_save_btn = ld_save_image_save_btn
    thz_img_tab.ld_save_image_curr_dir_lbl = ld_save_image_curr_dir_lbl
    thz_img_tab.ld_save_image_curr_dir_ledit = ld_save_image_curr_dir_ledit
    thz_img_tab.ld_save_image_desc_lbl = ld_save_image_desc_lbl
    thz_img_tab.ld_save_image_desc_ledit = ld_save_image_desc_ledit



    ####################################################################
    # Center and Right side widgets
    ####################################################################

    ####################################################################
    # Update button (REMOVED)
    #

    ####################################################################
    # Threshold adjustment widgets
    #
    # construct a grid layout for the widgets 
    thresh_grid_layout = QGridLayout()

    thresh_lbl = QLabel("Threshold (dB)")
    thresh_ledit = QLineEdit()
    thresh_ledit.setFixedWidth(50)

    # sets the limits of threshold values
    thresh_vmin, thresh_vmax = (0,80)
    thresh_ledit.setMaxLength(4)
    thresh_ledit.setAlignment(Qt.AlignCenter)
    thresh_slider = QSlider(Qt.Orientation.Horizontal, thz_img_tab)
    thresh_slider.setRange(thresh_vmin, thresh_vmax)

    # Add the threshold widgets to the layout
    thresh_lbl.setFixedHeight(30)
    thresh_grid_layout.addWidget(thresh_lbl, 0, 0, 1, 4)
    thresh_grid_layout.addWidget(thresh_ledit, 1, 0)
    thresh_grid_layout.addWidget(thresh_slider, 1, 1)

    # Add member variables
    thz_img_tab.thresh_lbl = thresh_lbl
    thz_img_tab.thresh_ledit = thresh_ledit
    thz_img_tab.thresh_slider = thresh_slider



    ####################################################################
    # Contrast adjustment widgets
    #
    # construct a grid layout for the widgets 
    contr_grid_layout = QGridLayout()

    contr_lbl = QLabel("Contrast (dB)")
    contr_ledit = QLineEdit()
    contr_ledit.setFixedWidth(50)
    contr_vmin, contr_vmax = (1,80)
    contr_ledit.setMaxLength(4)
    contr_ledit.setAlignment(Qt.AlignCenter)
    contr_slider = QSlider(Qt.Orientation.Horizontal, thz_img_tab)
    contr_slider.setRange(contr_vmin, contr_vmax)

    # Add the contrast widgets 
    contr_lbl.setFixedHeight(30)
    contr_grid_layout.addWidget(contr_lbl, 0, 0, 1, 4)
    contr_grid_layout.addWidget(contr_ledit, 1, 0)
    contr_grid_layout.addWidget(contr_slider, 1, 1)

    # Add member variables
    thz_img_tab.contr_lbl = contr_lbl
    thz_img_tab.contr_ledit = contr_ledit
    thz_img_tab.contr_slider = contr_slider



    ####################################################################
    # Peak width adjustment widgets 
    #
    pkwdth_lbl = QLabel("Half Peak Width")
    pkwdth_ledit = QLineEdit()
    pkwdth_ledit.setFixedWidth(50)
    pkwdth_vmin, pkwdth_vmax = (1,20)
    pkwdth_ledit.setValidator(QtGui.QIntValidator(pkwdth_vmin, 
                              pkwdth_vmax))
    pkwdth_ledit.setMaxLength(3)
    pkwdth_ledit.setAlignment(Qt.AlignCenter)
    pkwdth_slider = QSlider(Qt.Orientation.Horizontal, thz_img_tab)
    pkwdth_slider.setRange(pkwdth_vmin, pkwdth_vmax)

    # construct a grid layout for the widgets 
    pkwdth_grid_layout = QGridLayout()

    # Add the widgets 
    pkwdth_lbl.setFixedHeight(30)
    pkwdth_grid_layout.addWidget(pkwdth_lbl, 0, 0, 1, 4)
    pkwdth_grid_layout.addWidget(pkwdth_ledit, 1, 0)
    pkwdth_grid_layout.addWidget(pkwdth_slider, 1, 1)

    # Add member variables
    thz_img_tab.pkwdth_lbl = pkwdth_lbl
    thz_img_tab.pkwdth_ledit = pkwdth_ledit
    thz_img_tab.pkwdth_slider = pkwdth_slider



    ####################################################################
    # Color scale adjustment widgets
    #
    cs_lbl_title = QLabel("Color Scaling")
    cs_autoscale_chkb  = QCheckBox()
    cs_autoscale_chkb.setText("Auto Color Scale:")
    cs_autoscale_chkb.setChecked(True)

    cs_lbl_min   = QLabel("Min:")
    cs_lbl_min.setFixedWidth(30)
    cs_lbl_max   = QLabel("Max:")
    cs_lbl_max.setFixedWidth(30)

    cs_ledit_min = QLineEdit()
    cs_ledit_min.setFixedWidth(50)
    cs_ledit_max = QLineEdit()
    cs_ledit_max.setFixedWidth(50)

    cs_vmin, cs_vmax = (10,700)

    cs_ledit_min.setMaxLength(5)
    cs_ledit_max.setMaxLength(5)

    cs_ledit_min.setAlignment(Qt.AlignCenter)
    cs_ledit_max.setAlignment(Qt.AlignCenter)

    cs_slider_min = QSlider(Qt.Orientation.Horizontal, thz_img_tab)
    cs_slider_max = QSlider(Qt.Orientation.Horizontal, thz_img_tab)

    cs_slider_min.setRange(cs_vmin, cs_vmax)
    cs_slider_max.setRange(cs_vmin, cs_vmax)

    # construct a grid layout for the widgets 
    cs_grid_layout = QGridLayout()


    # Add the widgets 
    cs_lbl_title.setFixedHeight(30)
    cs_grid_layout.addWidget(cs_lbl_title, 0,0, 1, 4)
    cs_grid_layout.addWidget(cs_autoscale_chkb, 1, 0, 1, 4)
    cs_grid_layout.addWidget(cs_lbl_min, 2, 0)
    cs_grid_layout.addWidget(cs_ledit_min, 2, 1)
    cs_grid_layout.addWidget(cs_slider_min, 2, 2)
    cs_grid_layout.addWidget(cs_lbl_max, 3, 0)
    cs_grid_layout.addWidget(cs_ledit_max, 3, 1)
    cs_grid_layout.addWidget(cs_slider_max, 3, 2)


    # Add member variables
    thz_img_tab.cs_lbl_title  = cs_lbl_title
    thz_img_tab.cs_autoscale_chkb = cs_autoscale_chkb
    thz_img_tab.cs_lbl_min    = cs_lbl_min
    thz_img_tab.cs_lbl_max    = cs_lbl_max
    thz_img_tab.cs_ledit_min  = cs_ledit_min
    thz_img_tab.cs_ledit_max  = cs_ledit_max
    thz_img_tab.cs_slider_min = cs_slider_min
    thz_img_tab.cs_slider_max = cs_slider_max


    ####################################################################
    # Color map dropdown menu
    #
    cmap_lbl_title = QLabel("Colormap")
    cmap_cbox = QComboBox()

    # populate the colormap dropdown menu with all matplotlib colormaps
    import matplotlib.pyplot as plt
    colormaps = sorted(plt.colormaps())
    cmap_cbox.addItems(colormaps)
    dflt_cmap = thz_img_tab.cfg_dict.get("colormap", "turbo")
    if dflt_cmap in colormaps:
        cmap_cbox.setCurrentIndex(colormaps.index(dflt_cmap))

    cmap_layout = QVBoxLayout()

    # Add the widgets to the layout
    cmap_lbl_title.setFixedHeight(30)
    cmap_layout.addWidget(cmap_lbl_title)
    cmap_layout.addWidget(cmap_cbox)

    # Add member variables
    thz_img_tab.cmap_lbl_title = cmap_lbl_title
    thz_img_tab.cmap_cbox      = cmap_cbox
    thz_img_tab.colormaps      = colormaps
    thz_img_tab.cmap_layout    = cmap_layout



    ####################################################################
    # Aux-plot checkboxes
    #
    legend_chkb = QCheckBox()
    legend_chkb.setText("Legend Visible")
    legend_chkb.setChecked(True)

    noise_limits_chkb = QCheckBox()
    noise_limits_chkb.setText("Noise Delimiters")
    noise_limits_chkb.setChecked(True)

    noise_floor_chkb = QCheckBox()
    noise_floor_chkb.setText("Noise Floor")
    noise_floor_chkb.setChecked(True)

    thresh_chkb = QCheckBox()
    thresh_chkb.setText("Threshold")
    thresh_chkb.setChecked(True)

    contr_chkb = QCheckBox()
    contr_chkb.setText("Contrast")
    contr_chkb.setChecked(True)

    front_peak_chkb = QCheckBox()
    front_peak_chkb.setText("Front Peak Marker")
    front_peak_chkb.setChecked(True)

    back_peak_chkb = QCheckBox()
    back_peak_chkb.setText("Back Peak Marker")
    back_peak_chkb.setChecked(True)

    weight_sum_chkb = QCheckBox()
    weight_sum_chkb.setText("Weighted Sum")
    weight_sum_chkb.setChecked(False)

    pt_mrkrs_chkb = QCheckBox()
    pt_mrkrs_chkb.setText("Plot Point Markers")
    pt_mrkrs_chkb.setChecked(False)

    # Add member variables
    thz_img_tab.legend_chkb       = legend_chkb
    thz_img_tab.noise_limits_chkb = noise_limits_chkb
    thz_img_tab.noise_floor_chkb  = noise_floor_chkb
    thz_img_tab.thresh_chkb       = thresh_chkb
    thz_img_tab.contr_chkb        = contr_chkb
    thz_img_tab.front_peak_chkb   = front_peak_chkb
    thz_img_tab.back_peak_chkb    = back_peak_chkb
    thz_img_tab.weight_sum_chkb   = weight_sum_chkb
    thz_img_tab.pt_mrkrs_chkb     = pt_mrkrs_chkb


    ####################################################################
    # Final layout structure
    # Left col: image + plot style radio buttons below
    # Center col: aux plot + aux checkboxes below
    # Right col: load btn, sliders, colormap, load/save image
    ####################################################################

    main_layout = QVBoxLayout(thz_img_tab)
    upper_layout = QHBoxLayout()

    # Left column: image + plot style radio buttons
    left_col = QVBoxLayout()
    left_col.addLayout(thz_img_tab.thz_image_obj)
    plot_style_layout = QHBoxLayout()
    plot_style_layout.addWidget(front_peak_rbut)
    plot_style_layout.addWidget(back_peak_rbut)
    plot_style_layout.addWidget(front_surface_plot_rbut)
    plot_style_layout.addWidget(back_surface_plot_rbut)
    plot_style_layout.addWidget(integ_pwr_rbut)
    left_col.addLayout(plot_style_layout)

    # Center column: aux plot + aux checkboxes
    center_col = QVBoxLayout()
    center_col.addWidget(thz_img_tab.aux_plot_obj)
    ctrl_box_layout = QGridLayout()
    ctrl_box_layout.addWidget(legend_chkb,       0, 0, 1, 1)
    ctrl_box_layout.addWidget(noise_limits_chkb, 1, 0, 1, 1)
    ctrl_box_layout.addWidget(noise_floor_chkb,  2, 0, 1, 1)
    ctrl_box_layout.addWidget(thresh_chkb,       3, 0, 1, 1)
    ctrl_box_layout.addWidget(contr_chkb,        0, 1, 1, 1)
    ctrl_box_layout.addWidget(front_peak_chkb,   1, 1, 1, 1)
    ctrl_box_layout.addWidget(back_peak_chkb,    2, 1, 1, 1)
    ctrl_box_layout.addWidget(weight_sum_chkb,   0, 2, 1, 1)
    ctrl_box_layout.addWidget(pt_mrkrs_chkb,     1, 2, 1, 1)
    center_col.addLayout(ctrl_box_layout)

    # Right column: load button, sliders, colormap, load/save image
    right_layout.addWidget(load_h5_btn)
    right_layout.addLayout(thresh_grid_layout)
    right_layout.addLayout(contr_grid_layout)
    right_layout.addLayout(pkwdth_grid_layout)
    right_layout.addLayout(cs_grid_layout)
    right_layout.addLayout(cmap_layout)
    right_layout.addLayout(ld_save_image_sublayout_row1)
    right_layout.addLayout(ld_save_image_sublayout_row2)
    right_layout.addLayout(ld_save_image_sublayout_row3)
    right_layout.addStretch()

    upper_layout.addLayout(left_col, 3)
    upper_layout.addLayout(center_col, 3)
    upper_layout.addLayout(right_layout, 2)

    main_layout.addLayout(upper_layout)

    thz_img_tab.right_layout   = right_layout
    thz_img_tab.main_layout    = main_layout



# this is just a container for the callback functions that call "update_config"
# properly when data changes in each of the config GUI objects
# it's tedious and long but really doesn't provide much novel 
# information apart from the associated cfg_dict key for each config object
class setup_thz_tab_callbacks:
    def __init__(s, thz_tab, update_config):
        pass
        s.update_config = update_config

        # QLineEdits
        thz_tab.ld_save_image_desc_ledit.editingFinished.connect(
            lambda: s.ledit_update(thz_tab.ld_save_image_desc_ledit, 
            "save_image_desc", str))



        # Setting the signal to textChanged for the slider bound line edits
        # for now
        thz_tab.thresh_ledit.textChanged.connect(
            lambda: s.ledit_update(thz_tab.thresh_ledit, 
            "threshold_db", float))
        thz_tab.contr_ledit.textChanged.connect(
            lambda: s.ledit_update(thz_tab.contr_ledit, 
            "contrast_db", float))
        thz_tab.pkwdth_ledit.textChanged.connect(
            lambda: s.ledit_update(thz_tab.pkwdth_ledit, 
            "half_peak_width", int))
        thz_tab.cs_ledit_min.textChanged.connect(
            lambda: s.ledit_update(thz_tab.cs_ledit_min, 
            "color_scale_min", float))
        thz_tab.cs_ledit_max.textChanged.connect(
            lambda: s.ledit_update(thz_tab.cs_ledit_max, 
            "color_scale_max", float))

        # QRadioButtons
        thz_tab.front_peak_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.front_peak_rbut, 
            "front", "peak_selection"))
        thz_tab.front_peak_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.front_peak_rbut, 
            "front_peak_range", "plot_style"))

        thz_tab.back_peak_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.back_peak_rbut, 
            "back", "peak_selection"))
        thz_tab.back_peak_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.back_peak_rbut, 
            "back_peak_range", "plot_style"))

        thz_tab.front_surface_plot_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.front_surface_plot_rbut, 
            "front", "peak_selection"))
        thz_tab.front_surface_plot_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.front_surface_plot_rbut, 
            "front_surface_range", "plot_style"))

        thz_tab.back_surface_plot_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.back_surface_plot_rbut, 
            "back", "peak_selection"))
        thz_tab.back_surface_plot_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.back_surface_plot_rbut, 
            "back_surface_range", "plot_style"))

        thz_tab.integ_pwr_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.integ_pwr_rbut, 
            "integ_power_plot", "peak_selection"))
        thz_tab.integ_pwr_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.integ_pwr_rbut, 
            "integ_power_plot", "plot_style"))

        # QPushButtons
        # any config updates occur in their respective callback functions

        # QSliders
        # these are each bound to QLineEdits that contain the true information
        # so no need to handle these here

        # QCheckBoxes
        thz_tab.cs_autoscale_chkb.stateChanged.connect(
            lambda: s.chkbox_update(thz_tab.cs_autoscale_chkb,
            "autoscale_color"))

        # QComboBoxes
        thz_tab.cmap_cbox.currentIndexChanged.connect(
            lambda: s.combo_box_update(thz_tab.cmap_cbox,
            "colormap"))


    ##########################################################################
    #                             UPDATE FUNCTIONS                           #
    ##########################################################################
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
        
    def rbut_update(s, rbut_obj, val_if_en, key):
        if rbut_obj.isChecked():
            new_cfg_dict = OrderedDict()
            new_cfg_dict[key] = val_if_en
            s.update_config(new_cfg_dict)


    def chkbox_update(s, chkb_obj, key, invert=False):
        if invert:
            val = not bool(chkb_obj.isChecked())
        else:
            val = bool(chkb_obj.isChecked())

        new_cfg_dict = OrderedDict()
        new_cfg_dict[key] = val
        s.update_config(new_cfg_dict)

    def combo_box_update(s, cbox_obj, key):
        new_cfg_dict = OrderedDict()
        new_cfg_dict[key] = cbox_obj.currentText()
        s.update_config(new_cfg_dict)



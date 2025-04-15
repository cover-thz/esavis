# This file only contains widget generation and layout along with some parameter 
# settings of widgets (e.g. read-only for a QLineEdit widget) for the 
# THzImageTab
# 
# Signals and slots should not be assigned here.  The purpose of this file is 
# to make the THzImageTab file much cleaner and more concise
#

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
import THzImageObj as tio

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
)


class SourceTab(QWidget):

    def __init__(self):
        super().__init__()





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
    #layout = QHBoxLayout(thz_img_tab)
    left_layout     = QVBoxLayout()
    #center_layout   = QVBoxLayout()
    right_layout    = QVBoxLayout()

    # default label
    #label = QLabel("Content of Tab 2")
    #layout.addWidget(label)

    ####################################################################
    # Left side widgets
    ####################################################################

    ####################################################################
    # Image widgets
    # NOTE TODO need to use a stacked widget here to have the multiple 
    # plots overlap with only one visible at a time
    #
    thz_img_tab.thz_image_obj = tio.THzImageObj(thz_img_tab)

    
    ####################################################################
    # Processing config stuff.  This is a rather long section as it 
    # contains all the associated tabs
    #
    thz_image_tab.proc_cfg_tab_widget = QTabWidget()


    ####################################################################
    # "Source" tab
    #
    src_tab = QWidget()
    thz_image_tab.proc_cfg_tab_widget.addTab(src_tab, "Source")
    src_tab_top_layout = QVBoxLayout()
    src_tab_lbl_1 = QLabel("Data Source:")

    # src_tab_sublayout_row1
    src_tab_sublayout_row1 = QHBoxLayout()
    file_src_rbut       = QRadioButton()
    file_src_rbut.setText("File")
    daq_src_rbut       = QRadioButton()
    daq_src_rbut.setText("DAQ")
    src_tab_sublayout_row1.addWidget(file_src_rbut)
    src_tab_sublayout_row1.addWidget(daq_src_rbut)

    # src_tab_sublayout_row2
    src_tab_sublayout_row2 = QHBoxLayout()
    daq_status_lbl = QLabel("DAQ Status: ")
    daq_status_ledit = QLineEdit()
    daq_status_ledit.setFixedWidth(50)
    src_tab_sublayout_row2.addWidget(daq_status_lbl)
    src_tab_sublayout_row2.addWidget(daq_status_ledit)

    # src_tab_sublayout_row3
    src_tab_sublayout_row3 = QHBoxLayout()
    file_status_lbl = QLabel("File Status: ")
    file_status_ledit = QLineEdit()
    file_status_ledit.setFixedWidth(50)
    src_tab_sublayout_row3.addWidget(file_status_lbl)
    src_tab_sublayout_row3.addWidget(file_status_ledit)

    # Toplevel layout of "Source" tab
    src_tab_top_layout.addWidget(src_tab_lbl_1)
    src_tab_top_layout.addLayout(src_tab_sublayout_row1)
    src_tab_top_layout.addLayout(src_tab_sublayout_row2)
    src_tab_top_layout.addLayout(src_tab_sublayout_row3)

    # Add member variables
    # (not adding the sublayouts because we probably don't need them)
    thz_image_tab.src_tab = src_tab
    thz_image_tab.file_src_rbut = file_src_rbut
    thz_image_tab.daq_src_rbut  = daq_src_rbut
    thz_image_tab.daq_status_ledit = daq_status_ledit
    thz_image_tab.file_status_ledit = file_status_ledit
    thz_image_tab.src_tab_top_layout = src_tab_top_layout


    ####################################################################
    # "Load/Save Config" tab
    #
    ld_sv_tab = QWidget()
    thz_image_tab.proc_cfg_tab_widget.addTab(ld_sv_tab, "Load/Save\nConfig")
    ld_sv_tab_top_layout = QVBoxLayout()

    # ld_sv_sublaout_row1
    ld_sv_sublayout_row1 = QHBoxLayout()
    load_cfg_btn = QPushButton("Load Config\nFile")
    load_dflt_cfg_btn = QPushButton("Load Config\nDefaults")
    ld_sv_sublayout_row1.addWidget(load_cfg_btn)
    ld_sv_sublayout_row1.addWidget(load_dflt_cfg_btn)

    # ld_sv_sublaout_row2
    ld_sv_sublayout_row2 = QHBoxLayout()
    save_cfg_btn = QPushButton("Save Config\nFile")
    save_dflt_cfg_btn = QPushButton("Save New\nDefault Config")
    ld_sv_sublayout_row2.addWidget(save_cfg_btn)
    ld_sv_sublayout_row2.addWidget(save_dflt_cfg_btn)

    # Toplevel layout of "Load/Save Config" tab
    ld_sv_tab_top_layout.addLayout(ld_sv_sublayout_row1)
    ld_sv_tab_top_layout.addLayout(ld_sv_sublayout_row2)

    # Add member variables
    # (not adding the sublayouts because we probably don't need them)
    thz_img_tab.load_cfg_btn        = load_cfg_btn
    thz_img_tab.load_dflt_cfg_btn   = load_dflt_cfg_btn
    thz_img_tab.save_cfg_btn        = save_cfg_btn
    thz_img_tab.save_dflt_cfg_btn   = save_dflt_cfg_btn
    thz_image_tab.ld_sv_tab_top_layout = ld_sv_tab_top_layout


    ####################################################################
    # "Plot Style" tab
    #
    plot_style_tab = QWidget()
    thz_image_tab.proc_cfg_tab_widget.addTab(plot_style_tab, "Plot Style")
    plot_style_tab_top_layout = QHBoxLayout()
    plot_style_lbl      = QLabel("Plot Style:")

    # plot_style_sublayout_col1
    plot_style_sublayout_col1 = QVBoxLayout()
    plot_style_sublayout_col1.addWidget(plot_style_lbl)
    front_peak_rbut     = QRadioButton()
    front_peak_rbut.setText("Front Peak Range")
    plot_style_sublayout_col1.addWidget(front_peak_rbut)
    back_peak_rbut      = QRadioButton()
    back_peak_rbut.setText("Back Peak Range")
    plot_style_sublayout_col1.addWidget(back_peak_rbut)
    front_surface_plot_rbut   = QRadioButton()
    front_surface_plot_rbut.setText("Front Surface Plot")
    plot_style_sublayout_col1.addWidget(front_surface_plot_rbut)
    back_surface_plot_rbut   = QRadioButton()
    back_surface_plot_rbut.setText("Back Surface Plot")
    plot_style_sublayout_col1.addWidget(back_surface_plot_rbut)
    num_avgs_rbut     = QRadioButton()
    num_avgs_rbut.setText("Show Number of Averages")
    plot_style_sublayout_col1.addWidget(num_avgs_rbut)
    integ_pwr_rbut     = QRadioButton()
    integ_pwr_rbut.setText("Integrated Power")
    plot_style_sublayout_col1.addWidget(integ_pwr_rbut)
    point_cloud_rbut  = QRadioButton()
    #point_cloud_rbut.setText("Point Cloud")
    point_cloud_rbut.setEnabled(False)
    point_cloud_rbut.setText("RESERVED")
    plot_style_sublayout_col1.addWidget(point_cloud_rbut)

    #  plot_style_sublayout_col2
    plot_style_sublayout_col2 = QVBoxLayout()
    reset_camera_btn    = QPushButton("Reset Plot\nCamera")
    plot_style_sublayout_col2.addWidget(reset_camera_btn)

    # Toplevel layout of "Plot Style" tab
    # (might want to add more stuff here, we have the space)
    plot_style_tab_top_layout.addLayout(plot_style_sublayout_col1)
    plot_style_tab_top_layout.addLayout(plot_style_sublayout_col2)

    # Add member variables
    # (not adding the sublayouts because we probably don't need them)
    thz_img_tab.front_peak_rbut         = front_peak_rbut
    thz_img_tab.back_peak_rbut          = back_peak_rbut
    thz_img_tab.front_surface_plot_rbut = front_surface_plot_rbut
    thz_img_tab.back_surface_plot_rbut  = back_surface_plot_rbut
    thz_img_tab.num_avgs_rbut           = num_avgs_rbut
    thz_img_tab.integ_pwr_rbut          = integ_pwr_rbut
    thz_img_tab.point_cloud_rbut        = point_cloud_rbut
    thz_img_tab.reset_camera_btn        = reset_camera_btn

    # NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO
    # NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO
    # NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO
    #
    # This is where you left of on EOD 4/14/2025
    #
    # NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO
    # NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO
    # NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO


    ####################################################################
    # Plot style radiobuttons and save image buttons 
    # (and save status label)
    

    # Save buttons
    image_autosave_btn  = QPushButton("Autosave\nImage")
    image_save_btn      = QPushButton("Save\nImage")
    image_save_lbl      = QLabel("                  ")

    # Layout
    rbut_savebut_sublayout  = QHBoxLayout()
    rbut_sublayout          = QVBoxLayout()
    savebut_sublayout       = QVBoxLayout()

    rbut_sublayout.addWidget(plot_style_lbl)
    rbut_sublayout.addWidget(front_peak_rbut)
    rbut_sublayout.addWidget(back_peak_rbut)
    rbut_sublayout.addWidget(front_surface_plot_rbut)
    rbut_sublayout.addWidget(back_surface_plot_rbut)
    rbut_sublayout.addWidget(num_avgs_rbut)
    rbut_sublayout.addWidget(integ_pwr_rbut)
    rbut_sublayout.addWidget(point_cloud_rbut)

    savebut_sublayout.addWidget(image_autosave_btn)
    savebut_sublayout.addWidget(image_save_btn)
    savebut_sublayout.addWidget(image_save_lbl)
    

    rbut_savebut_sublayout.addLayout(rbut_sublayout)
    rbut_savebut_sublayout.addLayout(savebut_sublayout)


    # Add member variables
    thz_img_tab.plot_style_lbl          = plot_style_lbl
    thz_img_tab.front_peak_rbut         = front_peak_rbut
    thz_img_tab.back_peak_rbut          = back_peak_rbut
    thz_img_tab.front_surface_plot_rbut = front_surface_plot_rbut
    thz_img_tab.back_surface_plot_rbut  = back_surface_plot_rbut
    thz_img_tab.num_avgs_rbut           = num_avgs_rbut
    thz_img_tab.integ_pwr_rbut          = integ_pwr_rbut
    thz_img_tab.point_cloud_rbut        = point_cloud_rbut

    thz_img_tab.image_autosave_btn      = image_autosave_btn
    thz_img_tab.image_save_btn          = image_save_btn
    thz_img_tab.image_save_lbl          = image_save_lbl




    ####################################################################
    # Center and Right side widgets
    ####################################################################

    ####################################################################
    # Update button
    #
    update_btn = QPushButton("Update\nPlot")

    # Add member variables
    thz_img_tab.update_btn = update_btn
    

    ####################################################################
    # Threshold adjustment widgets
    #
    thresh_lbl = QLabel("Threshold (dB)")
    thresh_ledit = QLineEdit()
    thresh_ledit.setFixedWidth(50)

    # sets the limits of threshold values
    thresh_vmin, thresh_vmax = (0,80)
    #thresh_ledit.setValidator(QtGui.QIntValidator(thresh_vmin, 
    #                          thresh_vmax))
    thresh_ledit.setMaxLength(4)
    thresh_ledit.setAlignment(Qt.AlignCenter)
    #thresh_ledit.setFont(QFont("Arial", 20))
    thresh_slider = QSlider(Qt.Orientation.Horizontal, thz_img_tab)
    thresh_slider.setRange(thresh_vmin, thresh_vmax)

    # construct a grid layout for the widgets 
    thresh_grid_layout = QGridLayout()

    # Add the threshold widgets to the layout
    #center_layout.addWidget(thresh_lbl)
    #center_layout.addWidget(thresh_ledit)
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
    contr_lbl = QLabel("Contrast (dB)")
    contr_ledit = QLineEdit()
    contr_ledit.setFixedWidth(50)
    contr_vmin, contr_vmax = (1,80)
    # limiting the valid text is doing more harm than good
    #contr_ledit.setValidator(QtGui.QIntValidator(contr_vmin, 
    #                          contr_vmax))
    contr_ledit.setMaxLength(4)
    contr_ledit.setAlignment(Qt.AlignCenter)
    #contr_ledit.setFont(QFont("Arial", 20))
    contr_slider = QSlider(Qt.Orientation.Horizontal, thz_img_tab)
    contr_slider.setRange(contr_vmin, contr_vmax)

    # construct a grid layout for the widgets 
    contr_grid_layout = QGridLayout()

    # Add the contrast widgets 
    #center_layout.addWidget(contr_lbl)
    #center_layout.addWidget(contr_ledit)
    contr_lbl.setFixedHeight(30)
    contr_grid_layout.addWidget(contr_lbl, 0, 0, 1, 4)
    contr_grid_layout.addWidget(contr_ledit, 1, 0)
    contr_grid_layout.addWidget(contr_slider, 1, 1)

    # Add member variables
    thz_img_tab.contr_lbl = contr_lbl
    thz_img_tab.contr_ledit = contr_ledit
    thz_img_tab.contr_slider = contr_slider



    ####################################################################
    # Peak width adjustment widgets [NOTE removed for now]
    #
    """
    pkwdth_lbl = QLabel("Peak Width")
    pkwdth_ledit = QLineEdit()
    pkwdth_ledit.setFixedWidth(50)
    pkwdth_vmin, pkwdth_vmax = (1,50)
    pkwdth_ledit.setValidator(QtGui.QIntValidator(pkwdth_vmin, 
                              pkwdth_vmax))
    pkwdth_ledit.setMaxLength(3)
    pkwdth_ledit.setAlignment(Qt.AlignCenter)
    #pkwdth_ledit.setFont(QFont("Arial", 20))
    pkwdth_slider = QSlider(Qt.Orientation.Horizontal, thz_img_tab)
    pkwdth_slider.setRange(pkwdth_vmin, pkwdth_vmax)

    # construct a grid layout for the widgets 
    pkwdth_grid_layout = QGridLayout()

    # Add the peak width widgets 
    #center_layout.addWidget(pkwdth_lbl)
    #center_layout.addWidget(pkwdth_ledit)
    pkwdth_lbl.setFixedHeight(30)
    pkwdth_grid_layout.addWidget(pkwdth_lbl, 0, 0, 1, 4)
    pkwdth_grid_layout.addWidget(pkwdth_ledit, 1, 0)
    pkwdth_grid_layout.addWidget(pkwdth_slider, 1, 1)


    # Add member variables
    thz_img_tab.pkwdth_lbl = pkwdth_lbl
    thz_img_tab.pkwdth_ledit = pkwdth_ledit
    thz_img_tab.pkwdth_slider = pkwdth_slider

    """


    ####################################################################
    # Range cut adjustment widgets
    #
    rc_lbl_title = QLabel("Range Cut (cm)\n(modified)")
    rc_lbl_min   = QLabel("Min:")
    rc_lbl_min.setFixedWidth(30)
    rc_lbl_max   = QLabel("Max:")
    rc_lbl_max.setFixedWidth(30)

    rc_ledit_min = QLineEdit()
    rc_ledit_min.setFixedWidth(40)
    rc_ledit_max = QLineEdit()
    rc_ledit_max.setFixedWidth(40)

    rc_vmin, rc_vmax = (200,600)

    #rc_ledit_min.setValidator(QtGui.QIntValidator(rc_vmin, rc_vmax))
    #rc_ledit_max.setValidator(QtGui.QIntValidator(rc_vmin, rc_vmax))

    rc_ledit_min.setMaxLength(5)
    rc_ledit_max.setMaxLength(5)

    rc_ledit_min.setAlignment(Qt.AlignCenter)
    rc_ledit_max.setAlignment(Qt.AlignCenter)

    rc_slider_min = QSlider(Qt.Orientation.Horizontal, thz_img_tab)
    rc_slider_max = QSlider(Qt.Orientation.Horizontal, thz_img_tab)

    rc_slider_min.setRange(rc_vmin, rc_vmax)
    rc_slider_max.setRange(rc_vmin, rc_vmax)

    # construct a grid layout for the widgets 
    rc_grid_layout = QGridLayout()

    # Add the range cut widgets 
    #center_layout.addWidget(rc_lbl_title)
    #center_layout.addWidget(rc_lbl_min)
    #center_layout.addWidget(rc_lbl_max)

    rc_lbl_title.setFixedHeight(30)
    rc_grid_layout.addWidget(rc_lbl_title, 0,0, 1, 4)
    rc_grid_layout.addWidget(rc_lbl_min, 1, 0)
    rc_grid_layout.addWidget(rc_ledit_min, 1, 1)
    rc_grid_layout.addWidget(rc_slider_min, 1, 2)
    rc_grid_layout.addWidget(rc_lbl_max, 2, 0)
    rc_grid_layout.addWidget(rc_ledit_max, 2, 1)
    rc_grid_layout.addWidget(rc_slider_max, 2, 2)

    # Add member variables
    thz_img_tab.rc_lbl_title  = rc_lbl_title
    thz_img_tab.rc_lbl_min    = rc_lbl_min
    thz_img_tab.rc_lbl_max    = rc_lbl_max
    thz_img_tab.rc_ledit_min  = rc_ledit_min
    thz_img_tab.rc_ledit_max  = rc_ledit_max
    thz_img_tab.rc_slider_min = rc_slider_min
    thz_img_tab.rc_slider_max = rc_slider_max


    ####################################################################
    # Color scale adjustment widgets
    #
    cs_lbl_title = QLabel("Color Scaling")
    cs_autoscale_chkb  = QCheckBox()
    cs_autoscale_chkb.setText("Auto Color Scale:")

    cs_lbl_min   = QLabel("Min:")
    cs_lbl_min.setFixedWidth(30)
    cs_lbl_max   = QLabel("Max:")
    cs_lbl_max.setFixedWidth(30)

    cs_ledit_min = QLineEdit()
    cs_ledit_min.setFixedWidth(50)
    cs_ledit_max = QLineEdit()
    cs_ledit_max.setFixedWidth(50)

    cs_vmin, cs_vmax = (100,700)

    #cs_ledit_min.setValidator(QtGui.QIntValidator(cs_vmin, cs_vmax))
    #cs_ledit_max.setValidator(QtGui.QIntValidator(cs_vmin, cs_vmax))

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

    # Add the range cut widgets 
    #center_layout.addWidget(rc_lbl_title)
    #center_layout.addWidget(rc_lbl_min)
    #center_layout.addWidget(rc_lbl_max)

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

    # populate the colormap dropdown menu
    colormaps = ["jet_r", "jet", "gray", "binary", "Blues", "Greens"]
    colormaps += ["Reds", "copper", "twilight"]
    cmap_cbox.addItems(colormaps)

    cmap_layout = QVBoxLayout()

    # Add the contrast widgets 
    #center_layout.addWidget(contr_lbl)
    #center_layout.addWidget(contr_ledit)
    cmap_lbl_title.setFixedHeight(30)
    cmap_layout.addWidget(cmap_lbl_title)
    cmap_layout.addWidget(cmap_cbox)


    # Add member variables
    thz_img_tab.cmap_lbl_title = cmap_lbl_title
    thz_img_tab.cmap_cbox      = cmap_cbox
    thz_img_tab.colormaps      = colormaps
    thz_img_tab.cmap_layout    = cmap_layout


    ####################################################################
    # final layout structure (two columns)
    #
    main_layout = QHBoxLayout(thz_img_tab)

    # left side widgets
    left_layout.addLayout(thz_img_tab.thz_image_obj) 
    left_layout.addWidget(proc_cfg_lbl)
    left_layout.addLayout(#TODO)
    left_layout.addLayout(#TODO)
    left_layout.addLayout(rbut_savebut_sublayout)

    # right side widgets 
    right_layout.addWidget(update_btn)
    right_layout.addLayout(thresh_grid_layout)
    right_layout.addLayout(contr_grid_layout)
    #right_layout.addLayout(pkwdth_grid_layout) # disabled for now
    right_layout.addLayout(rc_grid_layout)
    right_layout.addLayout(cs_grid_layout)
    right_layout.addLayout(cmap_layout)

    # the second argument somehow changes the porprtion each layout 
    # takes in horizontal space.  It is confusing, using the age-old
    # guess-and-check method
    main_layout.addLayout(left_layout, 25)
    main_layout.addLayout(right_layout, 15)

    thz_img_tab.left_layout    = left_layout
    thz_img_tab.right_layout   = right_layout
    thz_img_tab.main_layout    = main_layout




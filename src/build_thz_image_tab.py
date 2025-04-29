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
from collections import OrderedDict

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
    QButtonGroup,
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
    # This is the main upper left widget that is the THz image plot
    # that takes up a significant portion of the screen.  
    # 
    # The processing config stuff below is the lower left 
    # portion of the screen
    # 
    # NOTE: Giving the cfg_dict to THzImageObj but again it does NOT alter it
    # only reads from it
    thz_img_tab.thz_image_obj = tio.THzImageObj(thz_img_tab, 
        thz_img_tab.cfg_dict, main_image=True)

    
    ####################################################################
    # Processing config stuff.  This is a rather long section as it 
    # contains all the associated tabs
    #
    #
    proc_cfg_tab_widget = QTabWidget()
    thz_img_tab.proc_cfg_tab_widget = proc_cfg_tab_widget


    ####################################################################
    # "Source" tab
    #
    src_tab = QWidget()
    proc_cfg_tab_widget.addTab(src_tab, "Source")
    src_tab_top_layout = QVBoxLayout()
    src_tab_lbl_1 = QLabel("Data Source:")

    # src_tab_sublayout_row1
    src_tab_sublayout_row1 = QHBoxLayout()
    file_src_rbut       = QRadioButton()
    file_src_rbut.setText("File")
    blank1_src_lbl       = QLabel("")
    blank2_src_lbl       = QLabel("")
    daq_src_rbut       = QRadioButton()
    daq_src_rbut.setText("DAQ")
    src_tab_sublayout_row1.addWidget(file_src_rbut)
    src_tab_sublayout_row1.addWidget(blank1_src_lbl)
    src_tab_sublayout_row1.addWidget(blank2_src_lbl)
    src_tab_sublayout_row1.addWidget(daq_src_rbut)

    # src_tab_sublayout_row2
    src_tab_sublayout_row2 = QHBoxLayout()
    daq_status_lbl = QLabel("DAQ Status: ")
    daq_status_ledit = QLineEdit()
    daq_status_ledit.setFixedWidth(170)
    daq_status_ledit.setReadOnly(True)

    src_tab_sublayout_row2.addWidget(daq_status_lbl)
    src_tab_sublayout_row2.addWidget(daq_status_ledit)

    # src_tab_sublayout_row3
    src_tab_sublayout_row3 = QHBoxLayout()
    file_status_lbl = QLabel("File Status: ")
    file_status_ledit = QLineEdit()
    file_status_ledit.setFixedWidth(170)
    file_status_ledit.setReadOnly(True)
    src_tab_sublayout_row3.addWidget(file_status_lbl)
    src_tab_sublayout_row3.addWidget(file_status_ledit)

    # Toplevel layout of "Source" tab
    src_tab_top_layout.addWidget(src_tab_lbl_1)
    src_tab_top_layout.addLayout(src_tab_sublayout_row1)
    src_tab_top_layout.addLayout(src_tab_sublayout_row2)
    src_tab_top_layout.addLayout(src_tab_sublayout_row3)

    # Add member variables
    # (not adding the sublayouts because we probably don't need them)
    thz_img_tab.src_tab = src_tab
    thz_img_tab.file_src_rbut = file_src_rbut
    thz_img_tab.daq_src_rbut  = daq_src_rbut
    thz_img_tab.daq_status_ledit = daq_status_ledit
    thz_img_tab.file_status_ledit = file_status_ledit
    thz_img_tab.src_tab_top_layout = src_tab_top_layout

    # final piece
    src_tab.setLayout(src_tab_top_layout)


    ####################################################################
    # NOTE This currently does nothing as ConfigTab takes care of all 
    # configuration considerations for now.  
    #
    # As a result it is currently not added as a tab and therefore does not
    # appear in the current layout 
    # 
    # "Load/Save Config" tab
    #
    ld_sv_cfg_tab = QWidget()
    #proc_cfg_tab_widget.addTab(ld_sv_cfg_tab, 
    #    "Load/Save\nConfig")
    ld_sv_cfg_tab_top_layout = QVBoxLayout()

    # ld_sv_cfg_sublaout_row1
    ld_sv_cfg_sublayout_row1 = QHBoxLayout()
    load_cfg_btn = QPushButton("Load Config\nFile")
    load_dflt_cfg_btn = QPushButton("Load Config\nDefaults")
    ld_sv_cfg_sublayout_row1.addWidget(load_cfg_btn)
    ld_sv_cfg_sublayout_row1.addWidget(load_dflt_cfg_btn)

    # ld_sv_cfg_sublaout_row2
    ld_sv_cfg_sublayout_row2 = QHBoxLayout()
    save_cfg_btn = QPushButton("Save Config\nFile")
    save_dflt_cfg_btn = QPushButton("Save New\nDefault Config")
    ld_sv_cfg_sublayout_row2.addWidget(save_cfg_btn)
    ld_sv_cfg_sublayout_row2.addWidget(save_dflt_cfg_btn)

    # Toplevel layout of "Load/Save Config" tab
    ld_sv_cfg_tab_top_layout.addLayout(ld_sv_cfg_sublayout_row1)
    ld_sv_cfg_tab_top_layout.addLayout(ld_sv_cfg_sublayout_row2)

    # Add member variables
    # (not adding the sublayouts because we probably don't need them)
    thz_img_tab.load_cfg_btn        = load_cfg_btn
    thz_img_tab.load_dflt_cfg_btn   = load_dflt_cfg_btn
    thz_img_tab.save_cfg_btn        = save_cfg_btn
    thz_img_tab.save_dflt_cfg_btn   = save_dflt_cfg_btn
    thz_img_tab.ld_sv_cfg_tab_top_layout = ld_sv_cfg_tab_top_layout

    # final piece
    #ld_sv_cfg_tab.setLayout(ld_sv_cfg_tab_top_layout)


    ####################################################################
    # "Plot Style" tab
    #
    plot_style_tab = QWidget()
    proc_cfg_tab_widget.addTab(plot_style_tab, "Plot Style")
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
    num_oversamp_rbut     = QRadioButton()
    #num_oversamp_rbut.setText("Show Degree of Oversampling") 
    num_oversamp_rbut.setEnabled(False)
    num_oversamp_rbut.setText("RESERVED")
    plot_style_sublayout_col1.addWidget(num_oversamp_rbut)
    integ_pwr_rbut     = QRadioButton()
    integ_pwr_rbut.setText("Integrated Power")
    plot_style_sublayout_col1.addWidget(integ_pwr_rbut)
    point_cloud_rbut  = QRadioButton()
    #point_cloud_rbut.setText("Point Cloud")
    point_cloud_rbut.setEnabled(False)
    point_cloud_rbut.setText("RESERVED")
    plot_style_sublayout_col1.addWidget(point_cloud_rbut)

    #  plot_style_sublayout_col2
    # (might want to add more stuff here, we have the space)
    plot_style_sublayout_col2 = QVBoxLayout()
    reset_camera_btn    = QPushButton("Reset Plot\nCamera")
    plot_style_sublayout_col2.addWidget(reset_camera_btn)

    # Toplevel layout of "Plot Style" tab
    plot_style_tab_top_layout.addLayout(plot_style_sublayout_col1)
    plot_style_tab_top_layout.addLayout(plot_style_sublayout_col2)

    # Add member variables
    # (not adding the sublayouts because we probably don't need them)
    thz_img_tab.front_peak_rbut         = front_peak_rbut
    thz_img_tab.back_peak_rbut          = back_peak_rbut
    thz_img_tab.front_surface_plot_rbut = front_surface_plot_rbut
    thz_img_tab.back_surface_plot_rbut  = back_surface_plot_rbut
    thz_img_tab.num_oversamp_rbut       = num_oversamp_rbut
    thz_img_tab.integ_pwr_rbut          = integ_pwr_rbut
    thz_img_tab.point_cloud_rbut        = point_cloud_rbut
    thz_img_tab.reset_camera_btn        = reset_camera_btn

    # final piece
    plot_style_tab.setLayout(plot_style_tab_top_layout)


    ####################################################################
    # "Frame Style" tab
    #
    frame_style_tab = QWidget()
    proc_cfg_tab_widget.addTab(frame_style_tab, "Frame Style")
    frame_style_tab_top_layout = QVBoxLayout()

    # frame_style_sublayout_row1
    frame_style_sublayout_row1  = QHBoxLayout()
    azi_turn_fs_rbut               = QRadioButton()
    azi_turn_fs_rbut.setText("Azimuth Turnaround")
    azi_hyst_fs_lbl               = QLabel("Az Hysteresis:")
    azi_hyst_fs_ledit             = QLineEdit()
    frame_style_sublayout_row1.addWidget(azi_turn_fs_rbut)
    frame_style_sublayout_row1.addWidget(azi_hyst_fs_lbl)
    frame_style_sublayout_row1.addWidget(azi_hyst_fs_ledit)

    # frame_style_sublayout_row2
    frame_style_sublayout_row2  = QHBoxLayout()
    num_rng_fs_rbut             = QRadioButton()
    num_rng_fs_rbut.setText("Number of Rangelines")
    azi_marg_fs_lbl             = QLabel("Az Margin:")
    azi_marg_fs_ledit           = QLineEdit()
    frame_style_sublayout_row2.addWidget(num_rng_fs_rbut)
    frame_style_sublayout_row2.addWidget(azi_marg_fs_lbl)
    frame_style_sublayout_row2.addWidget(azi_marg_fs_ledit)

    # frame_style_sublayout_row3
    frame_style_sublayout_row3  = QHBoxLayout()
    col_frac_fs_rbut               = QRadioButton()
    col_frac_fs_rbut.setText("Col Fraction Filled")
    num_rng_fs_lbl              = QLabel("Rangelines Thresh:")
    num_rng_fs_ledit            = QLineEdit()
    frame_style_sublayout_row3.addWidget(col_frac_fs_rbut)
    frame_style_sublayout_row3.addWidget(num_rng_fs_lbl)
    frame_style_sublayout_row3.addWidget(num_rng_fs_ledit)

    # frame_style_sublayout_row4
    frame_style_sublayout_row4  = QHBoxLayout()
    pix_frac_fs_rbut            = QRadioButton()
    pix_frac_fs_rbut.setText("Pixel Fraction Filled")
    tot_frac_fs_lbl              = QLabel("Col/Pix Fraction*:")
    tot_frac_fs_ledit            = QLineEdit()
    frame_style_sublayout_row4.addWidget(pix_frac_fs_rbut)
    frame_style_sublayout_row4.addWidget(tot_frac_fs_lbl)
    frame_style_sublayout_row4.addWidget(tot_frac_fs_ledit)


    # frame_style_sublayout_row4pt1
    frame_style_sublayout_row4pt1  = QHBoxLayout()
    daq_num_rng_fs_lbl        = QLabel("Num Rangelines Per\nDAQ Grab:")
    daq_num_rng_fs_ledit      = QLineEdit()
    frame_style_sublayout_row4pt1.addWidget(daq_num_rng_fs_lbl)
    frame_style_sublayout_row4pt1.addWidget(daq_num_rng_fs_ledit)


    # frame_style_sublayout_row5
    frame_style_sublayout_row5  = QHBoxLayout()
    frac_fs_lbl                 = QLabel("*Between 0 and 1")
    frame_style_sublayout_row5.addWidget(frac_fs_lbl)

    # Toplevel layout of "Frame Style" tab
    frame_style_tab_top_layout.addLayout(frame_style_sublayout_row1)
    frame_style_tab_top_layout.addLayout(frame_style_sublayout_row2)
    frame_style_tab_top_layout.addLayout(frame_style_sublayout_row3)
    frame_style_tab_top_layout.addLayout(frame_style_sublayout_row4)
    frame_style_tab_top_layout.addLayout(frame_style_sublayout_row4pt1)
    frame_style_tab_top_layout.addLayout(frame_style_sublayout_row5)

    # Add member variables
    # (not adding the sublayouts because we probably don't need them)
    thz_img_tab.azi_turn_fs_rbut = azi_turn_fs_rbut
    thz_img_tab.azi_hyst_fs_lbl = azi_hyst_fs_lbl
    thz_img_tab.azi_hyst_fs_ledit = azi_hyst_fs_ledit
    thz_img_tab.num_rng_fs_rbut = num_rng_fs_rbut
    thz_img_tab.azi_marg_fs_lbl = azi_marg_fs_lbl
    thz_img_tab.azi_marg_fs_ledit = azi_marg_fs_ledit
    thz_img_tab.col_frac_fs_rbut = col_frac_fs_rbut
    thz_img_tab.num_rng_fs_lbl = num_rng_fs_lbl
    thz_img_tab.daq_num_rng_fs_lbl   = daq_num_rng_fs_lbl
    thz_img_tab.daq_num_rng_fs_ledit = daq_num_rng_fs_ledit


    thz_img_tab.num_rng_fs_ledit = num_rng_fs_ledit
    thz_img_tab.pix_frac_fs_rbut = pix_frac_fs_rbut
    thz_img_tab.tot_frac_fs_lbl = tot_frac_fs_lbl
    thz_img_tab.tot_frac_fs_ledit = tot_frac_fs_ledit
    thz_img_tab.frac_fs_lbl = frac_fs_lbl

    # final piece
    frame_style_tab.setLayout(frame_style_tab_top_layout)


    ####################################################################
    # "Load Save Image" tab
    #
    ld_sv_image_tab = QWidget()
    proc_cfg_tab_widget.addTab(ld_sv_image_tab, 
                                             "Load/Save\nImage")
    ld_save_image_tab_top_layout = QVBoxLayout()

    # ld_save_image_sublayout_row1
    ld_save_image_sublayout_row1  = QHBoxLayout()
    ld_save_image_autosave_btn  = QPushButton("Autosave\nImage")
    ld_save_image_chng_dir_btn  = QPushButton("Change Save\nDirectory")
    ld_save_image_save_btn      = QPushButton("Save\nImage")
    ld_save_image_sublayout_row1.addWidget(ld_save_image_autosave_btn)
    ld_save_image_sublayout_row1.addWidget(ld_save_image_chng_dir_btn)
    ld_save_image_sublayout_row1.addWidget(ld_save_image_save_btn)

    # ld_save_image_sublayout_row2
    ld_save_image_sublayout_row2 = QHBoxLayout()
    ld_save_image_curr_dir_lbl    = QLabel("Current Save Dir:")
    ld_save_image_curr_dir_ledit  = QLineEdit()
    ld_save_image_curr_dir_ledit.setReadOnly(True)
    ld_save_image_sublayout_row2.addWidget(ld_save_image_curr_dir_lbl)
    ld_save_image_sublayout_row2.addWidget(ld_save_image_curr_dir_ledit)

    # ld_save_image_sublayout_row3
    ld_save_image_sublayout_row3 = QHBoxLayout()
    ld_save_image_desc_lbl    = QLabel("Image Description:")
    ld_save_image_desc_ledit  = QLineEdit()
    ld_save_image_sublayout_row3.addWidget(ld_save_image_desc_lbl)
    ld_save_image_sublayout_row3.addWidget(ld_save_image_desc_ledit)

    # Toplevel layout of "Framae Style" tab
    ld_save_image_tab_top_layout.addLayout(ld_save_image_sublayout_row1)
    ld_save_image_tab_top_layout.addLayout(ld_save_image_sublayout_row2)
    ld_save_image_tab_top_layout.addLayout(ld_save_image_sublayout_row3)

    # Add member variables
    # (not adding the sublayouts because we probably don't need them)
    thz_img_tab.azi_turn_fs_rbut = azi_turn_fs_rbut
    thz_img_tab.ld_save_image_autosave_btn = ld_save_image_autosave_btn
    thz_img_tab.ld_save_image_chng_dir_btn = ld_save_image_chng_dir_btn
    thz_img_tab.ld_save_image_save_btn = ld_save_image_save_btn
    thz_img_tab.ld_save_image_curr_dir_lbl = ld_save_image_curr_dir_lbl
    thz_img_tab.ld_save_image_curr_dir_ledit = ld_save_image_curr_dir_ledit
    thz_img_tab.ld_save_image_desc_lbl = ld_save_image_desc_lbl
    thz_img_tab.ld_save_image_desc_ledit = ld_save_image_desc_ledit

    # final piece
    ld_sv_image_tab.setLayout(ld_save_image_tab_top_layout)



    ####################################################################
    # Center and Right side widgets
    ####################################################################

    ####################################################################
    # Update button (REMOVED FOR NOW)
    #
    #update_btn = QPushButton("Update\nPlot")

    # Add member variables
    #thz_img_tab.update_btn = update_btn
    

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
    #thresh_ledit.setValidator(QtGui.QIntValidator(thresh_vmin, 
    #                          thresh_vmax))
    thresh_ledit.setMaxLength(4)
    thresh_ledit.setAlignment(Qt.AlignCenter)
    #thresh_ledit.setFont(QFont("Arial", 20))
    thresh_slider = QSlider(Qt.Orientation.Horizontal, thz_img_tab)
    thresh_slider.setRange(thresh_vmin, thresh_vmax)

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
    # construct a grid layout for the widgets 
    contr_grid_layout = QGridLayout()

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
    #pkwdth_ledit.setFont(QFont("Arial", 20))
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

    rc_vmin, rc_vmax = (10,700)

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

    cs_vmin, cs_vmax = (10,700)

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

    # populate the colormap dropdown menu
    colormaps = ["jet_r", "jet", "gray", "binary", "Blues", "Greens"]
    colormaps += ["Reds", "copper", "twilight"]
    cmap_cbox.addItems(colormaps)

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
    # Frame limits line edits
    #
    frame_limits_layout = QVBoxLayout()
    frame_pause_btn = QPushButton("Pause Capture")
    frame_limits_lbl = QLabel("Frame Limits")

    # fl_sublayout_row1
    fl_sublayout_row1   = QHBoxLayout()
    az_min_lim_lbl      = QLabel("Az min:")
    az_min_lim_ledit    = QLineEdit()
    fl_sublayout_row1.addWidget(az_min_lim_lbl)
    fl_sublayout_row1.addWidget(az_min_lim_ledit)

    # fl_sublayout_row2
    fl_sublayout_row2   = QHBoxLayout()
    az_max_lim_lbl      = QLabel("Az max:")
    az_max_lim_ledit    = QLineEdit()
    fl_sublayout_row2.addWidget(az_max_lim_lbl)
    fl_sublayout_row2.addWidget(az_max_lim_ledit)

    # fl_sublayout_row3
    fl_sublayout_row3   = QHBoxLayout()
    el_min_lim_lbl      = QLabel("El min:")
    el_min_lim_ledit    = QLineEdit()
    fl_sublayout_row3.addWidget(el_min_lim_lbl)
    fl_sublayout_row3.addWidget(el_min_lim_ledit)

    # fl_sublayout_row4
    fl_sublayout_row4   = QHBoxLayout()
    el_max_lim_lbl      = QLabel("El max:")
    el_max_lim_ledit    = QLineEdit()
    fl_sublayout_row4.addWidget(el_max_lim_lbl)
    fl_sublayout_row4.addWidget(el_max_lim_ledit)
     
    # Toplevel layout of frame limits
    frame_limits_layout.addWidget(frame_limits_lbl)
    frame_limits_layout.addWidget(frame_pause_btn)
    frame_limits_layout.addLayout(fl_sublayout_row1)
    frame_limits_layout.addLayout(fl_sublayout_row2)
    frame_limits_layout.addLayout(fl_sublayout_row3)
    frame_limits_layout.addLayout(fl_sublayout_row4)

    # Add member variables
    # (not adding the sublayouts because we probably don't need them)
    thz_img_tab.frame_limits_lbl    = frame_limits_lbl
    thz_img_tab.frame_pause_btn     = frame_pause_btn
    thz_img_tab.az_min_lim_lbl      = az_min_lim_lbl
    thz_img_tab.az_min_lim_ledit    = az_min_lim_ledit
    thz_img_tab.az_max_lim_lbl      = az_max_lim_lbl
    thz_img_tab.az_max_lim_ledit    = az_max_lim_ledit
    thz_img_tab.el_min_lim_lbl      = el_min_lim_lbl
    thz_img_tab.el_min_lim_ledit    = el_min_lim_ledit
    thz_img_tab.el_max_lim_lbl      = el_max_lim_lbl
    thz_img_tab.el_max_lim_ledit    = el_max_lim_ledit



    ####################################################################
    # Final layout structure (two columns)
    ####################################################################

    main_layout = QHBoxLayout(thz_img_tab)

    # left side widgets
    left_layout.addLayout(thz_img_tab.thz_image_obj) 
    left_layout.addWidget(proc_cfg_tab_widget)

    # right side widgets 
    #right_layout.addWidget(update_btn)
    right_layout.addLayout(thresh_grid_layout)
    right_layout.addLayout(contr_grid_layout)
    right_layout.addLayout(pkwdth_grid_layout) 
    right_layout.addLayout(rc_grid_layout)
    right_layout.addLayout(cs_grid_layout)
    right_layout.addLayout(cmap_layout)
    right_layout.addLayout(frame_limits_layout)

    # the second argument somehow changes the porprtion each layout 
    # takes in horizontal space.  It is confusing, using the age-old
    # guess-and-check method
    main_layout.addLayout(left_layout, 25)
    main_layout.addLayout(right_layout, 15)

    thz_img_tab.left_layout    = left_layout
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
        thz_tab.azi_hyst_fs_ledit.editingFinished.connect(
            lambda: s.ledit_update(thz_tab.azi_hyst_fs_ledit, 
            "turn_hyst", float))
        thz_tab.azi_marg_fs_ledit.editingFinished.connect(
            lambda: s.ledit_update(thz_tab.azi_marg_fs_ledit, 
            "turn_az_margin", float))
        thz_tab.num_rng_fs_ledit.editingFinished.connect(
            lambda: s.ledit_update(thz_tab.num_rng_fs_ledit, 
            "accum_rangelines_thresh", int))

        thz_tab.daq_num_rng_fs_ledit.editingFinished.connect(
            lambda: s.ledit_update(thz_tab.daq_num_rng_fs_ledit, 
            "daq_num_rangelines", int))

        thz_tab.tot_frac_fs_ledit.editingFinished.connect(
            lambda: s.ledit_update(thz_tab.tot_frac_fs_ledit, 
            "fraction_filled_thresh", float))

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
        thz_tab.rc_ledit_min.textChanged.connect(
            lambda: s.ledit_update(thz_tab.rc_ledit_min, 
            "min_range", float))
        thz_tab.rc_ledit_max.textChanged.connect(
            lambda: s.ledit_update(thz_tab.rc_ledit_max, 
            "max_range", float))
        thz_tab.cs_ledit_min.textChanged.connect(
            lambda: s.ledit_update(thz_tab.cs_ledit_min, 
            "color_scale_min", float))
        thz_tab.cs_ledit_max.textChanged.connect(
            lambda: s.ledit_update(thz_tab.cs_ledit_max, 
            "color_scale_max", float))

        thz_tab.az_min_lim_ledit.editingFinished.connect(
            lambda: s.ledit_update(thz_tab.az_min_lim_ledit, 
            "min_az", float))
        thz_tab.az_max_lim_ledit.editingFinished.connect(
            lambda: s.ledit_update(thz_tab.az_max_lim_ledit, 
            "max_az", float))
        thz_tab.el_min_lim_ledit.editingFinished.connect(
            lambda: s.ledit_update(thz_tab.el_min_lim_ledit, 
            "min_el", float))
        thz_tab.el_max_lim_ledit.editingFinished.connect(
            lambda: s.ledit_update(thz_tab.el_max_lim_ledit, 
            "max_el", float))


        # QRadioButtons
        thz_tab.file_src_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.file_src_rbut, 
            "dat_file", "data_src"))

        thz_tab.file_src_rbut.toggled.connect(
            lambda: thz_tab.update_data_src_status("PROC_FILE"))

        thz_tab.daq_src_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.daq_src_rbut, 
            "daq", "data_src"))

        thz_tab.daq_src_rbut.toggled.connect(
            lambda: thz_tab.update_data_src_status("NOT_CONNECTED"))


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

        thz_tab.num_oversamp_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.num_oversamp_rbut, 
            "num_oversamp_plot", "peak_selection"))
        thz_tab.num_oversamp_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.num_oversamp_rbut, 
            "num_oversamp_plot", "plot_style"))

        thz_tab.integ_pwr_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.integ_pwr_rbut, 
            "integ_power_plot", "peak_selection"))
        thz_tab.integ_pwr_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.integ_pwr_rbut, 
            "integ_power_plot", "plot_style"))

        thz_tab.point_cloud_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.point_cloud_rbut, 
            "point_cloud_plot", "peak_selection"))
        thz_tab.point_cloud_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.point_cloud_rbut, 
            "point_cloud_plot", "plot_style"))

        thz_tab.azi_turn_fs_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.azi_turn_fs_rbut, 
            "azimuth_turnaround", "frame_style"))
        thz_tab.num_rng_fs_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.num_rng_fs_rbut, 
            "accum_rangelines", "frame_style"))
        thz_tab.col_frac_fs_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.col_frac_fs_rbut, 
            "fraction_col_filled", "frame_style"))
        thz_tab.pix_frac_fs_rbut.toggled.connect(
            lambda: s.rbut_update(thz_tab.pix_frac_fs_rbut, 
            "fraction_pix_filled", "frame_style"))

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



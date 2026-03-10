# This file only contains widget generation and layout along with some parameter 
# settings of widgets (e.g. read-only for a QLineEdit widget) for the ConfigTab
# 
# Signals and slots should not be assigned here.  The purpose of this file is 
# to make the ConfigTab file much cleaner and more concise
#

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
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
    QScrollArea,
)



def build_config_tab(cfg_tab):
    """
    builds up the initial set of GUI objects and the layout of the GUI for 
    the ConfigTab along with some default parameters and adds them to the 
    cfg_tab object
    """
    # NOTE: Need to add the number of rangelines being processed per call 
    # to the daq grabbing function here.  Since it shouldn't really be 
    # something that changes all that much

    cfg_tab_contents    = QWidget()
    main_layout         = QVBoxLayout()


    ####################################################################
    # Second row of widgets on this tab page
    #
    row2_layout = QHBoxLayout()
    load_cfg_btn = QPushButton("Load Config\nFile")
    save_cfg_btn = QPushButton("Save Config\nFile")
    save_dflt_cfg_btn = QPushButton("Save New\nDefault Config")
    load_dflt_cfg_btn = QPushButton("Load\nDefault Config")


    # [DISABLE FOR NOW] make a mini-vertical layout for this last piece
    #row2_sublayout = QVBoxLayout()
    #cfg_file_loaded_desc_lbl = QLabel("Current Config File Loaded")
    #cfg_file_loaded_label = QLabel("")
    #row2_sublayout.addWidget(cfg_file_loaded_desc_lbl)
    #row2_sublayout.addWidget(cfg_file_loaded_label)

    # layout
    row2_layout.addWidget(load_cfg_btn)
    row2_layout.addWidget(save_cfg_btn)
    row2_layout.addWidget(save_dflt_cfg_btn)
    row2_layout.addWidget(load_dflt_cfg_btn)
    #row2_layout.addLayout(row2_sublayout)

    # add member variables
    cfg_tab.load_cfg_btn                = load_cfg_btn
    cfg_tab.save_cfg_btn                = save_cfg_btn
    cfg_tab.save_dflt_cfg_btn           = save_dflt_cfg_btn
    cfg_tab.load_dflt_cfg_btn           = load_dflt_cfg_btn
    #cfg_tab.cfg_file_loaded_desc_lbl    = cfg_file_loaded_desc_lbl
    #cfg_tab.cfg_file_loaded_label       = cfg_file_loaded_label


    ####################################################################
    # second and a half row of widgets on this tab page
    #
    row2pt5_layout      = QHBoxLayout()
    curr_cfg_val_lbl    = QLabel("Current Config File Loaded:")
    curr_cfg_val_ledit  = QLineEdit("")
    curr_cfg_val_ledit.setReadOnly(True)

    # layout
    row2pt5_layout.addWidget(curr_cfg_val_lbl)
    row2pt5_layout.addWidget(curr_cfg_val_ledit)

    # add member variables
    cfg_tab.curr_cfg_val_lbl   = curr_cfg_val_lbl
    cfg_tab.curr_cfg_val_ledit = curr_cfg_val_ledit



    ####################################################################
    # Third row of widgets on this tab page
    # TODO I will need to link all these lineedit objects to an update
    # function to ensure that the processing flags as "stale" if you 
    # change one of these things
    #
    row3_layout         = QHBoxLayout()
    el_s0_strt_lbl      = QLabel("Elevation Side 0 Start:")
    el_s0_strt_ledit    = QLineEdit()
    el_s0_end_lbl       = QLabel("Elevation Side 0 End:")
    el_s0_end_ledit     = QLineEdit()

    # layout
    row3_layout.addWidget(el_s0_strt_lbl)
    row3_layout.addWidget(el_s0_strt_ledit)
    row3_layout.addWidget(el_s0_end_lbl)
    row3_layout.addWidget(el_s0_end_ledit)

    # add member variables
    cfg_tab.el_s0_strt_lbl     = el_s0_strt_lbl
    cfg_tab.el_s0_strt_ledit   = el_s0_strt_ledit
    cfg_tab.el_s0_end_lbl      = el_s0_end_lbl
    cfg_tab.el_s0_end_ledit    = el_s0_end_ledit



    ####################################################################
    # Fourth row of widgets on this tab page
    # TODO I will need to link all these lineedit objects to an update
    # function to ensure that the processing flags as "stale" if you 
    # change one of these things
    #
    row4_layout         = QHBoxLayout()
    el_s1_strt_lbl      = QLabel("Elevation Side 1 Start:")
    el_s1_strt_ledit    = QLineEdit()
    el_s1_end_lbl       = QLabel("Elevation Side 1 End:")
    el_s1_end_ledit     = QLineEdit()

    # layout
    row4_layout.addWidget(el_s1_strt_lbl)
    row4_layout.addWidget(el_s1_strt_ledit)
    row4_layout.addWidget(el_s1_end_lbl)
    row4_layout.addWidget(el_s1_end_ledit)

    # add member variables
    cfg_tab.el_s1_strt_lbl     = el_s1_strt_lbl
    cfg_tab.el_s1_strt_ledit   = el_s1_strt_ledit
    cfg_tab.el_s1_end_lbl      = el_s1_end_lbl
    cfg_tab.el_s1_end_ledit    = el_s1_end_ledit


    ####################################################################
    # Fifth row of widgets on this tab page
    # TODO I will need to link all these lineedit objects to an update
    # function to ensure that the processing flags as "stale" if you 
    # change one of these things
    #
    row5_layout         = QHBoxLayout()
    process_side0_chkb  = QCheckBox()
    process_side0_chkb.setText("Process Side 0:")
    process_side1_chkb  = QCheckBox()
    process_side1_chkb.setText("Process Side 1:")

    # layout
    row5_layout.addWidget(process_side0_chkb)
    row5_layout.addWidget(process_side1_chkb)

    # add member variables
    cfg_tab.process_side0_chkb = process_side0_chkb
    cfg_tab.process_side1_chkb = process_side1_chkb


    ####################################################################
    # Sixth row of widgets on this tab page
    # TODO I will need to link all these lineedit objects to an update
    # function to ensure that the processing flags as "stale" if you 
    # change one of these things
    #
    row6_layout         = QHBoxLayout()
    num_elev_pix_lbl    = QLabel("Num Elevation Pixels:")
    num_elev_pix_ledit  = QLineEdit()
    num_azi_pix_lbl     = QLabel("Num Azimuth Pixels:")
    num_azi_pix_ledit   = QLineEdit()

    # layout
    row6_layout.addWidget(num_elev_pix_lbl)
    row6_layout.addWidget(num_elev_pix_ledit)
    row6_layout.addWidget(num_azi_pix_lbl)
    row6_layout.addWidget(num_azi_pix_ledit)


    # add member variables
    cfg_tab.num_elev_pix_lbl   = num_elev_pix_lbl
    cfg_tab.num_elev_pix_ledit = num_elev_pix_ledit
    cfg_tab.num_azi_pix_lbl    = num_azi_pix_lbl
    cfg_tab.num_azi_pix_ledit  = num_azi_pix_ledit


    ####################################################################
    # Seventh row of widgets on this tab page
    # TODO I will need to link all these lineedit objects to an update
    # function to ensure that the processing flags as "stale" if you 
    # change one of these things
    #
    row7_layout         = QHBoxLayout()
    fft_len_lbl         = QLabel("FFT Length*:")
    fft_len_ledit       = QLineEdit()
    num_noise_pts_lbl   = QLabel("Num samples for \nnoise floor calc:")
    num_noise_pts_ledit = QLineEdit()

    # layout
    row7_layout.addWidget(fft_len_lbl)
    row7_layout.addWidget(fft_len_ledit)
    row7_layout.addWidget(num_noise_pts_lbl)
    row7_layout.addWidget(num_noise_pts_ledit)

    # add member variables
    cfg_tab.fft_len_lbl            = fft_len_lbl
    cfg_tab.fft_len_ledit          = fft_len_ledit
    cfg_tab.num_noise_pts_lbl      = num_noise_pts_lbl
    cfg_tab.num_noise_pts_ledit    = num_noise_pts_ledit


    ####################################################################
    # Eighth row of widgets on this tab page
    #
    row8_layout         = QHBoxLayout()
    fft_len_note_lbl    = QLabel("*only used on\ntime-domain input data")
    cfg_tab.fft_len_note_lbl    = fft_len_note_lbl

    inv_range_chkb = QCheckBox()
    inv_range_chkb.setText("Invert Range       ")

    blank_cfg_lbl = QLabel("                ")
    noise_frac_lbl = QLabel("Noise fraction start:")
    noise_frac_ledit = QLineEdit()

    # layout
    row8_layout.addWidget(fft_len_note_lbl)
    row8_layout.addWidget(inv_range_chkb)
    row8_layout.addWidget(blank_cfg_lbl)
    row8_layout.addWidget(noise_frac_lbl)
    row8_layout.addWidget(noise_frac_ledit)

    # add member variables
    cfg_tab.blank_cfg_lbl       = blank_cfg_lbl
    cfg_tab.inv_range_chkb      = inv_range_chkb
    cfg_tab.noise_frac_lbl      = noise_frac_lbl
    cfg_tab.noise_frac_ledit    = noise_frac_ledit


    ####################################################################
    # Eight point 3rd row of widgets on this tab page
    #
    row8pt3_layout   = QHBoxLayout()
    data_format_lbl  = QLabel("Input Data Format:")
    df_time_domin_rbut  = QRadioButton()
    df_time_domin_rbut.setText("Time Domain")

    df_freq_domin_rbut  = QRadioButton()
    df_freq_domin_rbut.setText("Frequency Domain")

    df_power_domin_rbut = QRadioButton()
    df_power_domin_rbut.setText("Power Domain")

    # layout
    row8pt3_layout.addWidget(data_format_lbl)
    row8pt3_layout.addWidget(df_time_domin_rbut)
    row8pt3_layout.addWidget(df_freq_domin_rbut)
    row8pt3_layout.addWidget(df_power_domin_rbut)

    # add member variables
    cfg_tab.data_format_lbl     = data_format_lbl
    cfg_tab.df_time_domin_rbut  = df_time_domin_rbut
    cfg_tab.df_freq_domin_rbut  = df_freq_domin_rbut
    cfg_tab.df_power_domin_rbut = df_power_domin_rbut


    ####################################################################
    # Eight point 4th row of widgets on this tab page
    #
    row8pt4_layout      = QHBoxLayout()
    chirp_span_lbl      = QLabel("Chirp Span (GHz):")
    chirp_span_ledit    = QLineEdit()
    calc_wt_sum_chkb    = QCheckBox()
    calc_wt_sum_chkb.setText("Calculate Weighted Sum   ")
    dead_pix_lbl        = QLabel("Dead Pixel Replacement Value:")
    dead_pix_ledit      = QLineEdit()

    # layout
    row8pt4_layout.addWidget(chirp_span_lbl)
    row8pt4_layout.addWidget(chirp_span_ledit)
    row8pt4_layout.addWidget(calc_wt_sum_chkb)
    row8pt4_layout.addWidget(dead_pix_lbl)
    row8pt4_layout.addWidget(dead_pix_ledit)

    # add member variables
    cfg_tab.chirp_span_lbl      = chirp_span_lbl
    cfg_tab.chirp_span_ledit    = chirp_span_ledit
    cfg_tab.calc_wt_sum_chkb    = calc_wt_sum_chkb
    cfg_tab.dead_pix_lbl        = dead_pix_lbl
    cfg_tab.dead_pix_ledit      = dead_pix_ledit



    ####################################################################
    # Eighth and a halfth row of widgets on this tab page
    #
    row8pt5_layout   = QHBoxLayout()
    fsamp_freq_lbl   = QLabel("Sampling Frequency (MSPS):")
    fsamp_freq_ledit = QLineEdit()

    chirp_time_us_lbl   = QLabel("Chirp time \n(in microseconds)")
    chirp_time_us_ledit = QLineEdit()

    # layout
    row8pt5_layout.addWidget(fsamp_freq_lbl)
    row8pt5_layout.addWidget(fsamp_freq_ledit)

    row8pt5_layout.addWidget(chirp_time_us_lbl)
    row8pt5_layout.addWidget(chirp_time_us_ledit)

    # add member variables
    cfg_tab.fsamp_freq_lbl     = fsamp_freq_lbl
    cfg_tab.fsamp_freq_ledit   = fsamp_freq_ledit

    cfg_tab.chirp_time_us_lbl     = chirp_time_us_lbl
    cfg_tab.chirp_time_us_ledit   = chirp_time_us_ledit


    ####################################################################
    # Eight point 6th row of widgets on this tab page
    # (Power integration values have been moved to rangecut in THzImageTab)
    row8pt6_layout      = QHBoxLayout()

    enable_ch0_chkb    = QCheckBox()
    enable_ch0_chkb.setText("Enable Channel 0:")
    enable_ch1_chkb    = QCheckBox()
    enable_ch1_chkb.setText("Enable Channel 1:")

    # layout
    row8pt6_layout.addWidget(enable_ch0_chkb)
    row8pt6_layout.addWidget(enable_ch1_chkb)

    # add member variables
    cfg_tab.enable_ch0_chkb = enable_ch0_chkb
    cfg_tab.enable_ch1_chkb = enable_ch1_chkb


    ####################################################################
    # Eight point 7th row of widgets on this tab page
    #
    row8pt7_layout          = QHBoxLayout()
    el_offset0_lbl          = QLabel("El Mirror Side 0 Offset:")
    #rough_pwr_thresh_lbl    = QLabel("Rough power threshold (dB):")
    el_offset0_ledit        = QLineEdit()
    #rough_pwr_thresh_ledit  = QLineEdit()

    el_offset1_lbl          = QLabel("El Mirror Side 1 Offset:")
    #half_peak_width_lbl     = QLabel("Half peak width\n(in fft bins):")
    el_offset1_ledit        = QLineEdit()
    #half_peak_width_ledit   = QLineEdit()

    # layout
    row8pt7_layout.addWidget(el_offset0_lbl)
    row8pt7_layout.addWidget(el_offset0_ledit)
    row8pt7_layout.addWidget(el_offset1_lbl)
    row8pt7_layout.addWidget(el_offset1_ledit)


    # add member variables
    cfg_tab.el_offset0_lbl   = el_offset0_lbl
    cfg_tab.el_offset0_ledit = el_offset0_ledit
    cfg_tab.el_offset1_lbl    = el_offset1_lbl
    cfg_tab.el_offset1_ledit  = el_offset1_ledit


    ####################################################################
    # Eight point 8th row of widgets on this tab page
    #
    row8pt8_layout      = QHBoxLayout()
    center_rangeval_lbl   = QLabel("Center range value (cm):")
    center_rangeval_ledit = QLineEdit()
    dec_val_lbl   = QLabel("Decimation Value: ")
    dec_val_ledit = QLineEdit()

    # layout
    row8pt8_layout.addWidget(center_rangeval_lbl)
    row8pt8_layout.addWidget(center_rangeval_ledit)
    row8pt8_layout.addWidget(dec_val_lbl)
    row8pt8_layout.addWidget(dec_val_ledit)

    # add member variables
    cfg_tab.center_rangeval_lbl     = center_rangeval_lbl
    cfg_tab.center_rangeval_ledit   = center_rangeval_ledit
    cfg_tab.dec_val_lbl             = dec_val_lbl
    cfg_tab.dec_val_ledit           = dec_val_ledit



    ####################################################################
    # Eight point 9th row of widgets on this tab page
    #
    row8pt9_layout      = QHBoxLayout()
    ch0_offset_lbl     = QLabel("Channel 0 Az Offset\n(encoder counts):")
    ch0_offset_ledit   = QLineEdit()
    ch1_offset_lbl     = QLabel("Channel 1 Az Offset\n(encoder counts):")
    ch1_offset_ledit   = QLineEdit()

    # layout
    row8pt9_layout.addWidget(ch0_offset_lbl)
    row8pt9_layout.addWidget(ch0_offset_ledit)
    row8pt9_layout.addWidget(ch1_offset_lbl)
    row8pt9_layout.addWidget(ch1_offset_ledit)

    # add member variables
    cfg_tab.ch0_offset_lbl    =   ch0_offset_lbl
    cfg_tab.ch0_offset_ledit  =   ch0_offset_ledit
    cfg_tab.ch1_offset_lbl    =   ch1_offset_lbl
    cfg_tab.ch1_offset_ledit  =   ch1_offset_ledit


    ####################################################################
    # Row for loading an external HDF5 data cube
    #
    row_h5_layout          = QHBoxLayout()
    load_h5_btn            = QPushButton("Load External\nHDF5 Cube")

    row_h5_sub_layout      = QVBoxLayout()
    curr_h5_desc_lbl       = QLabel("Current HDF5 file loaded:")
    curr_h5_val_ledit      = QLineEdit("")
    curr_h5_val_ledit.setReadOnly(True)

    row_h5_sub_layout.addWidget(curr_h5_desc_lbl)
    row_h5_sub_layout.addWidget(curr_h5_val_ledit)

    row_h5_layout.addWidget(load_h5_btn)
    row_h5_layout.addLayout(row_h5_sub_layout)

    cfg_tab.load_h5_btn         = load_h5_btn
    cfg_tab.curr_h5_desc_lbl    = curr_h5_desc_lbl
    cfg_tab.curr_h5_val_ledit   = curr_h5_val_ledit

    main_layout.addLayout(row_h5_layout)

    # final layout structure
    main_layout.addLayout(row2_layout)
    main_layout.addLayout(row2pt5_layout)
    main_layout.addLayout(row3_layout)
    main_layout.addLayout(row4_layout)
    main_layout.addLayout(row5_layout)
    main_layout.addLayout(row6_layout)
    main_layout.addLayout(row7_layout)
    main_layout.addLayout(row8_layout)
    main_layout.addLayout(row8pt3_layout)
    main_layout.addLayout(row8pt4_layout)
    main_layout.addLayout(row8pt5_layout)
    main_layout.addLayout(row8pt6_layout)
    main_layout.addLayout(row8pt7_layout)
    main_layout.addLayout(row8pt8_layout)
    main_layout.addLayout(row8pt9_layout)

    

    cfg_tab.main_layout = main_layout
    cfg_tab.row2_layout = row2_layout
    cfg_tab.row2pt5_layout = row2pt5_layout
    cfg_tab.row3_layout = row3_layout
    cfg_tab.row4_layout = row4_layout
    cfg_tab.row5_layout = row5_layout
    cfg_tab.row6_layout = row6_layout
    cfg_tab.row7_layout = row7_layout
    cfg_tab.row8_layout = row8_layout
    cfg_tab.row8pt3_layout = row8pt3_layout
    cfg_tab.row8pt4_layout = row8pt4_layout
    cfg_tab.row8pt5_layout = row8pt5_layout
    cfg_tab.row8pt6_layout = row8pt6_layout
    cfg_tab.row8pt7_layout = row8pt7_layout
    cfg_tab.row8pt8_layout = row8pt8_layout
    cfg_tab.row8pt9_layout = row8pt9_layout

    cfg_tab_contents.setLayout(main_layout)


    ####################################################################
    # Scrollbar
    #
    # cfg_tab_obj is the QScrollArea
    cfg_tab.setWidgetResizable(True)
    cfg_tab.setWidget(cfg_tab_contents)





# this is just a container for the callback functions that call "update_config"
# properly when data changes in each of the config GUI objects
# it's tedious and long but really doesn't provide much novel 
# information apart from the associated cfg_dict key for each config object
class setup_config_callbacks:

    def __init__(s, cfg_tab, update_config):
        s.update_config = update_config
        s.cfg_tab = cfg_tab

        # QLineEdits
        cfg_tab.el_s0_strt_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.el_s0_strt_ledit, 
            "el_side_0_start", float))
        cfg_tab.el_s0_end_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.el_s0_end_ledit,
            "el_side_0_end", float))
        cfg_tab.el_s1_strt_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.el_s1_strt_ledit,
            "el_side_1_start", float))
        cfg_tab.el_s1_end_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.el_s1_end_ledit,
            "el_side_1_end", float))
        cfg_tab.num_elev_pix_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.num_elev_pix_ledit, 
            "ylen", int))
        cfg_tab.num_azi_pix_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.num_azi_pix_ledit,
            "xlen", int))
        cfg_tab.fft_len_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.fft_len_ledit,
            "fft_len", int))
        cfg_tab.num_noise_pts_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.num_noise_pts_ledit, 
            "num_noise_pts", int))
        cfg_tab.noise_frac_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.noise_frac_ledit,
            "noise_start_frac", float))

        cfg_tab.chirp_span_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.chirp_span_ledit,
            "chirp_span", float, 1e9))
        cfg_tab.chirp_time_us_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.chirp_time_us_ledit, 
            "chirp_time", float, 1e-6))

        cfg_tab.dead_pix_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.dead_pix_ledit,
            "dead_pix_val", float))
        cfg_tab.fsamp_freq_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.fsamp_freq_ledit,
            "fs_adc", float, 1e6))

        cfg_tab.el_offset0_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.el_offset0_ledit,
            "el_offset0", float))
        cfg_tab.el_offset1_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.el_offset1_ledit,
            "el_offset1", float))

        cfg_tab.center_rangeval_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.center_rangeval_ledit, 
            "center_rangeval", float))
        cfg_tab.dec_val_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.dec_val_ledit,
            "dec_val", int))

        cfg_tab.ch0_offset_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.ch0_offset_ledit,
            "ch0_offset", float))
        cfg_tab.ch1_offset_ledit.editingFinished.connect(
            lambda: s.ledit_update(cfg_tab.ch1_offset_ledit,
            "ch1_offset", float))


        # QCheckBoxes
        cfg_tab.process_side0_chkb.stateChanged.connect(
            lambda: s.chkbox_update(cfg_tab.process_side0_chkb,
            "disable_el_side0", True))

        cfg_tab.process_side1_chkb.stateChanged.connect(
            lambda: s.chkbox_update(cfg_tab.process_side1_chkb,
            "disable_el_side1", True))


        cfg_tab.inv_range_chkb.stateChanged.connect(
            lambda: s.chkbox_update(cfg_tab.inv_range_chkb,
            "invert_range"))

        cfg_tab.calc_wt_sum_chkb.stateChanged.connect(
            lambda: s.chkbox_update(cfg_tab.calc_wt_sum_chkb,
            "calc_weighted_sum"))

        cfg_tab.enable_ch0_chkb.stateChanged.connect(
            lambda: s.chkbox_update(cfg_tab.enable_ch0_chkb,
            "ch0_en"))

        cfg_tab.enable_ch1_chkb.stateChanged.connect(
            lambda: s.chkbox_update(cfg_tab.enable_ch1_chkb,
            "ch1_en"))


        # QRadioButtons
        cfg_tab.df_time_domin_rbut.toggled.connect(
            lambda: s.rbut_update(cfg_tab.df_time_domin_rbut, 
            "time_domain", "data_format_in"))

        cfg_tab.df_freq_domin_rbut.toggled.connect(
            lambda: s.rbut_update(cfg_tab.df_freq_domin_rbut, 
            "fft", "data_format_in"))

        cfg_tab.df_power_domin_rbut.toggled.connect(
            lambda: s.rbut_update(cfg_tab.df_power_domin_rbut, 
            "power_spectrum", "data_format_in"))


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
        

    def chkbox_update(s, chkb_obj, key, invert=False):
        if invert:
            val = not bool(chkb_obj.isChecked())
        else:
            val = bool(chkb_obj.isChecked())

        new_cfg_dict = OrderedDict()
        new_cfg_dict[key] = val
        s.update_config(new_cfg_dict)
        

    #def data_format_update(s, cfg_tab, key):
    #    if cfg_tab.df_time_domin_rbut.isChecked():
    #        val = "time_domain"

    #    elif cfg_tab.df_freq_domin_rbut.isChecked():
    #        val = "fft"

    #    elif cfg_tab.df_power_domin_rbut.isChecked():
    #        val = "power_spectrum"

    #    else:
    #        raise Exception("Invalid data format")

    #    new_cfg_dict = OrderedDict()
    #    new_cfg_dict[key] = val
    #    s.update_config(new_cfg_dict)


    def rbut_update(s, rbut_obj, val_if_en, key):
        if rbut_obj.isChecked():
            new_cfg_dict = OrderedDict()
            new_cfg_dict[key] = val_if_en
            s.update_config(new_cfg_dict)




# This file only contains widget generation and layout along with some parameter 
# settings of widgets (e.g. read-only for a QLineEdit widget) for the ConfigTab
# 
# Signals and slots should not be assigned here.  The purpose of this file is 
# to make the ConfigTab file much cleaner and more concise
#

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt

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



def build_config_tab(cfg_tab, mainwin_obj):
    """
    builds up the initial set of GUI objects and the layout of the GUI for 
    the ConfigTab along with some default parameters and adds them to the 
    cfg_tab object
    """
    # NOTE: Need to add the number of rangelines being processed per call 
    # to the daq grabbing function here.  Since it shouldn't really be 
    # something that changes all that much

    cfg_tab_contents = QWidget()
    main_layout = QVBoxLayout()

    ####################################################################
    # First row of widgets on this tab page
    #
    row1_layout = QHBoxLayout()
    autoload_btn = QPushButton("Autoload")
    autoload_desc_text  = "Automatically loads\n"
    autoload_desc_text += "the latest dat file saved"
    autoload_desc_label = QLabel(autoload_desc_text)

    # layout
    row1_layout.addWidget(autoload_btn)
    row1_layout.addWidget(autoload_desc_label)

    # add member variables
    cfg_tab.autoload_btn = autoload_btn
    cfg_tab.autoload_desc_text = autoload_desc_text
    cfg_tab.autoload_desc_label = autoload_desc_label


    ####################################################################
    # Second row of widgets on this tab page
    #
    row2_layout = QHBoxLayout()
    load_cfg_btn = QPushButton("Load Config\nFile")
    save_cfg_btn = QPushButton("Save Config\nFile")
    save_dflt_cfg_btn = QPushButton("Save New\nDefault Config")
    load_dflt_cfg_btn = QPushButton("Load\nDefault Config")


    # make a mini-vertical layout for this last piece
    row2_sublayout = QVBoxLayout()
    cfg_file_loaded_desc_lbl = QLabel("Current Config File Loaded")
    cfg_file_loaded_label = QLabel("")
    row2_sublayout.addWidget(cfg_file_loaded_label)
    row2_sublayout.addWidget(cfg_file_loaded_label)

    # layout
    row2_layout.addWidget(load_cfg_btn)
    row2_layout.addWidget(save_cfg_btn)
    row2_layout.addWidget(save_dflt_cfg_btn)
    row2_layout.addWidget(load_dflt_cfg_btn)
    row2_layout.addLayout(row2_sublayout)

    # add member variables
    cfg_tab.load_cfg_btn                = load_cfg_btn
    cfg_tab.save_cfg_btn                = save_cfg_btn
    cfg_tab.save_dflt_cfg_btn           = save_dflt_cfg_btn
    cfg_tab.load_dflt_cfg_btn           = load_dflt_cfg_btn
    cfg_tab.cfg_file_loaded_desc_lbl    = cfg_file_loaded_desc_lbl
    cfg_tab.cfg_file_loaded_label       = cfg_file_loaded_label


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
    fft_len_note_lbl    = QLabel("*only used on time-domain input data")
    row8_layout.addWidget(fft_len_note_lbl)
    cfg_tab.fft_len_note_lbl    = fft_len_note_lbl

    max_avgs_lbl = QLabel("Maximum Powspec/FFT Averages")
    max_avgs_ledit = QLineEdit()
    row8_layout.addWidget(max_avgs_lbl)
    row8_layout.addWidget(max_avgs_ledit)
    cfg_tab.max_avgs_lbl    = max_avgs_lbl
    cfg_tab.max_avgs_ledit  = max_avgs_ledit

    fft_avg_rbut   = QRadioButton()
    fft_avg_rbut.setText("Average in FFT Domain")
    row8_layout.addWidget(fft_avg_rbut)
    cfg_tab.fft_avg_rbut    = fft_avg_rbut

    pwr_avg_rbut   = QRadioButton()
    pwr_avg_rbut.setText("Average in Power Domain")
    row8_layout.addWidget(pwr_avg_rbut)
    cfg_tab.pwr_avg_rbut    = pwr_avg_rbut


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
    rough_pwr_thresh_lbl    = QLabel("Rough power threshold (dB):")
    rough_pwr_thresh_ledit  = QLineEdit()

    half_peak_width_lbl     = QLabel("Half peak width\n(in fft bins):")
    half_peak_width_ledit   = QLineEdit()

    # layout
    row8pt7_layout.addWidget(rough_pwr_thresh_lbl)
    row8pt7_layout.addWidget(rough_pwr_thresh_ledit)
    row8pt7_layout.addWidget(half_peak_width_lbl)
    row8pt7_layout.addWidget(half_peak_width_ledit)


    # add member variables
    cfg_tab.rough_pwr_thresh_lbl   = rough_pwr_thresh_lbl
    cfg_tab.rough_pwr_thresh_ledit = rough_pwr_thresh_ledit
    cfg_tab.half_peak_width_lbl    = half_peak_width_lbl
    cfg_tab.half_peak_width_ledit  = half_peak_width_ledit


    ####################################################################
    # Eight point 8th row of widgets on this tab page
    #
    row8pt8_layout      = QHBoxLayout()
    center_rangeval_lbl   = QLabel("Center range value (cm):")
    center_rangeval_ledit = QLineEdit()

    # layout
    row8pt8_layout.addWidget(center_rangeval_lbl)
    row8pt8_layout.addWidget(center_rangeval_ledit)

    # add member variables
    cfg_tab.center_rangeval_lbl   = center_rangeval_lbl
    cfg_tab.center_rangeval_ledit = center_rangeval_ledit



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
    # Ninth row of widgets on this tab page
    # TODO I will need to link all these lineedit objects to an update
    # function to ensure that the processing flags as "stale" if you 
    # change one of these things
    #
    row9_layout          = QHBoxLayout()
    load_ch0_btn         = QPushButton("Load Ch 0 Data")
    load_latest_ch0_btn  = QPushButton("Load Latest\nCh 0 Data")

    # sub-layout to group these objects in the same row
    row9_sub_layout         = QVBoxLayout()
    curr_loaded0_desc_lbl   = QLabel("Current Ch 0 file loaded:")
    curr_loaded0_val_ledit  = QLineEdit("")
    curr_loaded0_val_ledit.setReadOnly(True)

    # layout
    row9_sub_layout.addWidget(curr_loaded0_desc_lbl)
    row9_sub_layout.addWidget(curr_loaded0_val_ledit)

    row9_layout.addWidget(load_ch0_btn)
    row9_layout.addWidget(load_latest_ch0_btn)
    row9_layout.addLayout(row9_sub_layout)

    # add member variables
    cfg_tab.load_ch0_btn           = load_ch0_btn
    cfg_tab.load_latest_ch0_btn    = load_latest_ch0_btn
    cfg_tab.curr_loaded0_desc_lbl  = curr_loaded0_desc_lbl
    cfg_tab.curr_loaded0_val_ledit = curr_loaded0_val_ledit


    ####################################################################
    # 9 point 1th row of widgets on this tab page
    #
    row9pt1_layout      = QHBoxLayout()
    load_ch1_btn         = QPushButton("Load Ch 1 Data")
    load_latest_ch1_btn  = QPushButton("Load Latest\nCh 1 Data")

    # sub-layout to group these objects in the same row
    row9pt1_sub_layout         = QVBoxLayout()
    curr_loaded1_desc_lbl   = QLabel("Current Ch 1 file loaded:")
    curr_loaded1_val_ledit  = QLineEdit("")
    curr_loaded1_val_ledit.setReadOnly(True)

    # layout
    row9pt1_sub_layout.addWidget(curr_loaded1_desc_lbl)
    row9pt1_sub_layout.addWidget(curr_loaded1_val_ledit)

    row9pt1_layout.addWidget(load_ch1_btn)
    row9pt1_layout.addWidget(load_latest_ch1_btn)
    row9pt1_layout.addLayout(row9pt1_sub_layout)

    # add member variables
    cfg_tab.load_ch1_btn           = load_ch1_btn
    cfg_tab.load_latest_ch1_btn    = load_latest_ch1_btn
    cfg_tab.curr_loaded1_desc_lbl  = curr_loaded1_desc_lbl
    cfg_tab.curr_loaded1_val_ledit = curr_loaded1_val_ledit


    ####################################################################
    # 9 point 2th row of widgets on this tab page
    #
    row9pt2_layout        = QVBoxLayout()
    proc_status_sublayout = QHBoxLayout()
    process_data_btn      = QPushButton("Process\nData Files")
    curr_dat_proc_lbl     = QLabel("Processing Status:                ")

    proc_status_sublayout.addWidget(process_data_btn)
    proc_status_sublayout.addWidget(curr_dat_proc_lbl)

    # processed data sublayouts
    ch0_proc_sublayout = QHBoxLayout()
    curr_ch0_proc_lbl = QLabel("Current Processed Ch 0 File:") 
    curr_ch0_proc_ledit = QLineEdit("")
    curr_ch0_proc_ledit.setReadOnly(True)
    ch0_proc_sublayout.addWidget(curr_ch0_proc_lbl)
    ch0_proc_sublayout.addWidget(curr_ch0_proc_ledit)

    ch1_proc_sublayout= QHBoxLayout()
    curr_ch1_proc_lbl = QLabel("Current Processed Ch 1 File:") 
    curr_ch1_proc_ledit = QLineEdit("")
    curr_ch1_proc_ledit.setReadOnly(True)
    ch1_proc_sublayout.addWidget(curr_ch1_proc_lbl)
    ch1_proc_sublayout.addWidget(curr_ch1_proc_ledit)


    # layout
    row9pt2_layout.addLayout(proc_status_sublayout)
    row9pt2_layout.addLayout(ch0_proc_sublayout)
    row9pt2_layout.addLayout(ch1_proc_sublayout)

    # add member variables
    cfg_tab.process_data_btn       = process_data_btn
    cfg_tab.curr_dat_proc_lbl      = curr_dat_proc_lbl
    cfg_tab.curr_ch0_proc_lbl     = curr_ch0_proc_lbl
    cfg_tab.curr_ch0_proc_ledit   = curr_ch0_proc_ledit
    cfg_tab.curr_ch1_proc_lbl     = curr_ch1_proc_lbl
    cfg_tab.curr_ch1_proc_ledit   = curr_ch1_proc_ledit


    ####################################################################
    # Tenth row of widgets on this tab page
    #
    row10_layout                = QHBoxLayout()
    fft_calc_in_rfsoc_desc_lbl  = QLabel("FFT Calc in RFSoC:") 
    fft_calc_in_rfsoc_val_lbl   = QLabel("") 

    pwr_calc_in_rfsoc_desc_lbl  = QLabel("Power Spectrum Calc in RFSoC:")
    pwr_calc_in_rfsoc_val_lbl   = QLabel("") 

    # layout
    row10_layout.addWidget(fft_calc_in_rfsoc_desc_lbl)
    row10_layout.addWidget(fft_calc_in_rfsoc_val_lbl)
    row10_layout.addWidget(pwr_calc_in_rfsoc_desc_lbl)
    row10_layout.addWidget(pwr_calc_in_rfsoc_val_lbl)


    # add member variables
    cfg_tab.fft_calc_in_rfsoc_desc_lbl = fft_calc_in_rfsoc_desc_lbl
    cfg_tab.fft_calc_in_rfsoc_val_lbl  = fft_calc_in_rfsoc_val_lbl
    cfg_tab.pwr_calc_in_rfsoc_desc_lbl = pwr_calc_in_rfsoc_desc_lbl
    cfg_tab.pwr_calc_in_rfsoc_val_lbl  = pwr_calc_in_rfsoc_val_lbl



    ####################################################################
    # Eleventh row of widgets on this tab page
    # 
    row11_layout         = QHBoxLayout()
    decimation_desc_lbl  = QLabel("Decimation Value:") 
    decimation_val_lbl   = QLabel("") 

    pulse_length_desc_lbl   = QLabel("Time/Freq Domain Points Per Pulse:") 
    pulse_length_val_lbl    = QLabel("") 

    # layout
    row11_layout.addWidget(decimation_desc_lbl)
    row11_layout.addWidget(decimation_val_lbl)
    row11_layout.addWidget(pulse_length_desc_lbl)
    row11_layout.addWidget(pulse_length_val_lbl)

    # add member variables
    cfg_tab.decimation_desc_lbl    = decimation_desc_lbl
    cfg_tab.decimation_val_lbl     = decimation_val_lbl
    cfg_tab.pulse_length_desc_lbl  = pulse_length_desc_lbl
    cfg_tab.pulse_length_val_lbl   = pulse_length_val_lbl

    



    ####################################################################
    # final layout structure
    #
    main_layout.addLayout(row1_layout)
    main_layout.addLayout(row2_layout)
    main_layout.addLayout(row2pt5_layout)
    main_layout.addLayout(row3_layout)
    main_layout.addLayout(row4_layout)
    main_layout.addLayout(row5_layout)
    main_layout.addLayout(row6_layout)
    main_layout.addLayout(row7_layout)
    main_layout.addLayout(row8_layout)
    main_layout.addLayout(row8pt5_layout)
    main_layout.addLayout(row8pt6_layout)
    main_layout.addLayout(row8pt7_layout)
    main_layout.addLayout(row8pt8_layout)
    main_layout.addLayout(row8pt9_layout)
    main_layout.addLayout(row9_layout)
    main_layout.addLayout(row9pt1_layout)
    main_layout.addLayout(row9pt2_layout)
    #main_layout.addLayout(row9pt3_layout)
    main_layout.addLayout(row10_layout)
    main_layout.addLayout(row11_layout)

    

    cfg_tab.main_layout = main_layout
    cfg_tab.row1_layout = row1_layout
    cfg_tab.row2_layout = row2_layout
    cfg_tab.row2pt5_layout = row2pt5_layout
    cfg_tab.row3_layout = row3_layout
    cfg_tab.row4_layout = row4_layout
    cfg_tab.row5_layout = row5_layout
    cfg_tab.row6_layout = row6_layout
    cfg_tab.row7_layout = row7_layout
    cfg_tab.row8_layout = row8_layout
    cfg_tab.row8pt5_layout = row8pt5_layout
    cfg_tab.row8pt6_layout = row8pt6_layout
    cfg_tab.row8pt7_layout = row8pt7_layout
    cfg_tab.row8pt8_layout = row8pt8_layout
    cfg_tab.row8pt9_layout = row8pt9_layout
    cfg_tab.row9_layout = row9_layout
    cfg_tab.row9pt1_layout = row9pt1_layout
    cfg_tab.row9pt2_layout = row9pt2_layout
    #cfg_tab.row9pt3_layout = row9pt3_layout
    cfg_tab.row10_layout = row10_layout
    cfg_tab.row11_layout = row11_layout

    cfg_tab_contents.setLayout(main_layout)


    ####################################################################
    # Scrollbar
    #
    # cfg_tab_obj is the QScrollArea
    cfg_tab.setWidgetResizable(True)
    cfg_tab.setWidget(cfg_tab_contents)



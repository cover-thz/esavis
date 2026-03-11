# This is the code that creates the spectrum plot object
# that is used by SingPixTab


import os
import sys
import numpy as np
import ipdb
os.environ["QT_API"] = "PySide6"

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from collections import OrderedDict

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


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

class AuxPlotCanvas(FigureCanvas):
    def __init__(s, parent=None, width=5, height=4, dpi=100):
        s.plt_fig = Figure(figsize=(width, height), dpi=dpi)
        s.plt_axes = s.plt_fig.add_subplot(111)
        super().__init__(s.plt_fig)

        s.plt_axes.set_title("Pixel")





class AuxPlotObj(QWidget):

    def __init__(s, parent=None, width=5, height=4, dpi=100):
        super().__init__()
        s.canvas = AuxPlotCanvas(parent, width, height, dpi)
        s.plt_axes = s.canvas.plt_axes

        # semi-permanent plot settings
        s.plt_axes.grid()
        s.plt_axes.set_ylabel("dB")
        s.plt_axes.set_xlabel("Z (cm)")


        # plot handles
        s.aux_main_plt_hndl = None
        s.aux_pt_markers_hndl = None

        s.noise_plt_hndl_0 = None
        s.noise_plt_hndl_1 = None
        s.noise_floor_plt_hndl = None
        s.threshold_plt_hndl = None
        s.contrast_plt_hndl = None
        s.front_peak_plt_hndl = None
        s.back_peak_plt_hndl = None

        s.weight_sum_plt_hndl_0 = None
        s.weight_sum_plt_hndl_1 = None


        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        s.toolbar = NavigationToolbar(s.canvas, s)
        s.layout    = QVBoxLayout()
        s.layout.addWidget(s.toolbar)
        s.layout.addWidget(s.canvas)
        s.setLayout(s.layout)
        s.plot_handles = []
        s.labels_list = []

    def aux_update(s, aux_data_in, new_frame_flag, loc_cfg_params):
        if new_frame_flag and aux_data_in["data_valid"]:
            x_ind       = aux_data_in["x_ind"]
            y_ind       = aux_data_in["y_ind"]
            aux_az_val  = aux_data_in["aux_az_val"]
            aux_el_val  = aux_data_in["aux_el_val"]

            power_spectra_lin   = aux_data_in["power_spectra"]
            range_lut_cm    = aux_data_in["range_lut_cm"]
            peak_ranges     = aux_data_in["peak_ranges"]
            peak_powers_lin = aux_data_in["peak_powers_lin"]
            noise_floor     = aux_data_in["noise_floor"]
            num_peaks       = aux_data_in["num_peaks"]
            adj_lin_thresh  = aux_data_in["adj_lin_thresh"]
            adj_lin_contr   = aux_data_in["adj_lin_contr"]
            weight_sum_start = aux_data_in["weight_sum_start"]
            weight_sum_end  = aux_data_in["weight_sum_end"]
            
            # a funny thing happens if you disable the weighted sum
            # this fixes it
            if weight_sum_end >= len(range_lut_cm):
                weight_sum_end = len(range_lut_cm) - 1
            if weight_sum_start < 0:
                weight_sum_start = 0

            noise_ind_start = aux_data_in["noise_ind_start"]
            noise_ind_end   = aux_data_in["noise_ind_end"]

            # range values for noise
            noise_val_start = range_lut_cm[noise_ind_start]
            noise_val_end = range_lut_cm[noise_ind_end]

            # range values for weighted sum
            weight_sum_start_range = range_lut_cm[weight_sum_start]
            weight_sum_end_range  = range_lut_cm[weight_sum_end]


            # global linewidth setting
            lw = 3

            if num_peaks != 0:
                # properly adjusting the data and extracting most interesting peaks
                peak_ranges = peak_ranges[:num_peaks]
                peak_powers_lin = peak_powers_lin[:num_peaks]

                back_peak_range = peak_ranges[-1]
                front_peak_range = peak_ranges[0]

                back_peak_power_db = 10*np.log10(peak_powers_lin[-1])
                front_peak_power_db = 10*np.log10(peak_powers_lin[0])

            else:
                back_peak_range = 0
                front_peak_range = 0
                back_peak_power_db = 0
                front_peak_power_db = 0


            title = f"Pixel ({x_ind}, {y_ind})"
            title += f" X={aux_az_val:.2f}, Y={aux_el_val:.2f}"
            s.plt_axes.set_title(title)

            power_spectra_db = 10*np.log10(power_spectra_lin)
            noise_floor_db = 10*np.log10(noise_floor)
            adj_thresh_db = 10*np.log10(adj_lin_thresh)
            adj_contr_db  = 10*np.log10(adj_lin_contr)

            #ipdb.set_trace()

            s.plot_handles = []
            s.labels_list = []


            ##################################################################
            # main power spectrum
            label = "Pixel Power Spectrum [dB]"
            if s.aux_main_plt_hndl == None:
                s.aux_main_plt_hndl, = s.plt_axes.plot(range_lut_cm, 
                    power_spectra_db, 'r', label=label, linewidth=lw)

            else:
                #s.aux_main_plt_hndl.set_data([], [])
                s.aux_main_plt_hndl.set_data(range_lut_cm, power_spectra_db)

            s.plot_handles.append(s.aux_main_plt_hndl)
            s.labels_list.append(label)


            ##################################################################
            # main power spectrum x markers
            label = "Pixel Power Spectrum [dB]"
            if s.aux_pt_markers_hndl == None:
                s.aux_pt_markers_hndl, = s.plt_axes.plot(range_lut_cm, 
                    power_spectra_db, 'rx', label=label, linewidth=lw)

            if loc_cfg_params["pt_mrkrs_en"]:
                s.aux_pt_markers_hndl.set_data(range_lut_cm, power_spectra_db)

            else:
                s.aux_pt_markers_hndl.remove()
                s.aux_pt_markers_hndl = None


            ##################################################################
            # noise delimiters
            label = "Noise Floor Calc Delimiters"
            if s.noise_plt_hndl_0 == None:
                s.noise_plt_hndl_0 = s.plt_axes.axvline(x=noise_val_start, 
                    color="magenta", label=label, linewidth=lw)

                s.noise_plt_hndl_1 = s.plt_axes.axvline(x=noise_val_end, 
                    color="magenta", label=label, linewidth=lw)
                            
            if loc_cfg_params["noise_delim_en"]:
                s.noise_plt_hndl_0.set_xdata([noise_val_start, noise_val_start])
                s.noise_plt_hndl_1.set_xdata([noise_val_end, noise_val_end])
                # ignore 1 so we don't get duplicate legends
                s.plot_handles.append(s.noise_plt_hndl_0)
                s.labels_list.append(label)

            else:
                #s.noise_plt_hndl_0.set_xdata([])
                #s.noise_plt_hndl_1.set_xdata([])
                s.noise_plt_hndl_0.remove()
                s.noise_plt_hndl_1.remove()

                s.noise_plt_hndl_0 = None
                s.noise_plt_hndl_1 = None


            ##################################################################
            # noise floor
            label = "Noise Floor Power [dB]"
            if s.noise_floor_plt_hndl == None:
                s.noise_floor_plt_hndl = s.plt_axes.axhline(y=noise_floor_db, 
                    color="#924ae9", linestyle='-', label=label, 
                    linewidth=lw)


            if loc_cfg_params["noise_floor_en"]:
                s.noise_floor_plt_hndl.set_ydata([noise_floor_db, 
                    noise_floor_db])
                s.plot_handles.append(s.noise_floor_plt_hndl)
                s.labels_list.append(label)
            else:
                #s.noise_floor_plt_hndl.set_ydata([])
                s.noise_floor_plt_hndl.remove()
                s.noise_floor_plt_hndl = None


            ##################################################################
            # threshold 
            label = "Threshold Level [dB]"
            if s.threshold_plt_hndl == None:
                s.threshold_plt_hndl = s.plt_axes.axhline(y=adj_thresh_db, 
                    color='b', linestyle='-', label=label, linewidth=lw)

            if loc_cfg_params["thresh_en"]:
                s.threshold_plt_hndl.set_ydata([adj_thresh_db, 
                    adj_thresh_db])
                s.plot_handles.append(s.threshold_plt_hndl)
                s.labels_list.append(label)
            else:
                #s.threshold_plt_hndl.set_ydata([])
                s.threshold_plt_hndl.remove()
                s.threshold_plt_hndl = None
                    

            ##################################################################
            # contrast 
            label = "Contrast Level [dB]"
            if s.contrast_plt_hndl == None:
                s.contrast_plt_hndl = s.plt_axes.axhline(y=adj_contr_db, 
                    color="#fdbf6f", linestyle='-', label=label, 
                    linewidth=lw)


            if loc_cfg_params["contr_en"]:
                s.contrast_plt_hndl.set_ydata([adj_contr_db, 
                    adj_contr_db])

                s.plot_handles.append(s.contrast_plt_hndl)
                s.labels_list.append(label)
            else:
                #s.contrast_plt_hndl.set_ydata([])
                s.contrast_plt_hndl.remove()
                s.contrast_plt_hndl = None
                




            ##################################################################
            # Front peak
            if num_peaks != 0:
                label = "Front Peak Marker"
            else:
                label = "NO VALID PEAKS FOUND"
            if s.front_peak_plt_hndl == None:
                s.front_peak_plt_hndl, = s.plt_axes.plot([front_peak_range], 
                    [front_peak_power_db], 'kp', markersize=14, 
                    label=label)

            if loc_cfg_params["front_peak_en"]:
                s.front_peak_plt_hndl.set_data([front_peak_range], 
                    [front_peak_power_db])
                s.plot_handles.append(s.front_peak_plt_hndl)
                s.labels_list.append(label)
            else:
                s.front_peak_plt_hndl.set_data([], [])

            # override the front peaks so the marker doesn't show
            if num_peaks == 0:
                s.front_peak_plt_hndl.set_data([], [])
                    

            ##################################################################
            # Back peak
            if num_peaks != 0:
                label = "Back Peak Marker"
            else:
                label = "NO VALID PEAKS FOUND"
            if s.back_peak_plt_hndl == None:
                s.back_peak_plt_hndl, = s.plt_axes.plot([back_peak_range], 
                    [back_peak_power_db], 'gp', markersize=14, 
                    label=label)

            if loc_cfg_params["back_peak_en"]:
                s.back_peak_plt_hndl.set_data([back_peak_range], 
                    [back_peak_power_db])
                s.plot_handles.append(s.back_peak_plt_hndl)
                s.labels_list.append(label)
            else:
                s.back_peak_plt_hndl.set_data([], [])

            # override the front peaks so the marker doesn't show
            if num_peaks == 0:
                s.back_peak_plt_hndl.set_data([], [])



            ##################################################################
            # Weighted Sum delimiters
            label = "Weighted Sum Delimiters"
            if s.weight_sum_plt_hndl_0 == None:
                s.weight_sum_plt_hndl_0 = s.plt_axes.axvline(
                    x=weight_sum_start_range, 
                    color="#6ed1cc", label=label, linewidth=lw)

                s.weight_sum_plt_hndl_1 = s.plt_axes.axvline(
                    x=weight_sum_end_range, 
                    color="#6ed1cc", label=label, linewidth=lw)


            if loc_cfg_params["weight_sum_en"]:
                s.weight_sum_plt_hndl_0.set_xdata([weight_sum_start_range, 
                    weight_sum_start_range])
                s.weight_sum_plt_hndl_1.set_xdata([weight_sum_end_range, 
                    weight_sum_end_range])

                s.plot_handles.append(s.weight_sum_plt_hndl_0)
                s.labels_list.append(label)

            else:
                #s.weight_sum_plt_hndl_0.set_xdata([])
                #s.weight_sum_plt_hndl_1.set_xdata([])
                    
                s.weight_sum_plt_hndl_0.remove()
                s.weight_sum_plt_hndl_1.remove()

                s.weight_sum_plt_hndl_0 = None
                s.weight_sum_plt_hndl_1 = None



            ##############################################################
            ##############################################################
            # legend
            if loc_cfg_params["legend_en"]:
                s.legend = s.plt_axes.legend(s.plot_handles, s.labels_list)
            else:
                legend = s.plt_axes.get_legend()
                if type(legend) != type(None):
                    s.plt_axes.get_legend().remove()

            s.plt_axes.set_xlim(range_lut_cm[0], range_lut_cm[-1])
            s.plt_axes.relim()
            s.plt_axes.autoscale_view(scalex=False, scaley=True)
            s.canvas.draw()


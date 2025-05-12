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


class AuxPlotObj(FigureCanvas):

    def __init__(s, parent=None, width=5, height=4, dpi=100):
        s.plt_fig = Figure(figsize=(width, height), dpi=dpi)
        s.plt_axes = s.plt_fig.add_subplot(111)
        super().__init__(s.plt_fig)

        s.plt_axes.set_title("Auxiliary Pixel")
        s.aux_main_plot_handle = None


    def aux_update(s, aux_data_in, new_frame_flag):
        if new_frame_flag:
            x_ind       = aux_data_in["x_ind"]
            y_ind       = aux_data_in["y_ind"]
            rangeline_lin   = aux_data_in["rangeline"]
            range_lut_cm    = aux_data_in["range_lut_cm"]
            peak_ranges     = aux_data_in["peak_ranges"]
            peak_powers_lin = aux_data_in["peak_powers_lin"]
            noise_floor     = aux_data_in["noise_floor"]
            num_peaks       = aux_data_in["num_peaks"]
            adj_lin_thresh  = aux_data_in["adj_lin_thresh"]
            adj_lin_contr   = aux_data_in["adj_lin_contr"]
            weight_sum_start = aux_data_in["weight_sum_start"]
            weight_sum_end  = aux_data_in["weight_sum_end"]

            s.plt_axes.set_title(f"Auxiliary Pixel {x_ind},{y_ind}")

            rangeline_db = 10*np.log10(rangeline_lin)

            if s.aux_main_plot_handle == None:
                s.aux_main_plot_handle, = s.plt_axes.plot(range_lut_cm, rangeline_db, 'r')
            else:
                s.aux_main_plot_handle.set_data(range_lut_cm, rangeline_db)
            
            s.draw()


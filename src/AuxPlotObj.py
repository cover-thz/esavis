# This is the code that creates the spectrum plot object
# that is used by SingPixTab


import os
import sys
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

        s.plt_fig.title("TITLE THINGS!")
        




    

    


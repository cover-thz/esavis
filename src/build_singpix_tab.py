# This file only contains widget generation and layout along with some parameter 
# settings of widgets (e.g. read-only for a QLineEdit widget) for the 
# SingPixTab
# 
# Signals and slots should not be assigned here.  The purpose of this file is 
# to make the SingPixTab file much cleaner and more concise
#

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from collections import OrderedDict
#from matplotlib.backendsbackend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import AuxPlotObj as apo

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



# NOTE PRESENTLY UNUSED
def build_singlepix_tab(singpix_tab):
    """
    builds up the initial set of GUI objects and the layout of the GUI for 
    the SingPixTab along with some default parameters and adds them to the 
    singpix_tab object
    """
    
    # layout consists of three main regions: the THz image itself alongside
    # the plot of the spectrum.  These two appear on the top of the window
    # then underneath is a bunch of textboxes etc. indicating metadata
    #
    # Maybe should duplicate the contrast, peakwidth, threshold, and noise
    # floor determination knobs here
    # 
    main_layout  = QVBoxLayout() 
    upper_layout = QHBoxLayout()
    lower_layout = QHBoxLayout()
    



    # remember if you can to implement lines for the weighted sum as well
    aux_plot_obj = apo.AuxPlotObj()

    aux_plot_obj.axes.plot([0,1,2,3,4],[10,1,20,3,40], color="r")

    # member variables
    s.aux_plot_obj = aux_plot_obj

    upper_layout.addWidget(aux_plot_obj)








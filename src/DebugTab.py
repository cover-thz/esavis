
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
import os
import ipdb # NOTE REMOVE
import json
from math import nan
#import sys
#import signal
import copy
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from collections import OrderedDict
#from dataclasses import dataclass, field

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
    QDialog,
    QDialogButtonBox,
)


class DebugTab(QWidget):
    """
    This is a tab that allows debugging of the system in real-time
    """
    set_trace_val = False

    # NOTE: cfg_dict is the global configuration dictionary, it is
    # not to be modified outside of the MainWindow, it is only provided
    # to be read
    def __init__(s, CFG_DFLT_PATH, CONFIG_DIR, 
                 update_config, cfg_dict):
        super().__init__()

        s.CFG_DFLT_PATH  = CFG_DFLT_PATH
        s.CONFIG_DIR     = CONFIG_DIR
        s.update_config  = update_config
        s.cfg_dict       = cfg_dict

        # builds up all the widgets and layout adds them to s
        top_layout  = QVBoxLayout()
        row_1       = QHBoxLayout()
        read_cfg_key_btn    = QPushButton("Read from cfg_dict")
        read_cfg_key_lbl    = QLabel("Key:")
        read_cfg_key_ledit  =  QLineEdit()
        read_cfg_val_lbl    = QLabel("Value:")
        read_cfg_val_ledit  =  QLineEdit()
        read_cfg_val_ledit.setReadOnly(True)

        # addlayout
        row_1.addWidget(read_cfg_key_btn)
        row_1.addWidget(read_cfg_key_lbl)
        row_1.addWidget(read_cfg_key_ledit)
        row_1.addWidget(read_cfg_val_lbl)
        row_1.addWidget(read_cfg_val_ledit)

        # member vars
        s.read_cfg_key_btn   = read_cfg_key_btn
        s.read_cfg_key_lbl   = read_cfg_key_lbl
        s.read_cfg_key_ledit = read_cfg_key_ledit
        s.read_cfg_val_lbl   = read_cfg_val_lbl
        s.read_cfg_val_ledit = read_cfg_val_ledit

        read_cfg_key_btn.clicked.connect(s.read_cfg_key_btn_clicked)

        row_2       = QHBoxLayout()
        write_cfg_key_btn    = QPushButton("Write to cfg_dict")
        write_cfg_key_lbl    = QLabel("Key:")
        write_cfg_key_ledit  =  QLineEdit()
        write_cfg_val_lbl    = QLabel("Value:")
        write_cfg_val_ledit  =  QLineEdit()
        write_cfg_key_btn.clicked.connect(s.write_cfg_key_btn_clicked)

        # addlayout
        row_2.addWidget(write_cfg_key_btn)
        row_2.addWidget(write_cfg_key_lbl)
        row_2.addWidget(write_cfg_key_ledit)
        row_2.addWidget(write_cfg_val_lbl)
        row_2.addWidget(write_cfg_val_ledit)


        # member vars
        s.write_cfg_key_btn     = write_cfg_key_btn
        s.write_cfg_key_lbl     = write_cfg_key_lbl
        s.write_cfg_key_ledit   = write_cfg_key_ledit
        s.write_cfg_val_lbl     = write_cfg_val_lbl
        s.write_cfg_val_ledit   = write_cfg_val_ledit

        row_3       = QHBoxLayout()
        type_int_rbut = QRadioButton()
        type_int_rbut.setText("Int")

        type_float_rbut = QRadioButton()
        type_float_rbut.setText("Float")

        type_str_rbut = QRadioButton()
        type_str_rbut.setText("Str")
        type_str_rbut.setChecked(True)

        type_bool_rbut = QRadioButton()
        type_bool_rbut.setText("Bool")

        #type_int_rbut = QRadioButton()
        #type_int_rbut.setText("Int")

        row_3.addWidget(type_int_rbut)
        row_3.addWidget(type_float_rbut)
        row_3.addWidget(type_str_rbut)
        row_3.addWidget(type_bool_rbut)

        # member vars
        s.type_int_rbut     = type_int_rbut
        s.type_float_rbut   = type_float_rbut
        s.type_str_rbut     = type_str_rbut
        s.type_bool_rbut    = type_bool_rbut


        # ROW 4
        enable_profiler_chkb  = QCheckBox()
        enable_profiler_chkb.setText("Enable Profiler:")

        # member vars
        s.enable_profiler_chkb = enable_profiler_chkb
        s.enable_profiler_chkb.stateChanged.connect(s.enable_profiler_update())


        top_layout.addLayout(row_1)
        top_layout.addLayout(row_2)
        top_layout.addLayout(row_3)
        top_layout.addWidget(enable_profiler_chkb)

        s.row_1  = row_1
        s.row_2  = row_2
        s.row_3  = row_3
        s.top_layout = top_layout

        s.setLayout(top_layout)


    def read_cfg_key_btn_clicked(s):
        key = s.read_cfg_key_ledit.text()
        value = s.cfg_dict[key]
        s.read_cfg_val_ledit.setText(str(value))
        print(f"Read key: {key}, got value {value}")


    def write_cfg_key_btn_clicked(s):
        key     = s.write_cfg_key_ledit.text()
        value   = s.write_cfg_val_ledit.text()
        if s.type_int_rbut.isChecked():
            value = int(value)
        elif s.type_float_rbut.isChecked():
            value = float(value)
        elif s.type_str_rbut.isChecked():
            value = str(value)
            dtype = str
        elif s.type_bool_rbut.isChecked():
            value = value.strip()
            value = value.lower()
            if value == "true":
                value = True
            elif value == "1":
                value = True
            else:
                value = False
        s.cfg_dict[key] = value
        print(f"Wrote value: {value}, to key: {key}")


    def enable_profiler_update(s):
        print("CLICKED PROFILER CHECKBOX!")
        if s.enable_profiler_chkb.isChecked():
            prof_en = True
        else:
            prof_en = False
        key = "profiler"
        new_cfg_dict = OrderedDict()
        new_cfg_dict[key] = prof_en
        s.update_config(new_cfg_dict)


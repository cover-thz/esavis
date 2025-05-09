import copy
from dataclasses import dataclass
import json
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QCheckBox,
    QWidget,
)
from PySide6.QtGui import QTransform
from PySide6.QtCore import Signal
import numpy as np
import pyqtgraph as pg
import cv2

"""
from util import (
    add_int_edit,
    apply_config_popup,
    button_row,
    float_edit,
    get_fval,
    get_ival,
    add_float_edit,
)


@dataclass
class CameraConfig:
    visible: bool = False
    camera_index: int = 0
    opacity: float = 1
    h_scale: float = 1
    v_scale: float = 1
    x: float = 0
    y: float = 0
    flip_h: bool = False
    flip_v: bool = False

    def make_transform(self):
        t = QTransform()
        t.translate(self.x, self.y)
        t.scale(self.h_scale, self.v_scale)

        return t


class CameraConfigEditor(QWidget):
    config_applied = Signal(object)
    capture_triggered = Signal()

    start_config: CameraConfig

    def __init__(self, config: CameraConfig = CameraConfig()):
        super().__init__()

        self.setWindowTitle("THz Image Plot Image Editor")

        self.full_layout = QFormLayout()
        self.setLayout(self.full_layout)

        self.camera_index_edit = add_int_edit(self.full_layout, "Camera Index")

        self.visible_edit = QCheckBox()
        self.full_layout.addRow("Visible", self.visible_edit)

        self.opacity_edit = add_float_edit(self.full_layout, "Opactiy")

        scale_row = QHBoxLayout()
        self.full_layout.addRow("Scale (H, V)", scale_row)

        self.h_scale_edit = float_edit()
        scale_row.addWidget(self.h_scale_edit)

        self.v_scale_edit = float_edit()
        scale_row.addWidget(self.v_scale_edit)

        self.flip_h_edit = QCheckBox()
        self.flip_v_edit = QCheckBox()

        self.full_layout.addRow("Flip H", self.flip_h_edit)
        self.full_layout.addRow("Flip V", self.flip_v_edit)

        row, [self.load_btn, self.save_btn] = button_row("Load Config", "Save Config")
        self.full_layout.addRow(row)

        self.load_btn.clicked.connect(self.handle_load)
        self.save_btn.clicked.connect(self.handle_save)

        apply_scale_btn = QPushButton("Apply")
        apply_scale_btn.clicked.connect(self.apply_config)

        self.full_layout.addRow(apply_scale_btn)

        self.grid_layout = QGridLayout()
        self.full_layout.addRow("Pan", self.grid_layout)

        self.up_btn = QPushButton("^")
        self.up_btn.clicked.connect(lambda: self.step_position(0, -1))
        self.down_btn = QPushButton("v")
        self.down_btn.clicked.connect(lambda: self.step_position(0, 1))

        self.left_btn = QPushButton("<")
        self.left_btn.clicked.connect(lambda: self.step_position(1, 0))
        self.right_btn = QPushButton(">")
        self.right_btn.clicked.connect(lambda: self.step_position(-1, 0))

        self.grid_layout.addWidget(self.up_btn, 0, 1)

        self.grid_layout.addWidget(self.left_btn, 1, 0)
        self.grid_layout.addWidget(self.right_btn, 1, 2)

        self.grid_layout.addWidget(self.down_btn, 2, 1)

        self.step_edit = add_float_edit(self.full_layout, "Step")
        self.step_edit.setText(str(1.0))

        self.trigger_capture_btn = QPushButton("Trigger Capture")
        self.trigger_capture_btn.clicked.connect(lambda: self.capture_triggered.emit())

        self.full_layout.addRow(self.trigger_capture_btn)

        self.set_config(config)

    def set_config(self, config: CameraConfig, override_start=True):
        if override_start:
            self.start_config = copy.deepcopy(config)

        self.camera_index_edit.setText(str(config.camera_index))
        self.visible_edit.setChecked(config.visible)
        self.opacity_edit.setText(str(config.opacity))
        self.h_scale_edit.setText(str(config.h_scale))
        self.v_scale_edit.setText(str(config.v_scale))
        self.flip_h_edit.setChecked(config.flip_h)
        self.flip_v_edit.setChecked(config.flip_v)

    def make_config(self, x, y):
        config = CameraConfig()
        config.camera_index = get_ival(self.camera_index_edit)
        config.visible = self.visible_edit.isChecked()
        config.opacity = get_fval(self.opacity_edit)
        config.h_scale = get_fval(self.h_scale_edit)
        config.v_scale = get_fval(self.v_scale_edit)
        config.flip_h = self.flip_h_edit.isChecked()
        config.flip_v = self.flip_v_edit.isChecked()
        config.x = x
        config.y = y

        return config

    def handle_load(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Config", ".", "JSON Files (*.json)"
        )
        if len(file_name) > 0:
            with open(file_name, "r", encoding="utf-8") as file:
                self.load_config(file)

    def handle_save(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Config", "./cameraconfig.json", "JSON Files (*.json)"
        )
        if len(file_name) > 0:
            with open(file_name, "w", encoding="utf-8") as file:
                self.save_config(file)

    def save_config(self, f):
        json.dump(vars(self.make_config(self.start_config.x, self.start_config.y)), f)

    def load_config(self, f):
        content = json.load(f)
        as_config = CameraConfig(**content)
        self.set_config(as_config, override_start=False)
        # this is kinda a hack
        self.start_config.x = as_config.x
        self.start_config.y = as_config.y

    def closeEvent(self, _):
        if self.start_config != self.make_config(
            self.start_config.x, self.start_config.y
        ):
            if apply_config_popup(self):
                self.apply_config()

    def step_position(self, x_scalar: float, y_scalar: float):
        self.start_config.x += x_scalar * get_fval(self.step_edit)
        self.start_config.y += y_scalar * get_fval(self.step_edit)

        self.config_applied.emit(self.start_config)

    def apply_config(self):
        new_config = self.make_config(self.start_config.x, self.start_config.y)
        self.config_applied.emit(new_config)
        self.start_config = new_config
"""

class CameraItem(pg.ImageItem):
    index = -1
    camera = None

    flip_h = False
    flip_v = False

    def __init__(self):
        super().__init__(axisOrder="row-major", levels=None)

    def set_index(self, index):
        is_same = self.index == index
        self.index = index
        if self.camera and not is_same:
            self.check_and_start_capture()

    def stop_capture(self):
        if self.camera:
            self.camera.release()
        self.camera = None

    def check_and_start_capture(self):
        if self.index == -1:
            self.stop_capture()
            return
        if self.camera:
            self.stop_capture()
        self.camera = cv2.VideoCapture(self.index)
        # set buffer size to 1
        self.camera.set(38, 1)

    def capture_and_display(self):
        if not self.camera:
            self.clear()
            return

        # fill the buffer
        self.camera.read()
        ret, img = self.camera.read()
        if not ret:
            self.clear()
            print("Could not read from camera")
            return
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if self.flip_h:
            img = np.fliplr(img)
        if self.flip_v:
            img = np.flipud(img)

        self.setImage(img)

    def make_transform(s, x, y, h_scale, v_scale):
        t = QTransform()
        t.translate(x, y)
        t.scale(h_scale, v_scale)
        s.setTransform(t)


import json
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
                            QComboBox, QSlider, QPushButton, QColorDialog,
                            QFileDialog, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal

CONFIG_FILE = "profiles.json"

DEFAULT_PROFILES = {
    "Default Cross": {"style": "Cross", "size": 20, "thickness": 2, "color": "#00FF00", "opacity": 255, "offset_x": 0, "offset_y": 0, "image_path":""},
    "Sniper Dot": {"style": "Dot", "size": 6, "thickness": 1, "color": "#FF0000", "opacity": 255, "offset_x": 0, "offset_y": 0, "image_path": ""}
}

class SettingsWindow(QWidget):
    config_changed = pyqtSignal(dict)

    def __init__(self, fallback_config):
        super().__init__()
        self.setWindowTitle("CrossForge Settings")
        self.setMinimumWidth(350)

        self.profiles = self.load_profiles()
        if not self.profiles:
            self.profiles = DEFAULT_PROFILES.copy()

        self.current_profile_name = list(self.profiles.keys())[0]
        self.config = self.profiles[self.current_profile_name].copy()

        self.init_ui()
        self.notify_change()

    def load_profiles(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return{}

    def save_profiles(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.profiles, f, indent=4)
    
    def init_ui(self):
        main_layout = QVBoxLayout()

        profile_layout = QHBoxLayout()

        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.profiles.keys())
        self.profile_combo.setCurrentText(self.current_profile_name)
        self.profile_combo.currentTextChanged.connect(self.change_profile)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_current_profile)

        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new_profile)

        profile_layout.addWidget(self.profile_combo)
        profile_layout.addWidget(save_btn)
        profile_layout.addWidget(new_btn)
        main_layout.addLayout(profile_layout)

        layout = QFormLayout()

        self.style_combo = QComboBox()
        self.style_combo.addItems(["Cross", "Dot", "Circle", "X", "Image"])
        self.style_combo.setCurrentText(self.config["style"])
        self.style_combo.currentTextChanged.connect(self.update_style)
        layout.addRow("Style:", self.style_combo)

        self.size_slider = self.create_slider(1, 200, self.config["size"], self.update_size)
        layout.addRow("Size:", self.size_slider)

        self.thick_slider = self.create_slider(1, 20, self.config["thickness"], self.update_thickness)
        layout.addRow("Thickness:", self.thick_slider)

        self.opac_slider = self.create_slider(0, 255, self.config["opacity"], self.update_opacity)
        layout.addRow("Opacity:", self.opac_slider)

        self.color_btn = QPushButton("Select Color")
        self.color_btn.setStyleSheet(f"background-color: {self.config['color']}; color: black;")
        self.color_btn.clicked.connect(self.select_color)
        layout.addRow("Color:", self.color_btn)

        self.image_btn = QPushButton("Select Image")
        self.image_btn.clicked.connect(self.pick_image)
        layout.addRow("Custom Image:", self.image_btn)

        main_layout.addLayout(layout)
        self.setLayout(main_layout)
    
    def create_slider(self, min_val, max_val, current_val, callback):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(current_val)
        slider.valueChanged.connect(callback)
        return slider

    def change_profile(self, name):
        if name in self.profiles:
            self.current_profile_name = name
            self.config = self.profiles[name].copy()
            self.refresh_ui_from_config()
            self.notify_change()

    def save_current_profile(self):
        self.profiles[self.current_profile_name] = self.config.copy()
        self.save_profiles()
        QMessageBox.information(self, "Profile Saved", f"Profile '{self.current_profile_name}' has been saved.")

    def new_profile(self):
        text, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and text:
            self.current_profile_name = text
            self.profiles[text] = self.config.copy()
            self.profile_combo.addItem(text)
            self.profile_combo.setCurrentText(text)
            self.save_profiles()
    
    def refresh_ui_from_config(self):
        self.style_combo.blockSignals(True)
        self.style_combo.setCurrentText(self.config["style"])
        self.style_combo.blockSignals(False)

        self.size_slider.setValue(self.config["size"])
        self.thick_slider.setValue(self.config["thickness"])
        self.opac_slider.setValue(self.config["opacity"])
        self.color_btn.setStyleSheet(f"background-color: {self.config['color']}; color: black;")

    def update_style(self, value):
        self.config["style"] = value
        self.notify_change()
    
    def update_size(self, value):
        self.config["size"] = value
        self.notify_change()
    
    def update_thickness(self, value):
        self.config["thickness"] = value
        self.notify_change()
    
    def update_opacity(self, value):
        self.config["opacity"] = value
        self.notify_change()
    
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            self.config["color"] = hex_color
            self.color_btn.setStyleSheet(f"background-color: {self.config['color']}; color: black;")
            self.notify_change()

    def pick_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.bmp)")
        if file_path:
            self.config["image_path"] = file_path
            self.style_combo.setCurrentText("Image")
            self.notify_change()

    def notify_change(self):
        self.config_changed.emit(self.config.copy())
        
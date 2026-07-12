from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout,
                                 QComboBox, QSlider, QPushButton, QColorDialog,
                                 QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal

class SettingsWindow(QWidget):
    config_changed = pyqtSignal(dict)

    def __init__(self, current_config):
        super().__init__()
        self.setWindowTitle("Crosshair Settings")
        self.setMinimumWidth(300)

        self.config = current_config.copy()

        self.init_ui()
    
    def init_ui(self):
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
        self.color_btn.setStyleSheet(f"background-color: {self.config['color']};")
        self.color_btn.clicked.connect(self.select_color)
        layout.addRow("Color:", self.color_btn)

        self.image_btn = QPushButton("Select Image")
        self.image_btn.clicked.connect(self.pick_image)
        layout.addRow("Custom Image:", self.image_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        self.setLayout(main_layout)

    def create_slider(self, min_val, max_val, current_val, callback):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(current_val)
        slider.valueChanged.connect(callback)
        return slider
    
    def update_style(self, style):
        self.config["style"] = style
        self.notify_change()
    
    def update_size(self, size):
        self.config["size"] = size
        self.notify_change()

    def update_thickness(self, thickness):
        self.config["thickness"] = thickness
        self.notify_change()
    
    def update_opacity(self, opacity):
        self.config["opacity"] = opacity
        self.notify_change()
    
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            self.config["color"] = hex_color
            self.color_btn.setStyleSheet(f"background-color: {hex_color}; color: black;")
            self.notify_change()
    
    def pick_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.bmp)")
        if file_path:
            self.config["image_path"] = file_path
            self.style_combo.setCurrentText("Image")
            self.notify_change()

    def notify_change(self):
        self.config_changed.emit(self.config)



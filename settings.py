import json
import os
import base64
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
                            QComboBox, QSlider, QPushButton, QColorDialog,
                            QFileDialog, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap

CONFIG_FILE = "profiles.json"

DEFAULT_PROFILES = {
    "Default Cross": {"style": "Cross", "size": 20, "thickness": 2, "color": "#00FF00", "opacity": 255, "offset_x": 0, "offset_y": 0, "image_path":"", "outline": True, "gap": 5, "bloom": False, "bloom_amount": 10, "smart_color": False, "movement_bloom": False, "movement_bloom_amount": 15, "rotation": 0, "always_on_top": False, "monitor": 0},
    "Sniper Dot": {"style": "Dot", "size": 6, "thickness": 1, "color": "#FF0000", "opacity": 255, "offset_x": 0, "offset_y": 0, "image_path": "", "outline": False, "gap": 0, "bloom": False, "bloom_amount": 10, "smart_color": False, "movement_bloom": False, "movement_bloom_amount": 15, "rotation": 0, "always_on_top": False, "monitor": 0}
}
DARK_THEME = """
    QWidget {
        background-color: #0F1923;
        color: #ECE8E1;
        font-family: 'Segoe UI', sans-serif;
        font-size: 10pt;
    }
    QPushButton {
        background-color: #FF4655;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #E03C4A;
    }
    QComboBox {
        background-color: #1F2E3D;
        border: 1px solid #3E5266;
        border-radius: 4px;
        padding: 4px 8px;
    }
    QComboBox:hover {
        border: 1px solid #FF4655;
    }
    QComboBox::drop-down {
        border: none;
    }
    QSlider::groove:horizontal {
        border:none;
        height: 8px;
        background: #1F2E3D;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #FF4655;
        height: 16px;
        margin: -4px 0;
        border-radius: 8px;
    }
    QSlider::handle:horizontal:hover {
        background: #ECE8E1;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #3E5266;
        border-radius: 4px;
        background-color: #1F2E3D;
    }
    QCheckBox::indicator:checked {
        background-color: #FF4655;
        border: 1px solid #FF4655
    }
    """
class PreviewCanvas(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setFixedSize(150, 150)
    
    def update_preview(self):
        self.repaint()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(0, 0, self.width(), self.height(), QColor(30, 30, 30))

        color = QColor(self.config["color"])
        color.setAlpha(self.config["opacity"])
        painter.setPen(QPen(color, self.config["thickness"]))

        cx = self.width() // 2
        cy = self.height() // 2
        half_size = self.config["size"] // 2

        style = self.config["style"]
        
        if style == "Cross":
            painter.drawLine(cx - half_size, cy, cx + half_size, cy)
            painter.drawLine(cx, cy - half_size, cx, cy + half_size)
        elif style == "Dot":
            painter.setBrush(color)
            from PyQt6.QtCore import QPoint
            painter.drawEllipse(QPoint(cx, cy), half_size, half_size)
        elif style == "Circle":
            from PyQt6.QtCore import QPoint
            painter.drawEllipse(QPoint(cx, cy), half_size, half_size)
        elif style == "X":
            painter.drawLine(cx - half_size, cy - half_size, cx + half_size, cy + half_size)
            painter.drawLine(cx - half_size, cy + half_size, cx + half_size, cy - half_size)
        
        painter.end()

class SettingsWindow(QWidget):
    config_changed = pyqtSignal(dict)

    def __init__(self, fallback_config):
        super().__init__()
        self.setWindowTitle("CrossForge Settings")
        self.setMinimumWidth(350)
        self.setStyleSheet(DARK_THEME)

        self.profiles = self.load_profiles()
        if not self.profiles:
            self.profiles = DEFAULT_PROFILES.copy()

        self.current_profile_name = list(self.profiles.keys())[0]
        self.config = self.profiles[self.current_profile_name].copy()

        self.slider_labels = {}
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

        share_layout = QHBoxLayout()
        export_btn = QPushButton("Export Code")
        export_btn.clicked.connect(self.export_code)

        import_btn = QPushButton("Import Code")
        import_btn.clicked.connect(self.import_code)

        share_layout.addWidget(export_btn)
        share_layout.addWidget(import_btn)
        main_layout.addLayout(share_layout)

        preview_layout = QHBoxLayout()
        self.preview_canvas = PreviewCanvas(self.config)
        preview_layout.addStretch()
        preview_layout.addWidget(self.preview_canvas)
        preview_layout.addStretch()
        main_layout.addLayout(preview_layout)

        layout = QFormLayout()

        self.style_combo = QComboBox()
        self.style_combo.addItems(["Cross", "Dot", "Circle", "X", "Image"])
        self.style_combo.setCurrentText(self.config["style"])
        self.style_combo.currentTextChanged.connect(self.update_style)
        layout.addRow("Style:", self.style_combo)

        self.size_layout, self.size_slider = self.create_slider("size", 1, 200, self.config["size"], self.update_size)
        layout.addRow("Size:", self.size_layout)

        self.thick_layout, self.thick_slider = self.create_slider("thickness", 1, 20, self.config["thickness"], self.update_thickness)
        layout.addRow("Thickness:", self.thick_layout)

        self.opac_layout, self.opac_slider = self.create_slider("opacity", 0, 255, self.config["opacity"], self.update_opacity)
        layout.addRow("Opacity:", self.opac_layout)

        self.rot_layout, self.rot_slider = self.create_slider("rotation", 0, 360, self.config.get("rotation", 0), self.update_rotation)
        layout.addRow("Rotation Angle:", self.rot_layout)

        from PyQt6.QtWidgets import QCheckBox
        self.top_check = QCheckBox()
        self.top_check.setChecked(self.config.get("always_on_top", False))
        self.top_check.stateChanged.connect(self.update_always_on_top)
        layout.addRow("Keep settings on top:", self.top_check)

        from PyQt6.QtWidgets import QCheckBox
        self.bloom_check = QCheckBox()
        self.bloom_check.setChecked(self.config.get("bloom", False))
        self.bloom_check.stateChanged.connect(self.update_bloom)
        layout.addRow("Enable Click Bloom:", self.bloom_check)

        from PyQt6.QtWidgets import QCheckBox
        self.move_check = QCheckBox()
        self.move_check.setChecked(self.config.get("movement_bloom", False))
        self.move_check.stateChanged.connect(self.update_move_bloom)
        layout.addRow("Enable WASD Bloom:", self.move_check)

        self.move_layout, self.move_slider = self.create_slider("movement_bloom_amount", 1, 50, self.config.get("movement_bloom_amount", 15), self.update_move_amount)
        layout.addRow("WASD Bloom Amount:", self.move_layout)

        self.bloom_layout, self.bloom_slider = self.create_slider("bloom_amount", 1, 50, self.config.get("bloom_amount", 10), self.update_bloom_amount)
        layout.addRow("Bloom Amount:", self.bloom_layout)

        self.color_btn = QPushButton("Select Color")
        self.color_btn.setStyleSheet(f"background-color: {self.config['color']}; color: black;")
        self.color_btn.clicked.connect(self.select_color)
        layout.addRow("Color:", self.color_btn)

        from PyQt6.QtWidgets import QCheckBox
        self.smart_color_check = QCheckBox()
        self.smart_color_check.setChecked(self.config.get("smart_color", False))
        self.smart_color_check.stateChanged.connect(self.update_smart_color)
        layout.addRow("Auto-Contrast Mode:", self.smart_color_check)

        self.image_btn = QPushButton("Select Image")
        self.image_btn.clicked.connect(self.pick_image)
        layout.addRow("Custom Image:", self.image_btn)

        from PyQt6.QtWidgets import QApplication
        self.screen_combo = QComboBox()

        screens = QApplication.instance().screens()
        for idx in range(len(screens)):
            self.screen_combo.addItem(f"Monitor {idx + 1}")
        
        self.screen_combo.setCurrentIndex(self.config.get("monitor", 0))
        self.screen_combo.currentIndexChanged.connect(self.update_monitor)
        layout.addRow("Select Display:", self.screen_combo)


        main_layout.addLayout(layout)
        self.setLayout(main_layout)
    
    def create_slider(self, name, min_val, max_val, current_val, callback):
        row_layout = QHBoxLayout()
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(current_val)
        
        from PyQt6.QtWidgets import QLabel
        val_label = QLabel(str(current_val))
        val_label.setMinimumWidth(30)
        self.slider_labels[name] = val_label

        row_layout.addWidget(slider)
        row_layout.addWidget(val_label)

        def on_change(val):
            val_label.setText(str(val))
            callback(val)
        
        slider.valueChanged.connect(on_change)
        return row_layout, slider

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
        
        self.bloom_check.setChecked(self.config.get("bloom", False))
        self.bloom_slider.setValue(self.config.get("bloom_amount", 10))
        
        if hasattr(self, 'move_check'):
            self.move_check.setChecked(self.config.get("movement_bloom", False))
            self.move_slider.setValue(self.config.get("movement_bloom_amount", 15))

        self.size_slider.setValue(self.config["size"])
        self.thick_slider.setValue(self.config["thickness"])
        self.opac_slider.setValue(self.config["opacity"])
        self.color_btn.setStyleSheet(f"background-color: {self.config['color']}; color: black;")

        if hasattr(self, 'preview_canvas'):
            self.preview_canvas.config = self.config
            self.preview_canvas.update_preview()
        
        if hasattr(self, 'top_check'):
            self.top_check.setChecked(self.config.get("always_on_top", False))
            self.apply_always_on_top()
        
        self.screen_combo.setCurrentIndex(self.config.get("monitor", 0))

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
        
        if hasattr(self, 'preview_canvas'):
            self.preview_canvas.config = self.config
            self.preview_canvas.update_preview()

    def update_bloom(self, state):
        self.config["bloom"] = bool(state)
        self.notify_change()

    def update_bloom_amount(self, val):
        self.config["bloom_amount"] = val
        self.notify_change()

    def export_code(self):
        json_str = json.dumps(self.config)
        code = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(code)

        QMessageBox.information(self, "Export Successful", "Crosshair code copied to clipboard!\nShare this with your friends.")

    def import_code(self):
        code, ok = QInputDialog.getText(self, "Import Crosshair", "Paste code here:")
        if ok and code:
            try:
                json_str = base64.b64decode(code.encode("utf-8")).decode("utf-8")
                imported_config = json.loads(json_str)

                self.config.update(imported_config)
                self.refresh_ui_from_config()
                self.notify_change

                QMessageBox.information(self, "Import Sucessful", "Crosshair imported")
            except Exception as e:
                QMessageBox.warning(self, "Import Failed", "Invalid share code!")
    
    def update_move_bloom(self, state):
        self.config["movement_bloom"] = bool(state)
        self.notify_change()
    
    def update_move_amount(self, val):
        self.config["movement_bloom_amount"] = val
        self.notify_change()

    def update_smart_color(self, state):
        self.config["smart_color"] = bool(state)
        self.notify_change()

    def update_rotation(self, val):
        self.config["rotation"] = val
        self.notify_change()

    def update_always_on_top(self, state):
        self.config["always_on_top"] = bool(state)
        self.apply_always_on_top()
        self.notify_change()

    def apply_always_on_top(self):
        from PyQt6.QtCore import Qt
        if self.config.get("always_on_top", False):
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.show()
    
    def update_monitor(self, index):
        self.config["monitor"] = index
        self.notify_change()
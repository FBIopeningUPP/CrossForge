import sys
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap

class CrosshairOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.current_bloom = 0
        self.current_move_bloom = 0
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.config = {
            "style": "Cross",
            "size": 20,
            "thickness": 2,
            "color": "#FF0000",
            "opacity": 255,
            "offset_x": 0,
            "offset_y": 0,
            "image_path": ""
        }

        self.setGeometry(0, 0, 1920, 1080)

    def update_config(self, new_config):
        self.config.update(new_config)
        self.repaint()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = (self.width() // 2) + self.config["offset_x"]
        center_y = (self.height() // 2) + self.config["offset_y"]
        center = QPoint(center_x, center_y)

        size = self.config["size"]
        half_size = size // 2
        style = self.config["style"]
        gap = self.config.get("gap", 0) + self.current_bloom + self.current_move_bloom
        has_outline = self.config.get("outline", False)

        color = QColor(self.config["color"])
        color.setAlpha(self.config["opacity"])

        main_pen = QPen(color, self.config["thickness"])
        outline_pen = QPen(QColor(0, 0, 0, self.config["opacity"]), self.config["thickness"] + 2) 

        def draw_shape(pen, is_outline=False):
            painter.setPen(pen)

            if style == "Cross":
                painter.drawLine(center_x - half_size, center_y, center_x - gap, center_y)
                painter.drawLine(center_x + gap, center_y, center_x + half_size, center_y)
                painter.drawLine(center_x, center_y - half_size, center_x, center_y - gap) 
                painter.drawLine(center_x, center_y + gap, center_x, center_y + half_size)
            
            elif style == "Dot":
                if not is_outline:
                    painter.setBrush(color)
                else:
                    painter.setBrush(QColor(0, 0, 0, self.config["opacity"]))
                painter.drawEllipse(center, half_size + gap, half_size + gap)

            elif style == "Circle":
                painter.drawEllipse(center, half_size + gap, half_size + gap)
            
            elif style == "X":
                painter.drawLine(center_x - half_size, center_y - half_size, center_x - gap, center_y - gap)
                painter.drawLine(center_x + gap, center_y + gap, center_x + half_size, center_y + half_size)
                painter.drawLine(center_x - half_size, center_y + half_size, center_x - gap, center_y + gap)
                painter.drawLine(center_x + gap, center_y - gap, center_x + half_size, center_y - half_size)
            
            elif style == "Image" and self.config["image_path"]:
                if not is_outline:
                    pixmap = QPixmap(self.config["image_path"])
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        painter.drawPixmap(center_x - (scaled_pixmap.width() // 2), center_y - (scaled_pixmap.height() // 2), scaled_pixmap)
        
        if has_outline and style != "Image":
            draw_shape(outline_pen, is_outline=True)
        
        draw_shape(main_pen, is_outline=False)

        painter.end()
        
    def on_click(self):
        if self.config.get("bloom", False):
            self.current_bloom = self.config.get("bloom_amount", 10)
            self.repaint()
    
    def on_release(self):
        if self.config.get("bloom", False):
            self.current_bloom = 0
            self.repaint()
            
    def on_move_start(self):
        if self.config.get("movement_bloom", False):
            self.current_move_bloom = self.config.get("movement_bloom_amount", 15)
            self.repaint()

    def on_move_stop(self):
        if self.config.get("movement_bloom", False):
            self.current_move_bloom = 0
            self.repaint()
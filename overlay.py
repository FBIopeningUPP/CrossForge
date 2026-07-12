import sys
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap

class CrosshairOverlay(QWidget):
    def __init__(self):
        super().__init__()
        
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

        color = QColor(self.config["color"])
        color.setAlpha(self.config["opacity"])
        pen = QPen(color, self.config["thickness"])
        painter.setPen(pen)

        center_x = (self.width() // 2) + self.config["offset_x"]
        center_y = (self.height() // 2) + self.config["offset_y"]
        center = QPoint(center_x, center_y)

        size = self.config["size"]
        half_size = size // 2
        style = self.config["style"]

        if style == "Cross":
            painter.drawLine(center.x() - half_size, center.y(), center.x() + half_size, center.y())
            painter.drawLine(center.x(), center.y() - half_size, center.x(), center.y() + half_size)
        
        elif style == "Dot":
            painter.setBrush(color)
            painter.drawEllipse(center, half_size, half_size)
        
        elif style == "Circle":
            painter.drawEllipse(center, half_size, half_size)

        elif style == "X":
            painter.drawLine(center.x() - half_size, center.y() - half_size, center.x() + half_size, center.y() + half_size)
            painter.drawLine(center.x() - half_size, center.y() + half_size, center.x() + half_size, center.y() - half_size)
        
        elif style == "Image" and self.config["image_path"]:
            pixmap = QPixmap(self.config["image_path"])
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                painter.drawPixmap(center.x() - scaled_pixmap.width() // 2, center.y() - scaled_pixmap.height() // 2, scaled_pixmap)
        
        painter.end()
import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt6.QtCore import pyqtSignal, QObject
from pynput import keyboard

from overlay import CrosshairOverlay
from settings import SettingsWindow

class HotKeySignals(QObject):
    toggle_overlay = pyqtSignal()
    toggle_settings = pyqtSignal()

class CrossForgeApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.app.setQuitOnLastWindowClosed(False)

        self.overlay = CrosshairOverlay()
        self.settings = SettingsWindow(self.overlay.config)
        self.settings.config_changed.connect(self.overlay.update_config)

        self.setup_tray()
        self.setup_hotkeys()

        self.overlay.show()
        self.settings.show()

    def setup_tray(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("transparent"))
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, 64, 64, QColor("#1E1E1E"))
        painter.fillRect(28, 12, 8, 40, QColor("#00FF00"))
        painter.fillRect(12, 28, 40, 8, QColor("#00FF00"))
        painter.end()

        icon = QIcon(pixmap)
        self.tray = QSystemTrayIcon(icon, self.app)
        self.tray.setToolTip("CrossForge")

        menu = QMenu()

        settings_action = menu.addAction("Settings")
        settings_action.triggered.connect(self.toggle_settings)

        menu.addSeparator()

        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)

        self.tray.setContextMenu(menu)
        self.tray.show()
    
    def setup_hotkeys(self):
        self.signals = HotKeySignals()
        self.signals.toggle_overlay.connect(self.toggle_overlay)
        self.signals.toggle_settings.connect(self.toggle_settings)

    def on_press(key):
        if key == keyboard.Key.f2:
            self.signals.toggle_overlay.emit()
        elif key == keyboard.Key.f3:
            self.signals.toggle_settings.emit()

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
    
    def toggle_overlay(self):
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()
    
    def toggle_settings(self):
        if self.settings.isVisible():
            self.settings.hide()
        else:
            self.settings.show()
            self.settings.activateWindow()
    
    def quit_app(self):
        self.listener.stop()
        self.tray.hide()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    crossforge = CrossForgeApp()
    crossforge.run()
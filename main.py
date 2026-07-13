import sys
import ctypes
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt6.QtCore import pyqtSignal, QObject, QTimer
from pynput import keyboard

from overlay import CrosshairOverlay
from settings import SettingsWindow

class HotKeySignals(QObject):
    toggle_overlay = pyqtSignal()
    toggle_settings = pyqtSignal()
    toggle_sniper = pyqtSignal()
    mouse_pressed = pyqtSignal()
    mouse_released = pyqtSignal()

class CrossForgeApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.app.setQuitOnLastWindowClosed(False)

        self.overlay = CrosshairOverlay()
        self.settings = SettingsWindow(self.overlay.config)
        self.settings.config_changed.connect(self.overlay.update_config)

        self.setup_tray()
        self.setup_hotkeys()

        self.mouse_timer = QTimer()
        self.mouse_timer.timeout.connect(self.check_hardware)
        self.mouse_timer.start(16)

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

        self.signals.toggle_sniper.connect(self.overlay.toggle_sniper_mode)

        self.signals.mouse_pressed.connect(self.overlay.on_click)
        self.signals.mouse_released.connect(self.overlay.on_release)

        def on_press(key):
            key_str = str(key)

            if getattr(self.settings, 'listening_for', None):
                target = self.settings.listening_for
                self.settings.config[target] = key_str

                self.settings.active_bind_btn.setText(f"{target.split('_')[1].title()}: {key_str}")

                self.settings.listening_for = None
                self.settings.active_bind_btn = None
                self.settings.notify_change
            
            if key_str == self.settings.config.get("hotkey_overlay", "Key.f2"):
                self.signals.toggle_overlay.emit()
            elif key_str == self.settings.config.get("hotkey_settings", "Key.f3"):
                self.signals.toggle_settings.emit()
            elif key_str == self.settings.config.get("hotkey_sniper", "Key.f4"):
                self.signals.toggle_sniper.emit()
        
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
    
    def check_hardware(self):
        state = ctypes.windll.user32.GetAsyncKeyState(0x01)
        is_down = (state & 0x8000) != 0

        if is_down and not getattr(self, 'is_mouse_down', False):
            self.is_mouse_down = True
            self.signals.mouse_pressed.emit()
        elif not is_down and getattr(self, 'is_mouse_down', False):
            self.is_mouse_down = False
            self.signals.mouse_released.emit()
            
        # 2. WASD Check
        is_moving = False
        for key_code in (0x57, 0x41, 0x53, 0x44): # W, A, S, D
            if (ctypes.windll.user32.GetAsyncKeyState(key_code) & 0x8000) != 0:
                is_moving = True
                break
                
        if is_moving and not getattr(self, 'is_moving', False):
            self.is_moving = True
            self.overlay.on_move_start()
        elif not is_moving and getattr(self, 'is_moving', False):
            self.is_moving = False
            self.overlay.on_move_stop()

    def check_screen_color(self):
        if not self.settings.config.get("smart_color", False):
            return

        screen = self.app.primaryScreen()
        if not screen: return

        cx = screen.size().width() // 2
        cy = screen.size().height() // 2

        pixmap = screen.grabWindow(0, cx, cy, 1, 1)
        image = pixmap.toImage()
        pixel_color = image.pixelColor(0, 0)

        r = 255 - pixel_color.red()
        g = 255 - pixel_color.green()
        b = 255 - pixel_color.blue()

        if 100 < r < 155 and 100 < g < 155 and 100 < b < 155:
            r, g, b = 255, 0, 0
        
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.overlay.config["color"] = hex_color
        self.overlay.repaint()

        self.settings.color_btn.setStyleSheet(f"background-color: {hex_color}; color: black;")

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    crossforge = CrossForgeApp()
    crossforge.run()
import sys
from PyQt6.QtWidgets import QApplication
from overlay import CrosshairOverlay
from settings import SettingsWindow

def main():
    app = QApplication(sys.argv)

    overlay = CrosshairOverlay()

    settings = SettingsWindow(overlay.config)

    settings.config_changed.connect(overlay.update_config)

    overlay.show()
    settings.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
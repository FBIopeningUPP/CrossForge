import sys
from PyQt6.QtWidgets import QApplication
from overlay import CrosshairOverlay

def main():
    app = QApplication(sys.argv)

    overlay = CrosshairOverlay()

    overlay.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
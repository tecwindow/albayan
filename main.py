import sys
import os
# Change the working dir to current dir
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(current_dir)
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from ui.quran_interface import QuranInterface

def main():
    try:
        app = QApplication(sys.argv)
        main_window = QuranInterface()
        main_window.show()
        main_window.setFocus()
        QTimer.singleShot(200, main_window.quran_view.setFocus)
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "Error", str(e))

if __name__ == "__main__":
    main()

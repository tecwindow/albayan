import sys
import os
from multiprocessing import freeze_support
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from ui.quran_interface import QuranInterface
from utils.update import UpdateManager
from utils.settings import SettingsManager
from utils.const import program_name
from utils.logger import Logger

def main():
    try:
        app = QApplication(sys.argv)
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        main_window = QuranInterface(program_name)
        main_window.show()
        main_window.setFocus()
        QTimer.singleShot(500, main_window.quran_view.setFocus)
        main_window.check_auto_update()
        sys.exit(app.exec())
    except Exception as e:
        print(e)
        Logger.error(str(e))
        QMessageBox.critical(None, "Error", "حدث خطأ. يرجى الاتصال بالدعم للحصول على المساعدة.")

if __name__ == "__main__":
    freeze_support()
    main()

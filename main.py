import sys
import os
from multiprocessing import freeze_support
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt, QSharedMemory
from ui.quran_interface import QuranInterface
from utils.update import UpdateManager
from utils.settings import SettingsManager
from utils.const import program_name
from utils.logger import Logger
from utils.sound_Manager import BasmalaManager

class SingleInstanceApplication(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared_memory = QSharedMemory("Albayan")
        self.is_running = self.shared_memory.attach()

        if not self.is_running:
            self.shared_memory.create(1)
        elif self.is_running:
            print("Another instance of the application is already running.")
            sys.exit(0)

    def __del__(self):
        if not self.is_running:
            self.shared_memory.detach()

def call_after_starting(parent: QuranInterface) -> None:
    # Play sound effect with starting
    basmala_manager = BasmalaManager("Audio/basmala")
    basmala_manager.play()

    # Check auto update
    check_update_enabled = SettingsManager.current_settings["general"]["check_update_enabled"]
    update_manager = UpdateManager(parent, check_update_enabled)
    update_manager.check_auto_update()

    # Accessibility improvement
    parent.setFocus()
    QTimer.singleShot(500, parent.quran_view.setFocus)

def main():
    try:
        app = SingleInstanceApplication(sys.argv)
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        main_window = QuranInterface(program_name)
        main_window.show()
        call_after_starting(main_window)
        sys.exit(app.exec())
    except Exception as e:
        print(e)
        Logger.error(str(e))
        QMessageBox.critical(None, "Error", "حدث خطأ. يرجى الاتصال بالدعم للحصول على المساعدة.")

if __name__ == "__main__":
    freeze_support()
    main()

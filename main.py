import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer, Qt, QSharedMemory
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from ui.quran_interface import QuranInterface
from utils.update import UpdateManager
from utils.settings import SettingsManager
from utils.const import program_name
from utils.logger import Logger
from utils.sound_Manager import BasmalaManager

class SingleInstanceApplication(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName(program_name)
        self.server_name = "Albayan"
        self.local_server = QLocalServer(self)

        self.shared_memory = QSharedMemory("Albayan")
        self.is_running = self.shared_memory.attach()

        if not self.is_running:
            if not self.shared_memory.create(1):
                print(f"Failed to create shared memory segment: {self.shared_memory.errorString()}")
                sys.exit(1)
            self.setup_local_server()
        else:
            self.notify_existing_instance()
            sys.exit(0)

    def setup_local_server(self):
        if not self.local_server.listen(self.server_name):
            print(f"Failed to start local server: {self.local_server.errorString()}")
            sys.exit(1)
        self.local_server.newConnection.connect(self.handle_new_connection)

    def notify_existing_instance(self):
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)
        if socket.waitForConnected(1000):
            socket.write(b"SHOW")
            socket.flush()
            socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
        else:
            print("Failed to connect to existing instance.")

    def handle_new_connection(self):
        socket = self.local_server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: self.read_message(socket))

    def read_message(self, socket):
        message = socket.readAll().data().decode()
        if message == "SHOW" and hasattr(self, 'main_window'):
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
                print(message)
                socket.disconnectFromServer()

    def set_main_window(self, main_window):
        self.main_window = main_window
class SystemTrayManager:
    def __init__(self, app, main_window):
        self.tray_icon = QSystemTrayIcon(QIcon("icon.webp"), app)
        self.tray_icon.setToolTip(program_name)

        self.main_window = main_window
        
        tray_menu = QMenu()
        show_action = QAction("Show", app)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", app)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_main_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def quit_application(self):
        self.tray_icon.hide()
        QApplication.quit()

def call_after_starting(parent: QuranInterface) -> None:
    try:
        basmala_manager = BasmalaManager("Audio/basmala")
        basmala_manager.play()

        check_update_enabled = SettingsManager.current_settings["general"].get("check_update_enabled", False)
        update_manager = UpdateManager(parent, check_update_enabled)
        update_manager.check_auto_update()

        parent.setFocus()
        QTimer.singleShot(500, parent.quran_view.setFocus)
    except Exception as e:
        Logger.error(f"Error in call_after_starting: {str(e)}")
        QMessageBox.critical(parent, "Error", f"حدث خطأ: {e}")

def main():
    try:
        app = SingleInstanceApplication(sys.argv)
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        main_window = QuranInterface(program_name)
        app.set_main_window(main_window)

        main_window.show()
        tray_manager = SystemTrayManager(app, main_window)
        call_after_starting(main_window)
        sys.exit(app.exec())
    except Exception as e:
        print(e)
        Logger.error(str(e))
        QMessageBox.critical(None, "Error", "حدث خطأ. يرجى الاتصال بالدعم للحصول على المساعدة.")

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()

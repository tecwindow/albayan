import sys
import os
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(current_dir)

from multiprocessing import freeze_support
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt, QSharedMemory, QEvent
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from ui.quran_interface import QuranInterface
from core_functions.athkar.athkar_scheduler import AthkarScheduler
from utils.update import UpdateManager
from utils.settings import Config
from utils.const import program_name, program_icon, user_db_path
from utils.logger import Logger
from utils.audio_player import StartupSoundEffectPlayer, VolumeController

Logger.initialize_logger()
Config.load_settings()

class SingleInstanceApplication(QApplication):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        app_id = "Albayan" if sys.argv[0].endswith(".exe") else "Albayan_Source"
        self.setApplicationName(program_name)
        self.server_name = app_id
        self.local_server = QLocalServer(self)
        self.shared_memory = QSharedMemory(app_id)
        self.is_running = self.shared_memory.attach()
        self.volume_controller = VolumeController()
        self.installEventFilter(self) 

        if not self.is_running:
            if not self.shared_memory.create(1):
                Logger.error(f"Failed to create shared memory segment: {self.shared_memory.errorString()}")
                sys.exit(1)
            self.setup_local_server()
        else:
            self.notify_existing_instance()
            sys.exit(0)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            modifiers = event.modifiers()

            if key == Qt.Key.Key_F5:
                self.volume_controller.switch_category("next")
                return True
            elif key == Qt.Key.Key_F6:
                self.volume_controller.switch_category("previous")
                return True
            elif key == Qt.Key.Key_F7:
                if modifiers & Qt.KeyboardModifier.ControlModifier:  # Ctrl+F7
                    self.volume_controller.adjust_volume(-10)
                elif modifiers & Qt.KeyboardModifier.ShiftModifier:  # Shift+F7
                    self.volume_controller.adjust_volume(-5)
                elif modifiers & Qt.KeyboardModifier.AltModifier:  # Alt+F7
                    self.volume_controller.adjust_volume(-100)
                else:  # F7
                    self.volume_controller.adjust_volume(-1)
                return True
            elif key == Qt.Key.Key_F8:
                if modifiers & Qt.KeyboardModifier.ControlModifier:  # Ctrl+F8
                    self.volume_controller.adjust_volume(10)
                elif modifiers & Qt.KeyboardModifier.ShiftModifier:  # Shift+F8
                    self.volume_controller.adjust_volume(5)
                elif modifiers & Qt.KeyboardModifier.AltModifier:  # Alt+F8
                    self.volume_controller.adjust_volume(100)
                else:
                    self.volume_controller.adjust_volume(1)  # Default behavior (no modifiers)
                return True

        return super().eventFilter(obj, event)

    def setup_local_server(self) -> None:
        if not self.local_server.listen(self.server_name):
            Logger.error(f"Failed to start local server: {self.local_server.errorString()}")
            sys.exit(1)
        self.local_server.newConnection.connect(self.handle_new_connection)

    def notify_existing_instance(self) -> None:
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)
        if socket.waitForConnected(1000):
            socket.write(b"SHOW")
            socket.flush()
            socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
        else:
            Logger.error("Failed to connect to existing instance.")

    def handle_new_connection(self) -> None:
        socket = self.local_server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: self.read_message(socket))

    def read_message(self, socket) -> None:
        message = socket.readAll().data().decode()
        if message == "SHOW" and hasattr(self, 'main_window'):
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
                socket.disconnectFromServer()

    def set_main_window(self, main_window) -> None:
        self.main_window = main_window

def call_after_starting(parent: QuranInterface) -> None:
        
    basmala = StartupSoundEffectPlayer("Audio/basmala")
    basmala.play()

    check_update_enabled = getattr(Config.general, "check_update_enabled", False)
    update_manager = UpdateManager(parent, check_update_enabled)
    update_manager.check_auto_update()

    parent.setFocus()
    QTimer.singleShot(500, parent.quran_view.setFocus)
    

def main():
    try:
        app = SingleInstanceApplication(sys.argv)
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        main_window = QuranInterface(program_name)
        app.set_main_window(main_window)
        if "--minimized" not in sys.argv:
            main_window.show()
        call_after_starting(main_window)
        sys.exit(app.exec())
    except Exception as e:
        Logger.error(str(e))
        msg_box = QMessageBox(None)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("خطأ")
        msg_box.setText("حدث خطأ، إذا استمرت المشكلة، يرجى تفعيل السجل وتكرار الإجراء الذي تسبب بالخطأ ومشاركة رمز الخطأ والسجل مع المطورين.")

        ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()

        
if __name__ == "__main__":    
    freeze_support()
    main()

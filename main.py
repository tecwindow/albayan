# -*- coding: utf-8 -*-
import sys
import os

#set PYTHONPATH to the current directory
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(current_dir)

from utils.const import program_name, program_english_name, program_version, program_icon, user_db_path, CONFIG_PATH, LOG_PATH, dev_mode
from utils.settings import Config
from utils.logger import LogLevel, LoggerManager

#load the config file
Config.load_settings()
#setup the logger
LoggerManager.setup_logger(
    log_file=LOG_PATH, 
    log_level=LogLevel.from_name(Config.general.log_level),
    dev_mode=dev_mode
    )
logger = LoggerManager.get_logger(__name__)
logger.info(f"Starting {program_name}, {program_english_name}, version {program_version}...")

from multiprocessing import freeze_support
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt, QSharedMemory, QEvent
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from ui.quran_interface import QuranInterface
from core_functions.athkar.athkar_scheduler import AthkarScheduler
from utils.update import UpdateManager
from utils.audio_player import StartupSoundEffectPlayer, VolumeController


class SingleInstanceApplication(QApplication):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        app_id = "Albayan" if sys.argv[0].endswith(".exe") else "Albayan_Source"
        logger.debug("running from source." if app_id == "Albayan_Source" else "running from exe file.")
        self.setApplicationName(program_name)
        self.server_name = app_id
        logger.debug(f"Application ID: {app_id}")
        logger.debug(f"Server name: {self.server_name}")
        self.local_server = QLocalServer(self)
        self.shared_memory = QSharedMemory(app_id)
        self.is_running = self.shared_memory.attach()
        self.volume_controller = VolumeController()
        self.installEventFilter(self) 

        if not self.is_running:
            logger.debug("No previous instance detected, creating shared memory...")
            if not self.shared_memory.create(1):
                logger.error(f"Failed to create shared memory segment: {self.shared_memory.errorString()}", exc_info=True)
                sys.exit(1)
            self.setup_local_server()
        else:
            logger.warning("An existing instance is already running. Notifying it...")
            self.notify_existing_instance()
            sys.exit(0)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            modifiers = event.modifiers()

            if key == Qt.Key.Key_F5:
                logger.debug("F5 pressed: Switching to previous volume category.")
                self.volume_controller.switch_category("previous")
                return True
            elif key == Qt.Key.Key_F6:
                logger.debug("F6 pressed: Switching to next volume category.")
                self.volume_controller.switch_category("next")
                return True
            elif key == Qt.Key.Key_F7:
                volume_change = -1
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    volume_change = -10
                elif modifiers & Qt.KeyboardModifier.ShiftModifier:
                    volume_change = -5
                elif modifiers & Qt.KeyboardModifier.AltModifier:
                    volume_change = -100
                
                logger.debug(f"F7 pressed: Decreasing volume by {abs(volume_change)}.")
                self.volume_controller.adjust_volume(volume_change)
                return True
            elif key == Qt.Key.Key_F8:
                volume_change = 1
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    volume_change = 10
                elif modifiers & Qt.KeyboardModifier.ShiftModifier:
                    volume_change = 5
                elif modifiers & Qt.KeyboardModifier.AltModifier:
                    volume_change = 100
                
                logger.debug(f"F8 pressed: Increasing volume by {volume_change}.")
                self.volume_controller.adjust_volume(volume_change)
                return True

        return super().eventFilter(obj, event)

    def setup_local_server(self) -> None:
        logger.debug(f"Starting local server with name: {self.server_name}")
        if not self.local_server.listen(self.server_name):
            logger.error(f"Failed to start local server: {self.local_server.errorString()}", exc_info=True)
            sys.exit(1)
        self.local_server.newConnection.connect(self.handle_new_connection)

    def notify_existing_instance(self) -> None:
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)
        if socket.waitForConnected(1000):
            logger.debug("Connected to existing instance, sending 'SHOW' message.")
            socket.write(b"SHOW")
            socket.flush()
            socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
        else:
            logger.error("Failed to connect to existing instance.", exc_info=True)

    def handle_new_connection(self) -> None:
        socket = self.local_server.nextPendingConnection()
        if socket:
            logger.debug("New connection received, reading message...")
            socket.readyRead.connect(lambda: self.read_message(socket))

    def read_message(self, socket) -> None:
        message = socket.readAll().data().decode()
        logger.debug(f"Received message: {message}")
        if message == "SHOW" and hasattr(self, 'main_window'):
                logger.debug("Activating main window.")
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
                logger.debug("Main window activated.")
                socket.disconnectFromServer()

    def set_main_window(self, main_window) -> None:
        self.main_window = main_window
        logger.debug("Main window set in SingleInstanceApplication.")

def call_after_starting(parent: QuranInterface) -> None:
    try:
        logger.debug("Playing basmala sound effect...")
        basmala = StartupSoundEffectPlayer("Audio/basmala")
        basmala.play()
        logger.info("Basmala sound effect played successfully.")

        check_update_enabled = getattr(Config.general, "check_update_enabled", False)
        logger.info(f"Check update enabled: {check_update_enabled}")

        update_manager = UpdateManager(parent, check_update_enabled)
        logger.debug("Checking for auto-update...")
        update_manager.check_auto_update()

        logger.debug("Setting focus to parent window...")
        parent.setFocus()
        logger.debug("Parent window focus set successfully.")

        logger.debug("Setting focus to Quran view after a short delay...")
        QTimer.singleShot(500, parent.quran_view.setFocus)
        logger.debug("Focus to Quran view will be set after 500ms.")

    except Exception as e:
        logger.error(f"Error in call_after_starting: {str(e)}", exc_info=True)

def main():
    try:
        app = SingleInstanceApplication(sys.argv)
        logger.info("QApplication initialized successfully.")
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        logger.info("Layout direction set to RightToLeft.")
        main_window = QuranInterface(program_name)
        logger.info("Main window initialized successfully.")
        app.set_main_window(main_window)
        if "--minimized" not in sys.argv:
            logger.info("Application started in normal mode, showing main window.")
            main_window.show()
        else:
            logger.info("Application started minimized, not showing main window.")
        call_after_starting(main_window)
        logger.debug("Post-startup actions executed successfully.")
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        msg_box = QMessageBox(None)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("خطأ")
        msg_box.setText("حدث خطأ، إذا استمرت المشكلة، يرجى تفعيل السجل وتكرار الإجراء الذي تسبب بالخطأ ومشاركة رمز الخطأ والسجل مع المطورين.")

        ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()

        
if __name__ == "__main__":    
    freeze_support()
    main()

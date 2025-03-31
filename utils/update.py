import requests
from threading import Thread
from packaging import version
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from utils.logger import LoggerManager
from utils.settings import Config
from utils.const import program_name, program_version
from ui.dialogs.update_dialog import UpdateDialog
from exceptions.base import ErrorMessage

logger = LoggerManager.get_logger(__name__)

class UpdateChecker(QThread):
    update_available = pyqtSignal(dict)
    update_error = pyqtSignal(str)
    session = requests.Session()
    url = "https://raw.githubusercontent.com/tecwindow/albayan/main/info.json"
    
    def __init__(self):
        super().__init__()

    def run(self):
        try:
            logger.info("Attempting to check for updates...")
            response = UpdateChecker.session.get(UpdateChecker.url)
            response.raise_for_status()
            info = response.json()
            logger.info("Update check completed successfully.")
            self.update_available.emit(info)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error occurred: {ErrorMessage(e)}", exc_info=True)
            self.update_error.emit("لا يوجد اتصال بالإنترنت.")
        except Exception as e:
            logger.error(f"Error during the update check: {ErrorMessage(e)}", exc_info=True)
            self.update_error.emit("حدث خطأ أثناء الاتصال بالخادم.")


class UpdateManager:
    def __init__(self, parent, auto_update=False):
        self.parent = parent
        self.auto_update = auto_update
        logger.info(f"UpdateManager initialized with auto_update set to {self.auto_update}")

    def check_auto_update(self) -> None:
        try:
            logger.info("Checking for automatic updates...")
            if self.auto_update:
                self.check_updates()
            else:
                # Make one request in thread to open session
                logger.info("Making a background request to open session for update check.")
                Thread(target=UpdateChecker.session.get, kwargs={'url': UpdateChecker.url}, daemon=True).start()
        except Exception as e:
            logger.error(f"Error in check_auto_update: {ErrorMessage(e)}", exc_info=True)

    def check_updates(self):
        try:
            logger.info("Starting the update check process...")
            self.update_checker = UpdateChecker()
            self.update_checker.update_available.connect(lambda info: self.on_update_available(info))
            self.update_checker.update_error.connect(lambda error: self.on_update_error(error))
            self.update_checker.start()
        except Exception as e:
            logger.error(f"Error during updates check: {ErrorMessage(e)}", exc_info=True)


    def on_update_available(self, info:dict):
        """Checks for updates and notifies the user if an update is available."""
        try:
            logger.info("Update available detected, checking version...")
            latest_version = info.get("latest_version")
            if version.parse(latest_version) > version.parse(program_version):
                language = getattr(Config.general, "language", "Arabic")
                release_notes = info.get("release_notes", {}).get(language, info["release_notes"].get("Arabic", ""))
                download_url = info.get("download_url")
                logger.info(f"A new version {latest_version} is available. Displaying update dialog...")
                self.show_update_dialog(release_notes, download_url, latest_version)
            else:
                logger.info(f"Already on the latest version {program_version}. Displaying no update dialog.")
                self.show_no_update_dialog()
        except Exception as e:
            logger.error(f"Error in on_update_available: {ErrorMessage(e)}", exc_info=True)


    def on_update_error(self, error_message):
        try:
            logger.error(f"Update error: {error_message}")
            if not self.auto_update:
                msg_box = QMessageBox(self.parent)
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setWindowTitle("خطأ")
                msg_box.setText(error_message)

                ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
                msg_box.exec()
        except Exception as e:
            logger.error(f"Error in on_update_error: {ErrorMessage(e)}", exc_info=True)



    def show_update_dialog(self, release_notes, download_url, latest_version):
        try:
            logger.info("Displaying update dialog for new version...")
            UpdateDialog(self.parent, release_notes, download_url, latest_version).exec()
        except Exception as e:
            logger.error(f"Error in show_update_dialog: {ErrorMessage(e)}", exc_info=True)

    def show_no_update_dialog(self):
        try:
            if not self.auto_update:
                logger.info(f"No update found, displaying 'no update' dialog for version {program_version}.")
                msg_box = QMessageBox(self.parent)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setWindowTitle("لا يوجد تحديث.")
                msg_box.setText(f"أنت تستخدم {program_name} الإصدار {program_version}, وهو الإصدار الأحدث.")

                ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
                msg_box.exec()
        except Exception as e:
            logger.error(f"Error in show_no_update_dialog: {ErrorMessage(e)}", exc_info=True)

            
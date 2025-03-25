import requests
from threading import Thread
from packaging import version
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from utils.logger import Logger
from utils.settings import Config
from utils.const import program_name, program_version
from ui.dialogs.update_dialog import UpdateDialog
from exceptions.base import ErrorMessage


class UpdateChecker(QThread):
    update_available = pyqtSignal(dict)
    update_error = pyqtSignal(str)
    session = requests.Session()
    url = "https://raw.githubusercontent.com/tecwindow/albayan/main/info.json"
    
    def __init__(self):
        super().__init__()

    def run(self):
        try:
            response = UpdateChecker.session.get(UpdateChecker.url)
            response.raise_for_status()
            info = response.json()
            self.update_available.emit(info)
        except requests.exceptions.ConnectionError as e:
            Logger.error(ErrorMessage(e))
            self.update_error.emit("لا يوجد اتصال بالإنترنت.")
        except Exception as e:
            Logger.error(ErrorMessage(e))
            self.update_error.emit("حدث خطأ أثناء الاتصال بالخادم.")


class UpdateManager:
    def __init__(self, parent, auto_update=False):
        self.parent = parent
        self.auto_update = auto_update

    def check_auto_update(self) -> None:
        if self.auto_update:
            self.check_updates()
        else:
            # Make one request in thread to open session
            Thread(target=UpdateChecker.session.get, kwargs={'url': UpdateChecker.url}, daemon=True).start()

    def check_updates(self):
        self.update_checker = UpdateChecker()
        self.update_checker.update_available.connect(lambda info: self.on_update_available(info))
        self.update_checker.update_error.connect(lambda error: self.on_update_error(error))
        self.update_checker.start()

    def on_update_available(self, info:dict):
        """Checks for updates and notifies the user if an update is available."""
        latest_version = info.get("latest_version")
        if version.parse(latest_version) > version.parse(program_version):
            language = getattr(Config.general, "language", "Arabic")
            release_notes = info.get("release_notes", {}).get(language, info["release_notes"].get("Arabic", ""))
            download_url = info.get("download_url")
            self.show_update_dialog(release_notes, download_url, latest_version)
        else:
            self.show_no_update_dialog()

    def on_update_error(self, error_message):
        if not self.auto_update:
            msg_box = QMessageBox(self.parent)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("خطأ")
            msg_box.setText(error_message)

            ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
            msg_box.exec()

    def show_update_dialog(self, release_notes, download_url, latest_version):
        UpdateDialog(self.parent, release_notes, download_url, latest_version).exec()

    def show_no_update_dialog(self):
        if not self.auto_update:
            msg_box = QMessageBox(self.parent)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("لا يوجد تحديث.")
            msg_box.setText(f"أنت تستخدم {program_name} الإصدار {program_version}, وهو الإصدار الأحدث.")

            ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
            msg_box.exec()


import requests
from threading import Thread
from packaging import version
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from utils.logger import Logger
from utils.settings import SettingsManager
from utils.const import program_name, program_version
from ui.dialogs.update_dialog import UpdateDialog


class UpdateChecker(QThread):
    update_available = pyqtSignal(dict)
    update_error = pyqtSignal(str)
    session = requests.Session()
    url = "https://dl.tecwindow.net/info.json"
    
    def __init__(self):
        super().__init__()

    def run(self):
        try:
            response = UpdateChecker.session.get(UpdateChecker.url)
            response.raise_for_status()
            info = response.json()
            self.update_available.emit(info)
        except requests.exceptions.ConnectionError as e:
            Logger.error(str(e))
            self.update_error.emit("There is no internet connection.")
        except Exception as e:
            Logger.error(str(e))
            self.update_error.emit("An error occurred while connecting to the server.")


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
            language = SettingsManager.current_settings["general"].get("language", "Arabic")
            release_notes = info.get("release_notes", {}).get(language, info["release_notes"].get("Arabic", ""))
            download_url = info.get("download_url")
            self.show_update_dialog(release_notes, download_url, latest_version)
        else:
            self.show_no_update_dialog()

    def on_update_error(self, error_message):
        if not self.auto_update:
            QMessageBox.critical(self.parent, "Error", error_message)

    def show_update_dialog(self, release_notes, download_url, latest_version):
        UpdateDialog(self.parent, release_notes, download_url, latest_version).exec()

    def show_no_update_dialog(self):
        if not self.auto_update:
            QMessageBox.information(self.parent, "No update available", f"You are using {program_name} version {program_version}, which is the latest version.")


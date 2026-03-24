import requests
import subprocess
import os
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressDialog,
    QMessageBox,
    QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut
from core_functions.downloader import DownloadManager
from core_functions.downloader.status import DownloadProgress
from ui.widgets.qText_edit import ReadOnlyTextEdit
from utils.const import program_name, Globals
from utils.universal_speech import UniversalSpeech
from utils.paths import paths, is_portable, get_current_app_dir
from utils.logger import LoggerManager
import qtawesome as qta

logger = LoggerManager.get_logger(__name__)

class UpdateDialog(QDialog):

    # Remove the files in temp folder
    for file in os.listdir(paths.temp_folder):
        file_path = os.path.join(paths.temp_folder,file )
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Deleted temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not delete temporary file {file_path}: {e}")
        del file_path

    def __init__(self, parent, release_notes, download_url, latest_version):
        super().__init__(parent)
        self.download_url = download_url
        self.setWindowTitle("تحديث متاح")
        self.resize(400, 300)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        logger.debug(f"Opening update dialog for version {latest_version}")

        self.latest_version = latest_version
        self.label1_text = "{} الإصدار {} متاح.".format(program_name, latest_version)
        self.label2_text = "ما الجديد في الإصدار {}؟".format(latest_version)

        layout = QVBoxLayout()

        self.groupBox = QGroupBox(self)
        self.groupBox.setObjectName("groupBox")

        group_layout = QVBoxLayout(self.groupBox)

        label1 = QLabel(self.label1_text, self.groupBox)
        label2 = QLabel(self.label2_text, self.groupBox)

        self.release_notes_edit = ReadOnlyTextEdit(self.groupBox)
        self.release_notes_edit.setAccessibleName(label2.text())
        self.release_notes_edit.setText(release_notes)

        group_layout.addWidget(label1)
        group_layout.addWidget(label2)
        group_layout.addWidget(self.release_notes_edit)

        layout.addWidget(self.groupBox)

        buttons_layout = QHBoxLayout()
        self.update_button = QPushButton("تحديث")
        self.update_button.setDefault(True)
        self.update_button.setIcon(qta.icon("mdi.update"))

        self.copy_button = QPushButton("نسخ معلومات التحديث")
        self.copy_button.setIcon(qta.icon("fa5s.copy"))
        self.copy_button.setShortcut(QKeySequence("Shift+C"))
        self.copy_button.clicked.connect(self.copy_update_info)

        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))
        self.cancel_button.setIcon(qta.icon("fa5s.times"))

        self.update_button.clicked.connect(self.on_update)
        self.cancel_button.clicked.connect(self.reject)
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)

        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.copy_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.setFocus()
        QTimer.singleShot(300, self.release_notes_edit.setFocus)
        logger.debug("Update dialog initialized.")

    def on_update(self):
        logger.debug("Clicked update button.")
        self.progress_dialog = QProgressDialog("جارٍ التحديث...", "إغلاق", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.progress_dialog.setWindowTitle("يجري التحديث")
        self.progress_dialog.canceled.connect(self.on_cancel)
        self.progress_dialog.show()

        self.downloader = DownloadManager()
        self.downloader.add_download(self.download_url, paths.temp_folder)
        self.downloader.download_progress.connect(self.on_download_progress)
        self.downloader.download_finished.connect(self.on_download_finished)
        self.downloader.start()
        logger.info("Download thread started.")

    def on_download_progress(self, progress: DownloadProgress):
        self.progress_dialog.setValue(progress.percentage)
        self.progress_dialog.setLabelText(
            f"تم تنزيل {progress.downloaded_str} من {progress.total_str}\n"
        f"السرعة: {progress.speed_kbps:.2f} KB/s | الوقت المنقضي: {progress.elapsed_time_str} | الوقت المتبقي: {progress.remaining_time_str}"
    )

    def on_download_finished(self, download_id, file_path: str):
        logger.info(f"Download finished. Starting installation: {file_path}")
        self.progress_dialog.hide()
        try:
            if is_portable():
                subprocess.Popen([file_path, "/SILENT", "/PORTABLE", f"/DIR={get_current_app_dir()}", "/NOCANCEL", "/SUPPRESSMSGBOXES", "/NORESTART"])
            else:
                subprocess.Popen([file_path, "/SILENT", "/NOCANCEL", "/SUPPRESSMSGBOXES", "/NORESTART"])
            logger.info("Installer started successfully.")
            QApplication.exit()
            logger.info("Application exited after installation.")
        except Exception as e:
            logger.error(f"Failed to start installer: {e}", exc_info=True)

    def on_cancel(self):
        logger.debug("User canceled the update process.")
        self.downloader.cancel_all()
        self.progress_dialog.hide()
        self.reject()

    def reject(self):
        self.deleteLater()

    def closeEvent(self, event):
        logger.debug("Close event triggered.")
        return super().closeEvent(event)


    def copy_update_info(self):
        logger.debug("User requested to copy update information.")

        release_notes_text = self.release_notes_edit.toPlainText()

        final_text = (
            f"{self.label1_text}\n"
            f"{self.label2_text}\n\n"
            f"{release_notes_text}"
        )

        clipboard = QApplication.clipboard()
        clipboard.setText(final_text)

        UniversalSpeech.say(
            f"تم نسخ معلومات التحديث للإصدار {self.latest_version}."
        )

        Globals.effects_manager.play("copy")
        logger.info("Update information copied successfully.")

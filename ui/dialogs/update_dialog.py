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
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut
from ui.widgets.qText_edit import ReadOnlyTextEdit
from utils.const import program_name, temp_folder
from utils.logger import LoggerManager
import qtawesome as qta

logger = LoggerManager.get_logger(__name__)

class UpdateDialog(QDialog):

    # Remove the files in temp folder
    for file in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder,file )
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


        layout = QVBoxLayout()

        self.groupBox = QGroupBox(self)
        self.groupBox.setObjectName("groupBox")

        group_layout = QVBoxLayout(self.groupBox)

        label1 = QLabel("{} الإصدار {} متاح.".format(program_name, latest_version), self.groupBox)
        label2 = QLabel("ما الجديد في الإصدار {}؟".format(latest_version), self.groupBox)

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

        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))
        self.cancel_button.setIcon(qta.icon("fa.times"))


        self.update_button.clicked.connect(self.on_update)
        self.cancel_button.clicked.connect(self.reject)
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)

        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.setFocus()
        QTimer.singleShot(300, self.release_notes_edit.setFocus)

    def on_update(self):
        logger.debug("Clicked update button.")
        self.progress_dialog = QProgressDialog("جارٍ التحديث...", "إغلاق", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.progress_dialog.setWindowTitle("يجري التحديث")
        self.progress_dialog.canceled.connect(self.on_cancel)
        self.progress_dialog.show()

        self.download_thread = DownloadThread(self.download_url)
        self.download_thread.download_progress.connect(self.progress_dialog.setValue)
        self.download_thread.download_finished.connect(self.on_download_finished)
        self.download_thread.start()

    def on_download_finished(self, file_path):
        logger.info(f"Download finished. Starting installation: {file_path}")
        self.progress_dialog.hide()
        try:
            subprocess.Popen([file_path, "/SILENT", "/NOCANCEL", "/SUPPRESSMSGBOXES", "/NORESTART"])
            logger.info("Installer started successfully.")
            QApplication.exit()
            logger.info("Application exited after installation.")
        except Exception as e:
            logger.error(f"Failed to start installer: {e}", exc_info=True)


    def on_cancel(self):
        logger.debug("User canceled the update process.")
        self.download_thread.terminate()
        self.progress_dialog.hide()
        self.reject()


class DownloadThread(QThread):
    download_progress = pyqtSignal(int)
    download_finished = pyqtSignal(str)

    def __init__(self, download_url):
        super().__init__()
        self.download_url = download_url

    def run(self):
        file_name = self.download_url.split('/')[-1]
        file_path = os.path.join(temp_folder, file_name)
        logger.info(f"Starting download: {self.download_url}")
        try:
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0

            with open(file_path, 'wb') as file:
                for data in response.iter_content(chunk_size=4096):
                    bytes_downloaded += len(data)
                    file.write(data)
                    progress = int(bytes_downloaded * 100 / total_size)
                    self.download_progress.emit(progress)
                    logger.debug(f"Download progress: {progress}%")

            logger.info(f"Download completed successfully: {file_path}")
            self.download_finished.emit(file_path)

        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to update server.")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred while downloading: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}", exc_info=True)

            
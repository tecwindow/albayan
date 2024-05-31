import requests
import subprocess
import os
from threading import Thread
from packaging import version
from PyQt6.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QPushButton,  
    QProgressDialog, 
    QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from ui.widgets.qText_edit import ReadOnlyTextEdit
from utils.const import program_name, temp_folder

class UpdateDialog(QDialog):
    def __init__(self, parent, release_notes, download_url, latest_version):
        super().__init__(parent)
        self.download_url = download_url
        self.setWindowTitle("تحديث متاح")
        self.setFixedSize(400, 300)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout()
        label1 = QLabel("{} الإصدار {} متاح.".format(program_name, latest_version))
        label2 = QLabel("ما الجديد في الإصدار {}؟".format(latest_version))

        self.release_notes_edit = ReadOnlyTextEdit(self)
        self.release_notes_edit.setAccessibleName(label2.text())
        self.release_notes_edit.setText(release_notes)

        buttons_layout = QHBoxLayout()
        self.update_button = QPushButton("تحديث")
        self.cancel_button = QPushButton("إلغاء")

        self.update_button.clicked.connect(self.on_update)
        self.cancel_button.clicked.connect(self.reject)

        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(self.release_notes_edit)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.setFocus()
        QTimer.singleShot(300, self.release_notes_edit.setFocus)

    def on_update(self):
        self.progress_dialog = QProgressDialog("Updating...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.progress_dialog.setWindowTitle("يجري التحديث")
        self.progress_dialog.canceled.connect(self.on_cancel)
        self.progress_dialog.show()

        self.download_thread = DownloadThread(self.download_url)
        self.download_thread.download_progress.connect(self.progress_dialog.setValue)
        self.download_thread.download_finished.connect(self.on_download_finished)
        self.download_thread.start()

    def on_download_finished(self, file_path):
        self.progress_dialog.hide()
        subprocess.run([file_path, "/SILENT", "/NOCANCEL", "/SUPPRESSMSGBOXES", "/NORESTART"])
        self.accept()

    def on_cancel(self):
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
        response = requests.get(self.download_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        bytes_downloaded = 0

        with open(file_path, 'wb') as file:
            for data in response.iter_content(chunk_size=4096):
                bytes_downloaded += len(data)
                file.write(data)
                progress = int(bytes_downloaded * 100 / total_size)
                self.download_progress.emit(progress)

        self.download_finished.emit(file_path)


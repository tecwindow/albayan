import os
import qtawesome as qta
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QSlider, QWidget, QMainWindow
)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt
from core_functions.Reciters import SurahReciter
from core_functions.quran_class import QuranConst
from ui.widgets.toolbar import AudioPlayerThread
from utils.const import data_folder
from utils.audio_player import SurahPlayer


class SuraPlayerWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("مشغل القرآن")
        self.resize(600, 400)
        self.reciters = SurahReciter(data_folder / "quran" / "reciters.db")
        self.player = SurahPlayer()
        self.audio_player_thread = AudioPlayerThread(self.player, self)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.statusBar().showMessage("مرحبًا بك في مشغل القرآن")

        self.selection_group = QGroupBox("التحديدات")
        selection_layout = QHBoxLayout()

        self.reciter_label = QLabel("القارئ:")
        self.reciter_combo = QComboBox()
        self.reciter_combo.setAccessibleName(self.reciter_label.text())
        for row in self.reciters.get_reciters():
            display_text = f"{row['name']} - {row['rewaya']} - ({row['bitrate']} kbps)"
            self.reciter_combo.addItem(display_text, row["id"])

        self.surah_label = QLabel("السورة:")
        self.surah_combo = QComboBox()
        self.surah_combo.setAccessibleName(self.surah_label.text())
        for surah_name, surah_number in QuranConst.SURAS:
            self.surah_combo.addItem(surah_name, surah_number)

        selection_layout.addWidget(self.reciter_label)
        selection_layout.addWidget(self.reciter_combo)
        selection_layout.addWidget(self.surah_label)
        selection_layout.addWidget(self.surah_combo)
        self.selection_group.setLayout(selection_layout)

        control_layout = QHBoxLayout()
        self.rewind_button = QPushButton(qta.icon("fa.backward"), "")
        self.rewind_button.setAccessibleName("ترجيع")
        self.play_pause_button = QPushButton(qta.icon("fa.play"), "")
        self.play_pause_button.setAccessibleName("تشغيل")
        self.forward_button = QPushButton(qta.icon("fa.forward"), "")
        self.forward_button.setAccessibleName("تقديم")
        self.previous_surah_button = QPushButton(qta.icon("fa.step-backward"), "")
        self.previous_surah_button.setAccessibleName("السورة السابقة")
        self.next_surah_button = QPushButton(qta.icon("fa.step-forward"), "")
        self.next_surah_button.setAccessibleName("السورة التالية")
        self.volume_down_button = QPushButton(qta.icon("fa.volume-down"), "")
        self.volume_down_button.setAccessibleName("خفض الصوت")
        self.volume_up_button = QPushButton(qta.icon("fa.volume-up"), "")
        self.volume_up_button.setAccessibleName("رفع الصوت")

        control_layout.addWidget(self.volume_down_button)
        control_layout.addWidget(self.previous_surah_button)
        control_layout.addWidget(self.rewind_button)
        control_layout.addWidget(self.play_pause_button)
        control_layout.addWidget(self.forward_button)
        control_layout.addWidget(self.next_surah_button)
        control_layout.addWidget(self.volume_up_button)

        self.progress_group = QGroupBox("شريط التقدم")
        progress_layout = QVBoxLayout()
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setAccessibleName("TimeSlider")
        self.time_slider.setRange(0, 100)
        self.time_slider.setValue(0)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setAccessibleName("VolumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)

        self.elapsed_time_label = QLabel("0:00")
        self.remaining_time_label = QLabel("0:00")
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.elapsed_time_label)
        time_layout.addWidget(self.remaining_time_label)

        progress_layout.addWidget(self.time_slider)
        progress_layout.addWidget(QLabel("الصوت:"))
        progress_layout.addWidget(self.volume_slider)
        progress_layout.addLayout(time_layout)
        self.progress_group.setLayout(progress_layout)

        layout.addWidget(self.selection_group)
        layout.addLayout(control_layout)
        layout.addWidget(self.progress_group)

        self.reciter_combo.currentIndexChanged.connect(self.update_current_reciter)
        self.surah_combo.currentIndexChanged.connect(self.update_current_surah)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.forward_button.clicked.connect(self.forward)
        self.rewind_button.clicked.connect(self.rewind)
        self.volume_up_button.clicked.connect(lambda: self.player.increase_volume())
        self.volume_down_button.clicked.connect(lambda: self.player.decrease_volume())
        self.next_surah_button.clicked.connect(self.next_surah)
        self.previous_surah_button.clicked.connect(self.previous_surah)
        self.volume_slider.valueChanged.connect(self.update_volume)
        self.time_slider.valueChanged.connect(self.update_time)
        self.audio_player_thread.playback_time_changed.connect(self.OnUpdateTime)
        self.audio_player_thread.waiting_to_load.connect(self.set_buttons_status)

    def update_current_reciter(self):
        current_reciter = self.reciter_combo.currentText()
        self.statusBar().showMessage(f"القارئ الحالي: {current_reciter}")

    def update_current_surah(self):
        current_surah = self.surah_combo.currentText()
        self.statusBar().showMessage(f"السورة الحالية: {current_surah}")

    def toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_pause_button.setIcon(qta.icon("fa.play"))
            self.play_pause_button.setAccessibleName("تشغيل")
            self.statusBar().showMessage("إيقاف مؤقت")
        else:
            self.play_current_surah()
            self.play_pause_button.setIcon(qta.icon("fa.pause"))
            self.play_pause_button.setAccessibleName("إيقاف مؤقت")
            self.statusBar().showMessage("تشغيل")

    def play_current_surah(self) -> None:
        reciter_id = self.reciter_combo.currentData()
        surah_number = self.surah_combo.currentData()
        url = self.reciters.get_url(reciter_id, surah_number)
        self.audio_player_thread.set_audio_url(url)
        self.audio_player_thread.start()

    def forward(self):
        self.player.forward(seconds=1)

    def rewind(self):
        self.player.rewind(seconds=1)

    def next_surah(self):
        current_index = self.surah_combo.currentIndex()
        if current_index < self.surah_combo.count() - 1:
            self.surah_combo.setCurrentIndex(current_index + 1)
            self.play_current_surah()

    def previous_surah(self):
        current_index = self.surah_combo.currentIndex()
        if current_index > 0:
            self.surah_combo.setCurrentIndex(current_index - 1)
            self.play_current_surah()

    def update_volume(self):
        self.player.set_volume(self.volume_slider.value())

    def update_time(self, position):
        total_length = self.player.get_length()
        new_position = total_length * (position / 100)
        if not self.player.set_position(new_position):
            self.time_slider.blockSignals(True)
            current_position = self.player.get_position()
            self.time_slider.setValue(int((current_position / total_length) * 100))
            self.time_slider.blockSignals(False)

    def OnUpdateTime(self, position: float, length: float):
        if position and length:
            self.time_slider.blockSignals(True)
            position = int((position / length) * 100)
            self.time_slider.setValue(position)
            self.time_slider.blockSignals(False)
            self.elapsed_time_label.setText(self._format_time(position))
            self.remaining_time_label.setText(self._format_time(length - position))

    def _format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02}"

    def set_buttons_status(self, status: bool = 2) -> None:
        if status == True:
            self.audio_player_thread.timer.start()


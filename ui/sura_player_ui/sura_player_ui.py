import re
import os
from typing import List
import qtawesome as qta
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QSlider, QWidget, QMainWindow, QLineEdit
)
from core_functions.Reciters import SurahReciter
from core_functions.quran_class import QuranConst
from .FilterManager import Item, FilterManager
from ui.widgets.toolbar import AudioPlayerThread
from utils.const import data_folder
from utils.audio_player import SurahPlayer
from utils.universal_speech import UniversalSpeech


class SuraPlayerWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("مشغل القرآن")
        self.resize(600, 400)

        self.reciters = SurahReciter(data_folder / "quran" / "reciters.db")
        self.player = SurahPlayer()
        self.audio_player_thread = AudioPlayerThread(self.player, self)
        self.filter_manager = FilterManager()
        self.filter_mode = False
        self.search_text = ""

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.statusBar().showMessage("مرحبًا بك في مشغل القرآن")
        self.create_selection_group()
        self.create_control_buttons()
        self.create_progress_group()
        self.connect_signals()
        self.disable_focus()
        self.setup_shortcuts()
        

        layout.addWidget(self.selection_group)
        layout.addLayout(self.control_layout)
        layout.addWidget(self.progress_group)


    def create_selection_group(self):
        self.selection_group = QGroupBox("التحديدات")
        selection_layout = QHBoxLayout()

        self.reciter_label = QLabel("القارئ:")
        self.reciter_combo = QComboBox()
        self.reciter_combo.setAccessibleName(self.reciter_label.text())
        reciters_list = []
        for row in self.reciters.get_reciters():
            display_text = f"{row['name']} - {row['rewaya']} - ({row['type']}) - ({row['bitrate']} kbps)"
            self.reciter_combo.addItem(display_text, row["id"])
            reciters_list.append(Item(row["id"], display_text))

        self.filter_manager.set_category(1, "القارئ", reciters_list, self.reciter_combo)

        self.surah_label = QLabel("السورة:")
        self.surah_combo = QComboBox()
        self.surah_combo.setAccessibleName(self.surah_label.text())
        suras_list = []
        for surah_name, surah_number in QuranConst.SURAS:
            self.surah_combo.addItem(surah_name, surah_number)
            suras_list.append(Item(surah_number, surah_name))

        self.filter_manager.set_category(2, "السورة", suras_list, self.surah_combo)

        selection_layout.addWidget(self.reciter_label)
        selection_layout.addWidget(self.reciter_combo)
        selection_layout.addWidget(self.surah_label)
        selection_layout.addWidget(self.surah_combo)
        self.selection_group.setLayout(selection_layout)

    def create_control_buttons(self):
        self.control_layout = QHBoxLayout()
        self.rewind_button = QPushButton(qta.icon("fa.backward"), "")
        self.rewind_button.setAccessibleName("ترجيع")
        self.play_pause_button = QPushButton(qta.icon("fa.play"), "")
        self.play_pause_button.setAccessibleName("تشغيل")
        self.stop_button = QPushButton(qta.icon("fa.stop"), "")
        self.stop_button.setAccessibleName("إيقاف التشغيل")
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
        self.close_button = QPushButton(qta.icon("fa.window-close"), "")
        self.close_button.setAccessibleName("إغلاق المشغل")

        self.buttons = [
            self.volume_down_button, self.previous_surah_button, self.rewind_button,
            self.play_pause_button, self.stop_button, self.forward_button,
             self.next_surah_button, self.volume_up_button, self.close_button
        ]

        for button in self.buttons:
            self.control_layout.addWidget(button)

    def create_progress_group(self):
        self.progress_group = QGroupBox("شريط التقدم")
        progress_layout = QVBoxLayout()

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.setValue(0)
        self.time_slider.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.time_slider.setEnabled(False)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.player.volume)
        self.volume_slider.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

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

    def connect_signals(self):
        self.reciter_combo.currentIndexChanged.connect(self.update_current_reciter)
        self.surah_combo.currentIndexChanged.connect(self.update_current_surah)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.stop_button.clicked.connect(self.stop)
        self.forward_button.clicked.connect(self.forward)
        self.rewind_button.clicked.connect(self.rewind)
        self.volume_up_button.clicked.connect(lambda: self.player.increase_volume())
        self.volume_down_button.clicked.connect(lambda: self.player.decrease_volume())
        self.next_surah_button.clicked.connect(self.next_surah)
        self.previous_surah_button.clicked.connect(self.previous_surah)
        self.close_button.clicked.connect(self.on_close)
        self.volume_slider.valueChanged.connect(self.update_volume)
        self.time_slider.valueChanged.connect(self.update_time)

        self.audio_player_thread.playback_time_changed.connect(self.on_update_time)
        self.audio_player_thread.waiting_to_load.connect(self.update_buttons_status)
        self.audio_player_thread.statusChanged.connect(self.update_ui_status)

        self.filter_manager.filterModeChanged.connect(self.OnFilterModeChange)
        self.filter_manager.activeCategoryChanged.connect(self.OnActiveCategoryChanged)
        self.filter_manager.itemSelectionChanged.connect(self.OnItemSelectionChanged)
        self.filter_manager.filteredItemsUpdated.connect(self.OnFilteredItemsUpdated)
        self.filter_manager.itemeSelected.connect(self.play_current_surah)
        self.filter_manager.searchQueryUpdated.connect(self.OnSearchQueryUpdated)

    def disable_focus(self):

        widgets = [
            self.reciter_combo, self.surah_combo,
            self.time_slider, self.volume_slider
        ] + self.buttons

        for widget in widgets:
            widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def setup_shortcuts(self, disable=False, first_time=True):

        shortcuts = {
            self.play_pause_button: "Space",
            self.forward_button: "Right",
            self.rewind_button: "Left",
            self.volume_up_button: "Up",
            self.volume_down_button: "Down",
            self.stop_button: "S",
            self.close_button: "Ctrl+Q",
            self.next_surah_button: "Ctrl+Right",
            self.previous_surah_button: "Ctrl+Left",
    }

        for button, key_sequence in shortcuts.items():
            button.setShortcut(QKeySequence(key_sequence) if not disable else None)

        if first_time:
            QShortcut(QKeySequence("Ctrl+Down"), self).activated.connect(self.next_reciter)
            QShortcut(QKeySequence("Ctrl+Up"), self).activated.connect(self.previous_reciter)

    def update_current_reciter(self):
        self.statusBar().showMessage(f"القارئ الحالي: {self.reciter_combo.currentText()}")

    def update_current_surah(self):
        self.statusBar().showMessage(f"السورة الحالية: {self.surah_combo.currentText()}")

    def toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.play_current_surah()

    def play_current_surah(self):
        reciter_id = self.reciter_combo.currentData()
        surah_number = self.surah_combo.currentData()
        url = self.reciters.get_url(reciter_id, surah_number)
        self.audio_player_thread.set_audio_url(url)
        self.audio_player_thread.start()

    def stop(self):
        self.player.stop()

    def forward(self):
        self.player.forward(10)

    def rewind(self):
        self.player.rewind(10)

    def next_surah(self):
        current_index = self.surah_combo.currentIndex()
        if current_index < self.surah_combo.count() - 1:
            self.surah_combo.setCurrentIndex(current_index + 1)
            UniversalSpeech.say(self.surah_combo.currentText())
            self.play_current_surah()

    def previous_surah(self):
        current_index = self.surah_combo.currentIndex()
        if current_index > 0:
            self.surah_combo.setCurrentIndex(current_index - 1)
            UniversalSpeech.say(self.surah_combo.currentText())
            self.play_current_surah()

    def next_reciter(self):
        current_index = self.reciter_combo.currentIndex()
        if current_index < self.reciter_combo.count() - 1:
            self.reciter_combo.setCurrentIndex(current_index + 1)
        UniversalSpeech.say(self.reciter_combo.currentText())

    def previous_reciter(self):
        current_index = self.reciter_combo.currentIndex()
        if current_index > 0:
            self.reciter_combo.setCurrentIndex(current_index - 1)
        UniversalSpeech.say(self.reciter_combo.currentText())

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

    def on_update_time(self, position, length):
        if length > 0:
            self.time_slider.blockSignals(True)
            new_position_percentage = int((position / length) * 100)
            self.time_slider.setValue(new_position_percentage)
            self.elapsed_time_label.setText(self.format_time(position))
            self.remaining_time_label.setText(self.format_time(length - position))
        self.time_slider.blockSignals(False)

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02}"

    def update_buttons_status(self, status):
        controls = self.buttons + [self.time_slider]
        for control in controls:
            control.setEnabled(status)

        if status == True:
            self.audio_player_thread.timer.start(150)
            
    def update_ui_status(self):

        is_stop = self.player.is_stopped()
        self.time_slider.setEnabled(not is_stop)
        self.stop_button.setEnabled(not is_stop)

        if self.player.is_playing() or self.player.is_stalled():
            self.play_pause_button.setIcon(qta.icon("fa.pause"))
            self.play_pause_button.setAccessibleName("إيقاف مؤقت")
            self.statusBar().showMessage("تشغيل")
        else:
            self.play_pause_button.setIcon(qta.icon("fa.play"))
            self.play_pause_button.setAccessibleName("تشغيل")
            self.statusBar().showMessage("إيقاف مؤقت")

    def OnFilterModeChange(self, active: bool) -> None:
        for button in self.buttons:
            button.setEnabled(not active)
        UniversalSpeech.say("وضع الفلترة مفعَّل. استخدم الأسهم اليمين و اليسار للتنقل بين القرائ و السور, واستخدم الأسهم للأعلى والأسفل لتصفح المحدد, اكتب لتصفية القُرَّاء." if active else "وضع الفلترة معطَّل.")

    def OnActiveCategoryChanged(self, label: str) -> None:
        UniversalSpeech.say(label)

    def OnSearchQueryUpdated(self, search_query: str) -> None:
        UniversalSpeech.say(search_query)
        
    def OnItemSelectionChanged(self, widget: QComboBox, index: int) -> None:
        widget.setCurrentIndex(index)
        UniversalSpeech.say(widget.currentText())

    def OnFilteredItemsUpdated(self, widget: QComboBox, items: List[Item]) -> None:
        current_item = widget.currentText()
        widget.clear()
        for item in items:
            widget.addItem(item.text, item.id)

        widget.setCurrentText(current_item)

    def keyPressEvent(self, event: QKeyEvent):

        if self.filter_manager.handle_key_press(event):
            return
            
        super().keyPressEvent(event)

    def on_close(self):
        self.player.stop()
        self.audio_player_thread.quit()
        self.close()

import re
import os
import datetime
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
from utils.const import Globals, data_folder, user_db_path, program_name
from utils.audio_player import SurahPlayer
from utils.universal_speech import UniversalSpeech
from utils.user_data import PreferencesManager
from utils.settings import Config

from.menubar import MenuBar
from .key_handler import KeyHandler
from .audio_looper import AudioLooper


class SuraPlayerWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(f"{program_name} - مشغل القرآن")
        self.resize(600, 400)
        self.preferences_manager = PreferencesManager(user_db_path)
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)

        self.reciters = SurahReciter(data_folder / "quran" / "reciters.db")
        self.player = SurahPlayer()
        self.audio_player_thread = AudioPlayerThread(self.player, self)
        self.filter_manager = FilterManager()
        self.key_handler = KeyHandler(self)
        self.audio_looper = AudioLooper(self, self.player)


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
        self.setFocus()
        
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
        saved_reciter_id = self.preferences_manager.get_int("reciter_id", 123)
        for row in self.reciters.get_reciters():
            display_text = f"{row['name']} - {row['rewaya']} - ({row['type']}) - ({row['bitrate']} kbps)"
            self.reciter_combo.addItem(display_text, row["id"])
            reciters_list.append(Item(row["id"], display_text))
            if row["id"] == saved_reciter_id:
                self.reciter_combo.setCurrentText(display_text)

        self.filter_manager.set_category(1, "القارئ", reciters_list, self.reciter_combo)

        self.surah_label = QLabel("السورة:")
        self.surah_combo = QComboBox()
        self.surah_combo.setAccessibleName(self.surah_label.text())
        suras_list = []
        saved_sura_number = self.preferences_manager.get_int("sura_number")
        for surah_name, surah_number in QuranConst.SURAS:
            self.surah_combo.addItem(surah_name, surah_number)
            suras_list.append(Item(surah_number, surah_name))
            if surah_number == saved_sura_number:
                self.surah_combo.setCurrentText(surah_name)

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
        self.total_time = QLabel("0:00")
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.elapsed_time_label)
        time_layout.addWidget(self.remaining_time_label)
        time_layout.addWidget(self.total_time)

        progress_layout.addWidget(self.time_slider)
        progress_layout.addWidget(QLabel("الصوت:"))
        progress_layout.addWidget(self.volume_slider)
        progress_layout.addLayout(time_layout)
        self.progress_group.setLayout(progress_layout)

    def connect_signals(self):
        self.reciter_combo.currentIndexChanged.connect(self.update_current_reciter)
        self.surah_combo.currentIndexChanged.connect(self.update_current_surah)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.menubar.play_pause_action.triggered.connect(self.toggle_play_pause)
        self.stop_button.clicked.connect(self.stop)
        self.menubar.stop_action.triggered.connect(self.stop)
        self.forward_button.clicked.connect(lambda: self.forward())
        self.menubar.forward_action.triggered.connect(lambda: self.forward())
        self.rewind_button.clicked.connect(lambda: self.rewind())
        self.menubar.rewind_action.triggered.connect(lambda: self.rewind())
        self.menubar.replay_action.triggered.connect(self.replay)
        self.volume_up_button.clicked.connect(self.increase_volume)
        self.menubar.up_volume_action.triggered.connect(self.increase_volume)
        self.volume_down_button.clicked.connect(self.decrease_volume)
        self.menubar.down_volume_action.triggered.connect(self.decrease_volume)
        self.next_surah_button.clicked.connect(self.next_surah)
        self.previous_surah_button.clicked.connect(self.previous_surah)
        self.menubar.next_surah_action.triggered.connect(self.next_surah)
        self.menubar.previous_surah_action.triggered.connect(self.previous_surah)
        self.menubar.previous_reciter_action.triggered.connect(self.previous_reciter)
        self.menubar.next_reciter_action.triggered.connect(self.next_reciter)
        self.menubar.set_start_action.triggered.connect(self.audio_looper.set_loop_start)
        self.menubar.set_end_action.triggered.connect(self.audio_looper.set_loop_end)
        self.menubar.toggle_loop_action.triggered.connect(self.audio_looper.toggle_loop)
        self.menubar.return_to_start_action.triggered.connect(self.audio_looper.return_to_start)
        self.menubar.clear_loop_action.triggered.connect(self.audio_looper.clear_loop)
        self.close_button.clicked.connect(self.OnClose)
        self.volume_slider.valueChanged.connect(self.update_volume)
        self.time_slider.valueChanged.connect(self.update_time)

        self.audio_player_thread.playback_time_changed.connect(self.on_update_time)
        self.audio_player_thread.waiting_to_load.connect(self.update_buttons_status)
        self.audio_player_thread.statusChanged.connect(self.update_ui_status)
        self.audio_player_thread.file_changed.connect(self.audio_looper.clear_loop)

        self.filter_manager.filterModeChanged.connect(self.OnFilterModeChange)
        self.filter_manager.activeCategoryChanged.connect(self.OnActiveCategoryChanged)
        self.filter_manager.itemSelectionChanged.connect(self.OnItemSelectionChanged)
        self.filter_manager.selectOutOfRange.connect(self.OnOutOfRange)
        self.filter_manager.filteredItemsUpdated.connect(self.OnFilteredItemsUpdated)
        self.filter_manager.itemeSelected.connect(self.play_current_surah)
        self.filter_manager.searchQueryUpdated.connect(self.OnSearchQueryUpdated)
        self.setAccessibleDescription(F"أنت تستمع إلى سورة {self.surah_combo.currentText()}، للقارئ {self.reciter_combo.currentText().split(' - ')[0]}، اضغط Space للتشغيل. أو اضغط Ctrl+F لتغيير السورة أو القارئ.")


    def disable_focus(self):

        widgets = [
            self.reciter_combo, self.surah_combo,
            self.time_slider, self.volume_slider
        ] + self.buttons

        for widget in widgets:
            widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def setup_shortcuts(self, disable=False,):

        shortcuts = {
        self.menubar.play_pause_action: ["Space", "K"],
        self.menubar.forward_action: ["Right", "L"],
        self.menubar.rewind_action: ["Left", "J"],
        self.menubar.replay_action: ["Home"],
        self.menubar.up_volume_action: ["Up"],
        self.menubar.down_volume_action: ["Down"],
        self.menubar.previous_surah_action: ["Alt+Left"],
        self.menubar.next_surah_action: ["Alt+Right"],
        self.menubar.next_reciter_action: ["Alt+Down"],
        self.menubar.previous_reciter_action: ["Alt+Up"],
        self.menubar.stop_action: ["S", "Ctrl+Space"],
        self.menubar.close_window_action: ["Ctrl+W", "Ctrl+F4"],
        self.menubar.close_program_action: ["Ctrl+Shift+W", "Ctrl+Shift+F4"],
        self.menubar.set_start_action: ["[", "ج"],
        self.menubar.set_end_action: ["]", "د"],
        self.menubar.toggle_loop_action: ["Ctrl+R"],
        self.menubar.return_to_start_action: ["Shift+R"],
        self.menubar.clear_loop_action: ["Ctrl+shift+R"],
        }

        for widget, key_sequence in shortcuts.items():
            key_sequence = [key_sequence] if isinstance(key_sequence, str) else key_sequence
            widget.setShortcuts([QKeySequence(key) for key in key_sequence])

    def update_current_reciter(self):
        reciter_id = self.reciter_combo.currentData()
        reciter_data = self.reciters.get_reciter(reciter_id)

        if not reciter_data or not reciter_data["available_suras"]:
            return

        available_suras = sorted(map(int, reciter_data["available_suras"].split(",")))
        self.surah_combo.clear()

        sura_items = [Item(sura_number, QuranConst.SURAS[sura_number - 1][0]) for sura_number in available_suras]
        for item in sura_items:
            self.surah_combo.addItem(item.text, item.id)

        self.filter_manager.change_category_items(2, sura_items)
        self.statusBar().showMessage(f"القارئ الحالي: {self.reciter_combo.currentText()}")
        saved_sura = self.surah_combo.findData(self.preferences_manager.get_int("sura_number"))
        saved_sura = 0 if saved_sura == -1 else saved_sura
        self.surah_combo.setCurrentIndex(saved_sura)

    def update_current_surah(self):
        self.statusBar().showMessage(f"السورة الحالية: {self.surah_combo.currentText()}")

    def toggle_play_pause(self):
        if self.audio_looper.loop_active and self.player.is_paused():
            self.audio_looper   .resume()
        elif self.player.is_playing():
            self.player.pause()
        else:
            self.play_current_surah()

    def play_current_surah(self):
        reciter_id = self.reciter_combo.currentData()
        surah_number = self.surah_combo.currentData()
        url = self.reciters.get_url(reciter_id, surah_number)
        self.audio_player_thread.set_audio_url(url)
        self.audio_player_thread.start()
        self.preferences_manager.set_preference("reciter_id", self.reciter_combo.currentData())
        self.preferences_manager.set_preference("sura_number",  self.surah_combo.currentData())
        
    def stop(self):
        self.set_position(0)
        self.player.stop()
        self.audio_looper.clear_loop()


    def forward(self, step = 5):
        self.player.forward(step)
        self.on_update_time(self.player.get_position(), self.player.get_length())

    def rewind(self, step= 5):
        self.player.rewind(step)
        self.on_update_time(self.player.get_position(), self.player.get_length())

    def set_position(self, position: int, by_percent: bool = False) -> None:
        if not self.player.current_channel is None:
            if by_percent:
                total_length = self.player.get_length()
                position = total_length * (position / 100)
            self.player.set_position(position)
            self.on_update_time(self.player.get_position(), self.player.get_length())
            if by_percent:
                UniversalSpeech.say(f"{self.elapsed_time_label.text()}، الوقت الحالي.")

    def replay(self):
        self.set_position(0)
        #self.on_update_time(self.player.get_position(), self.player.get_length())
        UniversalSpeech.say(f"{self.elapsed_time_label.text()}، الوقت الحالي.")


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
            self.play_current_surah()
        UniversalSpeech.say(self.reciter_combo.currentText())

    def previous_reciter(self):
        current_index = self.reciter_combo.currentIndex()
        if current_index > 0:
            self.reciter_combo.setCurrentIndex(current_index - 1)
            self.play_current_surah()
        UniversalSpeech.say(self.reciter_combo.currentText())
        
    def increase_volume(self):
        self.player.increase_volume()
        volume = int(self.player.volume * 100)
        Config.audio.surah_volume_level = volume
        Config.save_settings()
 

    def decrease_volume(self):
        self.player.decrease_volume()
        volume = int(self.player.volume * 100)
        Config.audio.surah_volume_level = volume
        Config.save_settings()
 
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
            self.total_time.setText(self.format_time(self.player.get_length()))
        self.time_slider.blockSignals(False)

    def format_time(self, seconds):
        time_delta = datetime.timedelta(seconds=seconds)
        return str(time_delta).split(".")[0]

    def update_buttons_status(self, status):
        controls = self.buttons + self.menubar.get_player_actions() + [self.time_slider]
        for control in controls:
            control.setEnabled(status)

        if status == True:
            self.audio_player_thread.timer.start(150)
            
    def update_ui_status(self):

        is_stop = self.player.is_stopped()
        self.time_slider.setEnabled(not is_stop)
        self.stop_button.setEnabled(not is_stop)
        self.menubar.stop_action.setEnabled(not is_stop)

        if self.player.is_playing() or self.player.is_stalled():
            self.play_pause_button.setIcon(qta.icon("fa.pause"))
            self.play_pause_button.setAccessibleName("إيقاف مؤقت")
            self.menubar.play_pause_action.setText("إيقاف مؤقت")
            self.statusBar().showMessage("تشغيل")
            self.setAccessibleDescription(F"أنت تستمع إلى سورة {self.surah_combo.currentText()}، للقارئ {self.reciter_combo.currentText().split(' - ')[0]}، اضغط Ctrl+F لتغيير السورة أو القارئ.")
        else:
            self.play_pause_button.setIcon(qta.icon("fa.play"))
            self.play_pause_button.setAccessibleName("تشغيل")
            self.menubar.play_pause_action.setText("تشغيل")
            self.statusBar().showMessage("إيقاف مؤقت")
            self.setAccessibleDescription(F"أنت تستمع إلى سورة {self.surah_combo.currentText()}، للقارئ {self.reciter_combo.currentText().split(' - ')[0]}، اضغط Space للتشغيل. أو اضغط Ctrl+F لتغيير السورة أو القارئ.")

    def OnFilterModeChange(self, active: bool) -> None:
        Globals.effects_manager.play("filter clos") if not active else Globals.effects_manager.play("filter open")
        widgets = self.buttons + self.menubar.get_player_actions()
        for widget in widgets:
            widget.setEnabled(not active)
        UniversalSpeech.say("وضع الفلترة مفعَّل. استخدم الأسهم اليمين و اليسار للتنقل بين القُرَّاء و السور، واستخدم الأسهم للأعلى والأسفل لتصفح المحدد، اكتب لتصفية القُرَّاء و السور." if active else "وضع الفلترة معطَّل.")

    def OnActiveCategoryChanged(self, label: str) -> None:
        UniversalSpeech.say(label)

    def OnSearchQueryUpdated(self, search_query: str) -> None:
        UniversalSpeech.say(search_query)
        
    def OnItemSelectionChanged(self, widget: QComboBox, index: int) -> None:
        widget.setCurrentIndex(index)            
        UniversalSpeech.say(f"{widget.currentText()} {widget.currentIndex() + 1} من {widget.count()}")

    def OnOutOfRange(self):
        Globals.effects_manager.play("alert")

    def OnFilteredItemsUpdated(self, widget: QComboBox, items: List[Item], selected_item_text: str) -> None:
        widget.clear()
        for item in items:
            widget.addItem(item.text, item.id)

        #Set last selected item before filtering
        widget.setCurrentText(selected_item_text)
        UniversalSpeech.say(f"{widget.currentText()} {widget.currentIndex() + 1} من {widget.count()}", False)
        
    def keyPressEvent(self, event: QKeyEvent):
        if self.filter_manager.handle_key_press(event):
            return

        if self.key_handler.handle_key_press(event):
            return

        return super().keyPressEvent(event)    



    def OnClose(self):
        self.stop()
        self.audio_player_thread.quit()
        self.close()
        self.parent.show()

    def closeEvent(self, a0):
        self.OnClose()
    

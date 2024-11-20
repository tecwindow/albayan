import time
from typing import Optional
from PyQt6.QtWidgets import QToolBar, QPushButton, QSlider
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from core_functions.Reciters import RecitersManager
from utils.audio_player import AudioPlayer
from utils.settings import SettingsManager
from utils.const import data_folder


class AudioPlayerThread(QThread):
    statusChanged = pyqtSignal()
    waiting_to_load = pyqtSignal(bool)
    playback_finished = pyqtSignal()
    
    def __init__(self, player: AudioPlayer, parent: Optional[object] = None):
        super().__init__(parent)
        self.player = player
        self.url = None    
        self.manually_stopped = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_playback_status)

    def run(self):
        if self.url:
            if self.player.source != self.url or self.player.is_stopped():
                self.waiting_to_load.emit(False)
                self.player.load_audio(self.url)
            self.player.play()
            self.manually_stopped = False
            self.statusChanged.emit()
            self.waiting_to_load.emit(True)

    def check_playback_status(self):
        if not self.player.is_playing():
            self.timer.stop()
            self.statusChanged.emit()
            if not self.player.is_paused() and not self.manually_stopped:
                self.playback_finished.emit()

    def set_audio_url(self, url: str):
        self.url = url
        self.quit()
        self.wait()
        

class NavigationManager:
    def __init__(self, quran):
        self.quran = quran
        self.ayah_range = None
        self.current_surah = None
        self.current_ayah = None

    def initialize_ayah_range(self):
            self.ayah_range = self.quran.ayah_data.get_ayah_range()

    def reset_position(self):
        self.initialize_ayah_range()
        self.current_surah = min(self.ayah_range.keys())
        self.current_ayah = self.ayah_range[self.current_surah]["min_ayah"] - 1

    def set_position(self, surah_number: int, ayah_number: int) -> None:
        self.initialize_ayah_range()
        self.current_surah = surah_number
        self.current_ayah = ayah_number

    def navigate(self, direction: str) -> bool:

        self.initialize_ayah_range()
        if self.current_surah not in self.ayah_range or self.current_surah is None or self.current_ayah is None :
            self.reset_position()

        step = 1 if direction == "next" else -1
        self.current_ayah += step
            
        if direction == "next" and self.current_ayah > self.ayah_range[self.current_surah]["max_ayah"]:
            if self.current_surah + 1 in self.ayah_range:
                self.current_surah += 1
                self.current_ayah = self.ayah_range[self.current_surah]["min_ayah"]
            else:
                self.current_ayah = self.ayah_range[self.current_surah]["max_ayah"]
                return False
        elif direction == "previous" and self.current_ayah < self.ayah_range[self.current_surah]["min_ayah"]:
            if self.current_surah - 1 in self.ayah_range:
                self.current_surah -= 1
                self.current_ayah = self.ayah_range[self.current_surah]["max_ayah"]
            else:
                self.current_ayah = self.ayah_range[self.current_surah]["min_ayah"]
                return False

        return True

    def get_navigation_status(self, direction: str, ayah_step: int = 1, surah_step: int = 1) -> bool:
        if direction not in {"next", "previous"}:
            raise ValueError("Invalid direction. Use 'next' or 'previous'.")

        if not self.ayah_range:
            return False

        step_multiplier = 1 if direction == "next" else -1
        target_surah = self.current_surah + step_multiplier * surah_step
        target_ayah = self.current_ayah + step_multiplier * ayah_step

        max_surah = max(self.ayah_range.keys())
        min_surah = min(self.ayah_range.keys())

        if direction == "next":
            max_ayah = self.ayah_range[self.current_surah]["max_ayah"]
            return not (target_surah > max_surah and target_ayah > max_ayah)
        elif direction == "previous":
            min_ayah = self.ayah_range[self.current_surah]["min_ayah"]
            return not (target_surah < min_surah and target_ayah < min_ayah)


class AudioToolBar(QToolBar):
    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        self.parent = parent
        self.player = AudioPlayer()
        self.reciters = RecitersManager(data_folder / "quran" / "reciters.db")
        self.navigation = NavigationManager(self.parent.quran)
        self.audio_thread = AudioPlayerThread(self.player, self.parent)

        self.play_pause_button = self.create_button("استماع الآية الحالية", self.toggle_play_pause)
        self.stop_button = self.create_button("إيقاف", self.stop_audio)
        self.previous_button = self.create_button("الآية السابقة", self.OnPlayPrevious)
        self.previous_button.setEnabled(False)
        self.next_button = self.create_button("الآية التالية", self.OnPlayNext)
        self.next_button.setEnabled(False)
        self.volume_slider = self.create_slider(0, 100, 50, self.change_volume)

        self.audio_thread.statusChanged.connect(self.update_play_pause_button_text)
        self.audio_thread.waiting_to_load.connect(self.set_buttons_status)
        self.audio_thread.playback_finished.connect(self.OnActionAfterListening)

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.addWidget(button)
        return button

    def create_slider(self, min_value, max_value, default_value, callback):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(default_value)
        slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        slider.valueChanged.connect(callback)
        self.addWidget(slider)
        return slider

    def toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            ayah_info = self.parent.get_current_ayah_info()
            self.navigation.set_position(ayah_info[0], ayah_info[3])
            self.play_current_ayah()

    def stop_audio(self):
        self.audio_thread.manually_stopped = True
        self.player.stop()

    def play_current_ayah(self):
        self.stop_audio()
        reciter_id = SettingsManager.current_settings["listening"]["reciter"]
        url = self.reciters.get_url(reciter_id, self.navigation.current_surah, self.navigation.current_ayah)
        self.audio_thread.set_audio_url(url)
        self.audio_thread.start()
        self.set_buttons_status()

    def OnPlayNext(self) -> None:
        if self.navigation.navigate("next"):
            self.play_current_ayah()

    def OnPlayPrevious(self) -> None:
        if self.navigation.navigate("previous"):
            self.play_current_ayah()

    def OnActionAfterListening(self):
        action_after_listening = SettingsManager.current_settings["listening"]["action_after_listening"]
        if action_after_listening == 1:
            self.play_current_ayah()
        elif action_after_listening == 2:
            self.OnPlayNext()

    def change_volume(self, value: int) -> None:
        self.player.set_volume(value / 100)

    def update_play_pause_button_text(self):
        label = "إيقاف مؤقت" if self.player.is_playing() else "استماع الآية الحالية"
        self.play_pause_button.setText(label)
        if hasattr(self.parent, "menu_bar"):
            self.parent.menu_bar.play_pause_action.setText(label)

    def set_buttons_status(self, status: bool = 2) -> None:
        next_status = self.navigation.get_navigation_status("next") if status else False
        previous_status = self.navigation.get_navigation_status("previous") if status else False
        print(self.navigation.get_navigation_status("previous"))
        self.next_button.setEnabled(next_status)
        self.previous_button.setEnabled(previous_status)
        self.play_pause_button.setEnabled(status)
        if hasattr(self.parent, "menu_bar"):
            self.parent.menu_bar.play_next_action.setEnabled(next_status)
            self.parent.menu_bar.play_previous_action.setEnabled(previous_status)
            self.parent.menu_bar.play_pause_action.setEnabled(status)
            if  status == True:
                self.audio_thread.timer.start(100)

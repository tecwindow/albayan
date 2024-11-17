import time
from typing import Optional
from PyQt6.QtWidgets import QToolBar, QPushButton, QSlider
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from core_functions.Reciters import RecitersManager
from utils.audio_player import AudioPlayer
from utils.const import data_folder

class AudioPlayerThread(QThread):
    statusChanged = pyqtSignal()
    def __init__(self, player: AudioPlayer, parent: Optional[object]=None):
        super().__init__(parent)
        self.player = player
        self.url = None

    def run(self):
        if self.url:
            if self.player.source != self.url or self.player.is_stopped():
                self.player.load_audio(self.url)
            self.player.play()
            self.statusChanged.emit()

        while self.player.is_playing():
            time.sleep(0.1)
        else:
            self.statusChanged.emit()
        
    def set_audio_url(self, url: str):
        self.url = url

class AudioToolBar(QToolBar):
    def __init__(self, parent: Optional[object]=None):
        super().__init__(parent)
        self.parent = parent
        self.player = AudioPlayer()
        self.reciters = RecitersManager(data_folder / "quran" / "reciters.db")
        
        self.play_pause_button = self.create_button("استماع الآية الحالية", self.toggle_play_pause)
        self.stop_button = self.create_button("إقاف", self.stop_audio)
        self.volume_slider = self.create_slider(0, 100, 50, self.change_volume)

        self.audio_thread = AudioPlayerThread(self.player, self.parent)
        self.audio_thread.statusChanged.connect(self.update_play_pause_button_text)

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
            url = self.reciters.get_url(68, ayah_info[0], ayah_info[3])
            self.audio_thread.set_audio_url(url)
            self.audio_thread.start()

    def stop_audio(self):
        self.player.stop()

    def change_volume(self, value):
        self.player.set_volume(value / 100)

    def update_play_pause_button_text(self):
        label = "إيقاف مؤقت" if self.player.is_playing() else "استماع الآية الحالية"
        self.play_pause_button.setText(label)
        if hasattr(self.parent, "menu_bar"):
            self.parent.menu_bar.play_pause_action.setText(label)
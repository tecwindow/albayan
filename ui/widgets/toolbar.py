from PyQt6.QtWidgets import QToolBar, QPushButton, QSlider
from PyQt6.QtCore import Qt, QTimer
from core_functions.Reciters import RecitersManager
from utils.audio_player import AudioPlayer
from utils.const import data_folder

class AudioToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.player = AudioPlayer()
        self.reciters = RecitersManager(data_folder / "quran" / "reciters.db")
        
        self.play_pause_button = self.create_button("استماع الآية الحالية", self.toggle_play_pause)
        self.stop_button = self.create_button("إقاف", self.stop_audio)

        self.volume_slider = self.create_slider(0, 100, 50, self.change_volume)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_audio_status)
        self.timer.start(500)

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
            if self.player.source != url or self.player.is_stopped():
                self.player.load_audio(url)
            self.player.play()

        self.update_play_pause_button_text()

    def stop_audio(self):
        self.player.stop()
        self.update_play_pause_button_text()

    def change_volume(self, value):
        self.player.set_volume(value / 100)

    def check_audio_status(self):
        self.update_play_pause_button_text()

    def update_play_pause_button_text(self):
        label = "إيقاف مؤقت" if self.player.is_playing() else "استماع الآية الحالية"
        self.play_pause_button.setText(label)
        if hasattr(self.parent, "menu_bar"):
            self.parent.menu_bar.play_pause_action.setText(label)
        

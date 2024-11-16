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
        
        self.play_pause_button = QPushButton("استماع الآية الحالية")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.addWidget(self.play_pause_button)

        stop_button = QPushButton("إقاف")
        stop_button.clicked.connect(self.stop_audio)
        self.addWidget(stop_button)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setToolTip("شريط التحكم في الصوت")
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.addWidget(self.volume_slider)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_audio_status)
        self.timer.start(500)

    def toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_pause_button.setText("استماع الآية الحالية")
        else:
            ayah_info = self.parent.get_current_ayah_info()
            url = self.reciters.get_url(20, ayah_info[0], ayah_info[3])
            if not self.player.is_paused() or self.player.source != url:
                self.player.load_audio(url)
            self.player.play()

    def stop_audio(self):
        self.player.stop()
        self.play_pause_button.setText("استماع الآية الحالية")

    def change_volume(self, value):
        self.player.set_volume(value / 100)

    def check_audio_status(self):
        if not self.player.is_playing() and not self.player.is_paused():
            self.play_pause_button.setText("استماع الآية الحالية")
        elif self.player.is_playing():
            self.play_pause_button.setText("إيقاف مؤقت")

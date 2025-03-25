from PyQt6.QtWidgets import QMessageBox
from .bass_player import AudioPlayer
from utils.settings import Config


class SurahPlayer(AudioPlayer):
    instances = []
    def __init__(self) -> None:
        super().__init__(Config.audio.surah_volume_level, device=Config.audio.surah_device)
        SurahPlayer.instances.append(self)

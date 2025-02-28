from PyQt6.QtWidgets import QMessageBox
from .bass_player import AudioPlayer
from utils.settings import SettingsManager


class SurahPlayer(AudioPlayer):
    instances = []
    def __init__(self) -> None:
        super().__init__(SettingsManager.current_settings["audio"]["surah_volume_level"])    
        SurahPlayer.instances.append(self)

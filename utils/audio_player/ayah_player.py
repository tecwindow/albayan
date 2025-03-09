from PyQt6.QtWidgets import QMessageBox
from .bass_player import AudioPlayer
from utils.settings import SettingsManager


class AyahPlayer(AudioPlayer):
    instances = []
    def __init__(self) -> None:
        super().__init__(SettingsManager.current_settings["audio"]["ayah_volume_level"], device=SettingsManager.current_settings["audio"]["ayah_device"])
        AyahPlayer.instances.append(self)

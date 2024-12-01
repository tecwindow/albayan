from .bass_player import AudioPlayer
from utils.settings import SettingsManager


class AyahPlayer(AudioPlayer):
    instances = []
    def __init__(self) -> None:
        super().__init__(SettingsManager.current_settings["audio"]["ayah_volume_level"])
        AyahPlayer.instances.append(self)
        
from PyQt6.QtWidgets import QMessageBox
from .bass_player import AudioPlayer
from utils.settings import Config
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class AyahPlayer(AudioPlayer):
    instances = []

    def __init__(self) -> None:
        super().__init__(Config.audio.ayah_volume_level, device=Config.audio.ayah_device)
        AyahPlayer.instances.append(self)
        
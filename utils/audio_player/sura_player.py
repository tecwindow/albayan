from PyQt6.QtWidgets import QMessageBox
from .bass_player import AudioPlayer
from utils.settings import Config
from utils.logger import LoggerManager
logger = LoggerManager.get_logger(__name__)

class SurahPlayer(AudioPlayer):
    instances = []
    def __init__(self) -> None:
        super().__init__(Config.audio.surah_volume_level, device=Config.audio.surah_device)
        SurahPlayer.instances.append(self)
        logger.info("SurahPlayer initialized with volume level: %d and device: %s",
                    Config.audio.surah_volume_level, Config.audio.surah_device)
        
        
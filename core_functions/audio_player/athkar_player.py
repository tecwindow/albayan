import os
import time
from typing import List, Optional
from random import choice
from .bass_player import AudioPlayer
from core_functions.athkar.models import AudioAthkar
from utils.logger import LoggerManager
from utils.settings import Config
from exceptions.error_decorators import exception_handler

logger = LoggerManager.get_logger(__name__)

class AthkarPlayer(AudioPlayer):
    instances = []

    def __init__(self, athkar_folder: str, athkar_list: List[AudioAthkar]) -> None:
        super().__init__(Config.audio.athkar_volume_level, device=Config.audio.athkar_device)
        self.athkar_folder = athkar_folder
        self.athkar_list = athkar_list
        AthkarPlayer.instances.append(self)
        logger.debug(f"AthkarPlayer initialized with folder: {athkar_folder} and {len(athkar_list)} athkar files in database.")

    def __enter__(self):
        """Handles setup when entering the context manager"""
        logger.debug("Entering AthkarPlayer context.")
        return self
    
    @exception_handler
    def play(self) -> None:
        """Plays a random Athkar audio file"""
        logger.debug("Attempting to play a random Athkar audio file.")
        if not self.athkar_list:
            logger.warning("No Athkar files available to play.")
            return

        random_athkar = choice(self.athkar_list)
        file_path = os.path.join(self.athkar_folder, random_athkar.audio_file_name)
        logger.debug(f"Selected Athkar file: {file_path}")
        if not os.path.isfile(file_path):
            logger.error(f"File not found: {file_path}")
            return

        self.load_audio(file_path)
        logger.info(f"Playing Athkar: {file_path}")
        super().play()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Handles cleanup when exiting the context manager"""
        logger.debug("Exiting AthkarPlayer context and freeing resources.")
        while self.is_playing():
            time.sleep(1)

        AthkarPlayer.instances.remove(self)
        self.stop()
        logger.debug("AthkarPlayer instance stopped and removed.")
            
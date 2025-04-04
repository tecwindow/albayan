import os
from random import choice
from .bass_player import AudioPlayer
from utils.settings import Config
from utils.logger import LoggerManager
from exceptions.error_decorators import exception_handler

logger = LoggerManager.get_logger(__name__)

class StartupSoundEffectPlayer(AudioPlayer):
    instances = []

    def __init__(self, sounds_folder: str) -> None:
        super().__init__(Config.audio.volume_level, device=Config.audio.volume_device)
        self.sounds_folder = sounds_folder
        StartupSoundEffectPlayer.instances.append(self)
        logger.debug(f"StartupSoundEffectPlayer initialized with sounds folder: {self.sounds_folder}")
                
    @exception_handler
    def play(self) -> None:
        logger.debug("Attempting to play startup sound effect.")
        if not Config.audio.start_with_basmala_enabled:
            logger.info("Startup sound is disabled in the configuration.")
            return

        if not os.path.exists(self.sounds_folder):
            logger.error("Sounds folder does not exist: %s", self.sounds_folder)
            return

        audio_files =  [
            file for file in os.listdir(self.sounds_folder)
            if file.lower().endswith(self.supported_extensions)
            ]
        if not audio_files:
            logger.warning(f"No supported audio files found in folder:  {self.sounds_folder}")
            return

        random_file = choice(audio_files)
        file_path = os.path.join(self.sounds_folder, random_file)
        logger.debug(f"Selected random file for playback: {file_path}")
        self.load_audio(file_path)
        logger.info(f"Playing startup sound:  {file_path}")
        super().play()

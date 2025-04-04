import os
from typing import Optional
from .bass_player import AudioPlayer
from utils.settings import Config
from utils.logger import LoggerManager
from exceptions.error_decorators import exception_handler

logger = LoggerManager.get_logger(__name__)

class SoundEffectPlayer(AudioPlayer):
    instances = []

    def __init__(self, sounds_folder: str) -> None:
        super().__init__(Config.audio.volume_level, device=Config.audio.volume_device)
        self.sounds_folder = sounds_folder
        self.sounds = {}
        self.load_sound_effects()
        SoundEffectPlayer.instances.append(self)
        logger.debug(f"SoundEffectPlayer initialized with sounds folder: {self.sounds_folder}")

    @exception_handler
    def load_sound_effects(self) -> None:
        """Loads sound effects from the specified folder into a dictionary."""
        logger.debug(f"Loading sound effects from folder:  {self.sounds_folder}")
        if not os.path.exists(self.sounds_folder):
            logger.error(f"Sounds folder does not exist: {self.sounds_folder}")
            return

        loaded_count = 0
        for file in os.listdir(self.sounds_folder):
            if file.lower().endswith(self.supported_extensions):
                name, extension = os.path.splitext(file)
                self.sounds[name] = os.path.join(self.sounds_folder, file)
                loaded_count += 1

        if loaded_count == 0:
            logger.warning(f"No supported sound files found in folder: {self.sounds_folder}")
        else:
            logger.debug(f"Loaded {loaded_count} sound effects from folder: {self.sounds_folder}")

    @exception_handler
    def play(self, file_name: Optional[str]= None) -> None:
        """Plays a specified or random sound effect if enabled."""
        logger.debug(f"Attempting to play sound effect: {file_name}")
        if not Config.audio.sound_effect_enabled:
            logger.debug("Sound effects are disabled in the configuration.")
            return

        if file_name not in self.sounds:
            raise ValueError(f"Invalid file name '{file_name}'. Available sounds: {list(self.sounds.keys())}")

        file_path = self.sounds[file_name]
        logger.debug(f"Loading audio file for playback: {file_path}")
        self.load_audio(file_path)
        logger.info(f"Playing sound effect: {file_path}")
        super().play()

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
        logger.info("SoundEffectPlayer initialized with sounds folder: %s", self.sounds_folder)

    @exception_handler
    def load_sound_effects(self) -> None:
        """Loads sound effects from the specified folder into a dictionary."""
        if not os.path.exists(self.sounds_folder):
            logger.error("Sounds folder does not exist: %s", self.sounds_folder)
            return

        loaded_count = 0
        for file in os.listdir(self.sounds_folder):
            if file.lower().endswith(self.supported_extensions):
                name, extension = os.path.splitext(file)
                self.sounds[name] = os.path.join(self.sounds_folder, file)
                loaded_count += 1

        if loaded_count == 0:
            logger.warning("No supported sound files found in folder: %s", self.sounds_folder)
        else:
            logger.info("Loaded %d sound effects from folder: %s", loaded_count, self.sounds_folder)


    @exception_handler
    def play(self, file_name: Optional[str]= None) -> None:
        """Plays a specified or random sound effect if enabled."""
        if not Config.audio.sound_effect_enabled:
            logger.info("Sound effects are disabled in the configuration.")
            return

        if file_name not in self.sounds:
            logger.error("Invalid file name '%s'. Available sounds: %s", file_name, list(self.sounds.keys()))
            raise ValueError(f"Invalid file name '{file_name}'. Available sounds: {list(self.sounds.keys())}")

        file_path = self.sounds[file_name]
        logger.debug("Loading audio file for playback: %s", file_path)
        self.load_audio(file_path)
        logger.info("Playing sound effect: %s", file_path)
        super().play()

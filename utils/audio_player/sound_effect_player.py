import os
from typing import Optional
from .bass_player import AudioPlayer
from utils.settings import SettingsManager
from exceptions.error_decorators import exception_handler

class SoundEffectPlayer(AudioPlayer):
    instances = []
    def __init__(self, sounds_folder: str) -> None:
        super().__init__(SettingsManager.current_settings["audio"]["volume_level"], device=SettingsManager.current_settings["audio"]["volume_device": 1,])
        self.sounds_folder = sounds_folder
        self.sounds = {}
        self.load_sound_effects()
        SoundEffectPlayer.instances.append(self)

    @exception_handler
    def load_sound_effects(self) -> None:
        """Loads sound effects from the specified folder into a dictionary."""
        for file in os.listdir(self.sounds_folder):
            if file.lower().endswith(self.supported_extensions):
                name, extension = os.path.splitext(file)
                self.sounds[name] = os.path.join(self.sounds_folder, file)

    @exception_handler
    def play(self, file_name: Optional[str]= None) -> None:
        """Plays a specified or random sound effect if enabled."""
        if not SettingsManager.current_settings["audio"]["sound_effect_enabled"]:
            return

        if file_name not in self.sounds:
            raise ValueError(f"Invalid file name '{file_name}'. Available sounds: {list(self.sounds.keys())}")

        file_path = self.sounds[file_name]
        self.load_audio(file_path)
        super().play()

import os
from typing import Optional
from random  import choice
from .bass_player import AudioPlayer

class SoundEffectPlayer(AudioPlayer):
    def __init__(self, sounds_folder: str, is_effect_enabled: Optional[bool], play_random: Optional[bool] = False) -> None:
        super().__init__()
        self.sounds_folder = sounds_folder
        self.is_effect_enabled = is_effect_enabled
        self.play_random = play_random
        self.sounds = {}
        self.supported_extensions = ('.wav', '.mp3', '.ogg')
        self.load_sound_effects()
        
    def load_sound_effects(self) -> None:
        """Loads sound effects from the specified folder into a dictionary."""
        for file in os.listdir(self.sounds_folder):
            if file.lower().endswith(self.supported_extensions):
                name, extension = os.path.splitext(file)
                self.sounds[name] = os.path.join(self.sounds_folder, file)

    def play(self, file_name: Optional[str]= None) -> None:
        """Plays a specified or random sound effect if enabled."""
        if not self.is_effect_enabled:
            return

        if self.play_random and not file_name:
            file_name = choice(list(self.sounds.keys()))

        if file_name not in self.sounds:
            raise ValueError(f"Invalid file name '{file_name}'. Available sounds: {list(self.sounds.keys())}")

        file_path = self.sounds[file_name]
        self.load_audio(file_path)
        super().play()

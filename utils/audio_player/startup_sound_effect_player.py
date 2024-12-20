import os
from random import choice
from .bass_player import AudioPlayer
from utils.settings import SettingsManager
from exceptions.error_decorators import exception_handler


class StartupSoundEffectPlayer(AudioPlayer):
    instances = []
    def __init__(self, sounds_folder: str) -> None:
        super().__init__(SettingsManager.current_settings["audio"]["volume_level"])
        self.sounds_folder = sounds_folder
        StartupSoundEffectPlayer.instances.append(self)
        
    @exception_handler
    def play(self):
        if not SettingsManager.current_settings["audio"]["start_with_basmala_enabled"]:
            return

        audio_files =  [
            file for file in os.listdir(self.sounds_folder)
            if file.lower().endswith(self.supported_extensions)
            ]
        random_file = choice(audio_files)
        file_path = os.path.join(self.sounds_folder, random_file)
        self.load_audio(file_path)
        super().play()

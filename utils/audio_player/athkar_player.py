import os
import time
from typing import List, Optional
from random import choice
from .bass_player import AudioPlayer
from core_functions.athkar.models import AudioAthkar
from utils.settings import SettingsManager
from exceptions.error_decorators import exception_handler

class AthkarPlayer(AudioPlayer):
    instances = []
    def __init__(self, athkar_folder: str, athkar_list: List[AudioAthkar]) -> None:
        super().__init__(SettingsManager.current_settings["audio"]["athkar_volume_level"], device=1)
        self.athkar_folder = athkar_folder
        self.athkar_list = athkar_list
        AthkarPlayer.instances.append(self)

    def __enter__(self):
        return self
    
    @exception_handler
    def play(self) -> None:
        """Plays a random Athkar audio file"""

        random_athkar = choice(self.athkar_list)
        file_path = os.path.join(self.athkar_folder, random_athkar.audio_file_name)
        if not os.path.isfile(file_path):
            return
        
        self.load_audio(file_path)
        super().play()

    def __exit__(self, exc_type, exc_val, exc_tb):
        while self.is_playing():
            time.sleep(1)

        AthkarPlayer.instances.remove(self)
        self.stop()

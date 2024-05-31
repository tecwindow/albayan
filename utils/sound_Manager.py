import os
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from utils.settings import SettingsManager
from utils.logger import Logger

class SoundManager:
    def __init__(self):
        self.folder = "sounds"
        self.sounds = {}

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        else:
            self.load_all_sounds()

    def load_all_sounds(self):
        """Loads all sounds from the sounds folder."""
        for file_name in os.listdir(self.folder):
            if file_name.endswith(('.wav', '.mp3')):
                sound_name = os.path.splitext(file_name)[0]
                self.load_sound(sound_name, os.path.join(self.folder, file_name))

    def load_sound(self, name, file_path):
        """Loads a sound effect."""
        if os.path.isfile(file_path):
            sound = QSoundEffect()
            sound.setSource(QUrl.fromLocalFile(file_path))
            self.sounds[name] = sound
        else:
            Logger.error(f"File '{file_path}' not found!")

    def play_sound(self, name):
        """Plays a loaded sound effect."""

        if not SettingsManager.current_settings["general"]["sound_effect_enabled"]:
            return
        
        if name in self.sounds:
            self.sounds[name].play()
        else:
            Logger.error(f"Sound '{name}' not found!")


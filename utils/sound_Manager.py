import os
import ctypes
from  random import choice
from utils.settings import SettingsManager
from utils.logger import Logger

class SoundManager():
    bass = None

    @classmethod
    def initialize_bass(cls):
        """Initializes the BASS DLL."""

        if cls.bass is not None:
            return

        try:
            bass_dll_path = os.path.abspath("bass.dll")
            cls.bass = ctypes.CDLL(bass_dll_path)
            if not cls.bass.BASS_Init(-1, 44100, 0, 0, None):
                Logger.error("BASS initialization error")
            else:
                Logger.info("BASS initialized successfully")
        except OSError as e:
            Logger.error(f"Could not load BASS DLL: {e}")
        except Exception as e:
            Logger.error(f"BASS initialization error: {e}")
                

    def __init__(self, folder: str):
        self.folder = folder
        self.sounds = {}
        # Initialize BASS DLL
        self.initialize_bass()

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        else:
            self.load_all_sounds()

    def load_all_sounds(self):
        """Loads all sounds from the sounds folder."""
        try:
            Logger.info("Loading all sounds...")
            for file_name in os.listdir(self.folder):
                if file_name.lower().endswith(('.wav', '.mp3', '.ogg')):
                    sound_name = os.path.splitext(file_name)[0]
                    self.load_sound(sound_name, os.path.join(self.folder, file_name))
        except Exception as e:
            Logger.error(f"Error loading all sounds: {str(e)}")
            
    def load_sound(self, name, file_path):
        """Loads a sound effect."""
        try:
            Logger.info(f"Loading sound: {file_path}")
            if os.path.isfile(file_path):
                handle = self.bass.BASS_StreamCreateFile(False, file_path.encode('utf-8'), 0, 0, 0)
                if handle == 0:
                    Logger.error(f"Error loading audio file: {file_path}")
                else:
                    self.sounds[name] = handle
                    Logger.info(f"Sound loaded: {name}")
            else:
                Logger.error(f"File '{file_path}' not found!")
        except Exception as e:
            Logger.error(f"Error loading sound '{name}': {str(e)}")

    def play(self, name: str) -> None:
        """Plays a loaded sound."""
        try:
            Logger.info(f"Attempting to play sound: {name}")
            if name in self.sounds:
                if not self.bass.BASS_ChannelPlay(self.sounds[name], False):
                    Logger.error(f"Error playing sound: {name}")
                else:
                    Logger.info(f"Sound playing: {name}")
            else:
                Logger.error(f"Sound '{name}' not found!")
        except Exception as e:
            Logger.error(f"Error playing sound '{name}': {str(e)}")

class EffectsManager(SoundManager):
    def play(self, name: str) -> None:
        if SettingsManager.current_settings["general"]["sound_effect_enabled"]:
            super().play(name)
            

class BasmalaManager(SoundManager):
    def play(self) -> None:
        random_sound = choice(list(self.sounds.keys()))
        super().play(random_sound)

import os
import ctypes
import random
from utils.settings import SettingsManager
from utils.logger import Logger

class SoundManager:
    def __init__(self):
        self.folder = os.path.join("Audio", "sounds")
        self.sounds = {}
        self.bass = None

        # Initialize BASS DLL
        self.initialize_bass()

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        else:
            self.load_all_sounds()

    def initialize_bass(self):
        """Initializes the BASS DLL."""
        try:
            bass_dll_path = os.path.abspath("bass.dll")
            self.bass = ctypes.CDLL(bass_dll_path)
            if not self.bass.BASS_Init(-1, 44100, 0, 0, None):
                raise Exception("BASS initialization error")
            else:
                Logger.info("BASS initialized successfully")
        except OSError as e:
            Logger.error(f"Could not load BASS DLL: {e}")
            raise
        except Exception as e:
            Logger.error(f"BASS initialization error: {e}")
            raise

    def load_all_sounds(self):
        """Loads all sounds from the sounds folder."""
        try:
            Logger.info("Loading all sounds...")
            for file_name in os.listdir(self.folder):
                if file_name.endswith(('.wav', '.mp3', '.ogg')):
                    sound_name = os.path.splitext(file_name)[0]
                    self.load_sound(sound_name, os.path.join(self.folder, file_name))
        except Exception as e:
            Logger.error(f"Error loading all sounds: {str(e)}")
            raise

    def load_sound(self, name, file_path):
        """Loads a sound effect."""
        try:
            Logger.info(f"Loading sound: {file_path}")
            if os.path.isfile(file_path):
                handle = self.bass.BASS_StreamCreateFile(False, file_path.encode('utf-8'), 0, 0, 0)
                if handle == 0:
                    raise Exception(f"Error loading audio file: {file_path}")
                else:
                    self.sounds[name] = handle
                    Logger.info(f"Sound loaded: {name}")
            else:
                raise FileNotFoundError(f"File '{file_path}' not found!")
        except Exception as e:
            Logger.error(f"Error loading sound '{name}': {str(e)}")
            raise

    def play_sound(self, name):
        """Plays a loaded sound effect."""
        try:
            Logger.info(f"Attempting to play sound: {name}")
            if not SettingsManager.current_settings["general"]["sound_effect_enabled"]:
                Logger.info("Sound effects are disabled in settings.")
                return

            if name in self.sounds:
                if not self.bass.BASS_ChannelPlay(self.sounds[name], False):
                    raise Exception(f"Error playing sound: {name}")
                else:
                    Logger.info(f"Sound playing: {name}")
            else:
                raise KeyError(f"Sound '{name}' not found!")
        except Exception as e:
            Logger.error(f"Error playing sound '{name}': {str(e)}")
            raise

    def play_random_sound_from_folder(self, folder):
        """Plays a random sound from a specified folder."""
        try:
            Logger.info(f"Selecting a random sound from folder: {folder}")
            files = [f for f in os.listdir(folder) if f.endswith(('.ogg', '.mp3', '.wav'))]
            if files:
                random_file = random.choice(files)
                file_path = os.path.join(folder, random_file)
                Logger.info(f"Random file selected: {file_path}")
                sound_name = os.path.splitext(random_file)[0]
                self.load_sound(sound_name, file_path)
                self.play_sound(sound_name)
            else:
                Logger.error(f"No audio files found in folder '{folder}'")
        except Exception as e:
            Logger.error(f"Error playing random sound from folder '{folder}': {str(e)}")
            raise

    def __del__(self):
        """Frees BASS resources on deletion."""
        try:
            if hasattr(self, 'bass'):
                if not self.bass.BASS_Free():
                    raise Exception("Error freeing BASS resources")
                else:
                    Logger.info("BASS resources freed")
        except Exception as e:
            Logger.error(f"Error freeing BASS resources: {str(e)}")
            raise

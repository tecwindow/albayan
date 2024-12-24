import os
import ctypes
from ctypes import c_int, c_longlong, c_void_p, c_uint
from enum import IntFlag
from exceptions.audio_pplayer import PlaybackInitializationError


class BassFlag(IntFlag):
    AUTO_FREE = 0x40000  # Automatically free the stream when it stops/ends
    STREAM_BLOCK = 0x100000  # Download/play internet file stream in small blocks


class BassInitializer:
    def __init__(self, bass_library_path: str = "bass.dll"):
        """Initialize the BassInitializer object without loading the library or initializing BASS."""
        self.bass_library_path = os.path.abspath(bass_library_path)
        self.bass = None
        self.setup()

    def setup(self):
        """Prepares the BASS environment by loading the DLL and setting up argument types."""
        if not os.path.exists(self.bass_library_path):
            raise FileNotFoundError(f"BASS library not found at {self.bass_library_path}")

        # Load the BASS library
        self.bass = ctypes.CDLL(self.bass_library_path)

        # Setup argument and return types for BASS functions
        self.bass.BASS_StreamCreateFile.argtypes = [c_int, c_void_p, c_longlong, c_longlong, c_uint]
        self.bass.BASS_StreamCreateFile.restype = c_int
        self.bass.BASS_ErrorGetCode.restype = c_int

    def initialize(self):
        """Initializes BASS with error handling."""
        if not self.bass:
            raise RuntimeError("BASS library is not set up. Call `setup()` first.")

        if not self.bass.BASS_Init(-1, 44100, 0, 0, 0):
            raise PlaybackInitializationError()

        return self.bass

    def close(self):
        """Shuts down and frees resources used by BASS."""
        if self.bass:
            self.bass.BASS_Free()

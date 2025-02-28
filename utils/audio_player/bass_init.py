import os
import ctypes
from ctypes import c_int, c_longlong, c_void_p, c_uint, c_double, c_char_p
from enum import IntFlag
from dataclasses import dataclass
from typing import List
from exceptions.audio_pplayer import PlaybackInitializationError



class BassFlag(IntFlag):
    AUTO_FREE = 0x40000  # Automatically free the stream when it stops/ends
    STREAM_BLOCK = 0x100000  # Download/play internet file stream in small blocks
    MUSIC_NOSAMPLE = 0x100000
    STREAM_STATUS = 0x800000
    STREAM_RESTRATE = 0x80000

class BASS_DEVICEINFO(ctypes.Structure):
    _fields_ = [
        ("name", c_char_p),
        ("driver", c_char_p),
        ("flags", c_uint),
    ]

@dataclass(frozen=True)
class SoundCard:
    index: int
    name: str
    driver: str
    flag: int


class BassInitializer:
    def __init__(self, bass_library_path: str = "bass.dll"):
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
        self.bass.BASS_Init.argtypes = [c_int, c_uint, c_uint, c_void_p, c_void_p]
        self.bass.BASS_Init.restype = c_int
        self.bass.BASS_GetDeviceInfo.argtypes = [c_int, c_void_p]
        self.bass.BASS_GetDeviceInfo.restype = c_int
        self.bass.BASS_SetDevice.argtypes = [c_int]
        self.bass.BASS_SetDevice.restype = c_int
        self.bass.BASS_StreamCreateFile.argtypes = [c_int, c_void_p, c_longlong, c_longlong, c_uint]
        self.bass.BASS_StreamCreateFile.restype = c_int
        self.bass.BASS_StreamCreateURL.argtypes = [c_void_p, c_int, c_uint, c_void_p, c_void_p]
        self.bass.BASS_StreamCreateURL.restype = c_int
        self.bass.BASS_ChannelBytes2Seconds.argtypes = [c_int, c_longlong]
        self.bass.BASS_ChannelBytes2Seconds.restype = c_double
        self.bass.BASS_ChannelSeconds2Bytes.argtypes = [c_int, c_double]
        self.bass.BASS_ChannelSeconds2Bytes.restype = c_longlong
        self.bass.BASS_ChannelSetPosition.argtypes = [c_int, c_longlong, c_uint]
        self.bass.BASS_ChannelSetPosition.restype = c_int
        self.bass.BASS_ChannelGetLength.argtypes = [c_int, c_uint]
        self.bass.BASS_ChannelGetLength.restype = c_longlong
        self.bass.BASS_ChannelGetPosition.argtypes = [c_int, c_uint]
        self.bass.BASS_ChannelGetPosition.restype = c_longlong
        self.bass.BASS_ErrorGetCode.restype = c_int

    def initialize(self):
        """Initializes BASS with error handling."""
        if not self.bass:
            raise RuntimeError("BASS library is not set up. Call `setup()` first.")

        if not self.bass.BASS_Init(-1, 44100, 0, 0, 0):
            raise PlaybackInitializationError()

        return self.bass

    def get_sound_cards(self) -> List[SoundCard]:
        """Retrieve a list of available sound cards."""
        devices = []
        index = 0

        while True:
            info = BASS_DEVICEINFO()
            if not self.bass.BASS_GetDeviceInfo(index, ctypes.byref(info)):
                break
            devices.append(SoundCard(
                index=index,
                name=info.name.decode() if info.name else "Unknown",
                driver=info.driver.decode() if info.driver else "Unknown",
                flag=info.flags
            ))
            index += 1

        return devices

    def set_sound_card(self, device_index: int):
        """Set the active sound card by index."""
        if not self.bass.BASS_SetDevice(device_index):
            error_code = self.bass.BASS_ErrorGetCode()
            raise RuntimeError(f"Failed to set sound card. Error code: {error_code}")

    def close(self):
        """Shuts down and frees resources used by BASS."""
        if self.bass:
            self.bass.BASS_Free()

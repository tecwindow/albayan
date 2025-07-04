import os
import ctypes
from ctypes import c_int, c_longlong, c_void_p, c_uint, c_double, c_char_p, c_bool
from enum import IntFlag
from dataclasses import dataclass
from typing import List
from exceptions.audio_pplayer import PlaybackInitializationError, SetDeviceError
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class BassFlag(IntFlag):
    AUTO_FREE = 0x40000  # Automatically free the stream when it stops/ends
    STREAM_BLOCK = 0x100000  # Download/play internet file stream in small blocks
    MUSIC_NOSAMPLE = 0x100000
    STREAM_STATUS = 0x800000
    STREAM_RESTRATE = 0x80000
    BASS_DEVICE_DEFAULT = 0x2 
    BASS_DEVICE_ENABLED = 0x1 


class BASS_DEVICEINFO(ctypes.Structure):
    _fields_ = [
        ("name", c_char_p),
        ("driver", c_char_p),
        ("flags", c_uint),
    ]

@dataclass(eq=True, frozen=True)
class SoundCard:
    index: int
    name: str
    driver: str
    flag: int

    @property
    def is_default(self) -> bool:
        return bool(self.flag & BassFlag.BASS_DEVICE_DEFAULT)

    @property
    def is_enabled(self) -> bool:
        return bool(self.flag & BassFlag.BASS_DEVICE_ENABLED)


class BassInitializer:
    def __init__(self, bass_library_path: str = "bass.dll"):
        logger.info(f"Initializing BASS with library path: {bass_library_path}.")
        self.bass_library_path = os.path.abspath(bass_library_path)
        self.bass = None
        self.setup()

    def setup(self):
        """Prepares the BASS environment by loading the DLL and setting up argument types."""
        if not os.path.exists(self.bass_library_path):
            logger.error(f"BASS library not found at {self.bass_library_path}.")
            raise FileNotFoundError(f"BASS library not found at {self.bass_library_path}")

        # Load the BASS library
        self.bass = ctypes.CDLL(self.bass_library_path)
        logger.info("BASS library loaded successfully.")
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
        self.bass.BASS_ChannelSetDevice.argtypes = [c_uint, c_uint]
        self.bass.BASS_ChannelSetDevice.restype = c_bool
        self.bass.BASS_ErrorGetCode.restype = c_int

    def initialize(self):
        """Initializes BASS with error handling."""
        if not self.bass:
            logger.error("BASS library is not set up. Call `setup()` first.")
            raise PlaybackInitializationError("BASS library is not set up. Call `setup()` first.")

        for card in self.get_sound_cards():
            if not self.bass.BASS_Init(card.index, 44100, 0, 0, 0):
                logger.error(f"Failed to initialize BASS with device {card.name}: {self.bass.BASS_ErrorGetCode()}")
                raise PlaybackInitializationError(f"Failed to initialize BASS with device {card.name}: {self.bass.BASS_ErrorGetCode()}")

        logger.info("BASS initialized successfully.")
        return self.bass

    @staticmethod
    def decode_sound_card_name(name: bytes) -> str:
        encodings = ['cp1256', 'utf-8', 'latin1', 'iso8859-6', 'windows-1252',  'utf-16']
        for encoding in encodings:
            try:
                return name.decode(encoding)
            except (UnicodeDecodeError, UnicodeEncodeError):
                logger.debug(f"Failed to decode sound card name '{name}' with encoding '{encoding}'. Trying next encoding.")
                continue    

        logger.warning(f"Failed to decode sound card name '{name}' with all encodings. Returning original name.")
        return str(name)
        
    def get_sound_cards(self) -> List[SoundCard]:
        """Retrieve a list of available sound cards."""
        logger.debug("Retrieving available sound cards.")
        devices = []
        index = 1

        while True:
            info = BASS_DEVICEINFO()
            if not self.bass.BASS_GetDeviceInfo(index, ctypes.byref(info)):
                break
            
            name = self.decode_sound_card_name(info.name) if info.name else "Unknown"
            if name.strip().lower() == "default":
                name = "الافتراضي"
                
            devices.append(SoundCard(
                index=index,
                name=name,
                driver=info.driver.decode() if info.driver else "Unknown",
                flag=info.flags
            ))
            logger.debug(f"Found sound card: {devices[-1]}")
            index += 1
            
        logger.debug(f"Found {len(devices)} sound cards.")
        return devices

    def set_sound_card(self, device_index: int):
        """Set the active sound card by index."""
        logger.debug(f"Setting sound card to device index: {device_index} for all channels.")
        if not self.bass.BASS_SetDevice(device_index):
            logger.error(f"Failed to set sound card to device index: {device_index}. Error code: {self.bass.BASS_ErrorGetCode()}")
            raise SetDeviceError(device_index)

    def close(self):
        """Shuts down and frees resources used by BASS."""
        logger.info("Closing BASS and freeing resources.")
        if self.bass:
            self.bass.BASS_Free()
        logger.info("BASS closed successfully.")
        
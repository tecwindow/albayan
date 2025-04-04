import os
import time
import ctypes
from typing import List, Optional
from urllib.parse import urlparse
from .status import PlaybackStatus
from .bass_init import BassInitializer, BassFlag
from utils.logger import LoggerManager
from exceptions.audio_pplayer import (
    AudioFileNotFoundError, LoadFileError, UnsupportedFormatError, PlaybackControlError,
    InvalidSourceError, PlaybackInitializationError, PlaybackControlError, SetDeviceError
)

logger = LoggerManager.get_logger(__name__)
bass_initializer = BassInitializer()
bass = bass_initializer.initialize()

class AudioPlayer:
    instances = []

    @classmethod
    def apply_new_sound_card(cls, device: int) -> None:
        logger.info(f"Applying new sound card (device: {device}) to all instances of {cls.__name__}.")
        for instance in cls.instances:
            instance.set_channel_device(device)
            logger.info(f"Applied new sound card (device: {device}) to instance {instance.__class__.__name__}.")

    def __init__(self, volume: float, device: int, flag: int = BassFlag.AUTO_FREE) -> None:
        self.source: Optional[str] = None
        self.current_channel: Optional[int] = None
        self.volume = volume
        self.device = device
        self.supported_extensions = ('.wav', '.mp3', '.ogg')
        self.flag = flag
        AudioPlayer.instances.append(self)
        logger.debug(f"Initialized {self.__class__.__name__} with volume={volume}, device={device}, flag={flag}")    

    def load_audio(self, source: str, attempts: Optional[int] = 3) -> None:
        """Loads an audio file or a URL for playback."""
        logger.info(f"Loading audio: {source}")
        # Stop and release the previous file
        if self.current_channel:
            self.stop()  
            logger.info(f"Stopped previous audio: {self.source}")

        if not isinstance(source, str) or not source:
            raise InvalidSourceError(source)
        
        file_name, file_extension = os.path.splitext(source)
        if file_extension.lower() not in self.supported_extensions:
            raise UnsupportedFormatError(file_extension)

        parsed_url = urlparse(source)
        if parsed_url.scheme in ("http", "https") and parsed_url.netloc:
            # Stream from URL
            logger.info(f"Loading audio from URL: {source}")
            self.current_channel = bass.BASS_StreamCreateURL(source.encode(), 0, self.flag, None, None)
            logger.info(f"Loaded audio from URL: {source}")
        else:
            # Load from local file
            if not os.path.isfile(source):
                raise AudioFileNotFoundError(source)
            logger.info(f"Loading audio from file: {source}")
            self.current_channel = bass.BASS_StreamCreateFile(False, source.encode('utf-8'), 0, 0, self.flag)
            logger.info(f"Loaded audio from file: {source}")
        if not self.current_channel:
            if attempts:
                logger.warn(f"Failed to load audio: {source}. Retrying... ({3 - attempts + 1}/3)")
                time.sleep(0.1)
                return self.load_audio(source, attempts - 1)
                logger.error(f"Failed to load audio: {source}. No more attempts left.")
            raise LoadFileError(source)
        
        self.source = source
        self.set_channel_device(self.device)
        self.set_volume(self.volume) 
        logger.info(f"Successfully loaded: {source}, {self.volume}, {self.device}.")

    def play(self) -> None:
        """Plays the currently loaded audio."""
        if not self.current_channel:
            raise PlaybackControlError("play", "No audio file loaded. Use load_audio() first.")
        bass.BASS_ChannelPlay(self.current_channel, False)
        logger.debug(f"Playing audio: {self.source}, {self.__class__.__name__}, device: {self.device}.")

    def pause(self) -> None:
        """Pauses the currently playing audio."""
        if self.current_channel:
            bass.BASS_ChannelPause(self.current_channel)
            logger.debug(f"Paused audio: {self.source}, {self.__class__.__name__}.")

    def stop(self) -> None:
        """Stops the audio playback and releases the channel."""
        if self.current_channel:
            bass.BASS_ChannelStop(self.current_channel)
            logger.debug(f"Stopped audio: {self.source}, {self.__class__.__name__}.")
            bass.BASS_StreamFree(self.current_channel)
            self.current_channel = None
            logger.debug(f"Released audio channel: {self.source}, {self.__class__.__name__}.")

    def set_volume(self, volume: float) -> None:        
        """Sets the playback volume (0.0 to 1.0)."""    
        if isinstance(volume, int):
            volume = volume / 100

        self.volume = max(0.0, min(volume, 1.0))  
        if self.current_channel:
            bass.BASS_ChannelSetAttribute(self.current_channel, 2, ctypes.c_float(self.volume))
            logger.debug(f"Volume set to {self.volume}, {self.__class__.__name__}.")

    def increase_volume(self, step: float = 0.1) -> None:
        """Increases the volume by a specified step, default is 0.1 (10%)."""
        logger.debug(f"Increasing volume to {self.__class__.__name__} by {step}.")
        new_volume = min(self.volume + step, 1.0)
        self.set_volume(new_volume)

    def decrease_volume(self, step: float = 0.1) -> None:
        """Decreases the volume by a specified step, default is 0.1 (10%)."""
        logger.debug(f"Decreasing volume to {self.__class__.__name__} by {step}.")
        new_volume = max(self.volume - step, 0.0)
        self.set_volume(new_volume)

    def set_position(self, new_seconds: float) -> None:
        """Sets the playback position to the specified number of seconds."""
        if self.current_channel:
            new_seconds = max(0.0, new_seconds)
            logger.debug(f"Setting position to {new_seconds} seconds, {self.__class__.__name__}.")
        duration = self.get_length()
        new_seconds = min(new_seconds, duration-1)    
        new_position = bass.BASS_ChannelSeconds2Bytes(self.current_channel, new_seconds)
        logger.debug(f"Set position to {new_seconds} seconds, {self.__class__.__name__}.")    
        return bass.BASS_ChannelSetPosition(self.current_channel, new_position, 0)

    def forward(self, seconds: int = 5) -> None:
        """Forwards the audio playback by the specified number of seconds."""
        logger.debug(f"Forwarding audio by {seconds} seconds, {self.__class__.__name__}.")
        if self.current_channel:
            current_position = self.get_position()
            if current_position == -1:
                logger.error("Error getting current position.", self.get_error())
                return
        
            new_seconds = current_position + seconds
            self.set_position(new_seconds)

    def rewind(self, seconds: int = 5) -> None:
        """Rewinds the audio playback by the specified number of seconds."""
        logger.debug(f"Rewinding audio by {seconds} seconds, {self.__class__.__name__}.")
        if self.current_channel:
            current_position = self.get_position()
            if current_position == -1:
                logger.error("Error getting current position.", self.get_error())
                return
        
            new_seconds = current_position - seconds
            self.set_position(new_seconds)

    def get_length(self) -> float:
        logger.debug(f"Getting length of audio: {self.source}, {self.__class__.__name__}.")        
        if not self.current_channel:
            logger.error("No audio file loaded. Use load_audio() first.")
            return 0

        length = bass.BASS_ChannelGetLength( self.current_channel, 0)
        duration = bass.BASS_ChannelBytes2Seconds(self.current_channel, length)
        
        if duration == -1:
            logger.error("Error getting length.", self.get_error())
            return 0
        else:
            logger.debug(f"Audio length: {duration} seconds, {self.__class__.__name__}.")
            return duration
    
    def get_position(self) -> float:
        """Returns the current playback position in seconds."""
        logger.debug(f"Getting current position of audio: {self.source}, {self.__class__.__name__}.")
        if not self.current_channel:
            logger.error("No audio file loaded. Use load_audio() first.")
            return 0
        
        current_position = bass.BASS_ChannelGetPosition(self.current_channel, 0)
        current_seconds = bass.BASS_ChannelBytes2Seconds(self.current_channel, current_position)
        
        if current_seconds == -1:
            logger.error("Error getting current position.", self.get_error())
            return 0
        else:
            logger.debug(f"Current position: {current_seconds} seconds, {self.__class__.__name__}.")
            return current_seconds
            
    def get_playback_status(self) -> PlaybackStatus:
        """Returns the current playback status."""
        if not self.current_channel:
            # No channel is active, it's considered stopped
            return PlaybackStatus.STOPPED  

        status = bass.BASS_ChannelIsActive(self.current_channel)
        match status:
            case PlaybackStatus.PLAYING.value:
                return PlaybackStatus.PLAYING
            case PlaybackStatus.PAUSED.value:
                return PlaybackStatus.PAUSED
            case PlaybackStatus.STALLED.value:
                return PlaybackStatus.STALLED
            case other:
                return PlaybackStatus.STOPPED

    def is_playing(self) -> bool:
        """Checks if the audio is currently playing."""
        return self.get_playback_status() == PlaybackStatus.PLAYING

    def is_paused(self) -> bool:
        """Checks if the audio is currently paused."""
        return self.get_playback_status() == PlaybackStatus.PAUSED

    def is_stalled(self) -> bool:
        """Checks if the channel is activ but stalled waiting for more data"""
        return self.get_playback_status() == PlaybackStatus.STALLED

    def is_stopped(self) -> bool:
        """Checks if the audio is currently stopped."""
        return self.get_playback_status() == PlaybackStatus.STOPPED   

    def set_channel_device(self, device: int) -> None:
        """Sets the device for the current channel."""
        logger.info(f"Setting channel device to {device}, {self.__class__.__name__}.")
        try:
            if self.current_channel:
                if not bass.BASS_ChannelSetDevice(self.current_channel, device):
                    raise SetDeviceError(device)
        except Exception as e:
            logger.error(f"Error setting device: {e}", exc_info=True)
        finally:
            self.device = device
            logger.info(f"Device set to {device}, {self.__class__.__name__}.")

    def get_error(self) -> int:
        """Returns the last error code."""
        logger.debug(f"Getting last error code, {self.__class__.__name__}.")
        return bass.BASS_ErrorGetCode()

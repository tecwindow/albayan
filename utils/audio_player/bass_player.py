import os
import time
import ctypes
from typing import List, Optional
from urllib.parse import urlparse
from .status import PlaybackStatus
from .bass_init import BassInitializer, BassFlag
from exceptions.audio_pplayer import (
    AudioFileNotFoundError, LoadFileError, UnsupportedFormatError, PlaybackControlError,
    InvalidSourceError, PlaybackInitializationError, PlaybackControlError
)

bass_initializer = BassInitializer()
bass = bass_initializer.initialize()

class AudioPlayer:
    instances = []

    def __init__(self, volume: float, flag: int = BassFlag.AUTO_FREE) -> None:
        self.source: Optional[str] = None
        self.current_channel: Optional[int] = None
        self.volume = volume
        self.supported_extensions = ('.wav', '.mp3', '.ogg')
        self.flag = flag
        AudioPlayer.instances.append(self)
    
    def load_audio(self, source: str, attempts: Optional[int] = 3) -> None:
        """Loads an audio file or a URL for playback."""

        # Stop and release the previous file
        if self.current_channel:
            self.stop()  

        if not isinstance(source, str) or not source:
            raise InvalidSourceError(source)

        file_name, file_extension = os.path.splitext(source)
        if file_extension.lower() not in self.supported_extensions:
            raise UnsupportedFormatError(file_extension)

        parsed_url = urlparse(source)
        if parsed_url.scheme in ("http", "https") and parsed_url.netloc:
            # Stream from URL
            self.current_channel = bass.BASS_StreamCreateURL(source.encode(), 0, self.flag, None, None)
        else:
            # Load from local file
            if not os.path.isfile(source):
                raise AudioFileNotFoundError(source)
            self.current_channel = bass.BASS_StreamCreateFile(False, source.encode('utf-8'), 0, 0, self.flag)

        if not self.current_channel:
            if attempts:
                print(f"Trying too load: {source}.")
                time.sleep(0.1)
                return self.load_audio(source, attempts - 1)
            raise LoadFileError(source)
        
        self.source = source
        self.set_volume(self.volume) 
    
    def play(self) -> None:
        """Plays the currently loaded audio."""
        if not self.current_channel:
            raise PlaybackControlError("play", "No audio file loaded. Use load_audio() first.")
        bass.BASS_ChannelPlay(self.current_channel, False)
    
    def pause(self) -> None:
        """Pauses the currently playing audio."""
        if self.current_channel:
            bass.BASS_ChannelPause(self.current_channel)
    
    def stop(self) -> None:
        """Stops the audio playback and releases the channel."""
        if self.current_channel:
            bass.BASS_ChannelStop(self.current_channel)
            bass.BASS_StreamFree(self.current_channel)
            self.current_channel = None

    def set_volume(self, volume: float) -> None:        
        """Sets the playback volume (0.0 to 1.0)."""    
        if isinstance(volume, int):
            volume = volume / 100

        self.volume = max(0.0, min(volume, 1.0))  
        if self.current_channel:
            bass.BASS_ChannelSetAttribute(self.current_channel, 2, ctypes.c_float(self.volume))
    
    def increase_volume(self, step: float = 0.01) -> None:
        """Increases the volume by a specified step, default is 0.1 (10%)."""
        new_volume = min(self.volume + step, 1.0)
        self.set_volume(new_volume)
    
    def decrease_volume(self, step: float = 0.01) -> None:
        """Decreases the volume by a specified step, default is 0.1 (10%)."""
        new_volume = max(self.volume - step, 0.0)
        self.set_volume(new_volume)

    def set_position(self, new_seconds: float) -> None:
        """Sets the playback position to the specified number of seconds."""
        if self.current_channel:
            new_seconds = max(0.0, new_seconds)

        duration = bass.BASS_ChannelBytes2Seconds(self.current_channel, bass.BASS_ChannelGetLength( self.current_channel, 0))
        new_seconds = min(new_seconds, duration-1)    
        new_position = bass.BASS_ChannelSeconds2Bytes(self.current_channel, new_seconds)
        bass.BASS_ChannelSetPosition(self.current_channel, new_position, 0)

    def forward(self, seconds: int = 5) -> None:
        """Forwards the audio playback by the specified number of seconds."""
        if self.current_channel:
            current_position = bass.BASS_ChannelGetPosition(self.current_channel, 0)
            if current_position == -1:
                print("Error getting current position.")
                return
        
            current_seconds = bass.BASS_ChannelBytes2Seconds(self.current_channel, current_position)
            new_seconds = round(current_seconds + seconds)
            self.set_position(new_seconds)

    def rewind(self, seconds: int = 5) -> None:
        """Rewinds the audio playback by the specified number of seconds."""
        if self.current_channel:
            current_position = bass.BASS_ChannelGetPosition(self.current_channel, 0)
            if current_position == -1:
                print("Error getting current position.")
                return
        
            current_seconds = bass.BASS_ChannelBytes2Seconds(self.current_channel, current_position)
            new_seconds = current_seconds - seconds
            self.set_position(new_seconds)

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
    
    def get_error(self) -> int:
        return bass.BASS_ErrorGetCode()
    
    def get_length(self) -> int:
        length = int(bass.BASS_ChannelGetLength( self.current_channel, 0))
        return self.BASS_ChannelBytes2Seconds(self.current_channel, length)
    
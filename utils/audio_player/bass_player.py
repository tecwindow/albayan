import os
import time
from ctypes import CDLL, c_float
from typing import Optional
from urllib.parse import urlparse
from .status import PlaybackStatus

# Load bass.dll
bass_path = os.path.abspath("bass.dll")
bass = CDLL(bass_path)

# Initialize BASS
if not bass.BASS_Init(-1, 44100, 0, 0, 0):
    raise RuntimeError("BASS initialization failed")

class AudioPlayer:
    def __init__(self) -> None:
        self.source: Optional[str] = None
        self.current_channel: Optional[int] = None
        self.volume: float = 0.5
        self.supported_extensions = ('.wav', '.mp3', '.ogg')
    
    def load_audio(self, source: str, attempts: Optional[int] = 3) -> None:
        """Loads an audio file or a URL for playback."""

        # Stop and release the previous file
        if self.current_channel:
            self.stop()  

        if not isinstance(source, str):
            raise ValueError("Source must be a valid file path or URL.")
        
        parsed_url = urlparse(source)
        if parsed_url.scheme in ("http", "https") and parsed_url.netloc:
            # Stream from URL
            self.current_channel = bass.BASS_StreamCreateURL(source.encode(), 0, 0, None, None)
        else:
            # Load from local file
            if not os.path.isfile(source):
                raise FileNotFoundError(f"Audio file '{source}' not found")
            self.current_channel = bass.BASS_StreamCreateFile(False, source.encode('utf-8'), 0, 0, 0)

        if not self.current_channel:
            if attempts:
                print(f"Trying too load: {source}.")
                return self.load_audio(source, attempts - 1)
            raise RuntimeError("Failed to load audio file or URL: {}".format(source))
        
        self.source = source
        self.set_volume(self.volume) 
    
    def play(self) -> None:
        """Plays the currently loaded audio."""
        if not self.current_channel:
            raise RuntimeError("No audio file loaded. Use load_audio() first.")
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
        self.volume = max(0.0, min(volume, 1.0))  # Clamp volume between 0.0 and 1.0
        if self.current_channel:
            bass.BASS_ChannelSetAttribute(self.current_channel, 2, c_float(self.volume))
    
    def increase_volume(self, step: float = 0.1) -> None:
        """Increases the volume by a specified step, default is 0.1 (10%)."""
        new_volume = min(self.volume + step, 1.0)
        self.set_volume(new_volume)
    
    def decrease_volume(self, step: float = 0.1) -> None:
        """Decreases the volume by a specified step, default is 0.1 (10%)."""
        new_volume = max(self.volume - step, 0.0)
        self.set_volume(new_volume)

    def forward(self, seconds: float = 10) -> None:
        """Forwards the audio playback by the specified number of seconds."""
        if self.current_channel:
            current_position = bass.BASS_ChannelGetPosition(self.current_channel)
            new_position = current_position + seconds
            bass.BASS_ChannelSetPosition(self.current_channel, new_position)

    def rewind(self, seconds: float = 10) -> None:
        """Rewinds the audio playback by the specified number of seconds."""
        if self.current_channel:
            current_position = bass.BASS_ChannelGetPosition(self.current_channel)
            new_position = max(0.0, current_position - seconds)
            bass.BASS_ChannelSetPosition(self.current_channel, new_position)

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
    
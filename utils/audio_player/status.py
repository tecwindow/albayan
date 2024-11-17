from enum import Enum

class PlaybackStatus(Enum):
    STOPPED = 0
    PLAYING = 1
    FIRST_PLAYING = 2
    PAUSED = 3

from enum import Enum

class PlaybackStatus(Enum):
    STOPPED = 0
    PLAYING = 1
    STALLED = 2
    PAUSED = 3

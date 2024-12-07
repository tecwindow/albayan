from typing import Optional
from .base import BaseException


class AudioFileNotFoundError(BaseException):
    def __init__(self, file_path: str):
        super().__init__(f"Audio file '{file_path}' not found.", None, 1000)

class LoadFileError(BaseException):
    def __init__(self, source: str, cause: Optional[Exception] = None):
        super().__init__(f"Failed to load audio file or URL: {source}", cause, 1001)

class UnsupportedFormatError(BaseException):
    def __init__(self, format: str, cause: Optional[Exception] = None):
        super().__init__(f"Unsupported audio format: {format}", cause, 1002)

class InvalidSourceError(BaseException):
    def __init__(self, source: Optional[str]):
        super().__init__(f"Invalid audio source: '{source}'. Source must be a valid file path or URL.", None, 1003)

class PlaybackInitializationError(BaseException):
    def __init__(self, message: str = "Failed to initialize audio playback system (bass).", cause: Exception = None):
        super().__init__(message, cause, 1004)

class PlaybackControlError(BaseException):
    def __init__(self, action: str, message: str = None, cause: Exception = None):
        message = message or f"Failed to perform playback action: {action}."
        super().__init__(message, cause, 1005)

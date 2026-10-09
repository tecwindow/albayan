import time
from typing import Optional
from PySide6.QtCore import QThread, QTimer, Signal
from utils.audio_player import AyahPlayer
from utils.logger import LoggerManager
from exceptions.base import ErrorMessage

logger = LoggerManager.get_logger(__name__)


class AudioPlayerThread(QThread):
    statusChanged = Signal()
    waiting_to_load = Signal(bool)
    playback_finished = Signal()
    error_signal = Signal(ErrorMessage)
    playback_time_changed = Signal(float, float)
    file_changed = Signal(str)

    def __init__(self, player: AyahPlayer, parent: Optional[object] = None):
        super().__init__(parent)
        logger.debug("Initializing AudioPlayerThread.")
        self.player = player
        self.url = None
        self.manually_stopped = False
        self.send_error_signal = True
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_playback_status)
        logger.debug("AudioPlayerThread initialized.")

    def run(self):
        if self.url:
            logger.debug("Running AudioPlayerThread.")
            self.waiting_to_load.emit(False)
            try:
                if self.player.source != self.url or self.player.is_stopped():
                    logger.debug(f"Loading new audio file: {self.url}")
                    self.file_changed.emit(self.url)
                    self.player.load_audio(
                        self.url, end_callback=self.playback_finished.emit
                    )
                self.player.play()
                self.manually_stopped = False
                logger.debug(f"Playback started for: {self.url}")
            except Exception as e:
                message = ErrorMessage(e)
                logger.error(
                    f"Error during playback: {message.log_message}", exc_info=True
                )
                if self.send_error_signal:
                    self.error_signal.emit(message)
                    self.manually_stopped = True
                    logger.debug("Error signal emitted.")
                else:
                    logger.debug(
                        "Error signal not emitted due to send_error_signal=False."
                    )
                    self.playback_finished.emit()
            finally:
                self.statusChanged.emit()
                self.waiting_to_load.emit(True)
                logger.debug("Playback status updated.")

    def check_playback_status(self):
        self.playback_time_changed.emit(
            self.player.get_position(), self.player.get_length()
        )
        if not self.player.is_playing() and not self.player.is_stalled():
            self.timer.stop()
            self.statusChanged.emit()

    def set_audio_url(self, url: str, send_error_signal: bool = True):
        logger.debug(f"Setting audio URL: {url}")
        self.url = url
        self.send_error_signal = send_error_signal
        self.quit()
        self.wait()

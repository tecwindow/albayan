import time
from typing import Optional
from PyQt6.QtWidgets import QToolBar, QPushButton, QSlider, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from core_functions.quran.quran_manager import QuranManager
from core_functions.Reciters import AyahReciter
from utils.audio_player import AyahPlayer
from utils.settings import Config
from utils.const import data_folder
from utils.logger import LoggerManager
from exceptions.base import ErrorMessage

logger = LoggerManager.get_logger(__name__)

class AudioPlayerThread(QThread):
    statusChanged = pyqtSignal()
    waiting_to_load = pyqtSignal(bool)
    playback_finished = pyqtSignal()
    error_signal = pyqtSignal(ErrorMessage) 
    playback_time_changed = pyqtSignal(float, float)
    file_changed = pyqtSignal(str)

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
                        self.player.load_audio(self.url)
                    self.player.play()
                    self.manually_stopped = False
                    logger.debug(f"Playback started for: {self.url}")
                except Exception as e:
                    message = ErrorMessage(e)
                    logger.error(f"Error during playback: {message.title} - {message.body}", exc_info=True)
                    if self.send_error_signal:
                        self.error_signal.emit(message)
                        self.manually_stopped = True
                        logger.debug("Error signal emitted.")
                finally:
                    self.statusChanged.emit()
                    self.waiting_to_load.emit(True)
                    logger.debug("Playback status updated.")

    def check_playback_status(self):
        self.playback_time_changed.emit(self.player.get_position(), self.player.get_length())
        if not self.player.is_playing() and not self.player.is_stalled():
            self.timer.stop()
            self.statusChanged.emit()
            if not self.player.is_paused() and not self.manually_stopped:
                self.playback_finished.emit()

    def set_audio_url(self, url: str, send_error_signal: bool = True):
        logger.debug(f"Setting audio URL: {url}")
        self.url = url
        self.send_error_signal = send_error_signal
        self.quit()
        self.wait()        


class NavigationManager:
    def __init__(self, parent, quran_manager: QuranManager):
        logger.debug("Initializing NavigationManager.")
        self.parent = parent
        self.quran_manager = quran_manager
        self.ayah_range = None
        self.current_surah = None
        self.current_ayah = None
        self.has_basmala = False
        logger.debug("NavigationManager initialized.")

    def initialize_ayah_range(self):
            self.ayah_range = self.quran_manager.view_content.get_ayah_range()
            logger.debug("Ayah range initialized.")

    def reset_position(self):
        logger.debug("Resetting navigation position.")
        self.has_basmala = False
        self.initialize_ayah_range()
        current_ayah = self.parent.get_current_ayah()
        if current_ayah.sura_number != self.current_surah or not (self.ayah_range[self.current_surah]["min_ayah"] < current_ayah.number_in_surah < self.ayah_range[self.current_surah]["max_ayah"]):
            self.current_surah = min(self.ayah_range.keys())
            self.current_ayah = self.ayah_range[self.current_surah]["min_ayah"] - 1    
        logger.debug(f"Position reset to Surah: {self.current_surah}, Ayah: {self.current_ayah}")

    def set_position(self, surah_number: int, ayah_number: int) -> None:
        self.initialize_ayah_range()
        self.current_surah = surah_number
        self.current_ayah = ayah_number
        logger.debug(f"Position set to Surah: {surah_number}, Ayah: {ayah_number}")

    def navigate(self, direction: str) -> bool:
        logger.debug(f"Navigating {direction} from Surah: {self.current_surah}, Ayah: {self.current_ayah}")
        self.initialize_ayah_range()
        if self.current_surah not in self.ayah_range or self.current_surah is None or self.current_ayah is None :
            logger.warning("Invalid current position. Resetting...")
            self.reset_position()

        step = 1 if direction == "next" else -1
        self.current_ayah += step
            
        if direction == "next" and self.current_ayah > self.ayah_range[self.current_surah]["max_ayah"]:
            if self.current_surah + 1 in self.ayah_range:
                self.current_surah += 1
                self.current_ayah = self.ayah_range[self.current_surah]["min_ayah"]
                logger.debug(f"Moved to next sura: {self.current_surah}, Ayah: {self.current_ayah}")
            else:
                self.current_ayah = self.ayah_range[self.current_surah]["max_ayah"]
                logger.debug("Reached the last Ayah in the page.")
                return False
        elif direction == "previous" and self.current_ayah < self.ayah_range[self.current_surah]["min_ayah"]:
            if self.current_surah - 1 in self.ayah_range:
                self.current_surah -= 1
                self.current_ayah = self.ayah_range[self.current_surah]["max_ayah"]
                logger.debug(f"Moved to previous Surah: {self.current_surah}, Ayah: {self.current_ayah}")
            else:
                self.current_ayah = self.ayah_range[self.current_surah]["min_ayah"]
                logger.debug("Reached the first Ayah in the page.")
                return False
        logger.info(f"Navigation complete. New position: Surah {self.current_surah}, Ayah {self.current_ayah}")
        return True

    def get_navigation_status(self, direction: str, ayah_step: int = 1, surah_step: int = 1) -> bool:
        if direction not in {"next", "previous"}:
            logger.error(f"Invalid navigation direction: {direction}", exc_info=True)
            raise ValueError("Invalid direction. Use 'next' or 'previous'.")

        if not self.ayah_range:
            logger.warning("Ayah range is not initialized.")
            return False

        step_multiplier = 1 if direction == "next" else -1
        target_surah = self.current_surah + step_multiplier * surah_step
        target_ayah = self.current_ayah + step_multiplier * ayah_step

        max_surah = max(self.ayah_range.keys())
        min_surah = min(self.ayah_range.keys())

        if direction == "next":
            max_ayah = self.ayah_range[self.current_surah]["max_ayah"]
            result = not (target_surah > max_surah and target_ayah > max_ayah)
        elif direction == "previous":
            min_ayah = self.ayah_range[self.current_surah]["min_ayah"]
            result = not (target_surah < min_surah and target_ayah < min_ayah)

        logger.debug(f"Navigation status ({direction}): {result}")
        return result


class AudioToolBar(QToolBar):
#    ayahChanged = pyqtSignal(int)
    

    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        logger.debug("Initializing AudioToolBar.")
        self.parent = parent
        self.player = AyahPlayer()
        self.reciters = AyahReciter(data_folder / "quran" / "reciters.db")
        self.navigation = NavigationManager(self.parent, self.parent.quran_manager)
        self.audio_thread = AudioPlayerThread(self.player, self.parent)
        logger.debug("AudioToolBar initialized.")

        self.play_pause_button = self.create_button("تشغيلالآية الحالية", self.toggle_play_pause)
        self.stop_button = self.create_button("إيقاف", self.stop_audio)
        self.stop_button.setEnabled(False)
        self.previous_button = self.create_button("الآية السابقة", self.OnPlayPrevious)
        self.previous_button.setEnabled(False)
        self.next_button = self.create_button("الآية التالية", self.OnPlayNext)
        self.next_button.setEnabled(False)
        self.volume_slider = self.create_slider(0, 100, 50, self.change_volume)
        self.set_volume()

        self.audio_thread.statusChanged.connect(self.update_play_pause_button_text)
        self.audio_thread.waiting_to_load.connect(self.set_buttons_status)
        self.audio_thread.playback_finished.connect(self.OnActionAfterListening)
        self.audio_thread.error_signal.connect(self.show_error_message)

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.addWidget(button)
        return button

    def create_slider(self, min_value, max_value, default_value, callback):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(default_value)
        slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        slider.valueChanged.connect(callback)
        self.addWidget(slider)
        return slider

    def toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            logger.debug("Playback paused.")
        else:
            current_ayah = self.parent.get_current_ayah()
            self.navigation.set_position(current_ayah.sura_number, current_ayah.number_in_surah)
            logger.debug(f"Setting position to Surah: {current_ayah.number}, Ayah: {current_ayah.sura_number}")
            self.play_current_ayah()
            logger.debug("Playback started.")

    def stop_audio(self):
        logger.debug("Stopping audio playback.")
        self.audio_thread.manually_stopped = True
        self.player.stop()
        self.set_buttons_status()
        logger.debug("Audio playback stopped.")

    def play_current_ayah(self):
        logger.debug(f"Attempting to play Surah {self.navigation.current_surah}, Ayah {self.navigation.current_ayah}")
        current_ayah = self.parent.get_current_ayah()
        self.parent.statusBar().showMessage(f"آية {self.navigation.current_ayah} من  {current_ayah.sura_name}")

        if self.navigation.current_ayah == 1 and not self.navigation.has_basmala:
            self.navigation.current_ayah = 0
        elif self.navigation.current_ayah > 1:
            self.navigation.has_basmala = False

        reciter_id = Config.listening.reciter
        url = self.reciters.get_url(reciter_id, self.navigation.current_surah, self.navigation.current_ayah)
        logger.debug(f"Generated URL: {url}")
        self.audio_thread.set_audio_url(url, send_error_signal=False if self.navigation.current_ayah == 0 else True)
        self.audio_thread.start()
        self.set_buttons_status()
        logger.debug("Audio playback started.")

    def OnPlayNext(self) -> None:
        logger.debug("Playing next Ayah.")
        self.stop_audio()
        if self.navigation.navigate("next"):
            self.play_current_ayah()
            self.change_ayah_focus()
            logger.debug("Next Ayah played.")

    def OnPlayPrevious(self) -> None:
        logger.debug("Playing previous Ayah.")
        self.stop_audio()
        if self.navigation.navigate("previous"):
            self.play_current_ayah()
            self.change_ayah_focus()
            logger.debug("Previous Ayah played.")

    def change_ayah_focus(self, manual: bool = False) -> None:
        logger.debug(f"Changing ayah focus...")
        ayah = self.parent.quran_manager.view_content.get_by_ayah_number_in_surah(self.navigation.current_ayah or 1, self.navigation.current_surah)
        if Config.listening.auto_move_focus:
            logger.debug(f"Moving focus automatically to Ayah {ayah.number}.")
            self.parent.set_focus_to_ayah(ayah.number)
        if manual:
            logger.debug(f"Manual focus change to Ayah {ayah.number}.")
            self.parent.set_focus_to_ayah(ayah.number)       
            self.parent.quran_view.setFocus()

    def OnActionAfterListening(self):
        logger.debug("Action after listening triggered.")
        self.set_buttons_status()
        action_after_listening = Config.listening.action_after_listening
        if action_after_listening == 2 or self.navigation.current_ayah == 0:
            self.navigation.has_basmala = True if self.navigation.current_ayah < 2 else False
            self.OnPlayNext()
            logger.debug("Playing next Ayah after listening.")
        elif action_after_listening == 1:
            self.play_current_ayah()
            logger.debug("Playingcurrent Ayah after listening.")

    def change_volume(self, value: int) -> None:
        logger.debug(f"Changing ayah volume.")
        self.player.set_volume(value)
        logger.debug(f"Volume changed to {value}.")

    def set_volume(self) -> None:
        logger.debug("Setting ayah volume.")
        self.volume_slider.setValue(Config.audio.ayah_volume_level)
        logger.debug(f"Volume set to {Config.audio.ayah_volume_level}.")

    def update_play_pause_button_text(self):
        #logger.debug("Updating play/pause button text.")
        label = "إيقاف مؤقت" if self.player.is_playing() or self.player.is_stalled() else "تشغيل الآية الحالية"
        self.play_pause_button.setText(label)
        if hasattr(self.parent, "menu_bar"):
            self.parent.menu_bar.play_pause_action.setText(label)
        #logger.debug(f"Play/Pause button text updated to: {label}")

    def set_buttons_status(self, status: bool = 2) -> None:
        #logger.debug("Setting buttons status.")
        next_status = self.navigation.get_navigation_status("next") if status else False
        previous_status = self.navigation.get_navigation_status("previous") if status else False
        self.next_button.setEnabled(next_status)
        self.previous_button.setEnabled(previous_status)
        self.play_pause_button.setEnabled(status)
        self.stop_button.setEnabled(not self.player.is_stopped())
        if hasattr(self.parent, "menu_bar"):
            self.parent.menu_bar.play_next_action.setEnabled(next_status)
            self.parent.menu_bar.play_previous_action.setEnabled(previous_status)
            self.parent.menu_bar.play_pause_action.setEnabled(status)
            self.parent.menu_bar.stop_action.setEnabled(not self.player.is_stopped())
            self.parent.menu_bar.rewind_action.setEnabled(not self.player.is_stopped())
            self.parent.menu_bar.forward_action.setEnabled(not self.player.is_stopped())
            self.parent.menu_bar.replay_action.setEnabled(not self.player.is_stopped())
            if  status == True:
                self.audio_thread.timer.start(100)
        #logger.debug(f"Buttons status set: Next: {next_status}, Previous: {previous_status}, Play/Pause: {status}, Stop: {not self.player.is_stopped()}")

    def show_error_message(self, message: ErrorMessage):
        logger.debug(f"Showing error message: {message.title} - {message.body}")
        msg_box =QMessageBox(self.parent,)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(message.title)
        msg_box.setText(message.body)
        ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()

from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt
from utils.universal_speech import UniversalSpeech
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class KeyHandler:
    """
    Handles keyboard events in the application, including arrow key actions and keyboard shortcuts.

    This class separates key handling logic from the main window, making the code more modular and easier to maintain.
    """

    def __init__(self, parent):
        """
        Initializes the KeyHandler with references to the parent window's functions and UI elements.

        :param parent: The main application window (QMainWindow).
        """
        logger.debug("Initializing KeyHandler.")
        self.parent = parent

        # Mapping arrow keys to their respective functions
        self.arrow_actions = {
            Qt.Key_Left: parent.rewind,
            Qt.Key_Right: parent.forward
        }
        logger.debug(f"Arrow key actions mapped: {self.arrow_actions}")

        # Mapping modifier keys to the corresponding time values for rewinding/forwarding
        self.arrow_modifiers = {
            Qt.ControlModifier | Qt.ShiftModifier: 60,  # Ctrl + Shift -> 60 seconds
            Qt.ShiftModifier: 10,  # Shift -> 10 seconds
            Qt.ControlModifier: 20,  # Ctrl -> 20 seconds
        }
        logger.debug(f"Arrow key modifiers mapped: {self.arrow_modifiers}")

        # Mapping shortcut keys to their corresponding actions
        self.shortcuts = {
            ord("E"): lambda: UniversalSpeech.say(f"{parent.elapsed_time_label.text()}، الوقت المنقَضي."),
            ord("R"): lambda: UniversalSpeech.say(f"{parent.remaining_time_label.text()}، الوقت المتبقي."),
            ord("T"): lambda: UniversalSpeech.say(f"{parent.total_time.text()}، الوقت الإجمالي."),
            ord("C"): lambda: UniversalSpeech.say(f"{parent.reciter_combo.currentText().split(' - ')[0]}، القارئ الحالي."),
            ord("V"): lambda: UniversalSpeech.say(f"{parent.surah_combo.currentText()}، السورة الحالية."),
            ord("I"): lambda: UniversalSpeech.say(
                f"{parent.surah_combo.currentText()}، للقارئ، {parent.reciter_combo.currentText()}."
            ),
            Qt.Key_MediaTogglePlayPause: parent.toggle_play_pause,
            Qt.Key_MediaStop: parent.stop,
            Qt.Key_MediaPrevious: parent.previous_surah,
            Qt.Key_MediaNext: parent.next_surah,
        }
        logger.debug(f"Shortcut keys mapped: {self.shortcuts}")

    def handle_key_press(self, event: QKeyEvent) -> bool:
        """
        Handles key press events by delegating to the appropriate method.

        :param event: The key press event (QKeyEvent).
        :return: True if the event was handled, False otherwise.
        """
        #logger.debug(f"Key pressed: {event.text()} (KeyCode: {event.key()}, Native KeyCode: {event.nativeVirtualKey()})")
        if self.process_arrows(event):
            #logger.debug("Arrow key processed successfully.")
            return True

        if event.modifiers() & (Qt.ControlModifier | Qt.AltModifier):
            #logger.debug("Control or Alt key detected. Ignoring key event.")
            return True

        if  self.process_shortcuts(event):
            #logger.debug("Shortcut key processed successfully.")
            return True
        #logger.debug("Key event did not match any conditions, returning False.")
        return False

    def process_arrows(self, event: QKeyEvent) -> bool:
        """
        Handles left and right arrow keys with different modifier combinations.

        :param event: The key press event (QKeyEvent).
        :return: True if the event was handled, False otherwise.
        """
        action = self.arrow_actions.get(event.key())
        if action:
            for modifier, value in self.arrow_modifiers.items():
                if event.modifiers() == modifier:
                    action(value)
                    logger.debug(f"Executing action with modifier {modifier}: {value} seconds")
                    action(value)
                    return True
        return False

    def process_shortcuts(self, event: QKeyEvent) -> bool:
        """
        Handles predefined keyboard shortcuts for playback control and UI interactions.

        :param event: The key press event (QKeyEvent).
        :return: True if the event was handled, False otherwise.
        """
        key_code = event.nativeVirtualKey() or event.key()
        modifiers = event.modifiers()

        # Ensure Shift is pressed along with a number key (0-9)
        if modifiers & Qt.ShiftModifier:
            if Qt.Key_0 <= key_code <= Qt.Key_9:  # Shift + 0 to Shift + 9
                number = key_code - Qt.Key_0  # Convert key_code to 0-9
                logger.debug(f"Shift + {number} detected, setting position to {number * 10}%")
                self.parent.set_position(number * 10, by_percent=True)
                return True

        # Handle other shortcuts
        action = self.shortcuts.get(key_code)
        if action:
            action()
            return True

        return False

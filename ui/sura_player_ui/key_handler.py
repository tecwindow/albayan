from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt
from utils.universal_speech import UniversalSpeech


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
        self.parent = parent

        # Mapping arrow keys to their respective functions
        self.arrow_actions = {
            Qt.Key_Left: parent.rewind,
            Qt.Key_Right: parent.forward
        }

        # Mapping modifier keys to the corresponding time values for rewinding/forwarding
        self.arrow_modifiers = {
            Qt.ControlModifier | Qt.ShiftModifier: 60,  # Ctrl + Shift -> 60 seconds
            Qt.ShiftModifier: 10,  # Shift -> 10 seconds
            Qt.ControlModifier: 20,  # Ctrl -> 20 seconds
        }

        # Mapping shortcut keys to their corresponding actions
        self.shortcuts = {
            ord("E"): lambda: UniversalSpeech.say(parent.elapsed_time_label.text()),
            ord("R"): lambda: UniversalSpeech.say(parent.remaining_time_label.text()),
            ord("T"): lambda: UniversalSpeech.say(parent.total_time.text()),
            ord("C"): lambda: UniversalSpeech.say(parent.reciter_combo.currentText().split(' - ')[0]),
            ord("V"): lambda: UniversalSpeech.say(parent.surah_combo.currentText()),
            ord("I"): lambda: UniversalSpeech.say(
                f"{parent.surah_combo.currentText()}, {parent.reciter_combo.currentText()}"
            ),
            **{Qt.Key.Key_0 + i: lambda i=i: parent.set_position(i * 10, by_percent=True) for i in range(10)},
            Qt.Key_MediaTogglePlayPause: parent.toggle_play_pause,
            Qt.Key_MediaStop: parent.stop,
            Qt.Key_MediaPrevious: parent.previous_surah,
            Qt.Key_MediaNext: parent.next_surah,
        }

    def handle_key_press(self, event: QKeyEvent) -> bool:
        """
        Handles key press events by delegating to the appropriate method.

        :param event: The key press event (QKeyEvent).
        :return: True if the event was handled, False otherwise.
        """
        if self.process_arrows(event):
            return True

        if event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier | Qt.AltModifier):
            return True

        if  self.process_shortcuts(event):
            return True

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
                    return True
        return False

    def process_shortcuts(self, event: QKeyEvent) -> bool:
        """
        Handles predefined keyboard shortcuts for playback control and UI interactions.

        :param event: The key press event (QKeyEvent).
        :return: True if the event was handled, False otherwise.
        """
        key_code = event.nativeVirtualKey() or event.key()
        action = self.shortcuts.get(key_code)
        if action:
            action()
            return True
        return False

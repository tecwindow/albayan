import re
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QTextEdit


class ReadOnlyTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard| Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

class QuranViewer(ReadOnlyTextEdit):

    def keyPressEvent(self, e):
        super().keyPressEvent(e)
        current_line = self.textCursor().block().text()
        if "سُورَةُ" in current_line or current_line == "|" or not re.search(r"\(\d+\)$", current_line):
            self.parent.interpretation_verse.setEnabled(False)
        else:
            self.parent.interpretation_verse.setEnabled(True)
        return 

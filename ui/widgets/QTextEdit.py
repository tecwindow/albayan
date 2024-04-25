from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QTextEdit, QTextBrowser
from PyQt6.QtGui import QFocusEvent, QTextCursor

class QuranViewer(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.LinksAccessibleByKeyboard)


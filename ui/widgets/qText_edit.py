import re
from PyQt6.QtCore import Qt, QLocale
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QTextEdit


class ReadOnlyTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard| Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setLocale(QLocale("ar"))
        self.setAcceptRichText(True)


class QuranViewer(ReadOnlyTextEdit):

    def keyPressEvent(self, e):
        super().keyPressEvent(e)
        current_line = self.textCursor().block().text()
        status = False if "سُورَةُ" in current_line or current_line == "|" or not re.search(r"\(\d+\)$", current_line) else True
        self.parent.interpretation_verse.setEnabled(status)
        self.parent.save_current_position.setEnabled(status)
        self.parent.menu_bar.save_position_action.setEnabled(status)
        self.parent.menu_bar.surah_info_action.setEnabled(status)
        self.parent.menu_bar.verse_tafsir_action.setEnabled(status)
        self.parent.menu_bar.verse_info_action.setEnabled(status)
        self.parent.menu_bar.verse_grammar_action.setEnabled(status)
        self.parent.menu_bar.copy_verse_action.setEnabled(status)

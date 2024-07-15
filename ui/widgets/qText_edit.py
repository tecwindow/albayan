import re
from PyQt6.QtCore import QEvent, Qt, QLocale
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QTextEdit


class ReadOnlyTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard| Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        font = self.font()
        font.setPointSize(16)
        self.setFont(font)
        self.setAcceptRichText(True)


class QuranViewer(ReadOnlyTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.textChanged.connect(self.set_ctrl)


    def set_ctrl(self):
        current_line_text = self.textCursor().block().text()
        status = False if "سُورَةُ" in current_line_text or current_line_text == "|" or not re.search(r"\(\d+\)$", current_line_text) else True
        self.parent.interpretation_verse.setEnabled(status)
        self.parent.save_current_position.setEnabled(status)
        self.parent.menu_bar.save_position_action.setEnabled(status)
        self.parent.menu_bar.save_bookmark_action.setEnabled(status)
        #self.parent.menu_bar.surah_info_action.setEnabled(status)
        self.parent.menu_bar.verse_tafsir_action.setEnabled(status)
        self.parent.menu_bar.tafaseer_menu.setEnabled(status)
        self.parent.menu_bar.ayah_info_action.setEnabled(status)
        self.parent.menu_bar.verse_info_action.setEnabled(status)
        self.parent.menu_bar.verse_grammar_action.setEnabled(status)
        self.parent.menu_bar.copy_verse_action.setEnabled(status)

    def keyPressEvent(self, e):
        super().keyPressEvent(e)
        self.set_ctrl()

        #Disable temporarily
        return
        current_line = self.textCursor().block().blockNumber()
        total_lines = self.document().blockCount()
        
        if e.key() == Qt.Key.Key_Up:
            if (current_line == 0) and (self.parent.quran.current_pos > 1):
                self.parent.OnBack()
        elif e.key() == Qt.Key.Key_Down:
            if (current_line == total_lines - 1) and (self.parent.quran.current_pos < self.parent.quran.max_pos):
                self.parent.OnNext()



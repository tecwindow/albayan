import re
from PyQt6.QtCore import QEvent, Qt, QLocale
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QTextEdit
from utils.settings import SettingsManager
from utils.const import Globals


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
        document = self.document()
        document.setDefaultCursorMoveStyle(Qt.CursorMoveStyle.VisualMoveStyle)


class QuranViewer(ReadOnlyTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_page_turn_alert = False
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

        if not SettingsManager.current_settings["reading"]["auto_page_turn"]:
            return

        current_line = self.textCursor().block().blockNumber()
        total_lines = self.document().blockCount()
        
        if current_line >= 1 and current_line + 1 != total_lines:
            self.is_page_turn_alert = False

        if e.key() == Qt.Key.Key_Up:
            if (current_line == 0) and (self.parent.quran.current_pos > 1):
                if not self.is_page_turn_alert:
                    self.is_page_turn_alert = True
                    Globals.effects_manager.play("alert")
                    return
                self.parent.OnBack(is_auto_call=True)
        elif e.key() == Qt.Key.Key_Down:
            if (current_line == total_lines - 1) and (self.parent.quran.current_pos < self.parent.quran.max_pos):
                if not self.is_page_turn_alert:
                    self.is_page_turn_alert = True
                    Globals.effects_manager.play("alert")
                    return
                self.parent.OnNext()

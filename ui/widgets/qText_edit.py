import re
from PyQt6.QtCore import QEvent, Qt, QLocale
from PyQt6.QtGui import QKeyEvent, QTextCursor
from PyQt6.QtWidgets import QTextEdit
from core_functions.quran.types import NavigationMode
from utils.settings import Config
from utils.const import Globals
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class ReadOnlyTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("Initializing ReadOnlyTextEdit.")
        self.parent = parent
        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard| Qt.TextInteractionFlag.TextSelectableByMouse)
#        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        font = self.font()
        font.setPointSize(16)
        self.setFont(font)
        self.setAcceptRichText(True)
        document = self.document()
        document.setDefaultCursorMoveStyle(Qt.CursorMoveStyle.VisualMoveStyle)
        logger.debug(F"ReadOnlyTextEdit initialized, with font size: {font.pointSize()}")


class QuranViewer(ReadOnlyTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("Initializing QuranViewer.")
        self.parent = parent
        self.is_page_turn_alert = False
        self.textChanged.connect(self.set_ctrl)
        logger.debug("QuranViewer initialized.")

    def set_ctrl(self):
        #logger.debug("Setting control state.")
        current_line_text = self.textCursor().block().text()
        status = False if "سُورَةُ" in current_line_text or current_line_text == "|" or not re.search(r"\(\d+\)$", current_line_text) else True
        self.parent.interpretation_verse.setEnabled(status)
        self.parent.save_current_position.setEnabled(status)
        self.parent.menu_bar.save_position_action.setEnabled(status)
        self.parent.menu_bar.save_bookmark_action.setEnabled(status)
        self.parent.menu_bar.verse_tafsir_action.setEnabled(status)
        self.parent.menu_bar.tafaseer_menu.setEnabled(status)
        self.parent.menu_bar.ayah_info_action.setEnabled(status)
        self.parent.menu_bar.verse_info_action.setEnabled(status)
        self.parent.menu_bar.verse_grammar_action.setEnabled(status)
        self.parent.menu_bar.copy_verse_action.setEnabled(status)
        #logger.debug(f"Control state set to: {status}.")

    def keyPressEvent(self, e): 
        super().keyPressEvent(e)
        self.set_ctrl()

        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and self.parent.menu_bar.verse_tafsir_action.isEnabled():
            self.parent.OnInterpretation(event=e)
            logger.debug("Enter key pressed, triggering Tafsir.")
            return

        if e.key() == Qt.Key.Key_Space:
            if e.modifiers() & Qt.KeyboardModifier.ControlModifier:  # Ctrl + Space
                self.parent.toolbar.stop_audio()
                logger.debug("Audio stopped (Ctrl + Space).")
                return
            elif e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.parent.toolbar.toggle_play_pause()
                logger.debug("Audio toggled (Shift+Space).")
                return
            else:  
                   self.parent.toolbar.toggle_play_pause()
            logger.debug("Audio toggled (Space).")
            return

        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if e.key() == Qt.Key.Key_Shift:
                if e.nativeScanCode() == 42:  # Scan code for Left Shift
                    self.document().setDefaultCursorMoveStyle(Qt.CursorMoveStyle.LogicalMoveStyle)
                    self.parent.menu_bar.set_text_direction_ltr()
                    self.document().setDefaultCursorMoveStyle(Qt.CursorMoveStyle.VisualMoveStyle)
                    logger.debug("Text direction set to Left-to-Right (Ctrl + Left Shift).")
                elif e.nativeScanCode() == 54: # Scan code for Right Shift
                    self.document().setDefaultCursorMoveStyle(Qt.CursorMoveStyle.LogicalMoveStyle)
                    self.parent.menu_bar.set_text_direction_rtl()
                    self.document().setDefaultCursorMoveStyle(Qt.CursorMoveStyle.VisualMoveStyle)
                    logger.debug("Text direction set to Right-to-Left (Ctrl + Right Shift).")


        if not Config.reading.auto_page_turn or self.parent.quran_manager.navigation_mode == NavigationMode.CUSTOM_RANGE:
            return

        current_line = self.textCursor().block().blockNumber()
        total_lines = self.document().blockCount()
        
        if current_line >= 1 and current_line + 1 != total_lines:
            self.is_page_turn_alert = False

        if e.key() == Qt.Key.Key_Up:
            if (current_line == 0) and (self.parent.quran_manager.current_position > 1):
                if not self.is_page_turn_alert:
                    self.is_page_turn_alert = True
                    Globals.effects_manager.play("alert")
                    logger.debug("Reached top of page. Page turn alert triggered.")
                    return
                self.parent.OnBack(is_auto_call=True)
                logger.debug("Page turned back.")
        elif e.key() == Qt.Key.Key_Down:
            if (current_line == total_lines - 1) and (self.parent.quran_manager.current_position < self.parent.quran_manager.max_position):
                if not self.is_page_turn_alert:
                    self.is_page_turn_alert = True
                    Globals.effects_manager.play("alert")
                    logger.debug("Reached bottom of page. Page turn alert triggered.")
                    return
                self.parent.OnNext()
                logger.debug("Page turned forward.")


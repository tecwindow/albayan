import os
import re
import json
import random

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout, 
    QLabel, 
    QPushButton, 
    QMenu, 
    QHBoxLayout, 
    QMainWindow, 
    QMessageBox,
    QComboBox,
    QInputDialog,
    QApplication,
    QTextEdit,
    QSystemTrayIcon
)
import qtawesome as qta
from PyQt6.QtGui import QIcon, QAction, QShowEvent, QTextCursor, QKeySequence, QShortcut
from core_functions.quran.quran_manager import QuranManager
from core_functions.quran.formatter import FormatterOptions
from core_functions.quran.types import QuranFontType, NavigationMode, Ayah, MarksType
from core_functions.tafaseer import Category
from core_functions.info import MoshafInfo, E3rab, TanzilAyah, AyaInfo, SuraInfo, JuzInfo, HizbInfo, QuarterInfo, PageInfo
from core_functions.bookmark import BookmarkManager
from ui.dialogs.quick_access import QuickAccess
from ui.dialogs.find import SearchDialog
from ui.widgets.button import EnterButton
from ui.widgets.menu_bar import MenuBar
from ui.widgets.qText_edit import QuranViewer
from ui.dialogs.tafaseer_Dialog import TafaseerDialog
from ui.dialogs.info_dialog import InfoDialog
from ui.dialogs.custom_range import CustomRangeDialog
from ui.sura_player_ui.sura_player_ui import SuraPlayerWindow
from ui.widgets.system_tray import SystemTrayManager
from ui.widgets.toolbar import AudioToolBar
from utils.settings import Config
from utils.universal_speech import UniversalSpeech
from utils.user_data import PreferencesManager
from utils.const import program_name, program_icon, user_db_path, data_folder, Globals
from utils.logger import LoggerManager
from utils.audio_player import SoundEffectPlayer
from exceptions.error_decorators import exception_handler

logger = LoggerManager.get_logger(__name__)

class QuranInterface(QMainWindow):
    def __init__(self, title):
        super().__init__()
        logger.debug("Initializing QuranInterface...")
        self.setWindowTitle(title)
        self.resize(800, 600)
        self.center_window()
        self.setWindowIcon(QIcon("Albayan.ico"))
        self.quran_manager = QuranManager(
            QuranFontType.from_int(Config.reading.font_type)
        )
        self.quran_manager.formatter_options.auto_page_turn = Config.reading.auto_page_turn
        self.quran_manager.formatter_options.marks_type = MarksType.from_int(Config.reading.marks_type)
        self.preferences_manager = PreferencesManager(user_db_path)
        self.sura_player_window = None
        Globals.effects_manager = SoundEffectPlayer("Audio/sounds")

        self.toolbar = AudioToolBar(self)
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.addToolBar(self.toolbar)

        self.tray_manager = SystemTrayManager(self, program_name, program_icon)
        self.create_widgets()
        self.create_layout()
        self.set_text()
        self.set_shortcut()
        logger.debug("QuranInterface initialized successfully.")

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def set_shortcut(self):
        QShortcut(QKeySequence("Ctrl+M"), self).activated.connect(lambda: self.quran_view.setFocus())
        QShortcut(QKeySequence("C"), self).        activated.connect(self.say_played_ayah)
        QShortcut(QKeySequence("Alt+Shift+C"), self).activated.connect(lambda: self.toolbar.change_ayah_focus(manual=True))
        QShortcut(QKeySequence("V"), self).        activated.connect(self.say_focused_ayah)

    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.quran_title = QLabel()
        font = self.quran_title.font()
        font.setPointSize(16)
        font.setBold(True)
        self.quran_title.setFont(font)

        self.quran_view = QuranViewer(self)
        self.quran_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.quran_view.customContextMenuRequested.connect(self.onContextMenu)
        
        self.next_to = EnterButton()
        self.next_to.setIcon(qta.icon("fa.forward"))
        self.next_to.setToolTip(self.next_to.text())
        self.next_to.setAccessibleName(self.next_to.text())
        self.next_to.clicked.connect(self.OnNext)
        
        self.back_to = EnterButton()
        self.back_to.setIcon(qta.icon("fa.backward"))
        self.back_to.setToolTip(self.back_to.text())
        self.back_to.setAccessibleName(self.back_to.text())
        self.back_to.clicked.connect(self.OnBack)
        
        self.interpretation_verse = EnterButton()
        self.interpretation_verse.setIcon(qta.icon("fa.book"))
        self.interpretation_verse.setToolTip("تفسير الآية")
        self.interpretation_verse.setAccessibleName("تفسير الآية")
        self.interpretation_verse.setEnabled(False)
        self.interpretation_verse.clicked.connect(self.OnInterpretation)
        
        self.quick_access = EnterButton()
        self.quick_access.setIcon(qta.icon("fa.bolt"))
        self.quick_access.setToolTip("الوصول السريع")
        self.quick_access.setAccessibleName("الوصول السريع")
        self.quick_access.clicked.connect(self.OnQuickAccess)
        
        self.search_in_quran = EnterButton()
        self.search_in_quran.setIcon(qta.icon("fa.search"))
        self.search_in_quran.setToolTip("البحث في القرآن")
        self.search_in_quran.setAccessibleName("البحث في القرآن")
        self.search_in_quran.clicked.connect(self.OnSearch)
        
        self.save_current_position = EnterButton()
        self.save_current_position.setIcon(qta.icon("fa.save"))
        self.save_current_position.setToolTip("حفظ الموضع الحالي")
        self.save_current_position.setAccessibleName("حفظ الموضع الحالي")
        self.save_current_position.setEnabled(False)
        self.save_current_position.clicked.connect(self.OnSaveCurrentPosition)
        self.save_current_position.clicked.connect(self.OnSave_alert)
        
        self.tasbih = EnterButton()
        self.tasbih.setIcon(qta.icon("fa.circle"))
        self.tasbih.setToolTip("المسبحة")
        self.tasbih.setAccessibleName("المسبحة")
        self.tasbih.clicked.connect(self.menu_bar.OnTasbihAction)

        self.quran_player = EnterButton()
        self.quran_player.setIcon(qta.icon("fa.play-circle"))
        self.quran_player.setToolTip("مشغل القرآن")
        self.quran_player.setAccessibleName("مشغل القرآن")
        self.quran_player.clicked.connect(self.menu_bar.OnSuraPlayer)

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.quran_title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.quran_view)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.next_to)
        buttons_layout.addWidget(self.back_to)
        buttons_layout.addWidget(self.interpretation_verse)
        buttons_layout.addWidget(self.quick_access)
        buttons_layout.addWidget(self.search_in_quran)
        buttons_layout.addWidget(self.save_current_position)
        buttons_layout.addWidget(self.tasbih)
        buttons_layout.addWidget(self.quran_player)


        layout.addLayout(buttons_layout)
        self.centralWidget().setLayout(layout)


    def set_text(self):
        logger.debug("Loading Quran text...")
        ayah_number = self.preferences_manager.get_int("current_ayah_number", 1)
        current_position = self.preferences_manager.get_int("current_position", 1)
        mode = self.preferences_manager.get_int("navigation_mode", NavigationMode.SURAH.value)
        self.quran_manager.navigation_mode = NavigationMode.from_int(mode)
        logger.debug(f"Current position: {current_position}, Ayah number: {ayah_number}, Mode: {self.quran_manager.navigation_mode}")
        self.menu_bar.browse_mode_actions[mode].setChecked(True)
        
        if self.quran_manager.navigation_mode == NavigationMode.CUSTOM_RANGE:
            range = {key: self.preferences_manager.get_int(key, 1) for key in ("from_surah", "from_ayah", "to_surah", "to_ayah")}
            logger.debug(f"Custom range detected: {range}")
            text = self.quran_manager.get_range(**range)
        else:
            text = self.quran_manager.go_to(current_position)
            
        self.quran_view.setText(text)
        self.set_text_ctrl_label()
        self.set_focus_to_ayah(ayah_number)
        logger.debug("Quran text loaded successfully.")

    def set_focus_to_ayah(self, ayah_number: int):
        """set the Cursor to ayah_position in the text"""
        logger.debug(f"Setting focus to Ayah number: {ayah_number}")
        if ayah_number == -1:
            logger.debug("Setting focus to the end of the text.")
            text_position = len(self.quran_view.toPlainText())
        else:
            text_position = self.quran_manager.view_content.get_by_ayah_number(ayah_number).first_position
        logger.debug(f"Text position: {text_position}")

        cursor = QTextCursor(self.quran_view.document())
        cursor.setPosition(text_position)
        self.quran_view.setTextCursor(cursor)
        logger.debug("Focus set successfully.")

    def OnNext(self):
        logger.debug("Next button clicked.")
        self.quran_view.setText(self.quran_manager.next())
        self.set_text_ctrl_label()
        Globals.effects_manager.play("next")
        logger.debug("Text set successfully.")
        if self.quran_manager.current_position == self.quran_manager.max_position:
            logger.debug("Reached the end of the Quran.")
            self.quran_view.setFocus()

    def OnBack(self, is_auto_call: bool = False):
        logger.debug("Back button clicked.")
        self.quran_view.setText(self.quran_manager.back())
        self.set_text_ctrl_label()
        Globals.effects_manager.play("previous")
        logger.debug("Text set successfully.")
        if self.quran_manager.current_position == 1:            
            logger.debug("Reached the beginning of the Quran.")
            self.quran_view.setFocus()
        if Config.reading.auto_page_turn and is_auto_call:
            self.set_focus_to_ayah(-1)
            logger.debug("Focus set to end of previous Text.")

    def set_text_ctrl_label(self):
        logger.debug("Setting text control label.")
        
        label = self.quran_manager.view_content.label
        if self.quran_manager.navigation_mode in (NavigationMode.SURAH, NavigationMode.PAGE):
            next_label = "التالية"
            previous_label = "السابقة"
        else:
            next_label = "التالي"
            previous_label = "السابق"
        
        self.next_to.setText(f"ال{label} {next_label}")
        self.menu_bar.next_action.setText(f"ال{label} {next_label}")
        self.back_to.setText(f"ال{label} {previous_label}")
        self.menu_bar.previous_action.setText(f"ال{label} {previous_label}")

        # set the label
        label = self.quran_manager.view_content.edit_label
        self.quran_title.setText(label)
        self.quran_view.setAccessibleName(label)
        logger.debug(f"Label set to: {label}")
        if self.isActiveWindow():
                UniversalSpeech.say(label)

        # Enable back and next item
        next_status = self.quran_manager.current_position < self.quran_manager.max_position and self.quran_manager.navigation_mode != NavigationMode.CUSTOM_RANGE
        back_status = self.quran_manager.current_position > 1 and self.quran_manager.navigation_mode != NavigationMode.CUSTOM_RANGE
        self.next_to.setEnabled(next_status)
        self.menu_bar.next_action.setEnabled(next_status)
        self.back_to.setEnabled(back_status)
        self.menu_bar.previous_action.setEnabled(back_status)
        self.menu_bar.go_to_action.setEnabled(self.quran_manager.navigation_mode != NavigationMode.CUSTOM_RANGE)
        self.toolbar.navigation.reset_position()
        self.toolbar.set_buttons_status()
        logger.debug("Buttons status set.")

    @exception_handler(ui_element=QMessageBox)
    def OnQuickAccess(self, event):
        logger.debug("Quick access button clicked.")
        dialog = QuickAccess(self, "الوصول السريع")
        if not dialog.exec():
            logger.debug("QuickAccess dialog canceled.")
            return
        else:
            logger.debug("QuickAccess dialog accepted.")
        
        self.set_text_ctrl_label()
        self.quran_view.setFocus()

    @exception_handler(ui_element=QMessageBox)
    def OnSearch(self, event):
        logger.debug("Search button clicked.")
        search_dialog = SearchDialog(self, "بحث")
        if not search_dialog.exec():
            logger.debug("Search dialog canceled.")
            return  
        else:
            logger.debug("Search dialog accepted.")
            self.set_text_ctrl_label()

    def get_current_ayah(self) -> Ayah:
        logger.debug("Getting current Ayah info.")
        current_line = self.quran_view.textCursor().block()
        position = current_line.position()
        ayah = self.quran_manager.view_content.get_by_position(position)
        logger.debug(f"Retrieved current Ayah: {ayah.number}")
        return ayah
    
    @exception_handler(ui_element=QMessageBox)
    def OnInterpretation(self, event=None):
        logger.debug("Interpretation clicked.")

        sender = self.sender()
        if sender is not None:
            selected_category = sender.text()
            logger.debug(f"Selected category: {selected_category}")
        else:
            selected_category = "الميسر"
        logger.debug(f"set the default category: {selected_category}")
        if selected_category not in Category.get_categories_in_arabic():
            logger.warning("Invalid category, defaulting to الميسر.")
            selected_category = "الميسر"

        current_ayah = self.get_current_ayah()
        title = "تفسير آية {} من {}".format(current_ayah.number_in_surah, current_ayah.sura_name)
        logger.debug(f"Opening TafaseerDialog with title: {title}")
        dialog = TafaseerDialog(self, title, current_ayah, selected_category)
        dialog.exec()
        logger.debug("TafaseerDialog closed.")

    def onContextMenu(self):
        logger.debug("Context menu requested.")
        menu = QMenu(self)
        save_current_position = menu.addAction("حفظ الموضع الحالي")
        save_bookmark = menu.addAction("حفظ علامة")

        info_menu = menu.addMenu("المعلومات")
    
        ayah_info = info_menu.addAction("معلومات الآية")
        get_sura_info = info_menu.addAction("معلومات السورة")
        get_juz_info = info_menu.addAction("معلومات الجزء")
        get_hizb_info = info_menu.addAction("معلومات الحزب")
        get_quarter_info = info_menu.addAction("معلومات الربع")
        get_page_info = info_menu.addAction("معلومات الصفحة")
        get_moshaf_info = info_menu.addAction("معلومات المصحف")

        get_moshaf_info.triggered.connect(self.OnMoshafInfo)
        get_sura_info.triggered.connect(self.OnSurahInfo)
        get_juz_info.triggered.connect(self.OnJuzInfo)
        get_hizb_info.triggered.connect(self.OnHizbInfo)
        get_quarter_info.triggered.connect(self.OnQuarterInfo)
        get_page_info.triggered.connect(self.OnPageInfo)
        ayah_info.triggered.connect(self.OnAyahInfo)

        get_interpretation_verse = menu.addAction("تفسير الآية")
        get_interpretation_verse.triggered.connect(self.OnInterpretation)

        submenu = menu.addMenu("التفسير")
        arabic_categories = Category.get_categories_in_arabic()
        for arabic_category in arabic_categories:
            action = QAction(arabic_category, self)
            action.triggered.connect(self.OnInterpretation)
            submenu.addAction(action)

        save_current_position.triggered.connect(self.OnSaveCurrentPosition)
        save_current_position.triggered.connect(self.OnSave_alert)
        save_bookmark.triggered.connect(self.OnSaveBookmark)

        get_verse_syntax = menu.addAction("إعراب الآية")
        get_verse_syntax.triggered.connect(self.OnSyntax)
        get_verse_reasons = menu.addAction("أسباب نزول الآية")
        get_verse_reasons.triggered.connect(self.OnVerseReasons)
        copy_verse = menu.addAction("نسخ الآية")
        copy_verse.triggered.connect(self.on_copy_verse)

        current_line = self.quran_view.textCursor().block().text()
        if "سُورَةُ" in current_line or current_line == "" or not re.search(r"\(\d+\)$", current_line):
            save_current_position.setEnabled(False)
            save_bookmark.setEnabled(False)
            copy_verse.setEnabled(False)
            get_interpretation_verse.setEnabled(False)
            submenu.setEnabled(False)
            ayah_info.setEnabled(False)
            get_verse_syntax.setEnabled(False)
            get_verse_reasons.setEnabled(False)

        menu.setAccessibleName("الإجراءات")
        menu.setFocus()
        menu.exec(self.quran_view.mapToGlobal(self.quran_view.pos()))        
        logger.debug("Context menu executed.")

    def on_copy_verse(self):
        logger.debug("Copy verse action triggered.")
        current_line = self.quran_view.textCursor().block().text()
        clipboard = QApplication.clipboard()
        clipboard.setText(current_line)
        UniversalSpeech.say("تم نسخ الآية.")
        Globals.effects_manager.play("copy")
        logger.debug(f"Ayah {current_line} copied to clipboard.")

    @exception_handler(ui_element=QMessageBox)
    def OnSyntax(self, event):
        logger.debug("Syntax action triggered.")
        current_aya = self.get_current_ayah()
        title = "إعراب آية رقم {} من {}".format(current_aya.number_in_surah, current_aya.sura_name)
        label = "الإعراب"
        text = E3rab(current_aya.sura_number, current_aya.number).text
        logger.debug(f"Syntax details retrieved for ayah {current_aya.number_in_surah} in {current_aya.sura_name}")
        InfoDialog(self, title, label, text).exec()
        logger.debug("Syntax dialog closed.")

    @exception_handler(ui_element=QMessageBox)
    def OnVerseReasons(self, event):
        logger.debug("Verse reasons action triggered.")
        current_aya = self.get_current_ayah()
        title = "أسباب نزول آية رقم {} من {}".format(current_aya.number_in_surah, current_aya.sura_name)
        label = "الأسباب"
        text = TanzilAyah(current_aya.number).text

        if text:
            logger.debug(f"Reasons retrieved for ayah {current_aya.number_in_surah} in {current_aya.sura_name}")
            InfoDialog(self, title, label, text).exec()
            logger.debug("Verse reasons dialog closed.")
        else:
            logger.warning("No reasons available for this ayah.")
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("لا يتوفر معلومات للآية")
            msg_box.setText("للأسف لا يتوفر في الوقت الحالي معلومات لهذه الآية.")

            ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
            msg_box.exec()

    @exception_handler(ui_element=QMessageBox)
    def OnMoshafInfo(self, event):
        logger.debug("Moshaf info action triggered.")
        title = "معلومات المصحف"
        label = "معلومات المصحف:"
        text = MoshafInfo().text
        logger.debug("Displaying Moshaf information.")
        InfoDialog(self, title, label, text).open()

    @exception_handler(ui_element=QMessageBox)
    def OnAyahInfo(self, event):
        logger.debug("Ayah info action triggered.")
        current_aya = self.get_current_ayah()
        title = "معلومات آية رقم {} من {}".format(current_aya.number_in_surah, current_aya.sura_name)
        label = "معلومات الآية:"
        text = AyaInfo(current_aya.number).text
        logger.debug(f"Displaying information for ayah {current_aya.number_in_surah} in {current_aya.sura_name}")
        InfoDialog(self, title, label, text, is_html_content=True).open()

    @exception_handler(ui_element=QMessageBox)
    def OnSurahInfo(self, event):
        logger.debug("Surah info action triggered.")
        current_aya = self.get_current_ayah()
        title = "معلومات {}".format(current_aya.sura_name)
        label = "معلومات السورة:"
        sura_info = SuraInfo(current_aya.sura_number)
        logger.debug(f"Displaying information for surah {current_aya.sura_name}")
        InfoDialog(self, title, label, sura_info.text, is_html_content=True).open()

    @exception_handler(ui_element=QMessageBox)
    def OnJuzInfo(self, event):
        logger.debug("Juz info action triggered.")
        current_aya = self.get_current_ayah()
        title = "معلومات الجزء {}".format(current_aya.juz)
        label = "معلومات الجزء:"
        juz_info = JuzInfo(current_aya.juz)
        logger.debug(f"Displaying information for juz {current_aya.juz}")
        InfoDialog(self, title, label, juz_info.text).open()

    @exception_handler(ui_element=QMessageBox)
    def OnHizbInfo(self, event):
        logger.debug("Hizb info action triggered.")
        current_aya = self.get_current_ayah()
        title = "معلومات الحزب {}".format(current_aya.hizb)
        label = "معلومات الحزب:"
        hizb_info = HizbInfo(current_aya.hizb)
        logger.debug(f"Displaying information for hizb {current_aya.hizb}")
        InfoDialog(self, title, label, hizb_info.text).open()

    @exception_handler(ui_element=QMessageBox)
    def OnQuarterInfo(self, event):
        logger.debug("Quarter info action triggered.")
        current_aya = self.get_current_ayah()
        title = "معلومات الربع {}".format(current_aya.hizbQuarter)
        label = "معلومات الربع:"
        quarter_info = QuarterInfo(current_aya.hizbQuarter)
        logger.debug(f"Displaying information for quarter {current_aya.hizbQuarter}")
        InfoDialog(self, title, label, quarter_info.text).open()

    @exception_handler(ui_element=QMessageBox)
    def OnPageInfo(self, event):
        logger.debug("Page info action triggered.")
        current_aya = self.get_current_ayah()
        title = "معلومات الصفحة {}".format(current_aya.page)
        label = "معلومات الصفحة:"
        page_info = PageInfo(current_aya.page)
        logger.debug(f"Displaying information for page {current_aya.page}")
        InfoDialog(self, title, label, page_info.text).open()

    def say_played_ayah(self):
        logger.debug("Say played Ayah action triggered.")
        current_aya = self.get_current_ayah()
        text = f"آية {self.toolbar.navigation.current_ayah} من {current_aya.sura_name}"
        logger.debug(f"Text to be spoken: {text}")
        if self.toolbar.navigation.current_ayah:
            if self.toolbar.player.is_playing():
                UniversalSpeech.say(f"{text}، الآية المشغلة.")
                logger.debug(f"{text} is currently playing.")
            elif self.toolbar.player.is_paused():
                UniversalSpeech.say(f"{text}، تم إيقافها مؤقتًا.")
                logger.debug(f"{text} is paused.")
            elif self.toolbar.player.is_stopped():
                UniversalSpeech.say(f"{text}، تم إيقافها.")
                logger.debug(f"{text} is stopped.")
            elif self.toolbar.player.is_stalled():
                UniversalSpeech.say(f"{text}، يجري تحميلها.")
                logger.debug(f"{text} is stalled.")
        else:
            UniversalSpeech.say("لم يتم تشغيل أي آية.")
            logger.debug("No Ayah is currently playing.")

    def say_focused_ayah(self):
        logger.debug("Say focused Ayah action triggered.")
        current_aya = self.get_current_ayah()
        text = f"آية {current_aya.number_in_surah} من {current_aya.sura_name}، الآية الحالية."
        logger.debug(f"Text to be spoken: {text}")
        UniversalSpeech.say(text)

    @exception_handler(ui_element=QMessageBox)
    def OnSaveBookmark(self, event):
        logger.debug("Save bookmark action triggered.")

        bookmark_manager= BookmarkManager()
        current_aya = self.get_current_ayah()
        logger.debug(f"Information retrieved for bookmark: {current_aya} and navigation mode: {self.quran_manager.navigation_mode}")
        if bookmark_manager.is_exist(current_aya.number):
            logger.warning("Bookmark already exists for this ayah.")
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setWindowTitle("خطأ")
            msgBox.setText("تم حفظ العلامة المرجعية مسبقًا.")
            msgBox.addButton("موافق", QMessageBox.AcceptRole)
            msgBox.exec()
            return

        logger.debug("Bookmark does not exist, proceeding to save.")
        dialog = QInputDialog(self)
        dialog.setWindowTitle("اسم العلامة")
        dialog.setLabelText("أدخل اسم العلامة:")
        dialog.setTextValue("")
    
        dialog.setOkButtonText("إضافة")
        dialog.setCancelButtonText("إلغاء")
    
        if dialog.exec() == dialog.Accepted:
            name = dialog.textValue()
            if name:
                logger.debug(f"Bookmark name entered: {name}")
                bookmark_manager.insert_bookmark(
                    name, 
                    current_aya.number, 
                    current_aya.number_in_surah, 
                    current_aya.sura_number,
                    current_aya.sura_name, 
                    self.quran_manager.navigation_mode.value
                )
                logger.debug("Bookmark saved successfully.")                    
                self.quran_view.setFocus()
            else:
                logger.warning("Bookmark name is empty.")
                return
        else:
            logger.debug("Bookmark dialog canceled.")   
            return

    def OnSaveCurrentPosition(self):
        logger.debug("Save current position action triggered.")
        current_ayah = self.get_current_ayah()
        self.preferences_manager.set_preferences({
                "current_ayah_number": current_ayah.number,
                "current_position": self.quran_manager.current_position,
                "navigation_mode": self.quran_manager.navigation_mode.value
            })
        logger.debug(f"Current position saved: {self.quran_manager.current_position}, Ayah: {current_ayah.number}, navigation mode: {self.quran_manager.navigation_mode}")

    def OnSave_alert(self):
        logger.debug("Save alert action triggered.")
        UniversalSpeech.say("تم حفظ الموضع الحالي.")
        Globals.effects_manager.play("save")
        logger.debug("Save alert played.")

    def OnCustomRange(self):
        range = {key: self.preferences_manager.get_int(key, 1) for key in ("from_surah", "from_ayah", "to_surah", "to_ayah")}
        ccustom_range_dialog = CustomRangeDialog(self, self.quran_manager.get_surahs(), range)
        if ccustom_range_dialog.exec():
            range = ccustom_range_dialog.get_range()
            self.preferences_manager.set_preferences(range)
            text = self.quran_manager.get_range(**range)
            self.quran_view.setText(text)
            self.set_text_ctrl_label()
        
    def OnChangeNavigationMode(self, mode):
        logger.debug(f"Changing navigation mode to: {mode}")
        current_ayah = self.get_current_ayah()
        self.quran_manager.navigation_mode = NavigationMode.from_int(mode)
        self.menu_bar.browse_mode_actions[mode].setChecked(True)

        if mode == NavigationMode.CUSTOM_RANGE.value:
            return self.OnCustomRange()
            
        self.quran_view.setText(self.quran_manager.get_by_ayah_number(current_ayah.number))
        self.set_focus_to_ayah(current_ayah.number)
        self.set_text_ctrl_label()
        Globals.effects_manager.play("change")
        logger.debug(f"Navigation mode changed. Now focusing on ayah {current_ayah.number} in mode {self.quran_manager.navigation_mode}")

    def closeEvent(self, event):
        logger.debug("Close event triggered.")
        if Config.general.run_in_background_enabled:
            logger.debug("Running in background.")
            event.ignore()
            self.hide()
            icon_path = "Albayan.ico"
            logger.debug(f"Showing notification.")
            self.tray_manager.tray_icon.showMessage("البيان", "تم تصغير نافذة البيان على صينية النظام, البرنامج يعمل في الخلفية.", QIcon(icon_path), msecs=5000)
            logger.debug("notification shown.")
            logger.debug("App minimized to tray.")
        else:
            logger.debug("Closing application.")
            self.tray_manager.hide_icon()
            
    @exception_handler(ui_element=QMessageBox)
    def OnRandomMessages(self, event):
        logger.debug("Random messages action triggered.")
        info_dialog = InfoDialog(self, 'رسالة لك', '', "", is_html_content=False, show_message_button=True, save_message_as_img_button=True)
        info_dialog.choose_QuotesMessage()
        logger.debug("Random message dialog opened.")
        info_dialog.exec()
        logger.debug("Random message dialog closed.")

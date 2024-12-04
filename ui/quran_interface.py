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
    QTextEdit
)
from PyQt6.QtGui import QIcon, QAction, QShowEvent, QTextCursor, QKeySequence, QShortcut
from core_functions.quran_class import quran_mgr
from core_functions.tafaseer import Category
from core_functions.info import E3rab, TanzilAyah, AyaInfo
from core_functions.bookmark import BookmarkManager
from ui.dialogs.quick_access import QuickAccess
from ui.dialogs.find import SearchDialog
from ui.widgets.button import EnterButton
from ui.widgets.menu_bar import MenuBar
from ui.widgets.qText_edit import QuranViewer
from ui.dialogs.tafaseer_Dialog import TafaseerDialog
from ui.dialogs.info_dialog import InfoDialog
from ui.widgets.system_tray import SystemTrayManager
from ui.widgets.toolbar import AudioToolBar
from utils.settings import SettingsManager
from utils.universal_speech import UniversalSpeech
from utils.user_data import UserDataManager
from utils.const import program_name, program_icon, user_db_path, data_folder, Globals
from utils.audio_player import bass, SoundEffectPlayer


class QuranInterface(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)
        self.quran = quran_mgr()
        self.quran.load_quran(os.path.join("database", "quran", "quran.DB"))
        self.user_data_manager = UserDataManager(user_db_path)
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

    def set_shortcut(self):
        for i in range(0, 5):  
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            shortcut.activated.connect(lambda mode=i: self.OnChangeNavigationMode(mode))

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
        
        self.next_to = EnterButton("التالي")
        self.next_to.clicked.connect(self.OnNext)
        
        self.back_to = EnterButton("السابق")
        self.back_to.clicked.connect(self.OnBack)

        self.interpretation_verse = EnterButton("تفسير الآية")
        self.interpretation_verse.setEnabled(False)
        self.interpretation_verse.clicked.connect(self.OnInterpretation)

        self.quick_access = EnterButton("الوصول السريع")
        self.quick_access.clicked.connect(self.OnQuickAccess)

        self.search_in_quran = EnterButton("البحث في القرآن")
        self.search_in_quran.clicked.connect(self.OnSearch)
        self.save_current_position = EnterButton("حفظ الموضع الحالي")
        self.save_current_position.setEnabled(False)
        self.save_current_position.clicked.connect(self.OnSaveCurrentPosition)

        self.random_messages = EnterButton("رسالة عشوائية")
        self.random_messages.clicked.connect(self.OnRandomMessages)


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
        buttons_layout.addWidget(self.random_messages)


        layout.addLayout(buttons_layout)
        self.centralWidget().setLayout(layout)


    def set_text(self):
        position_data = self.user_data_manager.get_last_position()
        ayah_number = position_data.get("ayah_number", 1)
        current_positiom = position_data.get("position", 1)
        self.quran.type = position_data.get("criteria_number", 0)
        

        text = self.quran.goto(current_positiom)
        self.quran_view.setText(text)
        self.set_text_ctrl_label()
        self.set_focus_to_ayah(ayah_number)

    def set_focus_to_ayah(self, ayah_number: int):
        """set the Cursor to ayah_position in the text"""
        if ayah_number == -1:
            text_position = len(self.quran_view.toPlainText())
        else:
            text_position = self.quran.ayah_data.get_position(ayah_number)

        cursor = QTextCursor(self.quran_view.document())
        cursor.setPosition(text_position)
        self.quran_view.setTextCursor(cursor)
        

    def OnNext(self):
        self.quran_view.setText(self.quran.next())
        self.set_text_ctrl_label()
        Globals.effects_manager.play("next")
        if self.quran.current_pos == self.quran.max_pos:
            self.quran_view.setFocus()

    def OnBack(self):
        self.quran_view.setText(self.quran.back())
        self.set_text_ctrl_label()
        Globals.effects_manager.play("previous")
        if self.quran.current_pos == 1:            
            self.quran_view.setFocus()
        if SettingsManager.current_settings["reading"]["auto_page_turn"]:
            self.set_focus_to_ayah(-1)
    
    def set_text_ctrl_label(self):

        label = ""
        if self.quran.type == 0:
            label = f"الصفحة {self.quran.current_pos}"
            self.next_to.setText("الصفحة التالية")
            self.menu_bar.next_action.setText("الصفحة التالية")
            self.back_to.setText("الصفحة السابقة")
            self.menu_bar.previous_action.setText("الصفحة السابقة")
        elif self.quran.type == 1:
            label = self.quran.data_list[-1][2]
            self.next_to.setText("السورة التالية")
            self.menu_bar.next_action.setText("السورة التالية")
            self.back_to.setText("السورة السابقة")
            self.menu_bar.previous_action.setText("السورة السابقة")    
        elif self.quran.type == 2:
            label = f"الربع {self.quran.current_pos}"
            self.next_to.setText("الربع التالي")
            self.menu_bar.next_action.setText("الربع التالي")
            self.back_to.setText("الربع السابق")
            self.menu_bar.previous_action.setText("الربع السابق")
        elif self.quran.type == 3:
            label = f"الحزب {self.quran.current_pos}"
            self.next_to.setText("الحزب التالي")
            self.menu_bar.next_action.setText("الحزب التالي")
            self.back_to.setText("الحزب السابق")
            self.menu_bar.previous_action.setText("الحزب السابق")
        elif self.quran.type == 4:
            label = f"الجزء {self.quran.current_pos}"
            self.next_to.setText("الجزء التالي")
            self.menu_bar.next_action.setText("الجزء التالي")
            self.back_to.setText("الجزء السابق")
            self.menu_bar.previous_action.setText("الجزء السابق")


        # set the label
        self.quran_title.setText(label)
        self.quran_view.setAccessibleName(label)
        UniversalSpeech.say(label)
        
        # Enable back and next item
        next_status = self.quran.current_pos < self.quran.max_pos
        back_status = self.quran.current_pos > 1
        self.next_to.setEnabled(next_status)
        self.menu_bar.next_action.setEnabled(next_status)
        self.back_to.setEnabled(back_status)
        self.menu_bar.previous_action.setEnabled(back_status)
        self.toolbar.navigation.reset_position()
        
    def OnQuickAccess(self):
        dialog = QuickAccess(self, "الوصول السريع")
        if not dialog.exec():
            return
        
        self.set_text_ctrl_label()
        self.quran_view.setFocus()

    def OnSearch(self):
        search_dialog = SearchDialog(self, "بحث")
        if search_dialog.exec():
            self.set_text_ctrl_label()

    def get_current_ayah_info(self) -> list:

        current_line = self.quran_view.textCursor().block()
        position = current_line.position()
        ayah_info = self.quran.get_ayah_info(position)

        return ayah_info
    
    def OnInterpretation(self):

        selected_category = self.sender().text()
        if selected_category not in Category.get_categories_in_arabic():
            selected_category = "الميسر"

        ayah_info = self.get_current_ayah_info()
        title = "تفسير آية {} من {}".format(ayah_info[3], ayah_info[2])
        dialog = TafaseerDialog(self, title, ayah_info, selected_category)
        dialog.exec()

    def onContextMenu(self):
        menu = QMenu(self)
        save_current_position = menu.addAction("حفظ الموضع الحالي")
        save_bookmark = menu.addAction("حفظ علامة")
        #get_sura_info = menu.addAction("معلومات السورة")
        get_interpretation_verse = menu.addAction("تفسير الآية")
        get_interpretation_verse.triggered.connect(self.OnInterpretation)

        submenu = menu.addMenu("تفسير الآية")
        arabic_categories = Category.get_categories_in_arabic()
        for arabic_category in arabic_categories:
            action = QAction(arabic_category, self)
            action.triggered.connect(self.OnInterpretation)
            submenu.addAction(action)

        save_current_position.triggered.connect(self.OnSaveCurrentPosition)
        save_bookmark.triggered.connect(self.OnSaveBookmark)
        ayah_info = menu.addAction("معلومات الآية")
        ayah_info.triggered.connect(self.OnAyahInfo)
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
            #get_sura_info.setEnabled(False)
            get_interpretation_verse.setEnabled(False)
            submenu.setEnabled(False)
            ayah_info.setEnabled(False)
            get_verse_syntax.setEnabled(False)
            get_verse_reasons.setEnabled(False)

        menu.setAccessibleName("الإجراءات")
        menu.setFocus()
        menu.exec(self.quran_view.mapToGlobal(self.quran_view.pos()))        

    def on_copy_verse(self):
        current_line = self.quran_view.textCursor().block().text()
        clipboard = QApplication.clipboard()
        clipboard.setText(current_line)
        UniversalSpeech.say("تم نسخ الآية.")
        Globals.effects_manager.play("copy")


    def OnSyntax(self):
        aya_info = self.get_current_ayah_info()
        title = "إعراب آية رقم {} من {}".format(aya_info[3], aya_info[2])
        label = "الإعراب"
        text = E3rab(aya_info[0], aya_info[1]).text
        InfoDialog(title, label, text).exec()

    def OnVerseReasons(self):
        aya_info = self.get_current_ayah_info()
        title = "أسباب نزول آية رقم {} من {}".format(aya_info[3], aya_info[2])
        label = "الأسباب"
        text = TanzilAyah(aya_info[1]).text

        if text:
            InfoDialog(title, label, text).exec()
        else:
            QMessageBox.information(self, "لا يتوفر معلومات للآية", "للأسف لا يتوفر في الوقت الحالي معلومات لهذه الآية.")

    def OnAyahInfo(self):
        aya_info = self.get_current_ayah_info()
        title = "معلومات آية رقم {} من {}".format(aya_info[3], aya_info[2])
        label = "معلومات الآية:"
        text = AyaInfo(aya_info[1]).text
        InfoDialog(title, label, text, is_html_content=True).exec()
            
    def OnSaveBookmark(self):

        bookmark_manager= BookmarkManager()
        aya_info = self.get_current_ayah_info()
        criteria_number = self.quran.type

        if bookmark_manager.is_exist(aya_info[1]):
            QMessageBox.critical(self, "خطأ", f"تم حفظ العلامة المرجعية مسبقًا.")
            return

        name, ok = QInputDialog.getText(self, "اسم العلامة", "أدخل اسم العلامة:")
        if ok and name:
            bookmark_manager.insert_bookmark(name, aya_info[1], aya_info[3], aya_info[0], aya_info[2], criteria_number)
            self.quran_view.setFocus()

    def OnSaveCurrentPosition(self):
        self.user_data_manager.save_position(
            self.get_current_ayah_info()[1],
         self.quran.type,
         self.quran.current_pos
         )
        UniversalSpeech.say("تم حفظ الموضع الحالي.")

    def OnChangeNavigationMode(self, mode):
        ayah_info = self.get_current_ayah_info()
        if  ayah_info:
            ayah_number = ayah_info[1]
            self.quran.type = mode
            self.quran_view.setText(self.quran.get_by_ayah_number(ayah_number)["full_text"])
            self.set_focus_to_ayah(ayah_number)
            self.set_text_ctrl_label()
        Globals.effects_manager.play("change")
            
    def closeEvent(self, event):
        if SettingsManager.current_settings["general"]["run_in_background_enabled"]:
            event.ignore()
            self.hide()
            self.tray_manager.tray_icon.showMessage("البيان", "تم تصغير نافذة البيان على صينية النظام, البرنامج يعمل في الخلفية.", msecs=5000)
        else:
            self.tray_manager.hide_icon()
            bass.BASS_Free()

    def OnRandomMessages(self):
            with open(data_folder/"quotes/QuotesMessages.json", "r", encoding="utf-8") as file:
                quotes_list = json.load(file)
            message = random.choice(quotes_list)
            InfoDialog('اقتباس عشوائي', 'رسالة لك', message, is_html_content=False).exec()

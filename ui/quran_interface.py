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
from core_functions.quran_class import quran_mgr
from core_functions.tafaseer import Category
from core_functions.info import E3rab, TanzilAyah, AyaInfo, SuraInfo, JuzInfo, HizbInfo, QuarterInfo, PageInfo
from core_functions.bookmark import BookmarkManager
from ui.dialogs.quick_access import QuickAccess
from ui.dialogs.find import SearchDialog
from ui.widgets.button import EnterButton
from ui.widgets.menu_bar import MenuBar
from ui.widgets.qText_edit import QuranViewer
from ui.dialogs.tafaseer_Dialog import TafaseerDialog
from ui.dialogs.info_dialog import InfoDialog
from ui.sura_player_ui.sura_player_ui import SuraPlayerWindow
from ui.widgets.system_tray import SystemTrayManager
from ui.widgets.toolbar import AudioToolBar
from utils.settings import SettingsManager
from utils.universal_speech import UniversalSpeech
from utils.user_data import UserDataManager
from utils.const import program_name, program_icon, user_db_path, data_folder, Globals
from utils.audio_player import SoundEffectPlayer
from exceptions.error_decorators import exception_handler


class QuranInterface(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(800, 600)
        self.center_window()
        self.setWindowIcon(QIcon("Albayan.ico"))
        self.quran = quran_mgr()
        self.quran.load_quran(SettingsManager.current_settings["reading"]["font_type"])
        self.user_data_manager = UserDataManager(user_db_path)
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
        position_data = self.user_data_manager.get_last_position()
        ayah_number = position_data.get("ayah_number", 1)
        current_positiom = position_data.get("position", 1)
        mode = position_data.get("criteria_number", 0)
        self.quran.type = mode
        self.menu_bar.browse_mode_actions[mode].setChecked(True)
        
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

    def OnBack(self, is_auto_call: bool = False):
        self.quran_view.setText(self.quran.back())
        self.set_text_ctrl_label()
        Globals.effects_manager.play("previous")
        if self.quran.current_pos == 1:            
            self.quran_view.setFocus()
        if SettingsManager.current_settings["reading"]["auto_page_turn"] and is_auto_call:
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

        if self.isActiveWindow():
                UniversalSpeech.say(label)
        
        # Enable back and next item
        next_status = self.quran.current_pos < self.quran.max_pos
        back_status = self.quran.current_pos > 1
        self.next_to.setEnabled(next_status)
        self.menu_bar.next_action.setEnabled(next_status)
        self.back_to.setEnabled(back_status)
        self.menu_bar.previous_action.setEnabled(back_status)
        self.toolbar.navigation.reset_position()
        self.toolbar.set_buttons_status()

    @exception_handler(ui_element=QMessageBox)
    def OnQuickAccess(self, event):
        dialog = QuickAccess(self, "الوصول السريع")
        if not dialog.exec():
            return
        
        self.set_text_ctrl_label()
        self.quran_view.setFocus()

    @exception_handler(ui_element=QMessageBox)
    def OnSearch(self, event):
        search_dialog = SearchDialog(self, "بحث")
        if search_dialog.exec():
            self.set_text_ctrl_label()

    def get_current_ayah_info(self) -> list:

        current_line = self.quran_view.textCursor().block()
        position = current_line.position()
        ayah_info = self.quran.get_ayah_info(position)

        return ayah_info
    
    @exception_handler(ui_element=QMessageBox)
    def OnInterpretation(self, event=None):

        sender = self.sender()
        if sender is not None:
            selected_category = sender.text()
        else:
            selected_category = "الميسر"
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
        get_sura_info = menu.addAction("معلومات السورة")
        get_juz_info = menu.addAction("معلومات الجزء")
        get_hizb_info = menu.addAction("معلومات الحزب")
        get_quarter_info = menu.addAction("معلومات الربع")
        get_page_info = menu.addAction("معلومات الصفحة")
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
        ayah_info = menu.addAction("معلومات الآية")
        ayah_info.triggered.connect(self.OnAyahInfo)
        get_sura_info.triggered.connect(self.OnSurahInfo)
        get_juz_info.triggered.connect(self.OnJuzInfo)
        get_hizb_info.triggered.connect(self.OnHizbInfo)
        get_quarter_info.triggered.connect(self.OnQuarterInfo)
        get_page_info.triggered.connect(self.OnPageInfo)
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

    def on_copy_verse(self):
        current_line = self.quran_view.textCursor().block().text()
        clipboard = QApplication.clipboard()
        clipboard.setText(current_line)
        UniversalSpeech.say("تم نسخ الآية.")
        Globals.effects_manager.play("copy")

    @exception_handler(ui_element=QMessageBox)
    def OnSyntax(self, event):
        aya_info = self.get_current_ayah_info()
        title = "إعراب آية رقم {} من {}".format(aya_info[3], aya_info[2])
        label = "الإعراب"
        text = E3rab(aya_info[0], aya_info[1]).text
        InfoDialog(self, title, label, text).exec()

    @exception_handler(ui_element=QMessageBox)
    def OnVerseReasons(self, event):
        aya_info = self.get_current_ayah_info()
        title = "أسباب نزول آية رقم {} من {}".format(aya_info[3], aya_info[2])
        label = "الأسباب"
        text = TanzilAyah(aya_info[1]).text

        if text:
            InfoDialog(self, title, label, text).exec()
        else:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("لا يتوفر معلومات للآية")
            msg_box.setText("للأسف لا يتوفر في الوقت الحالي معلومات لهذه الآية.")

            ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
            msg_box.exec()


    @exception_handler(ui_element=QMessageBox)
    def OnAyahInfo(self, event):
        aya_info = self.get_current_ayah_info()
        title = "معلومات آية رقم {} من {}".format(aya_info[3], aya_info[2])
        label = "معلومات الآية:"
        text = AyaInfo(aya_info[1]).text
        InfoDialog(self, title, label, text, is_html_content=True).open()
        
    @exception_handler(ui_element=QMessageBox)
    def OnSurahInfo(self, event):
        aya_info = self.get_current_ayah_info()
        title = "معلومات {}".format(aya_info[2])
        label = "معلومات السورة:"
        sura_info = SuraInfo(aya_info[0])
        InfoDialog(self, title, label, sura_info.text, is_html_content=True).open()

    @exception_handler(ui_element=QMessageBox)
    def OnJuzInfo(self, event):
        aya_info = self.get_current_ayah_info()
        title = "معلومات الجزء {}".format(aya_info[4])
        label = "معلومات الجزء:"
        juz_info = JuzInfo(aya_info[4])
        InfoDialog(self, title, label, juz_info.text).open()

    @exception_handler(ui_element=QMessageBox)
    def OnHizbInfo(self, event):
        aya_info = self.get_current_ayah_info()
        title = "معلومات الحزب {}".format(aya_info[5])
        label = "معلومات الحزب:"
        hizb_info = HizbInfo(aya_info[5])
        InfoDialog(self, title, label, hizb_info.text).open()

    @exception_handler(ui_element=QMessageBox)
    def OnQuarterInfo(self, event):
        aya_info = self.get_current_ayah_info()
        title = "معلومات الربع {}".format(aya_info[6])
        label = "معلومات الربع:"
        quarter_info = QuarterInfo(aya_info[6])
        InfoDialog(self, title, label, quarter_info.text).open()

    @exception_handler(ui_element=QMessageBox)
    def OnPageInfo(self, event):
        aya_info = self.get_current_ayah_info()
        title = "معلومات الصفحة {}".format(aya_info[7])
        label = "معلومات الصفحة:"
        page_info = PageInfo(aya_info[7])
        InfoDialog(self, title, label, page_info.text).open()

    def say_played_ayah(self):
        ayah_info = self.get_current_ayah_info()
        text = f"آية {self.toolbar.navigation.current_ayah} من {ayah_info[2]}"
        if self.toolbar.navigation.current_ayah:
            if self.toolbar.player.is_playing():
                UniversalSpeech.say(f"{text}، الآية المشغلة.")
            elif self.toolbar.player.is_paused():
                UniversalSpeech.say(f"{text}، تم إيقافها مؤقتًا.")
            elif self.toolbar.player.is_stopped():
                UniversalSpeech.say(f"{text}، تم إيقافها.")
            elif self.toolbar.player.is_stalled():
                UniversalSpeech.say(f"{text}، يجري تحميلها.")
        else:
            UniversalSpeech.say("لم يتم تشغيل أي آية.")

    def say_focused_ayah(self):
        ayah_info = self.get_current_ayah_info()
        text = f"آية {ayah_info[3]} من {ayah_info[2]}، الآية الحالية."
        UniversalSpeech.say(text)

    @exception_handler(ui_element=QMessageBox)
    def OnSaveBookmark(self, event):

        bookmark_manager= BookmarkManager()
        aya_info = self.get_current_ayah_info()
        criteria_number = self.quran.type

        if bookmark_manager.is_exist(aya_info[1]):
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setWindowTitle("خطأ")
            msgBox.setText("تم حفظ العلامة المرجعية مسبقًا.")
            msgBox.addButton("موافق", QMessageBox.AcceptRole)
            msgBox.exec()

            return


        dialog = QInputDialog(self)
        dialog.setWindowTitle("اسم العلامة")
        dialog.setLabelText("أدخل اسم العلامة:")
        dialog.setTextValue("")
    

        dialog.setOkButtonText("إضافة")
        dialog.setCancelButtonText("إلغاء")
    

        if dialog.exec() == dialog.Accepted:
            name = dialog.textValue()
            if name:
                bookmark_manager.insert_bookmark(
                    name, 
                    aya_info[1], 
                    aya_info[3], 
                    aya_info[0], 
                    aya_info[2], 
                    criteria_number
                )
                self.quran_view.setFocus()
            else:
                # Optionally, handle the case where the user accepts without entering a name
                return
        else:
            return

    def OnSaveCurrentPosition(self):
        self.user_data_manager.save_position(
            self.get_current_ayah_info()[1],
         self.quran.type,
         self.quran.current_pos
         )

    def OnSave_alert(self):
        UniversalSpeech.say("تم حفظ الموضع الحالي.")
        Globals.effects_manager.play("save")

    def OnChangeNavigationMode(self, mode):
        ayah_info = self.get_current_ayah_info()
        if  ayah_info:
            ayah_number = ayah_info[1]
            self.quran.type = mode
            self.menu_bar.browse_mode_actions[mode].setChecked(True)
            self.quran_view.setText(self.quran.get_by_ayah_number(ayah_number)["full_text"])
            self.set_focus_to_ayah(ayah_number)
            self.set_text_ctrl_label()
        Globals.effects_manager.play("change")
            
    def closeEvent(self, event):
        if SettingsManager.current_settings["general"]["run_in_background_enabled"]:
            event.ignore()
            self.hide()
            icon_path = "Albayan.ico"
            self.tray_manager.tray_icon.showMessage("البيان", "تم تصغير نافذة البيان على صينية النظام, البرنامج يعمل في الخلفية.", QIcon(icon_path), msecs=5000)
        else:
            self.tray_manager.hide_icon()
            
    @exception_handler(ui_element=QMessageBox)
    def OnRandomMessages(self, event):
        info_dialog = InfoDialog(self, 'رسالة لك', '', "", is_html_content=False, show_message_button=True, save_message_as_img_button=True)
        info_dialog.choose_QuotesMessage()
        info_dialog.exec()


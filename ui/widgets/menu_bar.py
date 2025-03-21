import os
from PyQt6.QtWidgets import QApplication, QMenuBar, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QShortcut, QDesktopServices, QActionGroup
from PyQt6.QtCore import Qt, QUrl
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.bookmark_dialog import BookmarkDialog
from ui.dialogs.go_to import GoToDialog
from ui.dialogs.athkar_dialog import AthkarDialog
from ui.sura_player_ui import SuraPlayerWindow
from ui.dialogs.tasbih_dialog import TasbihDialog
from ui.dialogs.prophets_stories_dialog import ProphetsStoriesDialog
from core_functions.quran_class import QuranConst
from core_functions.tafaseer import Category
from utils.update import UpdateManager
from utils.settings import SettingsManager
from utils.logger import Logger
from utils.const import program_name, program_version, website, Globals
from utils.audio_player import bass
from theme import ThemeManager


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.theme_manager = ThemeManager(self.parent)
        self.update_manager = UpdateManager(self.parent)
        self.sura_player_window = None
        self.our_emails = {
            "محمود عاطف": "mahmoud.atef.987123@gmail.com",
            "قيس الرفاعي": "ww258148@gmail.com",
            "أحمد بكر": "AhmedBakr593@gmail.com"
        }
        self.create_menu()

    def create_menu(self):
        navigation_menu = self.addMenu("التنقل(&M)")
        self.next_action = QAction("التالي", self)
        self.next_action.triggered.connect(self.parent.OnNext)
        self.previous_action = QAction("السابق", self)
        self.previous_action.triggered.connect(self.parent.OnBack)
        self.go_to_saved_position_action = QAction("الذهاب إلى الموضع المحفوظ", self)
        self.go_to_saved_position_action.triggered.connect(self.parent.set_text)
        self.go_to_saved_position_action.triggered.connect(lambda: Globals.effects_manager.play("move"))
        self.search_action = QAction("البحث", self)
        self.search_action.triggered.connect(self.parent.OnSearch)        
        self.go_to_action = QAction("اذهب إلى", self)
        self.go_to_action.triggered.connect(self.OnGoTo)
        self.quick_access_action = QAction("الوصول السريع", self)
        self.quick_access_action.triggered.connect(self.parent.OnQuickAccess)
        self.close_action = QAction("إغلاق النافذة", self)
        self.close_action.triggered.connect(self.parent.close)
        self.close_action.setVisible(SettingsManager.current_settings["general"]["run_in_background_enabled"])
        self.exit_action = QAction("إغلاق البرنامج", self)
        self.exit_action.triggered.connect(self.quit_application)

        navigation_menu.addActions([self.next_action, self.previous_action, self.go_to_saved_position_action, self.search_action, self.go_to_action, self.quick_access_action, self.close_action, self.exit_action])


        player_menu = self.addMenu("المشغل(&P)")
        self.play_pause_action = QAction("تشغيل الآية الحالية", self)
        self.play_pause_action.triggered.connect(self.parent.toolbar.toggle_play_pause)
        self.stop_action = QAction("إيقاف", self)
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self.parent.toolbar.stop_audio)
        self.rewind_action = QAction("ترجيع", self)
        self.rewind_action.triggered.connect(lambda: self.parent.toolbar.player.rewind(SettingsManager.current_settings["listening"]["forward_time"]))
        self.forward_action = QAction("تقديم", self)
        self.forward_action.triggered.connect(lambda: self.parent.toolbar.player.forward(SettingsManager.current_settings["listening"]["forward_time"]))
        self.replay_action = QAction("إعادة", self)
        self.replay_action.triggered.connect(lambda: self.parent.toolbar.player.set_position(0))
        self.play_next_action = QAction("تشغيل الآية التالية", self)
        self.play_next_action.setEnabled(False)
        self.play_next_action.triggered.connect(self.parent.toolbar.OnPlayNext)
        self.play_previous_action = QAction("تشغيل الآية السابقة", self)
        self.play_previous_action.setEnabled(False)
        self.play_previous_action.triggered.connect(self.parent.toolbar.OnPlayPrevious)

        player_menu.addActions([self.play_pause_action, self.stop_action, self.rewind_action, self.forward_action, self.replay_action, self.play_next_action, self.play_previous_action])


        actions_menu = self.addMenu("الإجرائات(&A)")
        self.save_position_action = QAction("حفظ الموضع الحالي", self)
        self.save_position_action.triggered.connect(self.parent.OnSaveCurrentPosition)
        self.save_position_action.triggered.connect(self.parent.OnSave_alert)
        self.save_bookmark_action = QAction("حفظ علامة", self)
        self.save_bookmark_action.triggered.connect(self.parent.OnSaveBookmark)
        self.surah_info_action = QAction("معلومات السورة", self)
        self.surah_info_action.triggered.connect(self.parent.OnSurahInfo)
        self.juz_info_action = QAction("معلومات الجزء", self)
        self.juz_info_action.triggered.connect(self.parent.OnJuzInfo)
        self.verse_tafsir_action = QAction("تفسير الآية", self)
        self.verse_tafsir_action.triggered.connect(self.parent.OnInterpretation)

        self.tafaseer_menu = QMenu("التفسير")
        self.tafaseer_menu.setAccessibleName("قائمة المفسرين")
        tafaseershortcut = QShortcut(QKeySequence("Shift+T"), self)
        tafaseershortcut.activated.connect(self.OnTafaseerMenu)
        arabic_categories = Category.get_categories_in_arabic()
        for arabic_category in arabic_categories:
            action = QAction(arabic_category, self)
            action.triggered.connect(self.parent.OnInterpretation)
            self.tafaseer_menu.addAction(action)

        self.ayah_info_action = QAction("معلومات الآية", self)
        self.ayah_info_action.triggered.connect(self.parent.OnAyahInfo)
        self.verse_info_action = QAction("أسباب نزول الآية", self)
        self.verse_info_action.triggered.connect(self.parent.OnVerseReasons)
        self.verse_grammar_action = QAction("إعراب الآية", self)
        self.verse_grammar_action.triggered.connect(self.parent.OnSyntax)
        self.copy_verse_action = QAction("نسخ الآية", self)
        self.copy_verse_action.triggered.connect(self.parent.on_copy_verse)

        actions_menu.addActions([self.save_position_action, self.save_bookmark_action, self.surah_info_action, self.juz_info_action, self.verse_tafsir_action, self.ayah_info_action, self.verse_info_action, self.verse_grammar_action, self.copy_verse_action])
        actions_menu.insertMenu(self.ayah_info_action, self.tafaseer_menu)


    # Browse mode menu
        browse_mode_menu = self.addMenu("وضع التصفح(&B)")
        self.browse_mode_group = QActionGroup(self)
        self.browse_mode_actions = []  # List to store actions

        # List of browse modes (name, mode value, shortcut)
        modes = [
            ("سور", 1, "Ctrl+1"),
        ("صفحات", 0, "Ctrl+2"),
        ("أرباع", 2, "Ctrl+3"),
        ("أحزاب", 3, "Ctrl+4"),
        ("أجزاء", 4, "Ctrl+5"),
    ]

    # Create actions using a loop
        for name, mode, shortcut in modes:
            action = QAction(name, self)
            action.setCheckable(True)
            action.setShortcut(QKeySequence(shortcut))  # Assign shortcut
            action.triggered.connect(lambda checked, m=mode: self.parent.OnChangeNavigationMode(m))
            self.browse_mode_group.addAction(action)
            browse_mode_menu.addAction(action)
            self.browse_mode_actions.insert(mode, action)

        # Add the menu to the parent
        self.addMenu(browse_mode_menu)



        tools_menu = self.addMenu("الأدوات(&T)")
        self.athkar_action = QAction("الأذكار", self)
        self.athkar_action.triggered.connect(lambda: AthkarDialog(self.parent).open())
        self.bookmark_manager_action = QAction("مدير العلامات", self)
        self.bookmark_manager_action.triggered.connect(self.OnBookmarkManager)
        self.sura_player_action = QAction("مشغل القرآن", self)
        self.sura_player_action.triggered.connect(self.OnSuraPlayer)
        self.tasbih_action = QAction("المسبحة", self)
        self.tasbih_action.triggered.connect(self.OnTasbihAction)
        self.message_for_you_action = QAction("رسالة لك", self)
        self.message_for_you_action.triggered.connect(self.parent.OnRandomMessages)
        self.stories_action = QAction("قصص الأنبياء", self)
        self.stories_action.triggered.connect(self.OnStoriesAction)

        tools_menu.addAction(self.sura_player_action)
        tools_menu.addAction(self.athkar_action)
        tools_menu.addAction(self.bookmark_manager_action)
        tools_menu.addAction(self.tasbih_action)
        tools_menu.addAction(self.message_for_you_action)
        #tools_menu.addAction(self.stories_action)


        preferences_menu = self.addMenu("التفضيلات(&R)")
        self.settings_action = QAction("الإعدادات", self)
        self.settings_action.setShortcuts([QKeySequence("F3"), QKeySequence("Alt+S")])
        self.settings_action.triggered.connect(self.OnSettings)

        self.theme_menu = QMenu("تغيير الثيم", self)
        for theme in self.theme_manager.get_themes():
            self.theme_action = QAction(theme, self)
            self.theme_action.triggered.connect(self.OnTheme)
            self.theme_menu.addAction(self.theme_action)
        self.theme_manager.apply_theme(SettingsManager.current_settings["preferences"]["theme"])
        
        self.text_direction_action = QMenu("تغيير اتجاه النص", self)

        self.rtl_action = QAction("من اليمين لليسار", self)
        self.rtl_action.triggered.connect(self.set_text_direction_rtl)
        self.text_direction_action.addAction(self.rtl_action)
        self.ltr_action = QAction("من اليسار لليمين", self)
        self.ltr_action.triggered.connect(self.set_text_direction_ltr)
        self.text_direction_action.addAction(self.ltr_action)

        preferences_menu.addAction(self.settings_action)
        preferences_menu.addMenu(self.theme_menu)
        preferences_menu.addMenu(self.text_direction_action)


        self.help_menu = self.addMenu("المساعدة(&H)")
        self.user_guide_action = QAction("دليل البرنامج", self)
        self.user_guide_action.triggered.connect(lambda: self.open_documentation("user_guide"))
        self.whats_new_action = QAction("المستجدات", self)
        self.whats_new_action.triggered.connect(lambda: self.open_documentation("Whats_new"))
        self.contact_us_menu = QMenu("اتصل بنا", self)
        for name in self.our_emails:
            name_action = QAction(name, self)
            name_action.triggered.connect(self.OnContact)
            self.contact_us_menu.addAction(name_action)
        self.update_program_action = QAction("تحديث البرنامج", self)
        self.update_program_action.triggered.connect(self.OnUpdate)
        self.open_log_action = QAction("فتح ملف السجل", self)
        self.open_log_action.triggered.connect(self.Onopen_log_file)
        self.about_program_action = QAction("حول البرنامج", self)
        self.about_program_action.triggered.connect(self.OnAbout)

        self.help_menu.addActions([self.user_guide_action, self.whats_new_action, self.update_program_action, self.open_log_action, self.about_program_action])
        self.help_menu.insertMenu(self.open_log_action, self.contact_us_menu)



        self.setup_shortcuts()

    def OnSettings(self):
        SettingsDialog(self.parent).exec()
        self.close_action.setVisible(SettingsManager.current_settings["general"]["run_in_background_enabled"])

    def OnUpdate(self):
        self.update_manager.check_updates()



    def OnBookmarkManager(self):
        dialog = BookmarkDialog(self.parent)
        if dialog.exec():
            self.parent.set_text_ctrl_label()

    def OnSuraPlayer(self):
        if not self.sura_player_window:
            self.sura_player_window = SuraPlayerWindow(self.parent)
        self.sura_player_window.show()
        self.sura_player_window.activateWindow()
        self.parent.hide()


    def OnTasbihAction(self):
        tasbih_dialog = TasbihDialog(self.parent)
        tasbih_dialog.open()

    def OnStoriesAction(self):
        stories_dialog = ProphetsStoriesDialog(self.parent)
        stories_dialog.open()

    def OnTheme    (self):

        # apply theme
        theme = self.sender().text()
        theme = "default" if theme == "الافتراضي" else theme
        self.theme_manager.apply_theme(theme)

        # Save selected theme in the settings
        theme_setting = {
            "preferences": {
                "theme": theme
            }
        }
        SettingsManager.write_settings(theme_setting)

    def set_text_direction_rtl(self):
        option = self.parent.quran_view.document().defaultTextOption()
        option.setTextDirection(Qt.LayoutDirection.RightToLeft)
        self.parent.quran_view.document().setDefaultTextOption(option)

    def set_text_direction_ltr(self):
        option = self.parent.quran_view.document().defaultTextOption()
        option.setTextDirection(Qt.LayoutDirection.LeftToRight)
        self.parent.quran_view.document().setDefaultTextOption(option)

    def OnContact(self):
        name = self.sender().text()
        email = self.our_emails[name]
        try:
            url = QUrl(f"mailto:{email}")
            QDesktopServices.openUrl(url)
        except Exception as e:
            Logger.error(str(e))
            QMessageBox.critical(self, "خطأ", "حدث خطأ أثناء محاولة فتح برنامج البريد الإلكتروني")


    def OnAbout(self):
        about_text = (
            f"{program_name}، هو برنامج يهدف إلى مساعدة المسلم على قراءة القرآن بشكل سهل وبسيط مع العديد من المميزات.\n"
            "تم تصميم البرنامج من فريق نافذة التقنية: محمود عاطف، أحمد بكر وقيس الرفاعي.\n"
            f"إصدار البرنامج: {program_version}\n"
            f"الموقع الرسمي للبرنامج: {website}\n"
        )
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("حول البرنامج")
        msg_box.setText(about_text)
        ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()

    def OnGoTo(self):
        category_number = self.parent.quran.type
        current_position = self.parent.quran.current_pos
        max = QuranConst.get_max(category_number)
        category_label = QuranConst.get_category_label(category_number)
        go_to_dialog = GoToDialog(self.parent, current_position, max, category_label)
        if go_to_dialog.exec():
            value = go_to_dialog.get_input_value()
            text = self.parent.quran.goto(value)
            self.parent.quran_view.setText(text)
        self.parent.set_text_ctrl_label()
        self.parent.quran_view.setFocus()

    def OnTafaseerMenu(self):
        if self.tafaseer_menu.isEnabled():
            self.tafaseer_menu.exec()

    def quit_application(self):
        if SettingsManager.current_settings["general"]["auto_save_position_enabled"]:
            self.parent.OnSaveCurrentPosition()
        self.parent.tray_manager.hide_icon()
        if self.sura_player_window is not None:
            self.sura_player_window.close()
        QApplication.quit()
        bass.BASS_Free()

    def Onopen_log_file(self):
        appdata_path = os.path.expandvars('%appdata%')
        log_file_path = os.path.join(appdata_path, 'tecwindow', 'albayan', 'albayan.log')

        try:
            os.startfile(log_file_path)
        except FileNotFoundError:
            try:
                os.makedirs(os.path.dirname(log_file_path), exist_ok=True)  
                with open(log_file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                os.startfile(log_file_path)
            except Exception:
                pass

    def open_documentation(self, doc_type: str):
        file_map = {
            "user_guide": "UserGuide.html",
            "Whats_new": "WhatsNew.html"
        }
        file_name = file_map.get(doc_type)
        if not file_name:
            return
        doc_path = os.path.join("documentation", file_name)
        if os.path.exists(doc_path):
            os.startfile(doc_path)




    def setup_shortcuts(self, disable=False,):

        shortcuts = {
        # Navigation actions
            self.next_action: ["Ctrl+N", "Ctrl+Down", "Alt+Right", QKeySequence(Qt.Key.Key_PageDown)],
            self.previous_action: ["Ctrl+B", QKeySequence(Qt.Key.Key_PageUp), "Ctrl+Up", "Alt+Left"],
            self.go_to_saved_position_action: ["Ctrl+Backspace"],
            self.search_action: ["Ctrl+F"],
            self.go_to_action: ["Ctrl+G"],
            self.quick_access_action: ["Ctrl+Q"],
            self.close_action: ["Ctrl+W", "Ctrl+F4"],
            self.exit_action: ["Ctrl+Shift+W", "Ctrl+Shift+F4"],

            # Playback controls
            self.play_pause_action: ["K", "Ctrl+P"],
            self.stop_action: ["Ctrl+E"],
            self.rewind_action: ["J", "Ctrl+Alt+Left"],
            self.forward_action: ["L", "Ctrl+Alt+Right"],
            self.replay_action: ["Shift+J"],
            self.play_next_action: ["Ctrl+Shift+N"],
            self.play_previous_action: ["Ctrl+Shift+B"],

        # Actions
            self.save_position_action: ["Ctrl+S"],
            self.save_bookmark_action: ["Ctrl+D"],
            self.verse_tafsir_action: ["Shift+T"],
            self.ayah_info_action: ["Shift+I"],
            self.verse_info_action: ["Shift+R"],
            self.verse_grammar_action: ["Shift+E"],
            self.copy_verse_action: ["Shift+C"],

        #tools
                    self.sura_player_action: ["Shift+P"],
        self.athkar_action: ["Shift+A"],
        self.bookmark_manager_action: ["Shift+D"],
        self.tasbih_action: ["Shift+S"],
        self.message_for_you_action: ["Shift+M"],
            #self.stories_action: ["Shift+O"],

        # Preferences# Preferences
        self.settings_action: ["F3", "Alt+S"],    

        #Help
        self.user_guide_action: ["F1"],
        self.whats_new_action: ["F2"],
        self.update_program_action: ["Ctrl+F2"],
        self.open_log_action: ["Shift+L"],
        self.about_program_action: ["Ctrl+F1"],
        }


        for widget, key_sequence in shortcuts.items():
            key_sequence = [key_sequence] if isinstance(key_sequence, str) else key_sequence
            widget.setShortcuts([QKeySequence(key) for key in key_sequence])

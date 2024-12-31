from PyQt6.QtWidgets import QApplication, QMenuBar, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QShortcut, QDesktopServices
from PyQt6.QtCore import Qt, QUrl
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.bookmark_dialog import BookmarkDialog
from ui.dialogs.go_to import GoToDialog
from ui.dialogs.athkar_dialog import AthkarDialog
from ui.dialogs.sura_player_ import SuraPlayerDialog
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
        self.next_action.setShortcuts([QKeySequence("Ctrl+N"), QKeySequence("Ctrl+Down"), QKeySequence("Alt+Right"), QKeySequence(Qt.Key.Key_PageDown)])
        self.previous_action = QAction("السابق", self)
        self.previous_action.triggered.connect(self.parent.OnBack)
        self.previous_action.setShortcuts([QKeySequence("Ctrl+B"), QKeySequence(Qt.Key.Key_PageUp),
                                           QKeySequence("Ctrl+Up"), QKeySequence("Alt+Left")])
        self.go_to_saved_position_action = QAction("الذهاب إلى الموضع المحفوظ", self)
        self.go_to_saved_position_action.triggered.connect(self.parent.set_text)
        self.go_to_saved_position_action.triggered.connect(lambda: Globals.effects_manager.play("move"))
        self.go_to_saved_position_action.setShortcut("Ctrl+Backspace")
        self.search_action = QAction("البحث", self)
        self.search_action.triggered.connect(self.parent.OnSearch)        
        self.search_action.setShortcut(QKeySequence("Ctrl+F"))
        self.go_to_action = QAction("اذهب إلى", self)
        self.go_to_action.triggered.connect(self.OnGoTo)
        self.go_to_action.setShortcut(QKeySequence("Ctrl+G"))
        self.quick_access_action = QAction("الوصول السريع", self)
        self.quick_access_action.triggered.connect(self.parent.OnQuickAccess)
        self.quick_access_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.close_action = QAction("إغلاق النافذة", self)
        self.close_action.setShortcuts([QKeySequence("Ctrl+W"), QKeySequence("Ctrl+F4")])
        self.close_action.triggered.connect(self.parent.close)
        self.close_action.setVisible(SettingsManager.current_settings["general"]["run_in_background_enabled"])
        self.exit_action = QAction("إغلاق البرنامج", self)
        self.exit_action.setShortcuts([QKeySequence("Ctrl+X")])
        self.exit_action.triggered.connect(self.quit_application)

        navigation_menu.addAction(self.next_action)
        navigation_menu.addAction(self.previous_action)
        navigation_menu.addAction(self.go_to_saved_position_action)
        navigation_menu.addAction(self.search_action)
        navigation_menu.addAction(self.go_to_action)
        navigation_menu.addAction(self.quick_access_action)
        navigation_menu.addAction(self.close_action)
        navigation_menu.addAction(self.exit_action)

        player_menu = self.addMenu("المشغل(&P)")
        self.play_pause_action = QAction("تشغيل الآية الحالية", self)
        self.play_pause_action.setShortcuts([QKeySequence("K"), QKeySequence("Ctrl+P")])
        self.play_pause_action.triggered.connect(self.parent.toolbar.toggle_play_pause)
        self.stop_action = QAction("إيقاف", self)
        self.stop_action.setShortcut(QKeySequence("Ctrl+E"))
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self.parent.toolbar.stop_audio)
        self.rewind_action = QAction("ترجيع", self)
        self.rewind_action.setShortcuts([QKeySequence("J"), QKeySequence("Ctrl+Alt+Left")])
        self.rewind_action.triggered.connect(lambda: self.parent.toolbar.player.rewind(SettingsManager.current_settings["listening"]["forward_time"]))
        self.forward_action = QAction("تقديم", self)
        self.forward_action.setShortcuts([QKeySequence("L"), QKeySequence("Ctrl+Alt+Right")])
        self.forward_action.triggered.connect(lambda: self.parent.toolbar.player.forward(SettingsManager.current_settings["listening"]["forward_time"]))
        self.replay_action = QAction("إعادة", self)
        self.replay_action.setShortcut(QKeySequence("Ctrl+J"))
        self.replay_action.triggered.connect(lambda: self.parent.toolbar.player.set_position(0))

        self.play_next_action = QAction("تشغيل الآية التالية", self)
        self.play_next_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        self.play_next_action.setEnabled(False)
        self.play_next_action.triggered.connect(self.parent.toolbar.OnPlayNext)
        self.play_previous_action = QAction("تشغيل الآية السابقة", self)
        self.play_previous_action.setShortcut(QKeySequence("Ctrl+Shift+B"))
        self.play_previous_action.setEnabled(False)
        self.play_previous_action.triggered.connect(self.parent.toolbar.OnPlayPrevious)

        player_menu.addAction(self.play_pause_action)
        player_menu.addAction(self.stop_action)
        player_menu.addAction(self.rewind_action)
        player_menu.addAction(self.forward_action)
        player_menu.addAction(self.replay_action)
        player_menu.addAction(self.play_next_action)
        player_menu.addAction(self.play_previous_action)


        actions_menu = self.addMenu("الإجرائات(&A)")
        self.save_position_action = QAction("حفظ الموضع الحالي", self)
        self.save_position_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_position_action.triggered.connect(self.parent.OnSaveCurrentPosition)
        self.save_position_action.triggered.connect(self.parent.OnSave_alert)
        self.save_bookmark_action = QAction("حفظ علامة", self)
        self.save_bookmark_action.setShortcut(QKeySequence("Ctrl+D"))
        self.save_bookmark_action.triggered.connect(self.parent.OnSaveBookmark)
        #self.surah_info_action = QAction("معلومات السورة", self)
        #self.surah_info_action.setShortcut(QKeySequence("Shift+S"))
        self.verse_tafsir_action = QAction("تفسير الآية", self)
        self.verse_tafsir_action.triggered.connect(self.parent.OnInterpretation)
        self.verse_tafsir_action.setShortcut(QKeySequence("Ctrl+T"))

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
        self.ayah_info_action.setShortcut(QKeySequence("Ctrl+I"))
        self.verse_info_action = QAction("أسباب نزول الآية", self)
        self.verse_info_action.triggered.connect(self.parent.OnVerseReasons)
        self.verse_info_action.setShortcut(QKeySequence("Shift+A"))
        self.verse_grammar_action = QAction("إعراب الآية", self)
        self.verse_grammar_action.triggered.connect(self.parent.OnSyntax)
        self.verse_grammar_action.setShortcut(QKeySequence("Shift+E"))
        self.copy_verse_action = QAction("نسخ الآية", self)
        self.copy_verse_action.triggered.connect(self.parent.on_copy_verse)
        self.copy_verse_action.setShortcut(QKeySequence("Shift+C"))

        actions_menu.addAction(self.save_position_action)
        actions_menu.addAction(self.save_bookmark_action)
        #actions_menu.addAction(self.surah_info_action)
        actions_menu.addAction(self.verse_tafsir_action)
        actions_menu.addMenu(self.tafaseer_menu)
        actions_menu.addAction(self.ayah_info_action)
        actions_menu.addAction(self.verse_info_action)
        actions_menu.addAction(self.verse_grammar_action)
        actions_menu.addAction(self.copy_verse_action)

        tools_menu = self.addMenu("الأدوات(&T)")
        athkar_action = QAction("الأذكار", self)
        athkar_action.setShortcut(QKeySequence("Ctrl+Shift+D"))
        athkar_action.triggered.connect(lambda: AthkarDialog(self.parent).exec())
        bookmark_manager_action = QAction("مدير العلامات", self)
        bookmark_manager_action.setShortcut(QKeySequence("Shift+D"))
        bookmark_manager_action.triggered.connect(self.OnBookmarkManager)
        sura_player__action = QAction("مشغل القرآن", self)
        sura_player__action.setShortcut(QKeySequence("Shift+P"))
        sura_player__action.triggered.connect(self.OnSuraPlayer)
        tools_menu.addAction(athkar_action)
        tools_menu.addAction(bookmark_manager_action)
        tools_menu.addAction(sura_player__action)

        preferences_menu = self.addMenu("التفضيلات(&R)")
        settings_action = QAction("الإعدادات", self)
        settings_action.setShortcut(QKeySequence("F3"))
        settings_action.setShortcuts([QKeySequence("F3"), QKeySequence("Alt+S")])
        settings_action.triggered.connect(self.OnSettings)

        theme_menu = QMenu("تغيير الثيم", self)
        for theme in self.theme_manager.get_themes():
            theme_action = QAction(theme, self)
            theme_action.triggered.connect(self.OnTheme)
            theme_menu.addAction(theme_action)
        self.theme_manager.apply_theme(SettingsManager.current_settings["preferences"]["theme"])
        
        self.text_direction_action = QMenu("تغيير اتجاه النص", self)

        self.rtl_action = QAction("من اليمين لليسار", self)
        self.rtl_action.triggered.connect(self.set_text_direction_rtl)
        self.text_direction_action.addAction(self.rtl_action)
        self.ltr_action = QAction("من اليسار لليمين", self)
        self.ltr_action.triggered.connect(self.set_text_direction_ltr)
        self.text_direction_action.addAction(self.ltr_action)

        preferences_menu.addAction(settings_action)
        preferences_menu.addMenu(theme_menu)
        preferences_menu.addMenu(self.text_direction_action)


        help_menu = self.addMenu("المساعدة(&H)")
#        user_guide_action = QAction("دليل البرنامج", self)
#        user_guide_action.setShortcut(QKeySequence("F1"))
        contact_us_menu = QMenu("اتصل بنا", self)
        for name in self.our_emails:
            name_action = QAction(name, self)
            name_action.triggered.connect(self.OnContact)
            contact_us_menu.addAction(name_action)

        update_program_action = QAction("تحديث البرنامج", self)
        update_program_action.setShortcut(QKeySequence("Ctrl+F2"))
        update_program_action.triggered.connect(self.OnUpdate)

        about_program_action = QAction("حول البرنامج", self)
        about_program_action.setShortcut(QKeySequence("Ctrl+F1"))
        about_program_action.triggered.connect(self.OnAbout)

#        help_menu.addAction(user_guide_action)
        help_menu.addMenu(contact_us_menu)
        help_menu.addAction(update_program_action)
        help_menu.addAction(about_program_action)

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
        dialog = SuraPlayerDialog(self.parent)

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
        QMessageBox.about(self, "حول البرنامج", about_text)

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
        QApplication.quit()
        bass.BASS_Free()
        
        


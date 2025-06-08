import os
from PyQt6.QtWidgets import QApplication, QMenuBar, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QShortcut, QDesktopServices, QActionGroup
from PyQt6.QtCore import Qt, QUrl
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.bookmark_dialog import BookmarkDialog
from ui.dialogs.go_to import GoToDialog, GoToStyle
from ui.dialogs.athkar_dialog import AthkarDialog
from ui.sura_player_ui import SuraPlayerWindow
from ui.dialogs.tasbih_dialog import TasbihDialog
from ui.dialogs.prophets_stories_dialog import ProphetsStoriesDialog
from core_functions.quran.types import NavigationMode
from core_functions.tafaseer import Category
from utils.update import UpdateManager
from utils.settings import Config
from utils.logger import LoggerManager
from utils.const import albayan_folder, program_name, program_version, website, Globals
from utils.audio_player import bass
from theme import ThemeManager

logger = LoggerManager.get_logger(__name__)

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
        self.navigation_menu = self.addMenu("التنقل(&M)")
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
        self.go_to_ayah_action = QAction("الذهاب إلى آية", self)
        self.go_to_ayah_action.triggered.connect(self.OnGoToAyah)
        self.quick_access_action = QAction("الوصول السريع", self)
        self.quick_access_action.triggered.connect(self.parent.OnQuickAccess)
        self.close_action = QAction("إغلاق النافذة", self)
        self.close_action.triggered.connect(self.parent.close)
        self.close_action.setVisible(Config.general.run_in_background_enabled)
        self.exit_action = QAction("إغلاق البرنامج", self)
        self.exit_action.triggered.connect(self.quit_application)

        self.navigation_menu.addActions([self.next_action, self.previous_action, self.search_action, self.go_to_saved_position_action, self.go_to_ayah_action, self.go_to_action,  self.quick_access_action, self.close_action, self.exit_action])


        self.player_menu = self.addMenu("المشغل(&P)")
        self.play_pause_action = QAction("تشغيل الآية الحالية", self)
        self.play_pause_action.triggered.connect(self.parent.toolbar.toggle_play_pause)
        self.stop_action = QAction("إيقاف", self)
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self.parent.toolbar.stop_audio)
        self.rewind_action = QAction("ترجيع", self)
        self.rewind_action.triggered.connect(lambda: self.parent.toolbar.player.rewind(Config.listening.forward_time))
        self.forward_action = QAction("تقديم", self)
        self.forward_action.triggered.connect(lambda: self.parent.toolbar.player.forward(Config.listening.forward_time))
        self.replay_action = QAction("إعادة", self)
        self.replay_action.triggered.connect(lambda: self.parent.toolbar.player.set_position(0))
        self.play_next_action = QAction("تشغيل الآية التالية", self)
        self.play_next_action.setEnabled(False)
        self.play_next_action.triggered.connect(self.parent.toolbar.OnPlayNext)
        self.play_previous_action = QAction("تشغيل الآية السابقة", self)
        self.play_previous_action.setEnabled(False)
        self.play_previous_action.triggered.connect(self.parent.toolbar.OnPlayPrevious)

        self.player_menu.addActions([self.play_pause_action, self.stop_action, self.rewind_action, self.forward_action, self.replay_action, self.play_next_action, self.play_previous_action])


        self.actions_menu = self.addMenu("الإجرائات(&A)")
        self.save_position_action = QAction("حفظ الموضع الحالي", self)
        self.save_position_action.triggered.connect(self.parent.OnSaveCurrentPosition)
        self.save_position_action.triggered.connect(self.parent.OnSave_alert)
        self.save_bookmark_action = QAction("حفظ علامة", self)
        self.save_bookmark_action.triggered.connect(self.parent.OnSaveBookmark)
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
        self.verse_info_action = QAction("أسباب نزول الآية", self)
        self.verse_info_action.triggered.connect(self.parent.OnVerseReasons)
        self.verse_grammar_action = QAction("إعراب الآية", self)
        self.verse_grammar_action.triggered.connect(self.parent.OnSyntax)
        self.copy_verse_action = QAction("نسخ الآية", self)
        self.copy_verse_action.triggered.connect(self.parent.on_copy_verse)

        self.actions_menu.addActions([self.save_position_action, self.save_bookmark_action, self.verse_tafsir_action, self.verse_info_action, self.verse_grammar_action, self.copy_verse_action])
        self.actions_menu.insertMenu(self.verse_info_action, self.tafaseer_menu)


    # Browse mode menu
        self.browse_mode_menu = self.addMenu("وضع التصفح(&B)")
        self.browse_mode_group = QActionGroup(self)
        self.browse_mode_actions = []  # List to store actions

        # List of browse modes (name, mode value, shortcut)
        modes = [
            ("سور", NavigationMode.SURAH, "Ctrl+1"),
        ("صفحات", NavigationMode.PAGE, "Ctrl+2"),
        ("أرباع", NavigationMode.QUARTER, "Ctrl+3"),
        ("أحزاب", NavigationMode.HIZB, "Ctrl+4"),
        ("أجزاء", NavigationMode.JUZ, "Ctrl+5"),
        ("مخصص", NavigationMode.CUSTOM_RANGE, "Ctrl+6"),
    ]

    # Create actions using a loop
        for name, mode, shortcut in modes:
            action = QAction(name, self)
            action.setCheckable(True)
            action.setShortcut(QKeySequence(shortcut))  # Assign shortcut
            action.triggered.connect(lambda checked, m=mode: self.parent.OnChangeNavigationMode(m.value))
            self.browse_mode_group.addAction(action)
            self.browse_mode_menu.addAction(action)
            self.browse_mode_actions.insert(mode.value, action)

        # Add the menu to the parent
        self.addMenu(self.browse_mode_menu)

        self.info_menu = self.addMenu("المعلومات(&I)")
        self.ayah_info_action = QAction("معلومات الآية", self)
        self.ayah_info_action.triggered.connect(self.parent.OnAyahInfo)
        self.surah_info_action = QAction("معلومات السورة", self)
        self.surah_info_action.triggered.connect(self.parent.OnSurahInfo)
        self.juz_info_action = QAction("معلومات الجزء", self)
        self.juz_info_action.triggered.connect(self.parent.OnJuzInfo)
        self.hizb_info_action = QAction("معلومات الحزب", self)
        self.hizb_info_action.triggered.connect(self.parent.OnHizbInfo)
        self.quarter_info_action = QAction("معلومات الربع", self)
        self.quarter_info_action.triggered.connect(self.parent.OnQuarterInfo)
        self.page_info_action = QAction("معلومات الصفحة", self)
        self.page_info_action.triggered.connect(self.parent.OnPageInfo)
        self.moshaf_info_action = QAction("معلومات المصحف", self)
        self.moshaf_info_action.triggered.connect(self.parent.OnMoshafInfo)
        self.info_menu.addActions([self.ayah_info_action, self.surah_info_action, self.page_info_action, self.quarter_info_action, self.hizb_info_action, self.juz_info_action, self.moshaf_info_action])


        self.tools_menu =self.addMenu("الأدوات(&T)")
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

        self.tools_menu.addActions([self.sura_player_action, self.athkar_action, self.bookmark_manager_action, self.tasbih_action, self.message_for_you_action])


        self.preferences_menu = self.addMenu("التفضيلات(&R)")
        self.settings_action = QAction("الإعدادات", self)
        self.settings_action.triggered.connect(self.OnSettings)

        self.change_reciter_action = QAction("تغيير القارئ", self)
        self.change_reciter_action.triggered.connect(self.open_reciter_settings)

        self.change_after_listening_action = QAction("تغيير الإجراء بعد الاستماع", self)
        self.change_after_listening_action.triggered.connect(self.open_after_listening_settings)


        self.theme_menu = QMenu("تغيير الثيم", self)
        for theme in self.theme_manager.get_themes():
            self.theme_action = QAction(theme, self)
            self.theme_action.triggered.connect(self.OnTheme)
            self.theme_menu.addAction(self.theme_action)
        self.theme_manager.apply_theme(Config.preferences.theme)
        
        self.text_direction_action = QMenu("تغيير اتجاه النص", self)

        self.rtl_action = QAction("من اليمين لليسار", self)
        self.rtl_action.triggered.connect(self.set_text_direction_rtl)
        self.text_direction_action.addAction(self.rtl_action)
        self.ltr_action = QAction("من اليسار لليمين", self)
        self.ltr_action.triggered.connect(self.set_text_direction_ltr)
        self.text_direction_action.addAction(self.ltr_action)


        self.preferences_menu.addAction(self.change_reciter_action)
        self.preferences_menu.addAction(self.change_after_listening_action)
        self.preferences_menu.addMenu(self.theme_menu)
        self.preferences_menu.addMenu(self.text_direction_action)
        self.preferences_menu.addAction(self.settings_action)



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
        logger.debug("Opening settings dialog.")
        SettingsDialog(self.parent).exec()
        self.close_action.setVisible(Config.general.run_in_background_enabled)
        logger.debug("Settings dialog closed, setting visibility of close action as {Config.general.run_in_background_enabled}.")

    def OnUpdate(self):
        logger.debug("Opening update dialog.")
        self.update_manager.check_updates()
        logger.debug("Update dialog closed")

    def OnBookmarkManager(self):
        logger.debug("Opening bookmark manager dialog.")
        dialog = BookmarkDialog(self.parent)
        if dialog.exec():
            logger.debug("Bookmark manager closed with selected bookmarks.")
            self.parent.set_text_ctrl_label()
        else:
            logger.debug("Bookmark manager closed without selection.")

    def OnSuraPlayer(self):
        logger.debug("Opening Sura Player window.")
        if not self.sura_player_window:
            self.sura_player_window = SuraPlayerWindow(self.parent)
        self.sura_player_window.show()
        logger.debug("Sura Player window shown.")
        self.sura_player_window.activateWindow()
        logger.debug("Sura Player window activated.")
        self.parent.hide()
        logger.debug("Main window hidden.")

    def OnTasbihAction(self):
        logger.debug("Opening Tasbih dialog.")
        tasbih_dialog = TasbihDialog(self.parent)
        tasbih_dialog.open()
        logger.debug("Tasbih dialog opened.")

    def OnStoriesAction(self):
        stories_dialog = ProphetsStoriesDialog(self.parent)
        stories_dialog.open()

    def OnTheme    (self):

        # apply theme
        theme = self.sender().text()
        theme = "default" if theme == "الافتراضي" else theme
        logger.debug(f"Applying theme: {theme}")
        self.theme_manager.apply_theme(theme)
        logger.info(f"Applied theme: {theme}")
        
        # Save selected theme in the settings
        Config.preferences.theme = theme
        Config.save_settings()
        logger.debug(f"Theme '{theme}' saved in settings.")

    def set_text_direction_rtl(self):
        logger.debug("Setting text direction to RTL.")
        option = self.parent.quran_view.document().defaultTextOption()
        option.setTextDirection(Qt.LayoutDirection.RightToLeft)
        self.parent.quran_view.document().setDefaultTextOption(option)
        logger.debug("Text direction set to RTL.")

    def set_text_direction_ltr(self):
        logger.debug("Setting text direction to LTR.")
        option = self.parent.quran_view.document().defaultTextOption()
        option.setTextDirection(Qt.LayoutDirection.LeftToRight)
        self.parent.quran_view.document().setDefaultTextOption(option)
        logger.debug("Text direction set to LTR.")

    def OnContact(self):
        name = self.sender().text()
        email = self.our_emails[name]
        logger.debug(f"Contacting {name} at {email}.")
        try:
            url = QUrl(f"mailto:{email}")
            QDesktopServices.openUrl(url)
            logger.debug(f"Opened email client for {name}.")
        except Exception as e:
            logger.error(f"Error opening email client: {e}", exc_info=True)
            QMessageBox.critical(self, "خطأ", "حدث خطأ أثناء محاولة فتح برنامج البريد الإلكتروني")

    def OnAbout(self):
        logger.debug("Opening about dialog.")
        about_text = (
                    f"{program_name} - الإصدار {program_version}.\n"
            f"{program_name}، هو برنامج يهدف إلى مساعدة المسلم على قراءة القرآن بشكل سهل وبسيط مع العديد من المميزات.\n"
            "تم تصميم البرنامج من فريق نافذة التقنية: محمود عاطف، أحمد بكر وقيس الرفاعي.\n"
            f"الموقع الرسمي للبرنامج: {website}\n"
        )
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("حول البرنامج")
        msg_box.setText(about_text)
        ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()
        logger.debug("About dialog closed.")

    def OnGoTo(self):
        logger.debug("Opening GoTo dialog.")
        current_position = self.parent.quran_manager.current_position
        max_position = self.parent.quran_manager.max_position
        category_label = self.parent.quran_manager.view_content.label
        title = f"الذهاب إلى {category_label}"
        info_label = (f"أنت في  ال{category_label} {current_position}، يمكنك الذهاب بين ال{category_label} 1 و ال{category_label} {max_position}.")
        label = f"ادخل رقم ال{category_label}"
        logger.debug(f"Current position: {current_position}, Max: {max_position}, navigation_mode: {self.parent.quran_manager.navigation_mode}")
        go_to_dialog = GoToDialog(self.parent, title=title, initial_value=current_position, max_value=max_position, min_value=1)
        go_to_dialog.set_spin_label(label)
        go_to_dialog.set_info_label(info_label)
        if go_to_dialog.exec():
            value = go_to_dialog.get_input_value()
            text = self.parent.quran_manager.go_to(value)
            self.parent.quran_view.setText(text)
            logger.debug(f"GoTo dialog closed with value: {value}")
        self.parent.set_text_ctrl_label()
        self.parent.quran_view.setFocus()

    def OnGoToAyah(self):
        logger.debug("Opening GoTo dialog for Ayah.")
        current_ayah = self.parent.get_current_ayah()
        combo_data = {
            surah_number: {
            "label": data.get("surah_name"),
            "min": data.get("min_ayah"),
            "max": data.get("max_ayah")
            }
        for surah_number, data in self.parent.quran_manager.view_content.get_ayah_range().items()
        }

        combo_data[current_ayah.sura_number] ["initial_value"] = current_ayah.number_in_surah
        category_label = self.parent.quran_manager.view_content.label
        title = f"الذهاب إلى آية داخل ال{category_label}"
        spin_label = "ادخل رقم الآية"
        combo_label = "اختر السورة"
        
        logger.debug(f"Current Ayah: {current_ayah}, combo_data: {combo_data}")
        go_to_dialog = GoToDialog(self.parent, title=title, initial_value=current_ayah.sura_name, combo_data=combo_data, style=GoToStyle.NUMERIC_FIELD|GoToStyle.COMBO_FIELD)
        go_to_dialog.set_spin_label(spin_label)
        go_to_dialog.set_combo_label(combo_label)
        min_surah_number = min(combo_data.keys())
        max_surah_number = max(combo_data.keys())

        min_ayah_number = combo_data[min_surah_number]["min"]
        max_ayah_number = combo_data[max_surah_number]["max"]

        min_surah_name = combo_data[min_surah_number]["label"]
        max_surah_name = combo_data[max_surah_number]["label"]
        info_label = (f"أنت في الآية رقم {current_ayah.number_in_surah} من {current_ayah.sura_name}، يمكنك الذهاب بين الآية {min_ayah_number} من {min_surah_name} والآية {max_ayah_number} من {max_surah_name}.")
        go_to_dialog.set_info_label(info_label)
        if go_to_dialog.exec():
            surah_number, ayah_number_in_surah = go_to_dialog.get_input_value()
            ayah = self.parent.quran_manager.view_content.get_by_ayah_number_in_surah(ayah_number_in_surah, surah_number)
            self.parent.set_focus_to_ayah(ayah.number)
        self.parent.quran_view.setFocus()

    def OnTafaseerMenu(self):
        if self.tafaseer_menu.isEnabled():
            logger.debug("Opening tafaseer menu.")
            self.tafaseer_menu.exec()
            logger.debug("Tafaseer menu closed.")

    def quit_application(self):
        logger.info("Quitting application.")
        if Config.general.auto_save_position_enabled:
            logger.debug("Auto-saving current position.")
            self.parent.OnSaveCurrentPosition()
            logger.info("Current position auto-saved.")
        logger.debug("Hiding tray icon.")
        self.parent.tray_manager.hide_icon()
        logger.info("Tray icon hidden.")
        logger.debug("Closing Sura Player window if open.")
        if self.sura_player_window is not None:
            self.sura_player_window.close()
            logger.info("Sura Player window closed.")
        logger.debug("Freeing audio resources.")
        bass.BASS_Free()
        logger.info("Audio resources freed.")
        logger.debug("Closing main window.")
        QApplication.quit()
        logger.info("Application quit.")

    def Onopen_log_file(self):
        log_file_path = os.path.join(albayan_folder, "albayan.log")

        try:
            os.startfile(log_file_path)
        except FileNotFoundError:
            logger.error(f"Log file not found: {log_file_path}", exc_info=True)

    def open_documentation(self, doc_type: str):
        file_map = {
            "user_guide": "UserGuide.html",
            "Whats_new": "WhatsNew.html"
        }
        file_name = file_map.get(doc_type)
        if not file_name:
            logger.error(f"Invalid documentation type: {doc_type}")
            return
        doc_path = os.path.join("documentation", file_name)
        if os.path.exists(doc_path):
            os.startfile(doc_path)
            logger.debug(f"Opened documentation: {doc_path}")
        else:
            logger.error(f"Documentation file not found: {doc_path}")

    def setup_shortcuts(self, disable=False,):
        logger.debug("Setting up shortcuts.")
        shortcuts = {
        # Navigation actions
            self.next_action: ["Ctrl+N", "Ctrl+Down", "Alt+Right", QKeySequence(Qt.Key.Key_PageDown)],
            self.previous_action: ["Ctrl+B", QKeySequence(Qt.Key.Key_PageUp), "Ctrl+Up", "Alt+Left"],
            self.go_to_saved_position_action: ["Ctrl+Backspace"],
            self.search_action: ["Ctrl+F"],
            self.go_to_action: ["Ctrl+G"],
        self.go_to_ayah_action: ["Shift+G"],
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
            self.verse_tafsir_action: ["Ctrl+T"],
            self.verse_info_action: ["Shift+R"],
            self.verse_grammar_action: ["Shift+E"],
            self.copy_verse_action: ["Shift+C"],

        #info
            self.ayah_info_action: ["Shift+I", "Alt+Shift+7"],
            self.surah_info_action: ["Alt+Shift+1", "Ctrl+I"],
            self.page_info_action: ["Alt+Shift+2"],
            self.quarter_info_action: ["Alt+Shift+3"],
            self.hizb_info_action: ["Alt+Shift+4"],
            self.juz_info_action: ["Alt+Shift+5"],
            self.moshaf_info_action: ["Alt+Shift+6"],

        #tools
                    self.sura_player_action: ["Shift+P"],
        self.athkar_action: ["Shift+A"],
        self.bookmark_manager_action: ["Shift+D"],
        self.tasbih_action: ["Shift+S"],
        self.message_for_you_action: ["Shift+M"],
            #self.stories_action: ["Shift+O"],

        #Preferences
        self.settings_action: ["Alt+S", "F3"],
        self.change_reciter_action: ["Ctrl+Shift+R"],
        self.change_after_listening_action: ["Ctrl+Shift+U"],
        


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
            logger.debug(f"Set shortcuts for {widget.text()}: {key_sequence}")

        logger.debug("Shortcuts set up completed.")



    def open_reciter_settings(self):
        dialog = SettingsDialog(self.parent)
        dialog.open_listening_tab_and_focus_reciter()
        dialog.exec()

    def open_after_listening_settings(self):
        dialog = SettingsDialog(self.parent)
        dialog.open_listening_tab_and_focus_action()
        dialog.exec()
 
from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QIcon, QAction
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.bookmark_dialog import BookmarkDialog
from utils.update import UpdateManager
from utils.settings import SettingsManager

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.update_manager = UpdateManager(self.parent)
        self.create_menu()

    def create_menu(self):
        navigation_menu = self.addMenu("التنقل")
        next_action = QAction("التالي", self)
        previous_action = QAction("السابق", self)
        search_action = QAction("البحث", self)
        quick_access_action = QAction("الوصول السريع", self)


        navigation_menu.addAction(next_action)
        navigation_menu.addAction(previous_action)
        navigation_menu.addAction(search_action)
        navigation_menu.addAction(quick_access_action)

        actions_menu = self.addMenu("الإجرائات")
        save_position_action = QAction("حفظ الموضع الحالي", self)
        surah_info_action = QAction("معلومات السورة", self)
        verse_tafsir_action = QAction("تفسير الآية", self)
        verse_info_action = QAction("معلومات الآية", self)
        verse_grammar_action = QAction("اعراب الآية", self)
        copy_verse_action = QAction("نسخ الآية", self)

        actions_menu.addAction(save_position_action)
        actions_menu.addAction(surah_info_action)
        actions_menu.addAction(verse_tafsir_action)
        actions_menu.addAction(verse_info_action)
        actions_menu.addAction(verse_grammar_action)
        actions_menu.addAction(copy_verse_action)

        tools_menu = self.addMenu("Tools")
        bookmark_manager_action = QAction("Bookmark manager", self)
        bookmark_manager_action.triggered.connect(self.OnBookmarkManager)
        tools_menu.addAction(bookmark_manager_action )

        preferences_menu = self.addMenu("التفضيلات")
        settings_action = QAction("الإعدادات", self)
        settings_action.triggered.connect(self.OnSettings)
        theme_change_action = QAction("تغيير الثيم", self)
        text_direction_action = QAction("تغيير اتجاه النص", self)
        
        preferences_menu.addAction(settings_action)
        preferences_menu.addAction(theme_change_action)
        preferences_menu.addAction(text_direction_action)

        help_menu = self.addMenu("المساعدة")
        user_guide_action = QAction("دليل البرنامج", self)
        contact_us_action = QAction("اتصل بنا", self)
        update_program_action = QAction("تحديث البرنامج", self)
        update_program_action.triggered.connect(self.OnUpdate)

        help_menu.addAction(user_guide_action)
        help_menu.addAction(contact_us_action)
        help_menu.addAction(update_program_action)

    def OnSettings(self):
        SettingsDialog().exec()

    def OnUpdate(self):
         self.update_manager.check_updates()

    def OnBookmarkManager(self):
        dialog = BookmarkDialog(self.parent)
        if dialog.exec():
            pass


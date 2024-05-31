from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QIcon, QAction, QKeySequence
from PyQt6.QtCore import Qt
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.bookmark_dialog import BookmarkDialog
from utils.update import UpdateManager
from utils.settings import SettingsManager
from theme import ThemeManager

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_rtl = True
        self.theme_manager = ThemeManager(self.parent)
        self.update_manager = UpdateManager(self.parent)
        self.create_menu()

    def create_menu(self):
        navigation_menu = self.addMenu("التنقل")
        self.next_action = QAction("التالي", self)
        self.next_action.triggered.connect(self.parent.OnNext)
        self.next_action.setShortcut(QKeySequence("Ctrl+N"))
        self.previous_action = QAction("السابق", self)
        self.previous_action.triggered.connect(self.parent.OnBack)
        self.previous_action.setEnabled(False)
        self.previous_action.setShortcut(QKeySequence("Ctrl+P"))
        self.search_action = QAction("البحث", self)
        self.search_action.triggered.connect(self.parent.OnSearch)        
        self.search_action.setShortcut(QKeySequence("Ctrl+F"))
        self.quick_access_action = QAction("الوصول السريع", self)
        self.quick_access_action.triggered.connect(self.parent.OnQuickAccess)
        self.quick_access_action.setShortcut(QKeySequence("Ctrl+Q"))

        navigation_menu.addAction(self.next_action)
        navigation_menu.addAction(self.previous_action)
        navigation_menu.addAction(self.search_action)
        navigation_menu.addAction(self.quick_access_action)

        actions_menu = self.addMenu("الإجرائات")
        self.save_position_action = QAction("حفظ الموضع الحالي", self)
        self.save_position_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_position_action.triggered.connect(self.parent.OnSavePosition)
        self.surah_info_action = QAction("معلومات السورة", self)
        self.surah_info_action.setShortcut(QKeySequence("Shift+S"))
        self.verse_tafsir_action = QAction("تفسير الآية", self)
        self.verse_tafsir_action.triggered.connect(self.parent.OnInterpretation)
        self.verse_tafsir_action.setShortcut(QKeySequence("Ctrl+T"))
        self.verse_info_action = QAction("معلومات الآية", self)
        self.verse_info_action.triggered.connect(self.parent.OnVerseReasons)
        self.verse_info_action.setShortcut(QKeySequence("Shift+A"))
        self.verse_grammar_action = QAction("اعراب الآية", self)
        self.verse_grammar_action.triggered.connect(self.parent.OnSyntax)
        self.verse_grammar_action.setShortcut(QKeySequence("Shift+E"))
        self.copy_verse_action = QAction("نسخ الآية", self)
        self.copy_verse_action.triggered.connect(self.parent.on_copy_verse)
        self.copy_verse_action.setShortcut(QKeySequence("Ctrl+C"))

        actions_menu.addAction(self.save_position_action)
        actions_menu.addAction(self.surah_info_action)
        actions_menu.addAction(self.verse_tafsir_action)
        actions_menu.addAction(self.verse_info_action)
        actions_menu.addAction(self.verse_grammar_action)
        actions_menu.addAction(self.copy_verse_action)

        tools_menu = self.addMenu("الأدوات")
        bookmark_manager_action = QAction("مدير العلامات", self)
        bookmark_manager_action.setShortcut(QKeySequence("Shift+D"))
        bookmark_manager_action.triggered.connect(self.OnBookmarkManager)
        tools_menu.addAction(bookmark_manager_action )

        preferences_menu = self.addMenu("التفضيلات")
        settings_action = QAction("الإعدادات", self)
        settings_action.setShortcut(QKeySequence("F3"))
        settings_action.setShortcuts([QKeySequence("F3"), QKeySequence("Alt+S")])
        settings_action.triggered.connect(self.OnSettings)

        theme_menu = QMenu("تغيير الثيم", self)
        for theme in self.theme_manager.get_themes():
            theme_action = QAction(theme, self)
            theme_action.triggered.connect(self.OnTheme)
            theme_menu.addAction(theme_action)

        self.text_direction_action = QAction("تغيير اتجاه النص", self)
        self.text_direction_action.triggered.connect(self.toggle_text_direction)

        
        preferences_menu.addAction(settings_action)
        preferences_menu.addMenu(theme_menu)
        preferences_menu.addAction(self.text_direction_action)

        help_menu = self.addMenu("المساعدة")
        user_guide_action = QAction("دليل البرنامج", self)
        user_guide_action.setShortcut(QKeySequence("F1"))
        contact_us_action = QAction("اتصل بنا", self)
        update_program_action = QAction("تحديث البرنامج", self)
        update_program_action.setShortcuts([QKeySequence("F5"), QKeySequence("Ctrl+U")])
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

    def OnTheme    (self):
        theme = self.sender().text()
        self.theme_manager.apply_theme(theme)

    def toggle_text_direction(self):

        option = self.parent.quran_view.document().defaultTextOption()                                               
        if self.is_rtl:
            option.setTextDirection(Qt.LayoutDirection.LeftToRight)
            self.is_rtl = False
        else:
            option.setTextDirection(Qt.LayoutDirection.RightToLeft)
            self.is_rtl = True

        self.parent.quran_view.document().setDefaultTextOption(option)


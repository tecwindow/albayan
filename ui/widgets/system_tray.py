import utils.const as const
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction


class SystemTrayManager:
    def __init__(self, main_window, program_name: str, program_icon: str):
        self.tray_icon = QSystemTrayIcon(QIcon(program_icon), main_window)
        self.tray_icon.setToolTip(program_name)
        self.tray_icon.activated.connect(self.on_tray_icon_click)
        self.main_window = main_window
        const.tray_icon = self.tray_icon
        
        tray_menu = QMenu()
        show_action = QAction("إظهار النافذة الرائيسية", main_window)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("إغلاق البرنامج", main_window)
        quit_action.triggered.connect(self.main_window.menu_bar.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_main_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def on_tray_icon_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_main_window()

    def hide_icon(self):
        self.tray_icon.hide()

from PyQt6.QtWidgets import  QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction

class SystemTrayManager:
    def __init__(self, program_name: str, program_icon: str, app: QApplication, main_window):
        self.tray_icon = QSystemTrayIcon(QIcon(program_icon), app)
        self.tray_icon.setToolTip(program_name)
        self.main_window = main_window
        self.main_window.menu_bar.tray_icon = self.tray_icon
        
        tray_menu = QMenu()
        show_action = QAction("Show", app)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", app)
        quit_action.triggered.connect(self.main_window.menu_bar.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_main_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

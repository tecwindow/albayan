from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from utils.const import Globals
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class SystemTrayManager:
    def __init__(self, main_window, program_name: str, program_icon: str):
        logger.debug("Initializing SystemTrayManager.")
        self.tray_icon = QSystemTrayIcon(QIcon(program_icon), main_window)
        self.tray_icon.setToolTip(program_name)
        self.tray_icon.activated.connect(self.on_tray_icon_click)
        self.main_window = main_window
        Globals.TRAY_ICON = self.tray_icon
        logger.info(f"System tray icon created with program name: {program_name}.")

        tray_menu = QMenu()
        show_action = QAction("إظهار النافذة الرئيسية", main_window)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)

        sura_action = QAction("إظهار مشغل السور", main_window)
        sura_action.triggered.connect(self.show_sura_player)
        tray_menu.addAction(sura_action)

        quit_action = QAction("إغلاق البرنامج", main_window)
        quit_action.triggered.connect(self.main_window.menu_bar.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        logger.debug("System tray icon is now visible.")

    def show_main_window(self):
        logger.debug("Tray icon clicked - attempting to show main window.")
        if (
            self.main_window.menu_bar.sura_player_window is not None
            and self.main_window.menu_bar.sura_player_window.isVisible()
        ):
            logger.debug(
                "Sura Player window is active, closing it before showing main window."
            )
            self.main_window.menu_bar.sura_player_window.close()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        logger.debug("Main window is now visible and active.")

    def show_sura_player(self):
        logger.debug("Tray menu option clicked - attempting to show Sura Player.")
        if self.main_window.isVisible():
            logger.debug("Main window is active, hiding it before showing Sura Player.")
            self.main_window.hide()

        self.main_window.menu_bar.OnSuraPlayer()
        logger.debug("Sura Player window is now visible.")

    def on_tray_icon_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            logger.debug(
                "Tray icon clicked (ActivationReason.Trigger). Showing main window."
            )
            self.show_main_window()

    def hide_icon(self):
        logger.debug("Hiding system tray icon.")
        self.tray_icon.hide()
        logger.info("System tray icon hidden.")

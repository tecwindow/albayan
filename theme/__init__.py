import os
from PyQt6.QtWidgets import QMessageBox
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class ThemeManager:
    def __init__(self, window):
        logger.info("Initializing ThemeManager.")
        self.window = window
        self.theme_dir = os.path.dirname(__file__)
        self.themes = {}
        logger.info("ThemeManager initialized.")


    def get_themes(self):
        logger.debug("Fetching available themes...")
        self.themes = {"الافتراضي": "default"}
        for file in os.listdir(self.theme_dir):
            if file.endswith(".qss"):
                theme_name = os.path.splitext(file)[0]
                self.themes[theme_name] = file
        logger.info(f"Available themes: {list(self.themes.keys())}")
        return list(self.themes.keys())

    def apply_theme(self, selected_theme):
        logger.info(f"Applying theme: {selected_theme}")
        if selected_theme == "default":
            self.window.setStyleSheet("")
            logger.debug("Default theme applied.")
            return

        theme_file = self.themes.get(selected_theme)
        if not theme_file:
            logger.error(f"Theme not found: {selected_theme}.")
            return None

        theme_path = os.path.join(self.theme_dir, theme_file)
        if not os.path.isfile(theme_path):
            logger.error(f"File not found: {theme_path}.")
            return None

        try:
            with open(theme_path, 'r') as theme_file:
                stylesheet = theme_file.read()
                self.window.setStyleSheet(stylesheet)
                logger.info(f"Theme '{selected_theme}' applied successfully.")
        except Exception as e:
            logger.error(f"Error applying theme '{selected_theme}': {e}", exc_info=True)
            message_box = QMessageBox()
            message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            message_box.button(QMessageBox.StandardButton.Ok).setText("موافق")
            message_box.critical(self.window, "خطأ", "حدث خطأ أثناء تغيير الثيم.")
            message_box.exec()

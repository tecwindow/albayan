import os
from PySide6.QtWidgets import QMessageBox, QApplication
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
        app = QApplication.instance()
        if selected_theme in ("default", "الافتراضي"):
            self.window.setStyleSheet("")
            if app:
                app.setStyleSheet("")
            logger.debug("Default theme applied.")
            return

        if not self.themes:
            self.get_themes()

        theme_file = self.themes.get(selected_theme)
        if not theme_file and selected_theme:
            base = selected_theme.replace(".qss", "")
            theme_file = self.themes.get(base)
            if not theme_file and os.path.isfile(os.path.join(self.theme_dir, f"{base}.qss")):
                theme_file = f"{base}.qss"

        if theme_file == "default":
            self.window.setStyleSheet("")
            if app:
                app.setStyleSheet("")
            logger.debug("Default theme applied.")
            return

        if not theme_file:
            logger.error(f"Theme not found: {selected_theme}.")
            return None

        theme_path = os.path.join(self.theme_dir, theme_file)
        if not os.path.isfile(theme_path):
            logger.error(f"File not found: {theme_path}.")
            return None

        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()
                self.window.setStyleSheet(stylesheet)
                if app:
                    app.setStyleSheet(stylesheet)
                logger.info(f"Theme '{selected_theme}' applied successfully.")
        except Exception as e:
            logger.error(f"Error applying theme '{selected_theme}': {e}", exc_info=True)
            message_box = QMessageBox()
            message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            message_box.button(QMessageBox.StandardButton.Ok).setText("موافق")
            message_box.critical(self.window, "خطأ", "حدث خطأ أثناء تغيير الثيم.")
            message_box.exec()

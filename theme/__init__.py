import os
from PyQt6.QtWidgets import QMessageBox
from utils.logger import Logger

class ThemeManager:
    def __init__(self, window):
        self.window = window
        self.theme_dir = "theme"
        self.themes = {}

    def get_themes(self):
        self.themes = {os.path.splitext(file)[0]: file for file in os.listdir(self.theme_dir) if file.endswith(".qss")}
        return list(self.themes.keys())

    def apply_theme(self, selected_theme):

        theme_file = self.themes.get(selected_theme)
        if not theme_file:
            Logger.error(f"Theme not found: {selected_theme}")
            return None

        theme_path = os.path.join(self.theme_dir, theme_file)
        if not os.path.isfile(theme_path):
            Logger.error(f"File not found: {theme_path}")
            return None

        try:
            with open(theme_path, 'r') as theme_file:
                stylesheet = theme_file.read()
                self.window.setStyleSheet(stylesheet)  # تطبيق الثيم على النافذة المحددة
        except Exception as e:
            Logger.error(str(e))
            message_box = QMessageBox()
            message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            message_box.button(QMessageBox.StandardButton.Ok).setText("موافق")
            message_box.critical(self.window, "خطأ", "حدث خطأ أثناء تغيير الثيم.")
            message_box.exec()

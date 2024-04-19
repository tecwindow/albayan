import os
import sys
from PyQt6 import QtWidgets, QtGui
import configparser
import globals as g
from functions import *

class Settings:
    def __init__(self):
        AppData = os.path.join(os.getenv("AppData"), "WikiSearch")
        self.path = os.path.join(AppData, "Settingss.ini")
        self.config = configparser.ConfigParser()

        self.DefaultSettings = {
            "language": "English",
            "activ escape": "False",
            "results number": "20",
            "random articles number": "20",
            "auto update": "True",
            "close message": "True",
            "auto detect": "True",
            "search language": "English",
            "wepviewer": "0"
        }

    def write_settings(self, **new_settings):
        try:
            self.config.read(self.path, encoding='utf-8')
        except:
            pass

        try:
            self.config.add_section("default")
        except configparser.DuplicateSectionError:
            pass

        for setting in new_settings:
            self.config.set("default", setting, new_settings[setting])

        with open(self.path, "w", encoding='utf-8') as config_file:
            self.config.write(config_file)

    def read_settings(self):
        try:
            self.config.read(self.path, encoding='utf-8')
        except:
            self.write_settings(**self.DefaultSettings)

        current_settings = self.DefaultSettings.copy()

        for setting in current_settings:
            try:
                current_settings[setting] = self.config.get("default", setting)
            except:
                default_setting = {setting: self.DefaultSettings[setting]}
                self.write_settings(**default_setting)

        return current_settings

    def reset_settings(self):
        self.write_settings(**self.DefaultSettings)

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle(_("Program Settings"))
        self.resize(400, 600)
        self.current_settings = Settings().read_settings()
        self.setup_ui()

    def setup_ui(self):
        panel = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(panel)

        notebook = QtWidgets.QTabWidget()

        general_page = QtWidgets.QWidget()
        general_layout = QtWidgets.QVBoxLayout(general_page)

        language_title = QtWidgets.QLabel(_("Choose language:"))
        self.program_language = QtWidgets.QComboBox()
        self.program_language.addItems(['Arabic', 'English', 'Español', 'Français'])
        self.program_language.setCurrentText(self.current_settings["language"])

        self.viewer = QtWidgets.QGroupBox(_("Choose your prefered view:"))
        self.viewer_layout = QtWidgets.QVBoxLayout(self.viewer)
        self.normal_view = QtWidgets.QRadioButton(_("Normal View"))
        self.web_view = QtWidgets.QRadioButton(_("Web View(Not recommended)"))
        self.viewer_layout.addWidget(self.normal_view)
        self.viewer_layout.addWidget(self.web_view)
        self.viewer_button_group = QtWidgets.QButtonGroup()
        self.viewer_button_group.addButton(self.normal_view, 0)
        self.viewer_button_group.addButton(self.web_view, 1)
        self.viewer_button_group.buttonClicked[int].connect(self.on_viewer_selected)
        self.viewer_button_group.button(int(self.current_settings["wepviewer"])).setChecked(True)

        results_number_title = QtWidgets.QLabel(_("Select the number of results:"))
        self.number_results = QtWidgets.QSpinBox()
        self.number_results.setRange(1, 100)
        self.number_results.setValue(int(self.current_settings["results number"]))

        random_articles_title = QtWidgets.QLabel(_("Select the number of random articles:"))
        self.random_articles_number = QtWidgets.QSpinBox()
        self.random_articles_number.setRange(1, 100)
        self.random_articles_number.setValue(int(self.current_settings["random articles number"]))

        self.verification_msg = QtWidgets.QCheckBox(_("Show Close message when at least an article is open"))
        self.verification_msg.setChecked(self.current_settings["close message"] == "True")

        self.auto_detect = QtWidgets.QCheckBox(_("Auto detect links from the clipboard"))
        self.auto_detect.setChecked(self.current_settings["auto detect"] == "True")

        self.auto_update = QtWidgets.QCheckBox(_("Check for updates automatically"))
        self.auto_update.setChecked(self.current_settings["auto update"] == "True")

        self.close_article_with_scape = QtWidgets.QCheckBox(_("Close the article via the Escape key"))
        self.close_article_with_scape.setChecked(self.current_settings["activ escape"] == "True")

        general_layout.addWidget(language_title)
        general_layout.addWidget(self.program_language)
        general_layout.addWidget(self.viewer)
        general_layout.addWidget(results_number_title)
        general_layout.addWidget(self.number_results)
        general_layout.addWidget(random_articles_title)
        general_layout.addWidget(self.random_articles_number)
        general_layout.addWidget(self.verification_msg)
        general_layout.addWidget(self.auto_detect)
        general_layout.addWidget(self.auto_update)
        general_layout.addWidget(self.close_article_with_scape)
        general_layout.addStretch()

        notebook.addTab(general_page, _("General"))

        clean_page = QtWidgets.QWidget()
        clean_layout = QtWidgets.QVBoxLayout(clean_page)

        self.clean_history_button = QtWidgets.QPushButton(_("Delete history"))
        self.clean_favourites_button = QtWidgets.QPushButton(_("Delete favourites"))
        self.clean_saved_articles_button = QtWidgets.QPushButton(_("Delete saved articles"))
        self.default_settings_button = QtWidgets.QPushButton(_("Reset to default settings"))

        clean_layout.addWidget(self.clean_history_button)
        clean_layout.addWidget(self.clean_favourites_button)
        clean_layout.addWidget(self.clean_saved_articles_button)
        clean_layout.addWidget(self.default_settings_button)
        clean_layout.addStretch()

        notebook.addTab(clean_page, _("Advanced"))

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.on_save_settings)
        button_box.rejected.connect(self.reject)

        layout.addWidget(notebook)
        layout.addWidget(button_box)
        layout.addStretch()

        self.setTabOrder(self.program_language, self.number_results)
        self.setTabOrder(self.number_results, self.random_articles_number)
        self.setTabOrder(self.random_articles_number, self.verification_msg)
        self.setTabOrder(self.verification_msg, self.auto_detect)
        self.setTabOrder(self.auto_detect, self.auto_update)
        self.setTabOrder(self.auto_update, self.close_article_with_scape)

    def on_viewer_selected(self, id):
        self.current_settings["wepviewer"] = str(id)

    def on_save_settings(self):
        new_settings = {
            "language": self.program_language.currentText(),
            "results number": str(self.number_results.value()),
            "random articles number": str(self.random_articles_number.value()),
            "close message": str(self.verification_msg.isChecked()),
            "auto update": str(self.auto_update.isChecked()),
            "auto detect": str(self.auto_detect.isChecked()),
            "activ escape": str(self.close_article_with_scape.isChecked()),
            "search language": self.current_settings["search language"],
            "wepviewer": self.current_settings["wepviewer"]
        }

        Settings().write_settings(**new_settings)

        if new_settings["language"] != self.current_settings["language"]:
            confirm_restart_program = QtWidgets.QMessageBox.question(self, _("Confirm"),
                                                                      _("""You must restart the program for the new language to take effect.
Do you want to restart the program now?"""),
                                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                                      QtWidgets.QMessageBox.No)
            if confirm_restart_program == QtWidgets.QMessageBox.Yes:
                os.execv(sys.executable, ['python'] + sys.argv)
            else:
                self.close()

        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SettingsDialog()
    window.show()
    sys.exit(app.exec())

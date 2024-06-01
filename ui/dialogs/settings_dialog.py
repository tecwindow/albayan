from PyQt6.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QListWidget, 
    QHBoxLayout, 
    QListWidgetItem, 
    QCheckBox, 
    QPushButton, 
    QGroupBox,
QMessageBox
)
from PyQt6.QtGui import QKeySequence
from utils.settings import SettingsManager

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("الإعدادات")
        self.resize(500, 400)
        self.init_ui()
        self.set_current_settings()

    def init_ui(self):
        main_layout = QVBoxLayout()
        taps_layout = QHBoxLayout()

        list_widget = QListWidget()
        general_item = QListWidgetItem("الإعدادات العامة")
        search_item = QListWidgetItem("البحث")
        list_widget.addItem(general_item)
        list_widget.addItem(search_item)
        list_widget.currentItemChanged.connect(self.change_category)
        taps_layout.addWidget(list_widget, stretch=1)

        self.group_general = QGroupBox("الإعدادات العامة")
        self.group_general_layout = QVBoxLayout()
        self.sound_checkbox = QCheckBox("تفعيل المؤثرات الصوتية")
        self.speech_checkbox = QCheckBox("نطق الإجرائات")
        self.update_checkbox = QCheckBox("التحقق من التحديثات")
        self.log_checkbox = QCheckBox("تمكين تسجيل الأخطاء")
        self.reset_button = QPushButton("استعادة الإعدادات الافتراضية")
        self.reset_button.clicked.connect(self.OnReset)
        
        self.group_general_layout.addWidget(self.sound_checkbox)
        self.group_general_layout.addWidget(self.speech_checkbox)
        self.group_general_layout.addWidget(self.update_checkbox)
        self.group_general_layout.addWidget(self.log_checkbox)
        self.group_general_layout.addWidget(self.reset_button)
        self.group_general.setLayout(self.group_general_layout)
        self.group_general.setVisible(False)
        taps_layout.addWidget(self.group_general, stretch=2)

        self.group_search = QGroupBox("إعدادات البحث")
        self.group_search_layout = QVBoxLayout()
        self.ignore_tashkeel_checkbox = QCheckBox("تجاهل التشكيل")
        self.ignore_hamza_checkbox = QCheckBox("تجاهل الهمزات")

        self.group_search_layout.addWidget(self.ignore_tashkeel_checkbox)
        self.group_search_layout.addWidget(self.ignore_hamza_checkbox)
        self.group_search.setLayout(self.group_search_layout)
        self.group_search.setVisible(False)
        taps_layout.addWidget(self.group_search, stretch=2)

        main_layout.addLayout(taps_layout)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("حفظ")
        save_button.clicked.connect(self.save_settings)
        save_button.setDefault(True)
        close_button = QPushButton("إغلاق")
        close_button.setShortcut(QKeySequence("Ctrl+W"))
        close_button.clicked.connect(self.close)

        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(close_button)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)


    def change_category(self, current, previous):
        if current:
            if current.text() == "الإعدادات العامة":
                self.group_general.setVisible(True)
                self.group_search.setVisible(False)
            elif current.text() == "البحث":
                self.group_general.setVisible(False)
                self.group_search.setVisible(True)

    def save_settings(self):

        # Collect general settings
        general_settings = {
            "sound_effect_enabled": self.sound_checkbox.isChecked(),
            "speak_actions_enabled": self.speech_checkbox.isChecked(),
            "check_update_enabled": self.update_checkbox.isChecked(),
            "logging_enabled": self.log_checkbox.isChecked()
        }

        # Collect search settings
        search_settings = {
            "ignore_tashkeel": self.ignore_tashkeel_checkbox.isChecked(),
            "ignore_hamza": self.ignore_hamza_checkbox.isChecked()
        }

        # Update the current settings
        SettingsManager.write_settings({
            "general": general_settings,
            "search": search_settings
        })
        self.accept()

    def OnReset(self):

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("تحذير")
        msg_box.setText("هل أنت متأكد من إعادة تعيين الإعدادات إلى الإعدادات الافتراضية؟")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        yes_button = msg_box.addButton("نعم", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("لا", QMessageBox.ButtonRole.NoRole)
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            SettingsManager.reset_settings()
            self.set_current_settings()

    def set_current_settings(self):
        current_settings = SettingsManager.current_settings    
        self.sound_checkbox.setChecked(current_settings["general"]["sound_effect_enabled"])
        self.speech_checkbox.setChecked(current_settings["general"]["speak_actions_enabled"])
        self.update_checkbox.setChecked(current_settings["general"]["check_update_enabled"])
        self.log_checkbox.setChecked(current_settings["general"]["logging_enabled"])
        self.ignore_tashkeel_checkbox.setChecked(current_settings["search"]["ignore_tashkeel"])
        self.ignore_hamza_checkbox.setChecked(current_settings["search"]["ignore_hamza"])

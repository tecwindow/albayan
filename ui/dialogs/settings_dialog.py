from PyQt6.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QListWidget, 
    QHBoxLayout, 
    QListWidgetItem, 
    QCheckBox, 
    QPushButton, 
    QGroupBox
)

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("الإعدادات")
        self.setGeometry(100, 100, 400, 300)

        main_layout = QVBoxLayout()
        taps_layout = QHBoxLayout()

        list_widget = QListWidget()
        general_item = QListWidgetItem("الإعدادات العامة")
        search_item = QListWidgetItem("البحث")
        list_widget.addItem(general_item)
        list_widget.addItem(search_item)
        list_widget.currentItemChanged.connect(self.change_category)
        taps_layout.addWidget(list_widget)

        self.group_general = QGroupBox("الإعدادات العامة")
        self.group_general_layout = QVBoxLayout()
        self.sound_checkbox = QCheckBox("تفعيل المؤثرات الصوتية")
        self.speech_checkbox = QCheckBox("نطق الإجرائات")
        self.update_checkbox = QCheckBox("التحقق من التحديثات")
        self.log_checkbox = QCheckBox("تمكين تسجيل الأخطاء")
        self.reset_button = QPushButton("إعادة الإعدادات الافتراضية")

        self.sound_checkbox.setChecked(False)
        self.speech_checkbox.setChecked(True)
        self.update_checkbox.setChecked(True)
        self.log_checkbox.setChecked(True)

        self.group_general_layout.addWidget(self.sound_checkbox)
        self.group_general_layout.addWidget(self.speech_checkbox)
        self.group_general_layout.addWidget(self.update_checkbox)
        self.group_general_layout.addWidget(self.log_checkbox)
        self.group_general_layout.addWidget(self.reset_button)
        self.group_general.setLayout(self.group_general_layout)
        self.group_general.setVisible(False)
        taps_layout.addWidget(self.group_general)

        self.group_search = QGroupBox("إعدادات البحث")
        self.group_search_layout = QVBoxLayout()
        self.ignore_tashkeel_checkbox = QCheckBox("تجاهل التشكيل")
        self.ignore_hamza_checkbox = QCheckBox("تجاهل الهمزات")
        self.ignore_tashkeel_checkbox.setChecked(True)
        self.ignore_hamza_checkbox.setChecked(True)

        self.group_search_layout.addWidget(self.ignore_tashkeel_checkbox)
        self.group_search_layout.addWidget(self.ignore_hamza_checkbox)
        self.group_search.setLayout(self.group_search_layout)
        self.group_search.setVisible(False)
        taps_layout.addWidget(self.group_search)

        main_layout.addLayout(taps_layout)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("حفظ")
        save_button.clicked.connect(self.save_settings)
        close_button = QPushButton("إغلاق")
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
        pass

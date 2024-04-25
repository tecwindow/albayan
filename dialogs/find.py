import os
import json
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QCheckBox
)
from PyQt6.QtCore import Qt


class SearchDialog(QDialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 500, 400)
        self.initUI()

    def initUI(self):
        self.search_label = QLabel('اكتب ما تريد البحث عنه:')
        self.search_box = QLineEdit()
        self.search_box.setAccessibleName('اكتب ما تريد البحث عنه:')
        self.advanced_search_checkbox = QCheckBox('البحث المتقدم')
        self.advanced_search_checkbox.toggled.connect(self.show_advanced_options)
        self.search_button = QPushButton('بحث')
        self.cancel_button = QPushButton('إلغاء')

        self.advanced_search_groupbox = QGroupBox('البحث المتقدم')
        self.advanced_search_groupbox.setEnabled(False)
        self.search_type_label = QLabel('نوع البحث:')
        self.search_type_radio_page = QRadioButton('صفحة')
        self.search_type_radio_page.setChecked(True)
        self.search_type_radio_sura = QRadioButton('صورة')
        self.search_type_radio_juz = QRadioButton('جزء')
        self.search_type_radio_hizb = QRadioButton('حزب')
        self.search_type_radio_quarter = QRadioButton('ربع')

        self.search_from_label = QLabel('من:')
        self.search_from_combobox = QComboBox()
        self.search_from_combobox.setAccessibleName("من:")
        self.search_to_label = QLabel('إلى:')
        self.search_to_combobox = QComboBox()
        self.search_to_combobox.setAccessibleName("إلى:")
        self.ignore_diacritics_checkbox = QCheckBox('تجاهل التشكيل')
        self.ignore_hamza_checkbox = QCheckBox('تجاهل الهمزات')

        self.search_type_layout = QHBoxLayout()
        self.search_type_layout.addWidget(self.search_type_radio_page)
        self.search_type_layout.addWidget(self.search_type_radio_sura)
        self.search_type_layout.addWidget(self.search_type_radio_juz)
        self.search_type_layout.addWidget(self.search_type_radio_hizb)
        self.search_type_layout.addWidget(self.search_type_radio_quarter)

        self.search_from_to_layout = QHBoxLayout()
        self.search_from_to_layout.addWidget(self.search_from_label)
        self.search_from_to_layout.addWidget(self.search_from_combobox)
        self.search_from_to_layout.addWidget(self.search_to_label)
        self.search_from_to_layout.addWidget(self.search_to_combobox)

        self.search_options_layout = QVBoxLayout()
        self.search_options_layout.addWidget(self.search_type_label)
        self.search_options_layout.addLayout(self.search_type_layout)
        self.search_options_layout.addLayout(self.search_from_to_layout)
        self.search_options_layout.addWidget(self.ignore_diacritics_checkbox)
        self.search_options_layout.addWidget(self.ignore_hamza_checkbox)

        self.advanced_search_groupbox.setLayout(self.search_options_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.search_label)
        main_layout.addWidget(self.search_box)
        main_layout.addWidget(self.advanced_search_checkbox)
        main_layout.addWidget(self.advanced_search_groupbox)
        main_layout.addWidget(self.search_button)
        main_layout.addWidget(self.cancel_button)

        self.setLayout(main_layout)

        self.sura = []
        with open(os.path.join("database", "Surahs.Json"), encoding="UTF-8") as f:
            self.sura = json.load(f)["surahs"]
        self.pages = ["{:03d}".format(i) for i in range(1, 605)]
        self.quarters = ["{:03d}".format(i) for i in range(1, 241)]
        self.jus = ["{:02d}".format(i) for i in range(1, 31)]
        self.hizb = ["{:02d}".format(i) for i in range(1, 61)]

        self.search_button.clicked.connect(self.on_submit)
        self.cancel_button.clicked.connect(self.reject)
        self.search_type_radio_page.toggled.connect(self.on_radio_toggled)
        self.search_type_radio_sura.toggled.connect(self.on_radio_toggled)
        self.search_type_radio_juz.toggled.connect(self.on_radio_toggled)
        self.search_type_radio_hizb.toggled.connect(self.on_radio_toggled)
        self.search_type_radio_quarter.toggled.connect(self.on_radio_toggled)

        self.on_radio_toggled()

    def show_advanced_options(self):
        self.advanced_search_groupbox.setEnabled(self.advanced_search_checkbox.isChecked())

    def on_submit(self):
        self.accept()

    def on_radio_toggled(self):
        if self.search_type_radio_page.isChecked():
            self.search_from_combobox.clear()
            self.search_to_combobox.clear()
            self.search_from_combobox.addItems([str(i) for i in range(1, 605)])
            self.search_to_combobox.addItems([str(i) for i in range(1, 605)])
        elif self.search_type_radio_sura.isChecked():
            self.search_from_combobox.clear()
            self.search_to_combobox.clear()
            self.search_from_combobox.addItems([sura["name"] for sura in self.sura])
            self.search_to_combobox.addItems([sura["name"] for sura in self.sura])
        elif self.search_type_radio_juz.isChecked():
            self.search_from_combobox.clear()
            self.search_to_combobox.clear()
            self.search_from_combobox.addItems(self.jus)
            self.search_to_combobox.addItems(self.jus)
        elif self.search_type_radio_hizb.isChecked():
            self.search_from_combobox.clear()
            self.search_to_combobox.clear()
            self.search_from_combobox.addItems(self.hizb)
            self.search_to_combobox.addItems(self.hizb)
        elif self.search_type_radio_quarter.isChecked():
            self.search_from_combobox.clear()
            self.search_to_combobox.clear()
            self.search_from_combobox.addItems(self.quarters)
            self.search_to_combobox.addItems(self.quarters)
        self.search_to_combobox.setCurrentIndex(self.search_to_combobox.count() - 1)

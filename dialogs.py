import os
import json
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QTextEdit,
    QPushButton,
    QRadioButton,
    QComboBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt


class view_information(QDialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 550, 550)
        self.label = QLabel()
        self.view_text = QTextEdit()
        self.close = QPushButton("إغلاق")
        self.copy = QPushButton("نسخ")

        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.view_text, stretch=1)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.close)
        button_layout.addWidget(self.copy)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.close.clicked.connect(self.accept)

class QuickAccess(QDialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 300, 200)
        self.sura = []
        with open(os.path.join("database", "Surahs.Json"), encoding="UTF-8") as f:
            self.sura = json.load(f)["surahs"]
        self.pages = ["{:03d}".format(i) for i in range(1, 605)]
        self.quarters = ["{:03d}".format(i) for i in range(1, 241)]
        self.jus = ["{:02d}".format(i) for i in range(1, 31)]
        self.hizb = ["{:02d}".format(i) for i in range(1, 61)]

        layout = QVBoxLayout()

        self.view_by = QGroupBox("عرض وفقا ل:")
        view_by_layout = QVBoxLayout()
        self.sura_radio = QRadioButton("سور")
        self.pages_radio = QRadioButton("صفح")
        self.quarters_radio = QRadioButton("أرباع")
        self.hizb_radio = QRadioButton("أحزاب")
        self.jus_radio = QRadioButton("أجزاء")
        view_by_layout.addWidget(self.sura_radio)
        view_by_layout.addWidget(self.pages_radio)
        view_by_layout.addWidget(self.quarters_radio)
        view_by_layout.addWidget(self.hizb_radio)
        view_by_layout.addWidget(self.jus_radio)
        self.view_by.setLayout(view_by_layout)

        self.choices_label = QLabel("إنتقل إلى:")
        self.choices = QComboBox()
        self.go_button = QPushButton("اذهب")
        self.cancel_button = QPushButton("إغلاق")

        layout.addWidget(self.view_by)
        layout.addWidget(self.choices_label)
        layout.addWidget(self.choices)
        layout.addWidget(self.go_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        self.sura_radio.setChecked(True)
        self.choices.addItems([sura["name"] for sura in self.sura])

        self.go_button.clicked.connect(self.on_submit)
        self.sura_radio.toggled.connect(self.on_radio_toggled)
        self.pages_radio.toggled.connect(self.on_radio_toggled)
        self.quarters_radio.toggled.connect(self.on_radio_toggled)
        self.hizb_radio.toggled.connect(self.on_radio_toggled)
        self.jus_radio.toggled.connect(self.on_radio_toggled)

    def on_submit(self):
        self.accept()

    def on_radio_toggled(self):
        if self.sura_radio.isChecked():
            self.choices.clear()
            self.choices.addItems([sura["name"] for sura in self.sura])
        elif self.pages_radio.isChecked():
            self.choices.clear()
            self.choices.addItems(self.pages)
        elif self.quarters_radio.isChecked():
            self.choices.clear()
            self.choices.addItems(self.quarters)
        elif self.hizb_radio.isChecked():
            self.choices.clear()
            self.choices.addItems(self.hizb)
        elif self.jus_radio.isChecked():
            self.choices.clear()
            self.choices.addItems(self.jus)

    def get_selected_item(self):
        view_by = 0
        if self.sura_radio.isChecked():
            view_by = 0
        elif self.pages_radio.isChecked():
            view_by = 1
        elif self.quarters_radio.isChecked():
            view_by = 2
        elif self.hizb_radio.isChecked():
            view_by = 3
        elif self.jus_radio.isChecked():
            view_by = 4

        item = {
            "number": self.choices.currentIndex() + 1,
            "view_by": view_by
        }

        return item

if __name__ == "__main__":
    app = QApplication([])
    view_info_dialog = view_information(None, "معلومات الآية")
    view_info_dialog.exec()
    quick_access_dialog = QuickAccess(None, "الوصول السريع")
    quick_access_dialog.exec()

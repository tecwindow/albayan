import os
import json
from utils.audio_player import SoundEffectPlayer
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QComboBox,
    QGroupBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence


class QuickAccess(QDialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(title)
        self.resize(300, 200)
        self.effects_manager = SoundEffectPlayer("Audio/sounds")
        self.sura = []
        with open(os.path.join("database", "Surahs.Json"), encoding="UTF-8") as f:
            self.sura = json.load(f)["surahs"]
        self.pages = ["{}".format(i) for i in range(1, 605)]
        self.quarters = ["{}".format(i) for i in range(1, 241)]
        self.jus = ["{}".format(i) for i in range(1, 31)]
        self.hizb = ["{}".format(i) for i in range(1, 61)]

        layout = QVBoxLayout()
        self.view_by = QGroupBox("عرض وفقا ل:")
        view_by_layout = QVBoxLayout()
        self.sura_radio = QRadioButton("سور")
        self.pages_radio = QRadioButton("صفحات")
        self.quarters_radio = QRadioButton("أرباع")
        self.hizb_radio = QRadioButton("أحزاب")
        self.jus_radio = QRadioButton("أجزاء")
        view_by_layout.addWidget(self.sura_radio)
        view_by_layout.addWidget(self.pages_radio)
        view_by_layout.addWidget(self.quarters_radio)
        view_by_layout.addWidget(self.hizb_radio)
        view_by_layout.addWidget(self.jus_radio)
        self.view_by.setLayout(view_by_layout)

        self.choices_label = QLabel("انتقل إلى:")
        self.choices = QComboBox()
        self.choices.setAccessibleName(self.choices_label.text())
        
        button_layout = QHBoxLayout()  # استخدام QHBoxLayout لأزرار الإجراءات
        self.go_button = QPushButton("اذهب")
        self.cancel_button = QPushButton("إغلاق")
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))
        button_layout.addWidget(self.go_button)
        button_layout.addWidget(self.cancel_button)

        layout.addWidget(self.view_by)
        layout.addWidget(self.choices_label)
        layout.addWidget(self.choices)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.sura_radio.setChecked(True)
        self.choices.addItems([sura["name"] for sura in self.sura])

        self.go_button.clicked.connect(self.on_submit)
        self.cancel_button.clicked.connect(self.reject)
        self.sura_radio.toggled.connect(self.on_radio_toggled)
        self.pages_radio.toggled.connect(self.on_radio_toggled)
        self.quarters_radio.toggled.connect(self.on_radio_toggled)
        self.hizb_radio.toggled.connect(self.on_radio_toggled)
        self.jus_radio.toggled.connect(self.on_radio_toggled)

    def on_submit(self):
        selected_item = self.choices.currentIndex() + 1
        if self.sura_radio.isChecked():
            self.parent.quran_view.setText(self.parent.quran.get_surah(selected_item))
        elif self.pages_radio.isChecked():
            self.parent.quran_view.setText(self.parent.quran.get_page(selected_item))
        elif self.quarters_radio.isChecked():
            self.parent.quran_view.setText(self.parent.quran.get_quarter(selected_item))
        elif self.hizb_radio.isChecked():
            self.parent.quran_view.setText(self.parent.quran.get_hizb(selected_item))
        elif self.jus_radio.isChecked():
            self.parent.quran_view.setText(self.parent.quran.get_juzz(selected_item))
        self.accept()
        self.effects_manager.play("change")
        self.deleteLater()

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

    def reject(self):
        self.deleteLater()
        
import os
import qtawesome as qta
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
from PyQt6.QtGui import QKeySequence, QShortcut
from core_functions.quran.quran_manager import QuranManager
from utils.logger import LoggerManager
from utils.const import Globals

logger = LoggerManager.get_logger(__name__)

class QuickAccess(QDialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        logger.debug(f"Initializing QuickAccess dialog: {title}")
        self.parent = parent
        self.setWindowTitle(title)
        self.resize(300, 200)
        self.sura = [surah.name for surah in parent.quran_manager.get_surahs()]
        self.pages = ["{}".format(i) for i in range(1, QuranManager.MAX_PAGE + 1)]
        self.quarters = ["{}".format(i) for i in range(1, QuranManager.MAX_QUARTER + 1)]
        self.jus = ["{}".format(i) for i in range(1, QuranManager.MAX_JUZ + 1)]
        self.hizb = ["{}".format(i) for i in range(1, QuranManager.MAX_HIZB + 1)]

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
        self.go_button.setIcon(qta.icon("fa.location-arrow"))
        self.cancel_button = QPushButton("إغلاق")
        self.cancel_button.setIcon(qta.icon("fa.times"))
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))
        button_layout.addWidget(self.go_button)
        button_layout.addWidget(self.cancel_button)

        layout.addWidget(self.view_by)
        layout.addWidget(self.choices_label)
        layout.addWidget(self.choices)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.sura_radio.setChecked(True)
        self.choices.addItems(self.sura)

        self.go_button.clicked.connect(self.on_submit)
        self.cancel_button.clicked.connect(self.reject)
        self.sura_radio.toggled.connect(self.on_radio_toggled)
        self.pages_radio.toggled.connect(self.on_radio_toggled)
        self.quarters_radio.toggled.connect(self.on_radio_toggled)
        self.hizb_radio.toggled.connect(self.on_radio_toggled)
        self.jus_radio.toggled.connect(self.on_radio_toggled)
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)
        logger.debug("QuickAccess dialog initialized successfully.")

    def on_submit(self):    
        logger.debug("go button clicked.")
        selected_item = self.choices.currentIndex() + 1
        logger.debug(f"User selected index {selected_item}")
        if self.sura_radio.isChecked():
            selection_type = "Surah"
            content = self.parent.quran_manager.get_surah(selected_item)
        elif self.pages_radio.isChecked():
            selection_type = "Page"
            content = self.parent.quran_manager.get_page(selected_item)
        elif self.quarters_radio.isChecked():
            selection_type = "Quarter"
            content = self.parent.quran_manager.get_quarter(selected_item)
        elif self.hizb_radio.isChecked():
            selection_type = "Hizb"
            content = self.parent.quran_manager.get_hizb(selected_item)
        elif self.jus_radio.isChecked():
            selection_type = "Juzz"
            content = self.parent.quran_manager.get_juz(selected_item)
        else:
            logger.warning("No selection type was chosen!")
            return

        self.parent.quran_view.setText(content)
        self.accept()
        Globals.effects_manager.play("change")
        logger.info(f"User navigated to {selection_type} {selected_item}")
        self.deleteLater()

    def on_radio_toggled(self):
        logger.debug("Radio button toggled, updating choices.")
        if self.sura_radio.isChecked():
            self.choices.clear()
            self.choices.addItems(self.sura)
            logger.debug("Switched to Surah selection")
        elif self.pages_radio.isChecked():
            self.choices.clear()
            self.choices.addItems(self.pages)
            logger.debug("Switched to Page selection")
        elif self.quarters_radio.isChecked():
            self.choices.clear()
            self.choices.addItems(self.quarters)
            logger.debug("Switched to Quarter selection")
        elif self.hizb_radio.isChecked():
            self.choices.clear()
            self.choices.addItems(self.hizb)
            logger.debug("Switched to Hizb selection")
        elif self.jus_radio.isChecked():
            self.choices.clear()
            self.choices.addItems(self.jus)
            logger.debug("Switched to Juzz selection")

    def reject(self):
        self.deleteLater()
        
    def closeEvent(self, a0):
        logger.debug("QuickAccess dialog closed.")
        return super().closeEvent(a0)

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QGroupBox, QLabel
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from typing import List, Dict, Optional
from core_functions.quran.types import Surah
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class CustomRangeDialog(QDialog):
    def __init__(self, parent, surahs: List[Surah], saved_range: Optional[Dict[str, int]] = None):
        super().__init__(parent)
        self.surahs = surahs
        self.saved_range = saved_range
        self.setWindowTitle("اختيار السورة والآية")
        self.setMinimumWidth(400)
        self.init_ui()
        self.connect_events()
        self.set_surahs()

    def init_ui(self):
        """Initialize the UI components and layout."""
        main_layout = QVBoxLayout()

        group_from = QGroupBox("من")
        from_layout = QHBoxLayout()
        self.combo_surah_from = QComboBox()
        self.combo_surah_from.setAccessibleName("من سورة")

        self.combo_ayah_from = QComboBox()
        self.combo_ayah_from.setAccessibleName("من آية")

        from_layout.addWidget(QLabel("السورة:"))
        from_layout.addWidget(self.combo_surah_from)
        from_layout.addWidget(QLabel("الآية:"))
        from_layout.addWidget(self.combo_ayah_from)
        group_from.setLayout(from_layout)

        group_to = QGroupBox("إلى")
        to_layout = QHBoxLayout()
        self.combo_surah_to = QComboBox()
        self.combo_surah_to.setAccessibleName("إلى سورة")

        self.combo_ayah_to = QComboBox()
        self.combo_ayah_to.setAccessibleName("إلى آية")

        to_layout.addWidget(QLabel("السورة:"))
        to_layout.addWidget(self.combo_surah_to)
        to_layout.addWidget(QLabel("الآية:"))
        to_layout.addWidget(self.combo_ayah_to)
        group_to.setLayout(to_layout)

        button_layout = QHBoxLayout()
        self.btn_go = QPushButton("الذهاب")
        self.btn_go.setIcon(QIcon.fromTheme("go-next"))

        self.btn_close = QPushButton("إغلاق")
        self.btn_close.setIcon(QIcon.fromTheme("window-close"))

        button_layout.addWidget(self.btn_go)
        button_layout.addWidget(self.btn_close)

        main_layout.addWidget(group_from)
        main_layout.addWidget(group_to)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def connect_events(self):
        """Connect signals to their respective slots."""
        self.combo_surah_from.currentIndexChanged.connect(
            lambda: self.update_ayahs(self.combo_surah_from, self.combo_ayah_from)
        )
        self.combo_surah_to.currentIndexChanged.connect(
            lambda: self.update_ayahs(self.combo_surah_to, self.combo_ayah_to)
        )
        self.btn_go.clicked.connect(self.accept)
        self.btn_close.clicked.connect(self.reject)

    def set_surahs(self):
        """Populate the surah combo boxes with given list of Surah objects."""
        logger.debug("Setting surahs in CustomRangeDialog")
        self.combo_surah_from.clear()
        self.combo_surah_to.clear()

        for surah in self.surahs:
            self.combo_surah_from.addItem(surah.name, surah.number)
            self.combo_surah_to.addItem(surah.name, surah.number)

        if self.surahs:
            self.update_ayahs(self.combo_surah_from, self.combo_ayah_from)
            self.update_ayahs(self.combo_surah_to, self.combo_ayah_to)
        else:
            logger.warning("No surahs available to populate the combo boxes.")

        if self.saved_range:
            logger.debug("Restoring saved range in CustomRangeDialog")
            widgets = (
                (self.combo_surah_from, self.saved_range.get("from_surah")),
                       (self.combo_ayah_from, self.saved_range.get("from_ayah")),
                (self.combo_surah_to, self.saved_range.get("to_surah")),
                (self.combo_ayah_to, self.saved_range.get("to_ayah"))
            )
            for combo, value in widgets:
                if value is not None:
                    index = combo.findData(value)
                    if index != -1:
                        combo.setCurrentIndex(index)
                    else:
                        logger.warning(f"Value {value} not found in {combo.accessibleName()}")
                else:
                    logger.warning(f"Value for {combo.accessibleName()} is None, skipping selection.")

    def update_ayahs(self, combo_surah: QComboBox, combo_ayah: QComboBox):
        """Update the ayah combo box based on the currently selected surah."""
        logger.debug("Updating ayahs for surah selection")
        combo_ayah.clear()
        surah_number = combo_surah.currentData()
        if surah_number is not None and 1 <= surah_number <= len(self.surahs):
            surah = self.surahs[surah_number - 1]
            for ayah_number in range(1, surah.ayah_count + 1):
                combo_ayah.addItem(str(ayah_number), ayah_number)
        else:
            logger.warning("Invalid surah number for updating ayahs.")

    def get_range(self) -> Dict[str, Optional[int]]:
        """
        Return selected range as a dictionary:
        {
            'surah_from': int,
            'ayah_from': int,
            'surah_to': int,
            'ayah_to': int
        }
        Returns None if any data is missing or invalid.
        """
        return {
            "from_surah": self.combo_surah_from.currentData(),
            "from_ayah": self.combo_ayah_from.currentData(),
            "to_surah": self.combo_surah_to.currentData(),
            "to_ayah": self.combo_ayah_to.currentData()
        }

from typing import List, Dict, Optional
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QLabel,
    QGridLayout,
)
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import QTimer

from core_functions.quran.types import Surah
from core_functions.Reciters import RecitersManager
from .models import DownloadMode


class NewDownloadDialog(QDialog):
    """Dialog for downloading Surahs or Ayahs."""

    def __init__(
        self,
        parent,
        mode: DownloadMode,
        surahs: List[Surah],
        reciters_manager: RecitersManager,
    ) -> None:
        super().__init__(parent)
        self.mode = mode
        self.surahs = surahs
        self.reciters_manager = reciters_manager

        # Window settings
        self.setWindowTitle("تنزيل سور" if mode == DownloadMode.SURAH else "تنزيل آيات")

        layout = QVBoxLayout()
        grid = QGridLayout()

        # Reciter selection
        self.reciter_label = QLabel("القارئ:")
        self.reciter_combo = QComboBox()
        self.reciter_combo.setAccessibleName(self.reciter_label.text())
        for reciter in self.reciters_manager.get_reciters():
            self.reciter_combo.addItem(reciter["display_text"], reciter)

        grid.addWidget(self.reciter_label, 0, 0)
        grid.addWidget(self.reciter_combo, 0, 1)

        # From Surah
        self.from_surah_label = QLabel("من سورة:")
        self.from_surah_combo = QComboBox()
        self.from_surah_combo.setAccessibleName(self.from_surah_label.text())
        grid.addWidget(self.from_surah_label, 1, 0)
        grid.addWidget(self.from_surah_combo, 1, 1)

        row = 2

        # From Ayah (only in Ayah mode)
        if self.mode == DownloadMode.AYAH:
            self.from_ayah_label = QLabel("من آية:")
            self.from_ayah_combo = QComboBox()
            self.from_ayah_combo.setAccessibleName(self.from_ayah_label.text())

            grid.addWidget(self.from_ayah_label, row, 0)
            grid.addWidget(self.from_ayah_combo, row, 1)
            row += 1

            self.from_surah_combo.currentIndexChanged.connect(
                lambda _: self._populate_ayahs(
                    self.from_surah_combo, self.from_ayah_combo
                )
            )

        # To Surah
        self.to_surah_label = QLabel("إلى سورة:")
        self.to_surah_combo = QComboBox()
        self.to_surah_combo.setAccessibleName(self.to_surah_label.text())
        grid.addWidget(self.to_surah_label, row, 0)
        grid.addWidget(self.to_surah_combo, row, 1)
        row += 1

        # To Ayah (only in Ayah mode)
        if self.mode == DownloadMode.AYAH:
            self.to_ayah_label = QLabel("إلى آية:")
            self.to_ayah_combo = QComboBox()
            self.to_ayah_combo.setAccessibleName(self.to_ayah_label.text())

            grid.addWidget(self.to_ayah_label, row, 0)
            grid.addWidget(self.to_ayah_combo, row, 1)
            row += 1

            self.to_surah_combo.currentIndexChanged.connect(
                lambda _: self._populate_ayahs(self.to_surah_combo, self.to_ayah_combo)
            )

        layout.addLayout(grid)

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_download = QPushButton("بدء التنزيل")
        btn_download.clicked.connect(self.accept)
        btn_close = QPushButton("إغلاق")
        btn_close.clicked.connect(self.close)
        btn_close.setShortcut(QKeySequence("Ctrl+W"))
        QShortcut(QKeySequence("Ctrl+F4"), self).activated.connect(self.close)

        btn_layout.addWidget(btn_download)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Initial population
        self.reciter_combo.currentIndexChanged.connect(self._on_reciter_changed)
        self._on_reciter_changed()

        # Add delayed focus to fixe accessable issue
        self.setFocus()
        QTimer.singleShot(200, self.reciter_combo.setFocus)

        # for qais to test it
        self.reciter_combo.setAccessibleIdentifier("RECITERCOMBO")

    def _on_reciter_changed(self):
        """Update Surah and Ayah combos when reciter changes."""
        reciter = self.reciter_combo.currentData()
        if not reciter:
            return

        self._populate_surahs(reciter, self.from_surah_combo)
        self._populate_surahs(reciter, self.to_surah_combo)

        if self.mode == DownloadMode.AYAH:
            self._populate_ayahs(self.from_surah_combo, self.from_ayah_combo)
            self._populate_ayahs(self.to_surah_combo, self.to_ayah_combo)

    def _populate_surahs(self, reciter, combo: QComboBox):
        """Fill Surah combo with only available Surahs for the selected reciter."""
        combo.clear()
        available = (
            set(reciter.get("available_suras", []))
            if self.mode == DownloadMode.SURAH
            else set([surah.number for surah in self.surahs])
        )

        for sura in self.surahs:
            if sura.number in available:
                combo.addItem(sura.name, sura)

    def _populate_ayahs(self, surah_combo: QComboBox, ayah_combo: QComboBox):
        """Fill Ayah combo based on selected Surah."""
        sura: Surah = surah_combo.currentData()
        if not sura:
            return

        ayah_combo.clear()
        for i in range(sura.ayah_count):
            ayah_number = sura.first_ayah_number + i
            ayah_combo.addItem(str(i + 1), ayah_number)

    def get_selection(self) -> dict:
        """Return user selections as a dictionary with auto-correction."""
        reciter = self.reciter_combo.currentData()
        from_surah: Surah = self.from_surah_combo.currentData()
        to_surah: Surah = self.to_surah_combo.currentData()

        # Auto-correct surah range
        if from_surah.number > to_surah.number:
            to_surah = from_surah

        data = {
            "reciter": reciter,
            "from_surah": from_surah,
            "to_surah": to_surah,
        }

        if self.mode == DownloadMode.AYAH:
            from_ayah = self.from_ayah_combo.currentData()
            to_ayah = self.to_ayah_combo.currentData()

            # Auto-correct ayah range (only if same surah)
            if from_surah.number == to_surah.number and from_ayah > to_ayah:
                to_ayah = from_ayah

            data["from_ayah"] = from_ayah
            data["to_ayah"] = to_ayah

        return data

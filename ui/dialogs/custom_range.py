from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QGroupBox,
    QLabel,
    QStackedWidget,
    QWidget,
)
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtCore import Qt
from typing import List, Dict, Optional, Any
from core_functions.quran.types import Surah
from core_functions.quran.quran_manager import QuranManager
from ui.widgets.spin_box import SpinBox
from utils.const import Globals
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _play_sound(effect_name: str):
    if hasattr(Globals, "effects_manager") and Globals.effects_manager:
        try:
            Globals.effects_manager.play(effect_name)
        except Exception:
            pass


class CustomRangeDialog(QDialog):
    def __init__(
        self, parent, surahs: List[Surah], saved_range: Optional[Dict[str, Any]] = None
    ):
        super().__init__(parent)
        logger.debug("Initializing CustomRangeDialog...")
        self.surahs = surahs
        self.saved_range = saved_range or {}
        self.setWindowTitle("العرض المخصص")
        self.setMinimumWidth(420)
        self.resize(460, 260)

        self.init_ui()
        self.connect_events()
        self.set_surahs()
        self.restore_saved_range()

        _play_sound("open")
        logger.info("CustomRangeDialog opened successfully.")

    def init_ui(self):
        """Initialize the UI components and layout."""
        main_layout = QVBoxLayout(self)

        # 1. Range type selection combo box
        type_layout = QHBoxLayout()
        self.label_range_type = QLabel("تحديد النطاق بحسب:")
        self.label_range_type.setAccessibleName("تحديد النطاق بحسب")
        self.combo_range_type = QComboBox(self)
        self.combo_range_type.setAccessibleName("تحديد النطاق بحسب")

        # Range types in order: surah, page, juz, hizb, quarter
        self.combo_range_type.addItem("السور والآيات", "surah")
        self.combo_range_type.addItem("الصفحات", "page")
        self.combo_range_type.addItem("الأجزاء", "juz")
        self.combo_range_type.addItem("الأحزاب", "hizb")
        self.combo_range_type.addItem("الأرباع", "quarter")

        type_layout.addWidget(self.label_range_type)
        type_layout.addWidget(self.combo_range_type)
        main_layout.addLayout(type_layout)

        # 2. Group 'From' (من)
        self.group_from = QGroupBox("من")
        group_from_layout = QVBoxLayout(self.group_from)
        self.stack_from = QStackedWidget(self.group_from)

        # Page 0: Surah & Ayah
        page_surah_from = QWidget()
        layout_surah_from = QHBoxLayout(page_surah_from)
        layout_surah_from.setContentsMargins(0, 0, 0, 0)
        self.combo_surah_from = QComboBox(page_surah_from)
        self.combo_surah_from.setAccessibleName("من سورة")
        self.combo_ayah_from = QComboBox(page_surah_from)
        self.combo_ayah_from.setAccessibleName("من آية")
        layout_surah_from.addWidget(QLabel("السورة:"))
        layout_surah_from.addWidget(self.combo_surah_from)
        layout_surah_from.addWidget(QLabel("الآية:"))
        layout_surah_from.addWidget(self.combo_ayah_from)
        self.stack_from.addWidget(page_surah_from)

        # Page 1: Pages
        page_page_from = QWidget()
        layout_page_from = QHBoxLayout(page_page_from)
        layout_page_from.setContentsMargins(0, 0, 0, 0)
        self.spin_page_from = SpinBox(page_page_from)
        self.spin_page_from.setRange(1, QuranManager.MAX_PAGE)
        self.spin_page_from.setValue(1)
        self.spin_page_from.setAccessibleName("من صفحة")
        layout_page_from.addWidget(QLabel("الصفحة:"))
        layout_page_from.addWidget(self.spin_page_from)
        self.stack_from.addWidget(page_page_from)

        # Page 2: Juz
        page_juz_from = QWidget()
        layout_juz_from = QHBoxLayout(page_juz_from)
        layout_juz_from.setContentsMargins(0, 0, 0, 0)
        self.spin_juz_from = SpinBox(page_juz_from)
        self.spin_juz_from.setRange(1, QuranManager.MAX_JUZ)
        self.spin_juz_from.setValue(1)
        self.spin_juz_from.setAccessibleName("من جزء")
        layout_juz_from.addWidget(QLabel("الجزء:"))
        layout_juz_from.addWidget(self.spin_juz_from)
        self.stack_from.addWidget(page_juz_from)

        # Page 3: Hizb
        page_hizb_from = QWidget()
        layout_hizb_from = QHBoxLayout(page_hizb_from)
        layout_hizb_from.setContentsMargins(0, 0, 0, 0)
        self.spin_hizb_from = SpinBox(page_hizb_from)
        self.spin_hizb_from.setRange(1, QuranManager.MAX_HIZB)
        self.spin_hizb_from.setValue(1)
        self.spin_hizb_from.setAccessibleName("من حزب")
        layout_hizb_from.addWidget(QLabel("الحزب:"))
        layout_hizb_from.addWidget(self.spin_hizb_from)
        self.stack_from.addWidget(page_hizb_from)

        # Page 4: Quarter
        page_quarter_from = QWidget()
        layout_quarter_from = QHBoxLayout(page_quarter_from)
        layout_quarter_from.setContentsMargins(0, 0, 0, 0)
        self.spin_quarter_from = SpinBox(page_quarter_from)
        self.spin_quarter_from.setRange(1, QuranManager.MAX_QUARTER)
        self.spin_quarter_from.setValue(1)
        self.spin_quarter_from.setAccessibleName("من ربع")
        layout_quarter_from.addWidget(QLabel("الربع:"))
        layout_quarter_from.addWidget(self.spin_quarter_from)
        self.stack_from.addWidget(page_quarter_from)

        group_from_layout.addWidget(self.stack_from)
        main_layout.addWidget(self.group_from)

        # 3. Group 'To' (إلى)
        self.group_to = QGroupBox("إلى")
        group_to_layout = QVBoxLayout(self.group_to)
        self.stack_to = QStackedWidget(self.group_to)

        # Page 0: Surah & Ayah
        page_surah_to = QWidget()
        layout_surah_to = QHBoxLayout(page_surah_to)
        layout_surah_to.setContentsMargins(0, 0, 0, 0)
        self.combo_surah_to = QComboBox(page_surah_to)
        self.combo_surah_to.setAccessibleName("إلى سورة")
        self.combo_ayah_to = QComboBox(page_surah_to)
        self.combo_ayah_to.setAccessibleName("إلى آية")
        layout_surah_to.addWidget(QLabel("السورة:"))
        layout_surah_to.addWidget(self.combo_surah_to)
        layout_surah_to.addWidget(QLabel("الآية:"))
        layout_surah_to.addWidget(self.combo_ayah_to)
        self.stack_to.addWidget(page_surah_to)

        # Page 1: Pages
        page_page_to = QWidget()
        layout_page_to = QHBoxLayout(page_page_to)
        layout_page_to.setContentsMargins(0, 0, 0, 0)
        self.spin_page_to = SpinBox(page_page_to)
        self.spin_page_to.setRange(1, QuranManager.MAX_PAGE)
        self.spin_page_to.setValue(QuranManager.MAX_PAGE)
        self.spin_page_to.setAccessibleName("إلى صفحة")
        layout_page_to.addWidget(QLabel("الصفحة:"))
        layout_page_to.addWidget(self.spin_page_to)
        self.stack_to.addWidget(page_page_to)

        # Page 2: Juz
        page_juz_to = QWidget()
        layout_juz_to = QHBoxLayout(page_juz_to)
        layout_juz_to.setContentsMargins(0, 0, 0, 0)
        self.spin_juz_to = SpinBox(page_juz_to)
        self.spin_juz_to.setRange(1, QuranManager.MAX_JUZ)
        self.spin_juz_to.setValue(QuranManager.MAX_JUZ)
        self.spin_juz_to.setAccessibleName("إلى جزء")
        layout_juz_to.addWidget(QLabel("الجزء:"))
        layout_juz_to.addWidget(self.spin_juz_to)
        self.stack_to.addWidget(page_juz_to)

        # Page 3: Hizb
        page_hizb_to = QWidget()
        layout_hizb_to = QHBoxLayout(page_hizb_to)
        layout_hizb_to.setContentsMargins(0, 0, 0, 0)
        self.spin_hizb_to = SpinBox(page_hizb_to)
        self.spin_hizb_to.setRange(1, QuranManager.MAX_HIZB)
        self.spin_hizb_to.setValue(QuranManager.MAX_HIZB)
        self.spin_hizb_to.setAccessibleName("إلى حزب")
        layout_hizb_to.addWidget(QLabel("الحزب:"))
        layout_hizb_to.addWidget(self.spin_hizb_to)
        self.stack_to.addWidget(page_hizb_to)

        # Page 4: Quarter
        page_quarter_to = QWidget()
        layout_quarter_to = QHBoxLayout(page_quarter_to)
        layout_quarter_to.setContentsMargins(0, 0, 0, 0)
        self.spin_quarter_to = SpinBox(page_quarter_to)
        self.spin_quarter_to.setRange(1, QuranManager.MAX_QUARTER)
        self.spin_quarter_to.setValue(QuranManager.MAX_QUARTER)
        self.spin_quarter_to.setAccessibleName("إلى ربع")
        layout_quarter_to.addWidget(QLabel("الربع:"))
        layout_quarter_to.addWidget(self.spin_quarter_to)
        self.stack_to.addWidget(page_quarter_to)

        group_to_layout.addWidget(self.stack_to)
        main_layout.addWidget(self.group_to)

        # 4. Buttons
        button_layout = QHBoxLayout()
        self.btn_go = QPushButton("الذهاب")
        self.btn_go.setIcon(QIcon.fromTheme("go-next"))
        self.btn_go.setAccessibleName("الذهاب إلى النطاق المحدد")
        self.btn_go.setDefault(True)

        self.btn_close = QPushButton("إغلاق")
        self.btn_close.setIcon(QIcon.fromTheme("window-close"))
        self.btn_close.setAccessibleName("إغلاق نافذة العرض المخصص")
        self.btn_close.setShortcut("Ctrl+W")

        button_layout.addWidget(self.btn_go)
        button_layout.addWidget(self.btn_close)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def connect_events(self):
        """Connect signals to their respective slots."""
        self.combo_range_type.currentIndexChanged.connect(self._on_range_type_changed)

        self.combo_surah_from.currentIndexChanged.connect(
            lambda: self.update_ayahs(self.combo_surah_from, self.combo_ayah_from)
        )
        self.combo_surah_to.currentIndexChanged.connect(
            lambda: self.update_ayahs(self.combo_surah_to, self.combo_ayah_to)
        )

        self.btn_go.clicked.connect(self._on_submit)
        self.btn_close.clicked.connect(self.reject)
        QShortcut(QKeySequence("Ctrl+F4"), self).activated.connect(self.reject)

    def _on_range_type_changed(self, index: int):
        """Handle switching between range types (surah, page, juz, hizb, quarter)."""
        logger.debug(f"Range type index changed to: {index} ({self.combo_range_type.currentData()})")
        self.stack_from.setCurrentIndex(index)
        self.stack_to.setCurrentIndex(index)

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

    def restore_saved_range(self):
        """Restore previous range configuration if available in saved_range dictionary."""
        if not self.saved_range:
            return

        logger.debug(f"Restoring saved range in CustomRangeDialog: {self.saved_range}")

        # 1. Restore range_type
        saved_type = self.saved_range.get("range_type", "surah")
        type_idx = self.combo_range_type.findData(saved_type)
        if type_idx != -1:
            self.combo_range_type.setCurrentIndex(type_idx)

        # 2. Restore surah & ayah
        from_surah = self.saved_range.get("from_surah")
        if from_surah is not None:
            idx = self.combo_surah_from.findData(from_surah)
            if idx != -1:
                self.combo_surah_from.setCurrentIndex(idx)

        from_ayah = self.saved_range.get("from_ayah")
        if from_ayah is not None:
            idx = self.combo_ayah_from.findData(from_ayah)
            if idx != -1:
                self.combo_ayah_from.setCurrentIndex(idx)

        to_surah = self.saved_range.get("to_surah")
        if to_surah is not None:
            idx = self.combo_surah_to.findData(to_surah)
            if idx != -1:
                self.combo_surah_to.setCurrentIndex(idx)

        to_ayah = self.saved_range.get("to_ayah")
        if to_ayah is not None:
            idx = self.combo_ayah_to.findData(to_ayah)
            if idx != -1:
                self.combo_ayah_to.setCurrentIndex(idx)

        # 3. Restore page
        if "from_page" in self.saved_range and self.saved_range["from_page"] is not None:
            self.spin_page_from.setValue(int(self.saved_range["from_page"]))
        if "to_page" in self.saved_range and self.saved_range["to_page"] is not None:
            self.spin_page_to.setValue(int(self.saved_range["to_page"]))

        # 4. Restore juz
        if "from_juz" in self.saved_range and self.saved_range["from_juz"] is not None:
            self.spin_juz_from.setValue(int(self.saved_range["from_juz"]))
        if "to_juz" in self.saved_range and self.saved_range["to_juz"] is not None:
            self.spin_juz_to.setValue(int(self.saved_range["to_juz"]))

        # 5. Restore hizb
        if "from_hizb" in self.saved_range and self.saved_range["from_hizb"] is not None:
            self.spin_hizb_from.setValue(int(self.saved_range["from_hizb"]))
        if "to_hizb" in self.saved_range and self.saved_range["to_hizb"] is not None:
            self.spin_hizb_to.setValue(int(self.saved_range["to_hizb"]))

        # 6. Restore quarter
        if "from_quarter" in self.saved_range and self.saved_range["from_quarter"] is not None:
            self.spin_quarter_from.setValue(int(self.saved_range["from_quarter"]))
        if "to_quarter" in self.saved_range and self.saved_range["to_quarter"] is not None:
            self.spin_quarter_to.setValue(int(self.saved_range["to_quarter"]))

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

    def get_range(self) -> Dict[str, Any]:
        """
        Return the complete selected range configuration as a dictionary:
        {
            'range_type': str ('surah', 'page', 'juz', 'hizb', 'quarter'),
            'from_surah': int,
            'from_ayah': int,
            'to_surah': int,
            'to_ayah': int,
            'from_page': int,
            'to_page': int,
            'from_juz': int,
            'to_juz': int,
            'from_hizb': int,
            'to_hizb': int,
            'from_quarter': int,
            'to_quarter': int
        }
        """
        range_type = self.combo_range_type.currentData() or "surah"
        return {
            "range_type": range_type,
            "from_surah": self.combo_surah_from.currentData() or 1,
            "from_ayah": self.combo_ayah_from.currentData() or 1,
            "to_surah": self.combo_surah_to.currentData() or 1,
            "to_ayah": self.combo_ayah_to.currentData() or 1,
            "from_page": self.spin_page_from.value(),
            "to_page": self.spin_page_to.value(),
            "from_juz": self.spin_juz_from.value(),
            "to_juz": self.spin_juz_to.value(),
            "from_hizb": self.spin_hizb_from.value(),
            "to_hizb": self.spin_hizb_to.value(),
            "from_quarter": self.spin_quarter_from.value(),
            "to_quarter": self.spin_quarter_to.value(),
        }

    def _on_submit(self):
        logger.info(f"Custom range confirmed: {self.get_range()}")
        _play_sound("change")
        self.accept()

    def reject(self):
        logger.debug("CustomRangeDialog cancelled by user.")
        _play_sound("clos")
        super().reject()
        self.deleteLater()

    def closeEvent(self, event):
        logger.debug("CustomRangeDialog closed.")
        return super().closeEvent(event)

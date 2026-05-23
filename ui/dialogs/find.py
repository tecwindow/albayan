import os
import json
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QMenu,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QCheckBox,
QListWidget,
QListWidgetItem,
QMessageBox,
)
from PyQt6.QtCore import Qt, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QKeySequence,  QRegularExpressionValidator, QShortcut, QAction
from core_functions.search import SearchCriteria, QuranSearchManager
from core_functions.quran.quran_manager import QuranManager
from ui.widgets.search_box import ArabicSearchBox
from utils.settings import Config
from utils.universal_speech import UniversalSpeech
from utils.const import Globals
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class SearchDialog(QDialog):
    search_submitted = pyqtSignal(str)
    
    def __init__(self, parent, title, default_search_phrase: str = ""):
        super().__init__(parent)
        self.parent = parent
        self.default_search_phrase = default_search_phrase
        self.setWindowTitle(title)
        self.resize(500, 400)
        self.search_manager = QuranSearchManager()
        self.reset_search_options()
        self.criteria = None
        self.initUI()
        logger.debug(f"SearchDialog initialized with title: {title}.")

    def initUI(self):
        self.search_label = QLabel('اكتب ما تريد البحث عنه:')
        self.search_box = ArabicSearchBox(self)
        self.search_box.setText(self.default_search_phrase)
        regex = QRegularExpression("[\u0621-\u0652\u0670\u0671[:space:]]+")  # Arabic letters, hamzas, diacritics, and spaces.
        validator = QRegularExpressionValidator(regex)
        self.search_box.setValidator(validator)
        self.search_box.inputRejected.connect(QApplication.beep)
        self.search_box.textChanged.connect(self.OnEdit)
        self.search_box.setAccessibleName(self.search_label.text())
        self.advanced_search_checkbox = QCheckBox('البحث المتقدم')
        self.advanced_search_checkbox.toggled.connect(self.show_advanced_options)
        self.search_button = QPushButton('بحث')
        self.search_button.setEnabled(False)
        self.cancel_button = QPushButton('إلغاء')
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))

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
        self.search_from_combobox.setAccessibleName(self.search_from_label.text())
        self.search_to_label = QLabel('إلى:')
        self.search_to_combobox = QComboBox()
        self.search_to_combobox.setAccessibleName(self.search_to_label.text())
        self.ignore_diacritics_checkbox = QCheckBox('تجاهل التشكيل')
        self.ignore_diacritics_checkbox.setChecked(Config.search.ignore_tashkeel)
        self.ignore_hamza_checkbox = QCheckBox('تجاهل الهمزات')
        self.ignore_hamza_checkbox.setChecked(Config.search.ignore_hamza)
        self.match_whole_word_checkbox = QCheckBox('تطابق الكلمة بأكملها')
        self.match_whole_word_checkbox.setChecked(Config.search.match_whole_word)

        self.search_type_layout = QVBoxLayout()
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
        self.search_options_layout.addWidget(self.match_whole_word_checkbox)

        self.advanced_search_groupbox.setLayout(self.search_options_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.search_label)
        main_layout.addWidget(self.search_box)
        main_layout.addWidget(self.advanced_search_checkbox)
        main_layout.addWidget(self.advanced_search_groupbox)
        main_layout.addWidget(self.search_button)
        main_layout.addWidget(self.cancel_button)

        self.setLayout(main_layout)

        self.sura = [surah.name for surah in self.parent.quran_manager.get_surahs()]
        self.pages = ["{}".format(i) for i in range(1, QuranManager.MAX_PAGE + 1)]
        self.quarters = ["{}".format(i) for i in range(1, QuranManager.MAX_QUARTER + 1)]
        self.jus = ["{}".format(i) for i in range(1, QuranManager.MAX_JUZ + 1)]
        self.hizb = ["{}".format(i) for i in range(1, QuranManager.MAX_HIZB + 1)]

        self.search_button.clicked.connect(self.on_submit)
        self.cancel_button.clicked.connect(self.reject)
        self.search_type_radio_page.toggled.connect(self.on_radio_toggled)
        self.search_type_radio_sura.toggled.connect(self.on_radio_toggled)
        self.search_type_radio_juz.toggled.connect(self.on_radio_toggled)
        self.search_type_radio_hizb.toggled.connect(self.on_radio_toggled)
        self.search_type_radio_quarter.toggled.connect(self.on_radio_toggled)
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)

        self.on_radio_toggled()
        self.OnEdit()

    def OnEdit(self):
        self.search_button.setEnabled(bool(self.search_box.text()))
        logger.debug(f"User edited search box: {self.search_box.text()}.")

    def show_advanced_options(self):
        enabled = self.advanced_search_checkbox.isChecked()
        self.advanced_search_groupbox.setEnabled(enabled)
        logger.debug(f"Advanced search {'enabled' if enabled else 'disabled'}.")
        if not enabled:
            self.reset_search_options()
            
    def on_submit(self):
        logger.debug("Search button clicked.")
        self.set_options_search()
        search_text = self.search_box. text()
        self.search_submitted.emit(search_text)
        logger.debug(f"Searching for: {search_text}")
        search_result = self.search_manager.search(search_text)
        if not search_result:
            logger.warning(f"No results found for '{search_text}'.")
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("لا توجد نتائج")
            msg_box.setText("لا توجد نتائج متاحة لبحثك.")

            ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
            msg_box.exec()

            return
        logger.info(f"Search successful. {len(search_result)} results found.")
        result_dialog = SearchResultsDialog(self, search_result)
        if result_dialog.exec():
            selected_result = result_dialog.list_widget.currentRow()
            selected_result = search_result[selected_result]
            ayah_number = selected_result["number"]
            self.parent.quran_manager.navigation_mode = self.parent.get_valid_navigation_mode()
            ayah_result = self.parent.quran_manager.get_by_ayah_number(ayah_number)
            logger.info(f"User selected result {selected_result}")
            self.parent.quran_view.setText(ayah_result)
            self.parent.set_focus_to_ayah(ayah_number)
            self.parent.quran_view.setFocus()
            logger.info(f"Moved to Ayah: {selected_result['numberInSurah']} in Surah: {selected_result['sura_name']}")
            self.accept()
            self.deleteLater()

    def on_radio_toggled(self):
        logger.debug(f"Radio button toggled. Selected: {self.sender().text()}")
        
        #clear
        self.search_from_combobox.clear()
        self.search_to_combobox.clear()

        if self.search_type_radio_page.isChecked():    
            self.criteria = SearchCriteria.page
            self.search_from_combobox.addItems([str(i) for i in range(1, 605)])
            self.search_to_combobox.addItems([str(i) for i in range(1, 605)])
        elif self.search_type_radio_sura.isChecked():
            self.criteria = SearchCriteria.sura
            self.search_from_combobox.addItems(self.sura)
            self.search_to_combobox.addItems(self.sura)
        elif self.search_type_radio_juz.isChecked():
            self.criteria = SearchCriteria.juz
            self.search_from_combobox.addItems(self.jus)
            self.search_to_combobox.addItems(self.jus)
        elif self.search_type_radio_hizb.isChecked():
            self.criteria = SearchCriteria.hizb
            self.search_from_combobox.addItems(self.hizb)
            self.search_to_combobox.addItems(self.hizb)
        elif self.search_type_radio_quarter.isChecked():
            self.criteria = SearchCriteria.quarter
            self.search_from_combobox.addItems(self.quarters)
            self.search_to_combobox.addItems(self.quarters)
        self.search_to_combobox.setCurrentIndex(self.search_to_combobox.count() - 1)
        logger.debug(f"Search type changed to: {self.criteria}.")

    def set_options_search(self):
        logger.debug("Setting search options.")
        if not self.advanced_search_checkbox.isChecked():
            logger.debug("Advanced search is not enabled, skipping setting options.")
            return
        
        search_from = self.search_from_combobox.currentIndex() + 1
        search_to = self.search_to_combobox.currentIndex() + 1
        self.search_manager.set(
            no_tashkil=self.ignore_diacritics_checkbox.isChecked(),
            no_hamza=self.ignore_hamza_checkbox.isChecked(),
            match_whole_word=self.match_whole_word_checkbox.isChecked(),
            criteria=self.criteria,
            _from=search_from,
_to=search_to
        )
        logger.debug(f"Search options set: from {search_from} to {search_to}, criteria {self.criteria}, no_tashkil {self.ignore_diacritics_checkbox.isChecked()}, no_hamza {self.ignore_hamza_checkbox.isChecked()}, match_whole_word {self.match_whole_word_checkbox.isChecked()}.")

    def reset_search_options(self):
            self.search_manager.set(
                no_tashkil=Config.search.ignore_tashkeel,
                                   no_hamza=Config.search.ignore_hamza,
                                   match_whole_word=Config.search.match_whole_word,
            )

    def closeEvent(self, a0):
        logger.debug("SearchDialog closed.")
        return super().closeEvent(a0)
    
    
class SearchResultsDialog(QDialog):
    def __init__(self, parent=None, search_result=[]):
        super().__init__(parent)

        self.search_result = search_result

        self.setWindowTitle("نتائج البحث")

        logger.debug(
            f"SearchResultsDialog opened with {len(search_result)} results."
        )

        self.total_label = QLabel(
            "عدد النتائج: {}.".format(len(search_result))
        )

        self.label = QLabel("النتائج:")

        self.list_widget = QListWidget(self)

        self.list_widget.setAccessibleDescription(
            self.label.text()
        )

        self.list_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.list_widget.customContextMenuRequested.connect(
            self.show_context_menu
        )

        for i, row in enumerate(search_result):

            item = QListWidgetItem(
                self.format_result(row)
            )

            item.setData(
                Qt.ItemDataRole.AccessibleDescriptionRole,
                f"{i+1} من {len(search_result)}"
            )

            item.setToolTip(row["text"])

            self.list_widget.addItem(item)

        self.go_to_button = QPushButton("الذهاب للنتيجة")

        self.go_to_button.clicked.connect(
            self.go_to_current_result
        )

        self.cancel_button = QPushButton("إلغاء")

        self.cancel_button.setShortcut(
            QKeySequence("Ctrl+W")
        )

        self.cancel_button.clicked.connect(self.reject)

        close_shortcut = QShortcut(
            QKeySequence("Ctrl+F4"),
            self
        )

        close_shortcut.activated.connect(self.reject)

        copy_shortcut = QShortcut(
            QKeySequence("Shift+C"),
            self
        )

        copy_shortcut.activated.connect(
            self.copy_current_result
        )

        layout = QVBoxLayout()

        layout.addWidget(self.total_label)

        layout.addWidget(self.label)

        layout.addWidget(self.list_widget)

        layout.addWidget(self.go_to_button)

        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        self.list_widget.setCurrentRow(0)

        logger.debug(
            "SearchResultsDialog initialized successfully."
        )

    def format_result(self, row: dict) -> str:

        text = row["text"]

        words = text.split()

        text = " ".join(words[:5])

        text += "..." if len(words) > 5 else ""

        return "{} | الآية {} من {}".format(
            text,
            row["numberInSurah"],
            row["sura_name"]
        )

    def get_current_result(self):

        current_row = self.list_widget.currentRow()

        if current_row < 0:
            return None

        if current_row >= len(self.search_result):
            return None

        return self.search_result[current_row]

    def read_current_result(self):

        result = self.get_current_result()

        if not result:
            return

        UniversalSpeech.say(result["text"], interrupt=False, force=True)

        logger.debug(
            f"Reading result: "
            f"{result['numberInSurah']} "
            f"from {result['sura_name']}"
        )

    def copy_current_result(self):

        result = self.get_current_result()

        if not result:
            return

        text = result["text"]

        sura_name = result["sura_name"]

        ayah_number = result["numberInSurah"]

        final_text = (
            f"الآية {ayah_number} "
            f"من {sura_name}:\n{text}"
        )

        QApplication.clipboard().setText(
            final_text
        )

        UniversalSpeech.say(f"تم نسخ الآية {ayah_number} من {sura_name}.", interrupt=False, force=True)

        Globals.effects_manager.play("copy")

        logger.debug(
            f"Copied search result: "
            f"Ayah {ayah_number} "
            f"from {sura_name}"
        )

    def go_to_current_result(self):

        result = self.get_current_result()

        if not result:
            return

        Globals.effects_manager.play("move")

        self.accept()

    def show_context_menu(self, position):

        logger.debug(
            "User opened search result context menu."
        )

        current_item = self.list_widget.currentItem()

        if not current_item:
            return

        menu = QMenu(self)

        actions = {}

        go_action = QAction(
            "الذهاب للنتيجة",
            self
        )

        go_action.triggered.connect(
            self.go_to_current_result
        )

        actions["go"] = go_action

        menu.addAction(go_action)

        copy_action = QAction(
            "نسخ النتيجة",
            self
        )

        copy_action.triggered.connect(
            self.copy_current_result
        )

        actions["copy"] = copy_action

        menu.addAction(copy_action)

        read_action = QAction(
            "قراءة النتيجة",
            self
        )

        read_action.triggered.connect(
            self.read_current_result
        )

        actions["read"] = read_action

        menu.addAction(read_action)




        menu.setAccessibleName(
            "خيارات النتيجة"
        )

        menu.setFocus()

        logger.debug(
            "Search result context menu displayed."
        )

        menu.exec(
            self.list_widget.viewport().mapToGlobal(
                position
            )
        )


    def keyPressEvent(
        self,
        event: QKeyEvent | None
    ) -> None:

        if (
            event.key() == Qt.Key.Key_I
            and event.modifiers()
            == Qt.KeyboardModifier.ControlModifier
        ):

            UniversalSpeech.say(
                self.total_label.text(),
                force=True
            )

            logger.debug(
                "Ctrl+I pressed: "
                "Announcing total results count."
            )

        elif (
            event.key() == Qt.Key.Key_R
            and event.modifiers()
            == Qt.KeyboardModifier.ControlModifier
        ):

            self.read_current_result()

            logger.debug(
                "Ctrl+R pressed: "
                "Reading current result."
            )

        return super().keyPressEvent(event)

    def reject(self):

        self.deleteLater()

    def closeEvent(self, a0):

        logger.debug(
            "SearchResultsDialog closed."
        )

        return super().closeEvent(a0)
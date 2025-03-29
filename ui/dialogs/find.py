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
    QCheckBox,
QListWidget,
QListWidgetItem,
QMessageBox,
)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QKeyEvent, QKeySequence,  QRegularExpressionValidator, QShortcut
from core_functions.search import SearchCriteria, QuranSearchManager
from utils.settings import Config
from utils.universal_speech import UniversalSpeech
from utils.const import Globals




class SearchDialog(QDialog):
    search_phrase = ""

    @classmethod
    def set_search_phrase(cls, search_phrase: str) -> None:
        cls.search_phrase = search_phrase

    def __init__(self, parent, title):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(title)
        self.resize(500, 400)
        self.search_manager = QuranSearchManager()
        self.criteria = None

        self.initUI()

    def initUI(self):
        self.search_label = QLabel('اكتب ما تريد البحث عنه:')
        self.search_box = QLineEdit(self)
        self.search_box.setText(self.search_phrase)
        regex = QRegularExpression("[\u0621-\u0652\u0670\u0671[:space:]]+")  # Arabic letters, hamzas, diacritics, and spaces.
        validator = QRegularExpressionValidator(regex)
        self.search_box.setValidator(validator)
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

        self.sura = []
        with open(os.path.join("database", "Surahs.Json"), encoding="UTF-8") as f:
            self.sura = json.load(f)["surahs"]
        self.pages = ["{}".format(i) for i in range(1, 605)]
        self.quarters = ["{}".format(i) for i in range(1, 241)]
        self.jus = ["{}".format(i) for i in range(1, 31)]
        self.hizb = ["{}".format(i) for i in range(1, 61)]

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

    def show_advanced_options(self):
        self.advanced_search_groupbox.setEnabled(self.advanced_search_checkbox.isChecked())

    def on_submit(self):
        self.set_options_search()
        search_text = self.search_box. text()
        self.set_search_phrase(search_text)
        search_result = self.search_manager.search(search_text)
        if not search_result:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("لا توجد نتائج")
            msg_box.setText("لا توجد نتائج متاحة لبحثك.")

            ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
            msg_box.exec()

            return
        
        result_dialog = SearchResultsDialog(self, search_result)
        if result_dialog.exec():
            selected_result = result_dialog.list_widget.currentRow()
            ayah_number = search_result[selected_result]["number"]
            ayah_result = self.parent.quran.get_by_ayah_number(ayah_number)
            self.parent.quran_view.setText(ayah_result["full_text"])
            self.parent.set_focus_to_ayah(ayah_number)
            self.parent.quran_view.setFocus()
            self.accept()
            self.deleteLater()


    def on_radio_toggled(self):

        #clear
        self.search_from_combobox.clear()
        self.search_to_combobox.clear()

        if self.search_type_radio_page.isChecked():    
            self.criteria = SearchCriteria.page
            self.search_from_combobox.addItems([str(i) for i in range(1, 605)])
            self.search_to_combobox.addItems([str(i) for i in range(1, 605)])
        elif self.search_type_radio_sura.isChecked():
            self.criteria = SearchCriteria.sura
            self.search_from_combobox.addItems([sura["name"] for sura in self.sura])
            self.search_to_combobox.addItems([sura["name"] for sura in self.sura])
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

    def set_options_search(self):
        
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


class SearchResultsDialog(QDialog):
    def __init__(self, parent=None, search_result=[]):
        super().__init__(parent)
        self.search_result = search_result
        self.setWindowTitle("نتائج البحث")

        self.total_label = QLabel("عدد النتائج: {}.".format(len(search_result)))
        self.label = QLabel("النتائج:")
        self.list_widget = QListWidget(self)
        self.list_widget.setAccessibleDescription(self.label.text())

        for i, row in enumerate(search_result):
            item = QListWidgetItem(self.format_result(row))
            item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"{i+1} من {len(search_result)}")
            item.setToolTip(row["text"])
            self.list_widget.addItem(item)
            
        self.go_to_button = QPushButton("الذهاب للنتيجة")
        self.go_to_button.clicked.connect(self.accept)
        self.go_to_button.clicked.connect(lambda: Globals.effects_manager.play("move"))
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))
        self.cancel_button.clicked.connect(self.reject)
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)


        layout = QVBoxLayout()
        layout.addWidget(self.total_label)
        layout.addWidget(self.label)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.go_to_button)
        layout.addWidget(self.cancel_button)
        
        self.setLayout(layout)
        self.list_widget.setCurrentRow(0)


    def format_result(self, row:dict) -> str:
        text = row["text"]
        # take first 5 words from text
        words = text.split()
        text = " ".join(words[:5])
        text += "..." if len(words) > 5 else ""

        return "{} | الآية {} من {}".format(text, row["numberInSurah"], row["sura_name"])

    def keyPressEvent(self, event: QKeyEvent | None) -> None:

        if event.key() == Qt.Key.Key_I and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            UniversalSpeech.say(self.total_label.text())
        elif event.key() == Qt.Key.Key_R and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            current_row = self.list_widget.currentRow()
            text = self.search_result[current_row]["text"]
            UniversalSpeech.say(text)

        return super().keyPressEvent(event)

    def reject(self):
        self.deleteLater()
        
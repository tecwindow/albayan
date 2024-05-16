import os
import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout, 
    QLabel, 
    QPushButton, 
    QMenu, 
    QHBoxLayout, 
    QMainWindow, 
    QMessageBox,
    QComboBox,
    QApplication
)
from PyQt6.QtGui import QIcon, QAction
from core_functions.quran_class import quran_mgr
from core_functions.tafaseer import Category
from core_functions.info import E3rab, TanzilAyah
from ui.dialogs.quick_access import QuickAccess
from ui.dialogs.find import SearchDialog
from ui.widgets.button import EnterButton
from ui.widgets.menu_bar import MenuBar
from ui.widgets.qText_edit import QuranViewer
from ui.dialogs.tafaseer_Dialog import TafaseerDialog
from ui.dialogs.info_dialog import InfoDialog


class QuranInterface(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)
        self.quran = quran_mgr()
        self.quran.load_quran(os.path.join("database", "quran", "quran.DB"))
        self.quran.aya_to_line = True

        menu_bar = MenuBar(self)
        self.setMenuBar(menu_bar)
        self.create_widgets()
        self.create_layout()
        
    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.quran_title = QLabel()
        font = self.quran_title.font()
        font.setPointSize(16)
        font.setBold(True)
        self.quran_title.setFont(font)

        self.quran_view = QuranViewer(self)
        self.quran_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.quran_view.customContextMenuRequested.connect(self.onContextMenu)
        self.quran_view.setText(self.quran.get_page(1))
        self.set_text_ctrl_label()

        self.next_to = EnterButton("التالي")
        self.next_to.setEnabled(self.quran.current_pos != self.quran.max_pos)
        self.next_to.clicked.connect(self.OnNext)
        
        self.back_to = EnterButton("السابق")
        self.back_to.setEnabled(self.quran.current_pos != 1)
        self.back_to.clicked.connect(self.OnBack)

        self.interpretation_verse = EnterButton("تفسير الآية")
        self.interpretation_verse.setEnabled(False)
        self.interpretation_verse.clicked.connect(self.OnInterpretation)

        self.quick_access = EnterButton("الوصول السريع")
        self.quick_access.clicked.connect(self.OnQuickAccess)

        self.search_in_quran = EnterButton("البحث في القرآن")
        self.search_in_quran.clicked.connect(self.OnSearch)
        self.save_current_position = QPushButton("حفظ الموضع الحالي")

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.quran_title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.quran_view)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.next_to)
        buttons_layout.addWidget(self.back_to)
        buttons_layout.addWidget(self.interpretation_verse)
        buttons_layout.addWidget(self.quick_access)
        buttons_layout.addWidget(self.search_in_quran)
        buttons_layout.addWidget(self.save_current_position)

        layout.addLayout(buttons_layout)
        self.centralWidget().setLayout(layout)
        



    def OnNext(self):
        self.quran_view.setText(self.quran.next())
        self.set_text_ctrl_label()
        self.quran_view.setFocus()
        self.back_to.setEnabled(True)
        if self.quran.current_pos == self.quran.max_pos:
            self.next_to.setEnabled(False)

    def OnBack(self):
        self.quran_view.setText(self.quran.back())
        self.set_text_ctrl_label()
        self.quran_view.setFocus()
        self.next_to.setEnabled(True)
        if self.quran.current_pos == 1:
            self.back_to.setEnabled(False)

    def set_text_ctrl_label(self):
        if self.quran.type == 0:
            self.quran_title.setText(f"الصفحة {self.quran.current_pos}")
            self.quran_view.setAccessibleName(f"الصفحة {self.quran.current_pos}")
        elif self.quran.type == 1:
            self.quran_title.setText(self.quran.data_list[-1][2])
            self.quran_view.setAccessibleName(self.quran.data_list[-1][2])
        elif self.quran.type == 2:
            self.quran_title.setText(f"الربع {self.quran.current_pos}")
            self.quran_view.setAccessibleName(f"الربع {self.quran.current_pos}")
        elif self.quran.type == 3:
            self.quran_title.setText(f"الحزب {self.quran.current_pos}")
            self.quran_view.setAccessibleName(f"الحزب {self.quran.current_pos}")
        elif self.quran.type == 4:
            self.quran_title.setText(f"الجزء {self.quran.current_pos}")
            self.quran_view.setAccessibleName(f"الجزء {self.quran.current_pos}")

    def OnQuickAccess(self):
        dialog = QuickAccess(self, "الوصول السريع")
        if not dialog.exec():
            return
        
        self.set_text_ctrl_label()
        self.quran_view.setFocus()

        if self.quran.current_pos == 1:
            self.back_to.setEnabled(False)
        if self.quran.current_pos < self.quran.max_pos:
            self.next_to.setEnabled(True)
        if self.quran.current_pos > 1:
            self.back_to.setEnabled(True)
        if self.quran.current_pos == self.quran.max_pos:
            self.next_to.setEnabled(False)

    def OnSearch(self):
        search_dialog = SearchDialog(self, "بحث")
        if search_dialog.exec():
            self.set_text_ctrl_label()

    def get_current_ayah_info(self) -> dict:

        current_line = self.quran_view.textCursor().block().text()
        search = re.search(r"\(\d+\)", current_line)
        if search:
            number = search.group()
            current_line = current_line.replace(number, "").strip()
        ayah_info = self.quran.get_ayah_info(current_line)

        return ayah_info
    
    def OnInterpretation(self):

        selected_category = self.sender().text()
        if selected_category not in Category.get_categories_in_arabic():
            selected_category = "الميسر"

        current_line = self.quran_view.textCursor().block().text()
        title = "تفسير الآية رقم"
        search = re.search(r"\(\d+\)", current_line)
        if search:
            number = search.group()
            title += number
            current_line = current_line.replace(number, "").strip()
        ayah_info = self.quran.get_ayah_info(current_line)
        title += "من {}".format(ayah_info[2])
        dialog = TafaseerDialog(self, title, ayah_info, selected_category)
        dialog.exec()

    def onContextMenu(self):
        menu = QMenu(self)
        get_verse_info = menu.addAction("معلومات الآية")
        get_interpretation_verse = menu.addAction("تفسير الآية")
        get_interpretation_verse.triggered.connect(self.OnInterpretation)

        submenu = menu.addMenu("تفسير الآية")
        arabic_categories = Category.get_categories_in_arabic()
        for arabic_category in arabic_categories:
            action = QAction(arabic_category, self)
            action.triggered.connect(self.OnInterpretation)
            submenu.addAction(action)

        get_verse_syntax = menu.addAction("إعراب الآية")
        get_verse_syntax.triggered.connect(self.OnSyntax)
        get_verse_reasons = menu.addAction("أسباب نزول الآية")
        copy_verse = menu.addAction("نسخ الآية")
        copy_verse.triggered.connect(self.on_copy_verse)

        current_line = self.quran_view.textCursor().block().text()
        if "سُورَةُ" in current_line or current_line == "" or not re.search(r"\(\d+\)$", current_line):
            copy_verse.setEnabled(False)
            get_verse_info.setEnabled(False)
            get_interpretation_verse.setEnabled(False)
            submenu.setEnabled(False)
            get_verse_syntax.setEnabled(False)
            get_verse_reasons.setEnabled(False)

        menu.setAccessibleName("الإجراءات")
        menu.setFocus()
        menu.exec(self.quran_view.mapToGlobal(self.quran_view.pos()))
        
    def on_copy_verse(self):
        current_line = self.quran_view.textCursor().block().text()
        clipboard = QApplication.clipboard()
        clipboard.setText(current_line)

    def OnSyntax(self):
        aya_info = self.get_current_ayah_info()
        title = "إعراب آية رقم {} من {}".format(aya_info[3], aya_info[2])
        label = "الإعراب"
        text = E3rab(aya_info[0], aya_info[1]).text
        InfoDialog(title, label, text).exec()


import os
import re
import pyperclip
from PyQt6.QtCore import Qt, QDir, QFile, QTextStream
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
)
from PyQt6.QtGui import QIcon, QAction
from core_functions.quran_classe import quran_mgr
from ui.dialogs.quick_access import QuickAccess
from ui.dialogs.find import SearchDialog
from ui.widgets.button import EnterButton
from ui.widgets.menu_bar import MenuBar
from ui.widgets.qText_edit import ReadOnlyTextEdit
from ui.dialogs.tafaseer_Dialog import TafaseerDialog


class QuranInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qurani")
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

        self.quran_view = ReadOnlyTextEdit(self)
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
            return


    def OnInterpretation(self):
        current_line = self.quran_view.textCursor().block().text()
        title = "تفسير الآية رقم"
        search = re.search(r"\(\d+\)", current_line)
        if search:
            number = search.group()
            title += number
            current_line = current_line.replace(number, "").strip()
        dialog = TafaseerDialog(self, title)
        print(self.quran.get_ayah_number(current_line))
        if dialog.exec():
            print(current_line)

    def onContextMenu(self):
        menu = QMenu(self)
        get_verse_info = menu.addAction("معلومات الآية")
        get_interpretation_verse = menu.addAction("تفسير الآية")
        submenu = menu.addMenu("تفسير الآية")
        muyassar_interpretation = submenu.addAction("التفسير الميسر")
        qortoby_interpretation = submenu.addAction("تفسير القرطبي")
        katheer_interpretation = submenu.addAction("تفسير ابن كثير")
        tabary_interpretation = submenu.addAction("تفسير الطبري")
        saadiy_interpretation = submenu.addAction("تفسير السعدي")
        baghawy_interpretation = submenu.addAction("تفسير البغوي")
        jalalain_interpretation = submenu.addAction("تفسير الجلالين")
        get_verse_syntax = menu.addAction("إعراب الآية")
        get_verse_reasons = menu.addAction("أسباب نزول الآية")
        copy_verse = menu.addAction("نسخ الآية")
        copy_verse.triggered.connect(self.on_copy_verse)

        lineNum = len(self.quran_view.toPlainText().split("\n"))
        current_line = self.quran_view.textCursor().block().text()
        if "سُورَةُ" in current_line or current_line == "" or not re.search(r"\(\d+\)$", current_line):
            copy_verse.setEnabled(False)

        menu.setAccessibleName("الإجراءات")
        menu.setFocus()
        menu.exec(self.quran_view.mapToGlobal(self.quran_view.pos()))
        

    def on_copy_verse(self):
        lineNum = len(self.quran_view.toPlainText().split("\n"))
        current_line = self.quran_view.textCursor().block().text()
        pyperclip.copy(current_line)

    
import time
import sys
import os
import re
import json
import pyperclip
from widgets.button import EnterButton
from PyQt6.QtCore import Qt, QDir, QFile, QTextStream, QTimer
from PyQt6.QtWidgets import (
    QVBoxLayout, 
    QWidget, 
    QLabel, 
    QTextEdit, 
    QTextBrowser,
    QPlainTextEdit,
    QPushButton, 
    QMenu, 
    QHBoxLayout, 
    QMainWindow, 
    QApplication,
    QMessageBox,
    QComboBox,
)
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtGui import QIcon, QAction


from quran_classes import quran_mgr
from dialogs import QuickAccess, view_information

class QuranInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qurani")
        self.setGeometry(100, 100, 800, 600)
        self.quran = quran_mgr()
        self.quran.load_quran(os.path.join("database", "quran", "quran.DB"))
        self.quran.aya_to_line = True

        self.create_menu()
        self.create_widgets()
        self.create_layout()
        
    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        new_action = QAction(QIcon(), "&New", self)  # Adding empty QIcon
        file_menu.addAction(new_action)
        open_action = QAction(QIcon(), "&Open", self)
        file_menu.addAction(open_action)
        save_action = QAction(QIcon(), "&Save", self)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")
        copy_action = QAction("&Copy", self)
        edit_menu.addAction(copy_action)
        cut_action = QAction("Cu&t", self)
        edit_menu.addAction(cut_action)
        paste_action = QAction("&Paste", self)
        edit_menu.addAction(paste_action)

    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.quran_title = QLabel()
        font = self.quran_title.font()
        font.setPointSize(16)
        font.setBold(True)
        self.quran_title.setFont(font)

        self.quran_view = QTextEdit(self)
        self.quran_view.setReadOnly(True)
        self.quran_view.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard| Qt.TextInteractionFlag.TextSelectableByMouse)
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
        self.save_current_position = QPushButton("حفظ الموضع الحالي")

        # Theme dropdown
        self.theme_combo = QComboBox()
        self.populate_themes()
        self.theme_combo.currentIndexChanged.connect(self.apply_theme)

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
        buttons_layout.addWidget(self.theme_combo)

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
        dialog.exec_()
        selected_item = dialog.get_selected_item()
        number = selected_item["number"]
        if selected_item["view_by"] == 0:
            self.quran_view.setText(self.quran.get_surah(number))
        elif selected_item["view_by"] == 1:
            self.quran_view.setText(self.quran.get_page(number))
        elif selected_item["view_by"] == 2:
            self.quran_view.setText(self.quran.get_quarter(number))
        elif selected_item["view_by"] == 3:
            self.quran_view.setText(self.quran.get_hizb(number))
        elif selected_item["view_by"] == 4:
            self.quran_view.setText(self.quran.get_juzz(number))

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

    def OnInterpretation(self):
        lineNum = len(self.quran_view.toPlainText().split("\n"))
        current_line = self.quran_view.textCursor().block().text()
        title = "تفسير الآية رقم" + re.search(r"\(\d+\)", current_line).group()
        dialog = view_information(self, title)
        try:
            dialog.view_text.setPlainText(self.quran.get_tafasir(current_line[:-4].strip()))
            dialog.label.setText(title)
        except IndexError:
            QMessageBox.critical(self, "لم يتم تحديد آية", "قم بالوقوف على الآية المراد تفسيرها.")

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

        menu.setAccessibleName("Context menu")
        menu.setFocus()
        menu.exec(self.quran_view.mapToGlobal(self.quran_view.pos()))
        

    def on_copy_verse(self):
        lineNum = len(self.quran_view.toPlainText().split("\n"))
        current_line = self.quran_view.textCursor().block().text()
        pyperclip.copy(current_line)

    def populate_themes(self):
        theme_dir = QDir("theme")
        if not theme_dir.exists():
            print("مجلد الثيمات غير موجود")
            return

        theme_files = theme_dir.entryList(["*.qss"])
        if not theme_files:
            print("لا توجد ملفات ثيمات في المجلد")
            return

        for theme_file in theme_files:
            self.theme_combo.addItem(theme_file)

    def apply_theme(self):
        selected_theme = self.theme_combo.currentText()
        theme_path = QDir("theme").filePath(selected_theme)
        if not QFile.exists(theme_path):
            print("الملف غير موجود:", theme_path)
            return

        try:
            with open(theme_path, 'r') as theme_file:
                stylesheet = theme_file.read()
                self.setStyleSheet(stylesheet)
        except Exception as e:
            print("حدث خطأ أثناء قراءة الملف:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QuranInterface()
    main_window.show()
    main_window.setFocus()
    QTimer.singleShot(200, main_window.quran_view.setFocus)
    sys.exit(app.exec())

import sys
from PyQt6.QtWidgets import  QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QKeySequence
from ui.widgets.qText_edit import ReadOnlyTextEdit

class InfoDialog(QDialog):
    def __init__(self, title: str, label: str, text: str, is_html_content: bool=False):
        super().__init__()
        self.title = title
        self.label = label
        self.text = text
        self.is_html_content = is_html_content
        self.init_ui()


    def init_ui(self):
        
        self.setWindowTitle(self.title)
        self.resize(400, 300)
        self.setFocus()

        label = QLabel(self.label, self)
        
        text_edit = ReadOnlyTextEdit(self)
        text_edit.setAccessibleName(self.label)
        if self.is_html_content:
            text_edit.setHtml(self.text)
        else:
            text_edit.setText(self.text)

        close_button = QPushButton('إغلاق', self)
        close_button.setShortcut(QKeySequence("Ctrl+W"))
        close_button.clicked.connect(self.reject)
        close_button.setStyleSheet(f'background-color: red; color: white;')

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(text_edit)
        layout.addWidget(close_button)
        self.setLayout(layout)
        QTimer.singleShot(300, text_edit.setFocus)
        

        
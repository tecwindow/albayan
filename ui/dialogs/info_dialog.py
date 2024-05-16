import sys
from PyQt6.QtWidgets import  QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PyQt6.QtCore import QTimer
from ui.widgets.qText_edit import ReadOnlyTextEdit

class InfoDialog(QDialog):
    def __init__(self, title, label, text):
        super().__init__()
        self.title = title
        self.label = label
        self.text = text
        self.init_ui()


    def init_ui(self):
        
        self.setWindowTitle(self.title)
        self.resize(300, 200)
        self.setFocus()


        bg_color = 'lightGray'
        text_color = 'black'

        label = QLabel(self.label, self)
        label.setStyleSheet(f'color: {text_color};')
        
        text_edit = ReadOnlyTextEdit(self)
        text_edit.setText(self.text)
        text_edit.setStyleSheet(f'background-color: {bg_color}; color: {text_color};')
        text_edit.setAccessibleName(self.label)

        close_button = QPushButton('إغلاق', self)
        close_button.clicked.connect(self.reject)
        close_button.setStyleSheet(f'background-color: red; color: white;')

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(text_edit)
        layout.addWidget(close_button)
        self.setLayout(layout)
        QTimer.singleShot(300, text_edit.setFocus)
        

        
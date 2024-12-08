import sys
import json
import random
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QKeySequence, QClipboard
from ui.widgets.qText_edit import ReadOnlyTextEdit
from utils.universal_speech import UniversalSpeech
from utils.const import Globals, data_folder

class InfoDialog(QDialog):
    def __init__(self, title: str, label: str, text: str, is_html_content: bool = False):
        super().__init__()
        self.title = title
        self.label = label
        self.text = text
        self.is_html_content = is_html_content
        self.init_ui()
        Globals.effects_manager.play("open")


    def init_ui(self):
        self.setWindowTitle(self.title)
        self.resize(400, 300)
        self.setFocus()

        label = QLabel(self.label, self)
        
        self.text_edit = ReadOnlyTextEdit(self)
        self.text_edit.setAccessibleName(self.label)
        if self.is_html_content:
            self.text_edit.setHtml(self.text)
        else:
            self.text_edit.setText(self.text)

        # Copy button
        copy_button = QPushButton('نسخ', self)
        copy_button.clicked.connect(self.copy_text)
        copy_button.setShortcut(QKeySequence("Shift+C"))
        copy_button.setStyleSheet('background-color: red; color: white;')

        # Message to you button
        message_to_you_button = QPushButton('رسالة لك', self)
        message_to_you_button.clicked.connect(self.message_to_you)
        message_to_you_button.setShortcut(QKeySequence("Ctrl+M"))
        message_to_you_button.setStyleSheet('background-color: red; color: white;')

        # Close button
        close_button = QPushButton('إغلاق', self)
        close_button.setShortcut(QKeySequence("Ctrl+W"))
        close_button.clicked.connect(self.reject)
        close_button.setStyleSheet('background-color: red; color: white;')

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.text_edit)
        layout.addWidget(copy_button)
        layout.addWidget(message_to_you_button)
        layout.addWidget(close_button)
        self.setLayout(layout)
        
        # Focus the text edit after dialog opens
        QTimer.singleShot(300, self.text_edit.setFocus)

    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        UniversalSpeech.say("تم نسخ النص إلى الحافظة")
        Globals.effects_manager.play("copy")

    def reject(self):
        Globals.effects_manager.play("clos")
        self.deleteLater()
        
    def message_to_you(self):
        # Load the quotes and choose a random message
        with open(data_folder/"quotes/QuotesMessages.json", "r", encoding="utf-8") as file:
            quotes_list = json.load(file)
        new_message = random.choice(quotes_list)

        # Update the text without opening a new dialog
        self.text_edit.setText(new_message)
        UniversalSpeech.say(new_message)

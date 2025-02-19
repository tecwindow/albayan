import sys
import json
import random
import qtawesome as qta
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QKeySequence, QClipboard
from ui.widgets.qText_edit import ReadOnlyTextEdit
from utils.universal_speech import UniversalSpeech
from utils.const import Globals, data_folder
from exceptions.json import JSONFileNotFoundError, InvalidJSONFormatError
from exceptions.error_decorators import exception_handler

class InfoDialog(QDialog):
    def __init__(self, parent, title: str, label: str, text: str, is_html_content: bool = False, show_message_button: bool = False):
        super().__init__(parent)
        self.title = title
        self.label = label
        self.text = text
        self.parent = parent
        self.is_html_content = is_html_content
        self.show_message_button = show_message_button
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
        copy_button.setIcon(qta.icon("fa.copy"))
        copy_button.clicked.connect(self.copy_text)
        copy_button.setShortcut(QKeySequence("Shift+C"))
        copy_button.setStyleSheet('background-color: red; color: white;')


        # Message to you button (conditionally added)
        message_to_you_button = QPushButton('رسالة لك', self)
        message_to_you_button.setIcon(qta.icon("fa.envelope"))
        message_to_you_button.clicked.connect(self.OnNewMessage)
        message_to_you_button.setShortcut(QKeySequence("Shift+M"))
        message_to_you_button.setStyleSheet('background-color: red; color: white;')
        message_to_you_button.setVisible(self.show_message_button)
        message_to_you_button.setDefault(True)


        if not self.show_message_button:
                    copy_button.setDefault(True)


        # Close button
        close_button = QPushButton('إغلاق', self)
        close_button.setIcon(qta.icon("fa.times"))
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

    def choose_QuotesMessage(self):
        file_path = data_folder/"quotes/QuotesMessages.json"
        if not file_path.exists():
            raise JSONFileNotFoundError(file_path)
            
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                quotes_list = json.load(file)
                message = random.choice(quotes_list)
        except json.JSONDecodeError as e:
                raise InvalidJSONFormatError(file_path, e)

        self.text_edit.setText(message)
        UniversalSpeech.say(message)
        
    def OnNewMessage(self):
        self.choose_QuotesMessage()
        Globals.effects_manager.play("message")
        

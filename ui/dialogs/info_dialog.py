import os
import sys
import json
import random
import qtawesome as qta
from datetime import datetime
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QTextEdit, QPushButton, QApplication, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QKeySequence, QClipboard, QShortcut, QPixmap, QFontMetrics, QPainter, QFont
from ui.widgets.qText_edit import ReadOnlyTextEdit
from utils.universal_speech import UniversalSpeech
from utils.const import albayan_documents_dir, Globals, data_folder
from utils.logger import LoggerManager
from exceptions.json import JSONFileNotFoundError, InvalidJSONFormatError
from exceptions.error_decorators import exception_handler

logger = LoggerManager.get_logger(__name__)


class InfoDialog(QDialog):
    def __init__(self, parent, title: str, label: str, text: str, is_html_content: bool = False, show_message_button: bool = False, save_message_as_img_button: bool = False):
        super().__init__(parent)
        self.title = title
        self.label = label
        self.text = text
        self.parent = parent
        self.is_html_content = is_html_content
        self.show_message_button = show_message_button
        self.save_message_as_img_button = save_message_as_img_button
        self.init_ui()
        Globals.effects_manager.play("open")
        logger.debug(f"InfoDialog initialized with title: {title}, label: {label}.")

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.resize(500, 400)
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

        # Save as Image button (conditionally added)
        save_img_button = QPushButton('حفظ كصورة', self)
        save_img_button.setIcon(qta.icon("fa.image"))
        save_img_button.clicked.connect(self.save_text_as_image)
        save_img_button.setStyleSheet('background-color: red; color: white;')
        save_img_button.setVisible(self.save_message_as_img_button)
        save_img_button.setShortcut(QKeySequence("Shift+S"))

        # Close button
        close_button = QPushButton('إغلاق', self)
        close_button.setIcon(qta.icon("fa.times"))
        close_button.setShortcut(QKeySequence("Ctrl+W"))
        close_button.clicked.connect(self.reject)
        close_button.setStyleSheet('background-color: red; color: white;')
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)


        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.text_edit)
        button_layout = QGridLayout()
        button_layout.addWidget(message_to_you_button, 0, 0)
        button_layout.addWidget(save_img_button, 0, 1)
        button_layout.addWidget(copy_button, 1, 0)
        button_layout.addWidget(close_button, 1, 1)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        

        # Focus the text edit after dialog opens
        QTimer.singleShot(300, self.text_edit.setFocus)

    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        UniversalSpeech.say("تم نسخ النص إلى الحافظة")
        Globals.effects_manager.play("copy")
        logger.debug("User copied text to clipboard.")


    def reject(self):
        logger.debug("User closed InfoDialog.")
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
                logger.debug(f"Loaded quote: {message}")
        except json.JSONDecodeError as e:
                raise InvalidJSONFormatError(file_path, e)

        self.text_edit.setText(message)
        UniversalSpeech.say(message)
        
    def OnNewMessage(self):
        self.choose_QuotesMessage()
        Globals.effects_manager.play("message")
        logger.debug("User triggered 'OnNewMessage', displaying a new message.")


    def save_text_as_image(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        options = QFileDialog.Options()
        file_name = os.path.join(albayan_documents_dir, f"البيان_{self.windowTitle()}_{timestamp}.png")
        file_path, _ = QFileDialog.getSaveFileName(
        self, "حفظ الصورة", file_name, "Images (*.png *.jpg *.bmp)", options=options
        )
        if file_path:
            text = self.text_edit.toPlainText()
            font = self.text_edit.font()  
            font.setPointSize(22)
            font.setBold(True)
            font.setFamily("Arial")

            metrics = QFontMetrics(font)
            text_width = max([metrics.horizontalAdvance(line) for line in text.split("\n")]) + 40
            text_height = metrics.lineSpacing() * (len(text.split("\n")) + 2)

            pixmap = QPixmap(text_width, text_height)
            pixmap.fill(Qt.GlobalColor.black)

            painter = QPainter(pixmap)
            painter.setFont(font)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
            painter.end()

            pixmap.save(file_path)

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("تم الحفظ")
            msg_box.setText(f"تم حفظ الصورة في: {file_path}")

            ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
            msg_box.exec()
            logger.debug(f"Saved text as image to {file_path}.")


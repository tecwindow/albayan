import sys
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout, 
    QVBoxLayout, 
    QPushButton, 
    QDialog, 
    QApplication,
    QFileDialog,
    QLabel,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from ui.widgets.qText_edit import ReadOnlyTextEdit
from core_functions.tafaseer import TafaseerManager, Category


class TafaseerDialog(QDialog):
    def __init__(self, parent, title, aya_info):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 300, 200)
        self.setFocus()
        self.tafaseer_manager = TafaseerManager()
        self.tafaseer_manager.set(Category.muyassar)


        self.layout = QVBoxLayout(self)
        
        self.label = QLabel(self)
        self.label.setText("التفسير:")
        self.layout.addWidget(self.label)

        self.text_edit = ReadOnlyTextEdit(self)
        self.text_edit.setText(self.tafaseer_manager.get_tafaseer(aya_info[0], aya_info[1]))
        self.layout.addWidget(self.text_edit)

        self.button_layout = QVBoxLayout()

        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_content)
        self.button_layout.addWidget(self.copy_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_content)
        self.button_layout.addWidget(self.save_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.close_button)

        self.layout.addLayout(self.button_layout)
        QTimer.singleShot(200, self.text_edit.setFocus)
        

    def copy_content(self):
        self.copied_content = self.text_edit.toPlainText()

    def save_content(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Text Files (*.txt);;All Files (*)", options=options
        )
        if file_name:
            with open(file_name, "w") as file:
                file.write(self.text_edit.toPlainText())

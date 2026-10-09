from PySide6.QtWidgets import QPushButton, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from core_functions.tafaseer import Category


class EnterButton(QPushButton):
    def keyPressEvent(self, event):

        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Space, Qt.Key.Key_Enter}:
            self.clicked.emit()

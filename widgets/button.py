from PyQt6.QtWidgets import QPushButton, QApplication
from PyQt6.QtCore import Qt

class EnterButton(QPushButton):
    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Space:
            self.clicked.emit()


from PyQt6.QtWidgets import QSpinBox, QApplication
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt


class SpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_validator()

    def update_validator(self):
        validator = QIntValidator(self.minimum(), self.maximum(), self)
        self.lineEdit().setValidator(validator)
        self.lineEdit().inputRejected.connect(QApplication.beep)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.lineEdit().selectAll()

    def fixup(self, text: str
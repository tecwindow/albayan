from PyQt6.QtWidgets import QLineEdit, QApplication
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression


class ArabicSearchBox(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a regular expression to allow only Arabic letters, diacritics, and spaces
        regex = QRegularExpression("[\u0621-\u0652\u0670\u0671[:space:]]+")
        validator = QRegularExpressionValidator(regex, self)
        self.setValidator(validator)
        self.inputRejected.connect(QApplication.beep)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.selectAll()

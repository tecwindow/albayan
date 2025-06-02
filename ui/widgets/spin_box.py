from PyQt6.QtWidgets import QSpinBox, QApplication
from PyQt6.QtGui import QValidator
from PyQt6.QtCore import Qt


class CustomRangeValidator(QValidator):
    def __init__(self, min_val: int, max_val: int, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, input_str: str, pos: int):
        if input_str == "":
            return QValidator.State.Intermediate, input_str, pos

        if input_str.isdigit():
            value = int(input_str)
            if self.min_val <= value <= self.max_val:
                return QValidator.State.Acceptable, input_str, pos
            else:
                return QValidator.State.Invalid, input_str, pos
        return QValidator.State.Invalid, input_str, pos

    def fixup(self, input_str: str):
        return str(self.min_val)


class SpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.validator = CustomRangeValidator(self.minimum(), self.maximum(), self)
        self.lineEdit().setValidator(self.validator)
        self.lineEdit().inputRejected.connect(QApplication.beep)

    def update_validator(self):
        self.validator.min_val = self.minimum()
        self.validator.max_val = self.maximum()
        
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.lineEdit().selectAll()

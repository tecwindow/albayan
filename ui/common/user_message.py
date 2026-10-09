from PySide6.QtWidgets import QMessageBox, QWidget
from typing import Optional


class UserMessageService:
    """
    Centralized dialog service for Confirm / Info / Error dialogs.
    Ensures consistent UX and reduces UI duplication across the app.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        self.parent = parent

    def confirm(
        self,
        title: str,
        message: str,
        *,
        yes_text: str = "نعم",
        no_text: str = "لا",
        icon: QMessageBox.Icon = QMessageBox.Icon.Warning,
    ) -> bool:
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        yes_button = msg_box.addButton(yes_text, QMessageBox.ButtonRole.AcceptRole)
        msg_box.addButton(no_text, QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()
        return msg_box.clickedButton() == yes_button

    def info(
        self,
        title: str,
        message: str,
    ) -> None:
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()

    def error(
        self,
        title: str,
        message: str,
    ) -> None:
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()

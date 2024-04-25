from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QIcon, QAction

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.create_menu()

    def create_menu(self):
        file_menu = self.addMenu("&File")
        new_action = QAction("&New", self)
        file_menu.addAction(new_action)
        open_action = QAction("&Open", self)
        file_menu.addAction(open_action)
        save_action = QAction("&Save", self)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = self.addMenu("&Edit")
        copy_action = QAction("&Copy", self)
        edit_menu.addAction(copy_action)
        cut_action = QAction("Cu&t", self)
        edit_menu.addAction(cut_action)
        paste_action = QAction("&Paste", self)
        edit_menu.addAction(paste_action)

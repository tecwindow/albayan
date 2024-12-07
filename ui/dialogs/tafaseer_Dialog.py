import os
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout, 
    QVBoxLayout, 
    QPushButton, 
    QDialog, 
    QFileDialog,
    QLabel,
    QMenu,
    QApplication
)
from PyQt6.QtGui import QIcon, QAction, QKeySequence
from PyQt6.QtCore import QTimer
from ui.widgets.qText_edit import ReadOnlyTextEdit
from core_functions.tafaseer import TafaseerManager, Category
from utils.universal_speech import UniversalSpeech
from utils.const import albayan_documents_dir, Globals


class TafaseerDialog(QDialog):
    def __init__(self, parent, title, ayah_info, default_category):
        super().__init__(parent)
        self.parent = parent
        self.ayah_info = ayah_info
        self.default_category = default_category
        self.setWindowTitle(title)
        self.resize(500, 400)
        self.tafaseer_manager = TafaseerManager()
        self.tafaseer_manager.set(Category.get_category_by_arabic_name(self.default_category))
        Globals.effects_manager.play("open")

        self.layout = QVBoxLayout(self)
        
        self.label = QLabel("التفسير:", self)
        self.layout.addWidget(self.label)

        self.text_edit = ReadOnlyTextEdit(self)
        self.text_edit.setAccessibleName(self.label.text())
        self.text_edit.setText(self.tafaseer_manager.get_tafaseer(ayah_info[0], ayah_info[1]))
        self.layout.addWidget(self.text_edit)

        self.button_layout = QHBoxLayout()  # استخدام QHBoxLayout بدلاً من QVBoxLayout

        self.category_button = QPushButton(self.default_category, self)
        self.category_button.clicked.connect(self.show_menu)
        self.button_layout.addWidget(self.category_button)

        self.copy_button = QPushButton("نسخ التفسير")
        self.copy_button.setShortcut(QKeySequence("Shift+C"))
        self.copy_button.clicked.connect(self.copy_content)
        self.button_layout.addWidget(self.copy_button)

        self.save_button = QPushButton("حفظ التفسير")
        self.save_button.setShortcut(QKeySequence("Ctrl+S"))
        self.save_button.clicked.connect(self.save_content)
        self.button_layout.addWidget(self.save_button)

        self.close_button = QPushButton("إغلاق")
        self.close_button.setShortcut(QKeySequence("Ctrl+W"))
        self.close_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.close_button)

        self.layout.addLayout(self.button_layout)
        self.setFocus()
        QTimer.singleShot(300, self.text_edit.setFocus)
        
    def show_menu(self):
        menu = QMenu(self)
        arabic_categories = Category.get_categories_in_arabic()
        actions = {}
        for arabic_category in arabic_categories:
            action = QAction(arabic_category, self)
            action.triggered.connect(self.handle_category_selection)
            actions[arabic_category] = action
            menu.addAction(action)

        selected_category_name = self.category_button.text()
        selected_action = actions.get(selected_category_name)
        if selected_action:
            selected_action.setCheckable(True)
            selected_action.setChecked(True)
            menu.setActiveAction(selected_action)

        menu.setAccessibleName("اختر المفسر:")
        menu.setFocus()
        menu.exec(self.category_button.mapToGlobal(self.category_button.rect().bottomLeft()))

    def handle_category_selection(self):
        selected_category = self.sender().text()
        self.category_button.setText(selected_category)
        self.tafaseer_manager.set(Category.get_category_by_arabic_name(selected_category))
        self.text_edit.setText(self.tafaseer_manager.get_tafaseer(self.ayah_info[0], self.ayah_info[1]))
        self.text_edit.setFocus()
        Globals.effects_manager.play("change")

    def copy_content(self):
        copied_content = self.text_edit.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(copied_content) 
        UniversalSpeech.say("تم نسخ التفسير.")
        Globals.effects_manager.play("copy")        
    def save_content(self):            

        file_name = os.path.join(albayan_documents_dir, self.windowTitle())
        # Open the file dialog in the Albayan directory
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", file_name, "Text files (*.txt)",
        )

        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_edit.toPlainText())

    def reject(self):
        Globals.effects_manager.play("clos")
        self.deleteLater()

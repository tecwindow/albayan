import os
import qtawesome as qta
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout, 
    QVBoxLayout, 
    QPushButton, 
    QDialog, 
    QFileDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QApplication
)
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QShortcut
from PyQt6.QtCore import QTimer
from ui.widgets.qText_edit import ReadOnlyTextEdit
from core_functions.tafaseer import TafaseerManager, Category
from core_functions.quran.types import Ayah
from utils.universal_speech import UniversalSpeech
from utils.const import albayan_documents_dir, Globals
from utils.logger import LoggerManager
from exceptions.error_decorators import exception_handler

logger = LoggerManager.get_logger(__name__)

class TafaseerDialog(QDialog):
    def __init__(self, parent, title, ayah: Ayah, default_category):
        super().__init__(parent)
        logger.debug("Initializing TafaseerDialog...")
        self.parent = parent
        self.ayah = ayah
        self.title = title
        self.default_category = default_category
        self.setWindowTitle(f"{self.title} - {default_category}")
        logger.debug(f"TafaseerDialog initialized with title: {self.title}.")
        self.resize(500, 400)
        self.tafaseer_manager = TafaseerManager()
        self.tafaseer_manager.set(Category.get_category_by_arabic_name(self.default_category))
        Globals.effects_manager.play("open")
        logger.debug(f"Loaded Tafaseer category: {self.default_category}")

        self.layout = QVBoxLayout(self)
        
        self.label = QLabel("التفسير:", self)
        self.layout.addWidget(self.label)

        self.text_edit = ReadOnlyTextEdit(self)
        self.text_edit.setAccessibleName(self.label.text())
        self.text_edit.setText(self.tafaseer_manager.get_tafaseer(ayah.sura_number, ayah.number))
        logger.debug("Tafaseer content loaded into text edit")
        self.layout.addWidget(self.text_edit)

        self.button_layout = QHBoxLayout()  # استخدام QHBoxLayout بدلاً من QVBoxLayout

        self.category_button = QPushButton(self.default_category, self)
        self.category_button.setIcon(qta.icon("fa.list"))
        self.category_button.setShortcut(QKeySequence("Alt+C"))
        self.category_button.clicked.connect(self.show_menu)
        self.button_layout.addWidget(self.category_button)

        self.copy_button = QPushButton("نسخ التفسير")
        self.copy_button.setIcon(qta.icon("fa.copy"))
        self.copy_button.setShortcut(QKeySequence("Shift+C"))
        self.copy_button.clicked.connect(self.copy_content)
        self.button_layout.addWidget(self.copy_button)

        self.save_button = QPushButton("حفظ التفسير")
        self.save_button.setIcon(qta.icon("fa.save"))
        self.save_button.setShortcut(QKeySequence("Ctrl+S"))
        self.save_button.clicked.connect(self.save_content)
        self.button_layout.addWidget(self.save_button)

        self.close_button = QPushButton("إغلاق")
        self.close_button.setIcon(qta.icon("fa.times"))
        self.close_button.setShortcut(QKeySequence("Ctrl+W"))
        self.close_button.clicked.connect(self.reject)
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)

        self.button_layout.addWidget(self.close_button)

        self.layout.addLayout(self.button_layout)
        self.setFocus()
        QTimer.singleShot(300, self.text_edit.setFocus)
        logger.debug("TafaseerDialog setup completed.")


    @exception_handler(ui_element=QMessageBox)
    def show_menu(self, event):
        logger.info("User opened Tafaseer category selection menu.")
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
        logger.debug("Tafaseer category menu displayed.")
        menu.exec(self.category_button.mapToGlobal(self.category_button.rect().bottomLeft()))

    @exception_handler(ui_element=QMessageBox)
    def handle_category_selection(self, event):
        selected_category = self.sender().text()
        logger.debug(f"User selected Tafaseer category: {selected_category}")
        self.category_button.setText(selected_category)
        self.tafaseer_manager.set(Category.get_category_by_arabic_name(selected_category))
        self.text_edit.setText(self.tafaseer_manager.get_tafaseer(self.ayah.sura_number, self.ayah.number))
        self.setWindowTitle(f"{self.title} - {selected_category}")
        self.text_edit.setFocus()
        Globals.effects_manager.play("change")
        logger.info(f"Tafaseer content updated for category: {selected_category}")

    def copy_content(self):
        logger.debug("User requested to copy Tafaseer content.")
        tafseer_text = self.text_edit.toPlainText()
        category_name = self.category_button.text().strip()
        ayah_info = f"آية {self.ayah.number} من {self.ayah.sura_name}، تفسير: {category_name}."
        final_text = f"{ayah_info}\n{tafseer_text}"

        clipboard = QApplication.clipboard()
        clipboard.setText(final_text)

        UniversalSpeech.say(f"تم نسخ التفسير: آية {self.ayah.number} من {self.ayah.sura_name} للمفسر {category_name}.")
        Globals.effects_manager.play("copy")
        logger.info(f"Tafseer copied with header: {ayah_info}")


    def save_content(self):            
        logger.debug("User requested to save Tafaseer content.")

        file_name = os.path.join(albayan_documents_dir, self.windowTitle())
        logger.debug(f"User attempting to save Tafaseer content to: {file_name}")
        # Open the file dialog in the Albayan directory
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", file_name, "Text files (*.txt)",
        )

        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_edit.toPlainText())
                logger.info(f"Tafaseer content successfully saved to: {file_path}")

    def reject(self):
        Globals.effects_manager.play("clos")
        self.deleteLater()

    def closeEvent(self, a0):
        logger.debug("TafaseerDialog closed.")
        return super().closeEvent(a0)

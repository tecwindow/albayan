import os
from typing import Optional
import qtawesome as qta
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QDialog,
    QFileDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QApplication,
)
from PySide6.QtGui import QIcon, QAction, QKeySequence, QShortcut
from PySide6.QtCore import QTimer, Signal
from ui.widgets.qText_edit import ReadOnlyTextEdit
from core_functions.tafaseer import (
    TafaseerManager,
    Category,
    DEFAULT_BUNDLED_TAFSIR_ID,
    TAFASEER_CATALOG,
)
from ui.dialogs.tafaseer_manager_dialog import TafaseerManagerDialog
from core_functions.quran.types import Ayah
from utils.universal_speech import UniversalSpeech
from utils.const import Globals
from utils.paths import paths
from utils.logger import LoggerManager
from exceptions.error_decorators import exception_handler

logger = LoggerManager.get_logger(__name__)


def _play_sound(effect_name: str):
    if hasattr(Globals, "effects_manager") and Globals.effects_manager:
        try:
            Globals.effects_manager.play(effect_name)
        except Exception:
            pass


class TafaseerDialog(QDialog):
    tafaseer_updated = Signal(str)

    def __init__(self, parent, title, ayah: Ayah, default_category):
        super().__init__(parent)
        logger.debug("Initializing TafaseerDialog...")
        self.parent = parent
        self.ayah = ayah
        self.title = title

        # Verify if the requested category is installed; fallback to default if not
        cat_id = Category.get_category_by_arabic_name(default_category)
        if not cat_id or not Category.is_installed(cat_id):
            cat_id = DEFAULT_BUNDLED_TAFSIR_ID
            self.default_category = Category.get_arabic_name_by_category(DEFAULT_BUNDLED_TAFSIR_ID) or "الميسر"
        else:
            self.default_category = default_category

        self.setWindowTitle(f"{self.title} - {self.default_category}")
        logger.debug(f"TafaseerDialog initialized with title: {self.title}.")
        self.resize(550, 420)
        self.tafaseer_manager = TafaseerManager()
        self.tafaseer_manager.set(cat_id)
        _play_sound("open")
        logger.debug(f"Loaded Tafaseer category: {self.default_category}")

        self.layout = QVBoxLayout(self)

        self.label = QLabel("التفسير:", self)
        self.label.setAccessibleName("عنوان التفسير")
        self.layout.addWidget(self.label)

        self.text_edit = ReadOnlyTextEdit(self)
        self.text_edit.setAccessibleName(self.label.text())
        self.text_edit.setText(
            self.tafaseer_manager.get_tafaseer(ayah.sura_number, ayah.number)
        )
        logger.debug("Tafaseer content loaded into text edit")
        self.layout.addWidget(self.text_edit)

        self.button_layout = QHBoxLayout()

        self.category_button = QPushButton(self.default_category, self)
        self.category_button.setIcon(qta.icon("fa5s.list"))
        self.category_button.setAccessibleName(f"المفسر الحالي: {self.default_category}")
        self.category_button.setShortcut(QKeySequence("Alt+C"))
        self.category_button.clicked.connect(self.show_menu)
        self.button_layout.addWidget(self.category_button)

        self.manage_button = QPushButton("إدارة التفاسير", self)
        self.manage_button.setIcon(qta.icon("fa5s.cog"))
        self.manage_button.setAccessibleName("إدارة وتنزيل التفاسير")
        self.manage_button.setShortcut(QKeySequence("Alt+M"))
        self.manage_button.clicked.connect(self.open_tafaseer_manager)
        self.button_layout.addWidget(self.manage_button)

        self.copy_button = QPushButton("نسخ التفسير")
        self.copy_button.setIcon(qta.icon("fa5s.copy"))
        self.copy_button.setAccessibleName("نسخ التفسير")
        self.copy_button.setShortcut(QKeySequence("Shift+C"))
        self.copy_button.clicked.connect(self.copy_content)
        self.button_layout.addWidget(self.copy_button)

        self.save_button = QPushButton("حفظ التفسير")
        self.save_button.setIcon(qta.icon("fa5s.save"))
        self.save_button.setAccessibleName("حفظ التفسير")
        self.save_button.setShortcut(QKeySequence("Ctrl+S"))
        self.save_button.clicked.connect(self.save_content)
        self.button_layout.addWidget(self.save_button)

        self.close_button = QPushButton("إغلاق")
        self.close_button.setIcon(qta.icon("fa5s.times"))
        self.close_button.setAccessibleName("إغلاق نافذة التفسير")
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
    def show_menu(self, event=None):
        logger.info("User opened Tafaseer category selection menu.")
        menu = QMenu(self)
        menu.setAccessibleName("قائمة اختيار المفسر")

        current_category_name = self.category_button.text().strip()

        # Add installed tafaseer first
        installed_arabic = Category.get_installed_categories_arabic()
        actions = {}
        for arabic_category in installed_arabic:
            action = QAction(arabic_category, self)
            action.triggered.connect(self.handle_category_selection)
            if arabic_category == current_category_name:
                action.setCheckable(True)
                action.setChecked(True)
            actions[arabic_category] = action
            menu.addAction(action)

        # Uninstalled tafaseer
        all_arabic = Category.get_categories_in_arabic()
        uninstalled_arabic = [name for name in all_arabic if name not in installed_arabic]

        if uninstalled_arabic:
            menu.addSeparator()
            uninstalled_menu = menu.addMenu("تفاسير غير مُنزّلة")
            uninstalled_menu.setAccessibleName("قائمة تفاسير غير منزلة")
            for arabic_category in uninstalled_arabic:
                action = QAction(f"{arabic_category} (تنزيل)", self)
                action.setData(arabic_category)
                action.triggered.connect(self.handle_uninstalled_selection)
                uninstalled_menu.addAction(action)

        # Management shortcut
        menu.addSeparator()
        manage_action = QAction("إدارة وتنزيل التفاسير...", self)
        manage_action.setIcon(qta.icon("fa5s.cog"))
        manage_action.triggered.connect(lambda: self.open_tafaseer_manager())
        menu.addAction(manage_action)

        menu.setFocus()
        logger.debug("Tafaseer category menu displayed.")
        menu.exec(
            self.category_button.mapToGlobal(self.category_button.rect().bottomLeft())
        )

    @exception_handler(ui_element=QMessageBox)
    def handle_category_selection(self, event=None):
        sender = self.sender()
        if not sender:
            return

        selected_category = sender.text().strip()
        cat_id = Category.get_category_by_arabic_name(selected_category)
        if not cat_id or not Category.is_installed(cat_id):
            UniversalSpeech.say("هذا التفسير غير متوفر حالياً.")
            return

        logger.debug(f"User selected Tafaseer category: {selected_category}")
        self.category_button.setText(selected_category)
        self.category_button.setAccessibleName(f"المفسر الحالي: {selected_category}")
        self.tafaseer_manager.set(cat_id)
        self.tafaseer_updated.emit(selected_category)
        self.text_edit.setText(
            self.tafaseer_manager.get_tafaseer(self.ayah.sura_number, self.ayah.number)
        )
        self.setWindowTitle(f"{self.title} - {selected_category}")
        self.text_edit.setFocus()
        _play_sound("change")
        logger.info(f"Tafaseer content updated for category: {selected_category}")

    def handle_uninstalled_selection(self):
        sender = self.sender()
        if not sender:
            return

        arabic_category = sender.data() or sender.text().replace(" (تنزيل)", "").strip()
        cat_id = Category.get_category_by_arabic_name(arabic_category)
        logger.info(f"User selected uninstalled tafsir '{arabic_category}' ({cat_id}) in TafaseerDialog.")

        confirm = QMessageBox.question(
            self,
            "تنزيل التفسير",
            f"تفسير ({arabic_category}) غير مُنزّل على جهازك.\nهل تريد فتح نافذة إدارة التفاسير لتنزيله الآن؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            logger.info(f"User confirmed opening TafaseerManagerDialog for '{arabic_category}'.")
            self.open_tafaseer_manager(target_category_id=cat_id)
        else:
            logger.debug(f"User cancelled downloading '{arabic_category}'.")

    def open_tafaseer_manager(self, target_category_id: Optional[str] = None):
        logger.info(f"Opening TafaseerManagerDialog from TafaseerDialog (target: {target_category_id})...")
        dialog = TafaseerManagerDialog(self)
        if target_category_id:
            dialog.refresh_list(select_category_id=target_category_id)
        dialog.tafaseer_changed.connect(self._on_tafaseer_collection_changed)
        dialog.exec()
        logger.debug("TafaseerManagerDialog closed.")

    def _on_tafaseer_collection_changed(self):
        logger.debug("Tafaseer collection changed signal received; checking current active category.")
        current_cat_name = self.category_button.text().strip()
        current_cat_id = Category.get_category_by_arabic_name(current_cat_name)

        if not current_cat_id or not Category.is_installed(current_cat_id):
            logger.warning(
                f"Active tafsir '{current_cat_name}' ({current_cat_id}) is no longer installed; resetting to default."
            )
            # The active tafsir was deleted; switch back to bundled default
            default_arabic = Category.get_arabic_name_by_category(DEFAULT_BUNDLED_TAFSIR_ID) or "الميسر"
            self.category_button.setText(default_arabic)
            self.category_button.setAccessibleName(f"المفسر الحالي: {default_arabic}")
            self.tafaseer_manager.set(DEFAULT_BUNDLED_TAFSIR_ID)
            self.tafaseer_updated.emit(default_arabic)
            self.text_edit.setText(
                self.tafaseer_manager.get_tafaseer(self.ayah.sura_number, self.ayah.number)
            )
            self.setWindowTitle(f"{self.title} - {default_arabic}")
            logger.info(f"Active tafsir successfully reset to default: {default_arabic}")

    def copy_content(self):
        logger.debug("User requested to copy Tafaseer content.")
        tafseer_text = self.text_edit.toPlainText()
        category_name = self.category_button.text().strip()
        ayah_info = f"آية {self.ayah.number_in_surah} من {self.ayah.sura_name}، تفسير: {category_name}."
        final_text = f"{ayah_info}\n{tafseer_text}"

        clipboard = QApplication.clipboard()
        clipboard.setText(final_text)

        UniversalSpeech.say(
            f"تم نسخ التفسير: آية {self.ayah.number_in_surah} من {self.ayah.sura_name} تفسير {category_name}."
        )
        _play_sound("copy")
        logger.info(f"Tafseer copied with header: {ayah_info}")

    def save_content(self):
        logger.debug("User requested to save Tafaseer content.")

        file_name = os.path.join(paths.documents_dir, self.windowTitle())
        logger.debug(f"User attempting to save Tafaseer content to: {file_name}")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            file_name,
            "Text files (*.txt)",
        )

        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.text_edit.toPlainText())
                logger.info(f"Tafaseer content successfully saved to: {file_path}")

    def reject(self):
        _play_sound("clos")
        self.deleteLater()

    def closeEvent(self, a0):
        logger.debug("TafaseerDialog closed.")
        return super().closeEvent(a0)

import qtawesome as qta
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QHBoxLayout,
    QLabel, 
    QLineEdit, 
    QPushButton, 
    QListWidget, 
    QListWidgetItem,
    QMessageBox, 
    QInputDialog
)
from PyQt6.QtGui import QKeySequence, QShortcut
from core_functions.bookmark import BookmarkManager
from core_functions.quran.types import NavigationMode
from utils.const import Globals
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class BookmarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("مدير العلامات")
        self.resize(600, 400)
        self.manager = BookmarkManager()
        logger.debug("Bookmark manager dialog opend.")

        self.search_label = QLabel("بحث:")
        self.search_input = QLineEdit()
        self.search_input.setAccessibleName(self.search_label.text())

        self.bookmarks_label = QLabel("العلامات:")
        self.bookmark_list = QListWidget()
        self.bookmark_list.setAccessibleDescription(self.bookmarks_label.text())

        self.update_button = QPushButton("تعديل الاسم")
        self.update_button.setIcon(qta.icon("fa.pencil"))
        self.update_button.setShortcut(QKeySequence("F2"))

        self.delete_button = QPushButton("حذف العلامة")
        self.delete_button.setIcon(qta.icon("fa.trash"))
        self.delete_button.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        
        self.go_button = QPushButton("الذهاب إلى العلامة")
        self.go_button.setIcon(qta.icon("fa.location-arrow"))
        self.go_button.setDefault(True)
        
        self.cancel_button = QPushButton("إغلاق")
        self.cancel_button.setIcon(qta.icon("fa.times"))
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.update_button)
        form_layout.addWidget(self.delete_button)
        form_layout.addWidget(self.go_button)
        form_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.bookmarks_label)
        layout.addWidget(self.bookmark_list)
        layout.addLayout(form_layout)
        self.setLayout(layout)

        self.search_input.textChanged.connect(self.search_bookmarks)
        self.update_button.clicked.connect(self.update_bookmark)
        self.delete_button.clicked.connect(self.delete_bookmark)
        self.go_button.clicked.connect(self.go_to_bookmark)
        self.cancel_button.clicked.connect(self.reject)

        self.load_bookmarks()

    def load_bookmarks(self, bookmarks=None):
        logger.debug("Loading bookmarks...")
        self.bookmark_list.clear()
        if bookmarks is None:
            bookmarks = self.manager.get_bookmarks()

        status = bool(len(bookmarks))
        self.update_button.setEnabled(status)
        self.delete_button.setEnabled(status)
        self.go_button.setEnabled(status)
        if not bookmarks:
            logger.warning("No bookmarks found.")

        for bookmark in bookmarks:
            item_text = f"{bookmark['name']} (آية: {bookmark['ayah_number_in_surah']}, {bookmark['surah_name'].replace('سورة', 'السورة:')}, التاريخ: {bookmark['date']})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, bookmark)
            self.bookmark_list.addItem(item)
        self.bookmark_list.setCurrentRow(0)
        logger.info(f"{len(bookmarks)} bookmarks loaded.")

    def search_bookmarks(self):
        search_text = self.search_input.text()
        logger.debug(f"Searching bookmarks for: {search_text}")
        bookmarks = self.manager.search_bookmarks(search_text)
        self.load_bookmarks(bookmarks)

    def update_bookmark(self):
        logger.debug("Updating bookmark...")
        selected_items = self.bookmark_list.selectedItems()
        if not selected_items:
            logger.warning("No bookmark selected for renaming.")
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("خطأ في التحديد")
            msg_box.setText("لم يتم تحديد أي علامة.")
        
            ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
            msg_box.exec()
            return

        item = selected_items[0]
        bookmark = item.data(Qt.ItemDataRole.UserRole)
        bookmark_id = bookmark["id"]
        logger.debug(f"Renaming bookmark: {bookmark['name']}")
        new_name = ""
    # Create an instance of QInputDialog
        dialog = QInputDialog(self)
        dialog.setWindowTitle("تحديث العلامة")
        dialog.setLabelText("أدخل اسم جديد للعلامة:")
        dialog.setTextValue(bookmark["name"])
    
        # Change the button texts to Arabic.
        dialog.setOkButtonText("حفظ")
        dialog.setCancelButtonText("إلغاء")
    
        # Execute the dialog and check the result.
        if dialog.exec() == QDialog.Accepted:
            new_name = dialog.textValue()
        if new_name:
                self.manager.update_bookmark(bookmark_id, new_name)
                logger.info(f"Bookmark renamed to: {new_name}")
                current_row = self.bookmark_list.currentRow()
                self.load_bookmarks()
                self.bookmark_list.setCurrentRow(current_row)
                self.bookmark_list.setFocus()

    def delete_bookmark(self):
        logger.debug("Deleting bookmark...")

        selected_items = self.bookmark_list.selectedItems()
        if not selected_items:
            logger.warning("No bookmark selected for deletion.")
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("خطأ في التحديد")
            msg_box.setText("لم يتم تحديد أي علامة.")
      
            ok_button = msg_box.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)

            msg_box.exec()

            return

        
        item = selected_items[0]
        bookmark = item.data(Qt.ItemDataRole.UserRole)
        bookmark_id = bookmark["id"]
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("تحذير")
        msg_box.setText(f"هل أنت متأكد إنك تريد حذف هذه العلامة؟\n\nالاسم: {bookmark['name']}")
    
        yes_button = msg_box.addButton("نعم", QMessageBox.ButtonRole.AcceptRole)
        no_button = msg_box.addButton("لا", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            self.manager.delete_bookmark(bookmark_id)
            logger.info(f"Bookmark deleted: {bookmark['name']}")
            self.load_bookmarks()
            self.bookmark_list.setFocus()

    def go_to_bookmark(self):
        selected_items = self.bookmark_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            bookmark = item.data(Qt.ItemDataRole.UserRole)
            logger.info(f"Navigating to bookmark: {bookmark['name']} (Ayah: {bookmark['ayah_number']})")
            self.parent.quran_manager.navigation_mode = NavigationMode.from_int(bookmark["criteria_number"])
            ayah_result = self.parent.quran_manager.get_by_ayah_number(bookmark["ayah_number"])
            self.parent.quran_view.setText(ayah_result)
            self.parent.set_focus_to_ayah(bookmark["ayah_number"])
            self.parent.quran_view.setFocus()
            self.accept()
            Globals.effects_manager.play("move")
            logger.info(f"Moved to Ayah: {bookmark['ayah_number']} in Surah: {bookmark['surah_name']}")
            self.deleteLater()

    def reject(self):
        self.deleteLater()
        
    def closeEvent(self, a0):
        logger.debug("Bookmark manager dialog closed.")
        return super().closeEvent(a0)

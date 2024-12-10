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
from PyQt6.QtGui import QKeySequence
from core_functions.bookmark import BookmarkManager
from utils.const import Globals




class BookmarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("مدير العلامات")
        self.resize(600, 400)

        self.manager = BookmarkManager()

        self.search_label = QLabel("بحث:")
        self.search_input = QLineEdit()
        self.search_input.setAccessibleName(self.search_label.text())

        self.bookmarks_label = QLabel("العلامات:")
        self.bookmark_list = QListWidget()
        self.bookmark_list.setAccessibleDescription(self.bookmarks_label.text())

        self.update_button = QPushButton("تعديل الاسم")
        self.delete_button = QPushButton("حذف العلامة")
        self.delete_button.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        self.go_button = QPushButton("الذهاب إلى العلامة")
        self.go_button.setDefault(True)
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))


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
        self.bookmark_list.clear()
        if bookmarks is None:
            bookmarks = self.manager.get_bookmarks()

        status = bool(len(bookmarks))
        self.update_button.setEnabled(status)
        self.delete_button.setEnabled(status)
        self.go_button.setEnabled(status)

        for bookmark in bookmarks:
            item_text = f"{bookmark['name']} (آية: {bookmark['ayah_number_in_surah']}, {bookmark['surah_name'].replace('سورة', 'السورة:')}, التاريخ: {bookmark['date']})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, bookmark)
            self.bookmark_list.addItem(item)
        self.bookmark_list.setCurrentRow(0)

    def search_bookmarks(self):
        search_text = self.search_input.text()
        bookmarks = self.manager.search_bookmarks(search_text)
        self.load_bookmarks(bookmarks)

    def update_bookmark(self):

        selected_items = self.bookmark_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "لم يتم تحديد أي علامة")
            return

        item = selected_items[0]
        bookmark = item.data(Qt.ItemDataRole.UserRole)
        bookmark_id = bookmark["id"]
        new_name, ok = QInputDialog.getText(self, "Update Bookmark", "Enter new bookmark name:", text=bookmark["name"])
        if ok and new_name:
            self.manager.update_bookmark(bookmark_id, new_name)
            current_row = self.bookmark_list.currentRow()
            self.load_bookmarks()
            self.bookmark_list.setCurrentRow(current_row)
            self.bookmark_list.setFocus()

    def delete_bookmark(self):

        selected_items = self.bookmark_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "لم يتم تحديد أي علامة.")
            return
        
        item = selected_items[0]
        bookmark = item.data(Qt.ItemDataRole.UserRole)
        bookmark_id = bookmark["id"]

        reply = QMessageBox.warning(
                self, "تحذير",
                f"هل أنت متأكد إنك تريد حذف هذه العلامة؟\n\nالاسم: {bookmark['name']}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

        if reply == QMessageBox.StandardButton.Yes:
            self.manager.delete_bookmark(bookmark_id)
            self.load_bookmarks()
            self.bookmark_list.setFocus()

    def go_to_bookmark(self):
        selected_items = self.bookmark_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            bookmark = item.data(Qt.ItemDataRole.UserRole)
            self.parent.quran.type = bookmark["criteria_number"]
            ayah_result = self.parent.quran.get_by_ayah_number(bookmark["ayah_number"])
            self.parent.quran_view.setText(ayah_result["full_text"])
            self.parent.set_focus_to_ayah(bookmark["ayah_number"])
            self.parent.quran_view.setFocus()
            self.accept()
            Globals.effects_manager.play("move")
            self.deleteLater()

    def reject(self):
        self.deleteLater()
        
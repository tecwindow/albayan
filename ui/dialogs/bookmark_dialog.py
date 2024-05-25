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
from core_functions.bookmark import BookmarkManager


class BookmarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Bookmark Manager")
        self.resize(600, 400)

        self.manager = BookmarkManager()

        self.search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setAccessibleName("Search:")

        self.bookmarks_label = QLabel("Bookmarks:")
        self.bookmark_list = QListWidget()
        self.bookmark_list.setAccessibleDescription("Bookmarks:")

        self.update_button = QPushButton("Update Bookmark")
        self.delete_button = QPushButton("Delete Bookmark")
        self.go_button = QPushButton("Go to Bookmark")

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.update_button)
        form_layout.addWidget(self.delete_button)
        form_layout.addWidget(self.go_button)

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

        self.load_bookmarks()

    def load_bookmarks(self, bookmarks=None):
        self.bookmark_list.clear()
        if bookmarks is None:
            bookmarks = self.manager.get_bookmarks()
        for bookmark in bookmarks:
            item_text = f"{bookmark['name']} (Ayah: {bookmark['ayah_number']}, Surah: {bookmark['surah_number']}, Criteria: {bookmark['criteria_number']}, Date: {bookmark['date']})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, bookmark)
            self.bookmark_list.addItem(item)

    def search_bookmarks(self):
        search_text = self.search_input.text()
        bookmarks = self.manager.search_bookmarks(search_text)
        self.load_bookmarks(bookmarks)

    def update_bookmark(self):
        selected_items = self.bookmark_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            bookmark = item.data(Qt.ItemDataRole.UserRole)
            bookmark_id = bookmark["id"]
            new_name, ok = QInputDialog.getText(self, "Update Bookmark", "Enter new bookmark name:")
            if ok and new_name:
                self.manager.update_bookmark(bookmark_id, new_name)
                self.load_bookmarks()
                self.search_input.clear()
            else:
                QMessageBox.warning(self, "Input Error", "Bookmark name cannot be empty.")
        else:
            QMessageBox.warning(self, "Selection Error", "No bookmark selected.")

    def delete_bookmark(self):
        selected_items = self.bookmark_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            bookmark = item.data(Qt.ItemDataRole.UserRole)
            bookmark_id = bookmark["id"]
            self.manager.delete_bookmark(bookmark_id)
            self.load_bookmarks()
        else:
            QMessageBox.warning(self, "Selection Error", "No bookmark selected.")

    def go_to_bookmark(self):
        selected_items = self.bookmark_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            bookmark = item.data(Qt.ItemDataRole.UserRole)

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QPushButton, QInputDialog,
    QLineEdit, QLabel, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from core_functions.tasbih import TasbihController
from core_functions.tasbih.model import TasbihEntry
from utils.const import athkar_db_path
from utils.universal_speech import UniversalSpeech


class TasbihDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.controller = TasbihController(athkar_db_path)
        self.setWindowTitle("المسبحة")
        self.resize(400, 300)
        
        # Create UI elements.
        self.listWidget = QListWidget()
        self.addButton = QPushButton("إضافة تسبيح")
        self.delete_button = QPushButton("حذف تسبيح")
        self.delete_button.setEnabled(False)
        self.incrementButton = QPushButton("زيادة العداد")
        self.incrementButton.setEnabled(False)
        self.resetButton = QPushButton("مسح العداد")
        self.resetButton.setEnabled(False)
        
        # Layout.
        layout = QVBoxLayout()
        layout.addWidget(QLabel("التسابيح"))
        layout.addWidget(self.listWidget)
        layout.addWidget(self.addButton)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.incrementButton)
        layout.addWidget(self.resetButton)
        self.setLayout(layout)
        
        # Connect UI button clicks to slots.
        self.addButton.clicked.connect(self.handle_add_entry)
        self.delete_button.clicked.connect(self.handle_delete_entry)
        self.incrementButton.clicked.connect(self.handle_increment)
        self.resetButton.clicked.connect(self.handle_reset)
        self.listWidget.itemSelectionChanged.connect(self.OnItemSelectionChanged)
        
        # Connect controller signals to dialog slots.
        self.controller.entrieAdded.connect(self.handle_entry_added)
        self.controller.entrieUpdated.connect(self.handle_entry_updated)
        # Populate the list with existing entries.
        self.populate_list()
        self.set_shortcuts()

    def set_shortcuts(self):
        shortcuts = {
            self.incrementButton: "C",
            self.delete_button: "Delete",
            self.resetButton: "R"
        }
        
        for widget, shortcut in shortcuts.items():
            widget.setShortcut(QKeySequence(shortcut))
            
    def OnLineEdit(self):
        self.addButton.setEnabled(bool(self.entryLineEdit.text()))
        
    def OnItemSelectionChanged(self):    
        status = bool(self.listWidget.selectedItems())
        self.incrementButton.setEnabled(status)
        self.resetButton.setEnabled(status)
        self.delete_button.setEnabled(status)
        
    def populate_list(self):
        """Populate the list widget with all current tasbih entries."""
        entries = self.controller.get_all_entries()
        for entry in entries:
            self.add_list_item(entry)
            
    def add_list_item(self, entry):
        """Create and add a QListWidgetItem for the given tasbih entry."""
        item_text = f"{entry.name} | {entry.counter}"
        item = QListWidgetItem(item_text)
        # Store the entry id in the item for later reference.
        item.setData(Qt.ItemDataRole.UserRole, entry.id)
        self.listWidget.addItem(item)
        
    def handle_add_entry(self):
        """Called when the Add button is clicked.
        
        Opens a QInputDialog to obtain the name for the new tasbih entry.
        If a valid name is entered, it is added to the list and the list is focused.
        """
        new_name, ok = QInputDialog.getText(self, "إضافة تسبيح", "أدخل اسم التسبيح:")
        if ok and new_name.strip():
            self.controller.add_entry(new_name.strip())
            self.listWidget.setFocus()

    def handle_entry_added(self, entry: TasbihEntry):
        """
        Slot called when a new entry is added.
        Retrieves the full entry info and adds it to the list.
        """
        self.add_list_item(entry)
        self.listWidget.setCurrentRow(self.listWidget.count() - 1)

            
    def handle_entry_updated(self, entry: TasbihEntry):
        """
        Slot called when an entry is updated (via increment or reset).
        Updates the corresponding list item.
        """
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == entry.id:
                item_text = f"{entry.name} | {entry.counter}"
                item.setText(item_text)
                UniversalSpeech.say(item_text)
                break

    def handle_increment(self):
        """Increment the counter for the selected entry."""
        selected_item = self.listWidget.currentItem()
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        self.controller.increment_entry_counter(entry_id)
        
    def handle_reset(self):
        """Reset the counter for the selected entry."""
        selected_item = self.listWidget.currentItem()
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        self.controller.reset_entry_counter(entry_id)

    def handle_delete_entry(self):
        """Delete the selected entry."""
        selected_item = self.listWidget.currentItem()
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        self.controller.delete_entry(entry_id)
        row = self.listWidget.row(selected_item)
        self.listWidget.takeItem(row)
        self.listWidget.setFocus()
    
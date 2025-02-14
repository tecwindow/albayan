from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QListWidget, QPushButton, QInputDialog, 
     QLabel, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QAction
from core_functions.tasbih import TasbihController
from core_functions.tasbih.model import TasbihEntry
from utils.const import athkar_db_path
from utils.universal_speech import UniversalSpeech

 
class TasbihDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.controller = TasbihController(athkar_db_path)
        self.setWindowTitle("المسبحة")
        self.resize(400, 400)
        
        # Create UI elements.
        self.listWidget = QListWidget()
        self.listWidget.setMinimumHeight(150)  # set list Height
        self.openButton = QPushButton("اختيار التسبيح")
        self.addButton = QPushButton("إضافة تسبيح")
        self.delete_button = QPushButton("حذف تسبيح")
        self.delete_button.setEnabled(False)
        self.incrementButton = QPushButton("زيادة العداد")
        self.incrementButton.setEnabled(False)
        self.decrementButton = QPushButton("إنقاص العداد")
        self.decrementButton.setEnabled(False)
        self.resetButton = QPushButton("مسح العداد")
        self.resetButton.setEnabled(False)
        self.resetAllButton = QPushButton("إعادة تعيين الكل")
        self.resetAllButton.setEnabled(False)
        self.deleteAllButton = QPushButton("حذف الكل")
        self.deleteAllButton.setEnabled(False)
        self.closeButton = QPushButton("إغلاق")

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("التسابيح"))
        mainLayout.addWidget(self.listWidget)

        # Buttons layout (2 rows)
        gridLayout = QGridLayout()
        gridLayout.addWidget(self.openButton, 0, 0)
        gridLayout.addWidget(self.addButton, 0, 1)
        gridLayout.addWidget(self.delete_button, 0, 2)
        gridLayout.addWidget(self.incrementButton, 1, 0)
        gridLayout.addWidget(self.decrementButton, 1, 1)
        gridLayout.addWidget(self.resetButton, 1, 2)
        gridLayout.addWidget(self.resetAllButton, 2, 0)
        gridLayout.addWidget(self.deleteAllButton, 2, 1)
        gridLayout.addWidget(self.closeButton, 2, 2)
        
        mainLayout.addLayout(gridLayout)        
        self.setLayout(mainLayout)

        # Connect UI button clicks to slots.
        self.openButton.clicked.connect(self.open_tasbih_entry_dialog)
        self.addButton.clicked.connect(self.handle_add_entry)
        self.delete_button.clicked.connect(self.handle_delete_entry)
        self.incrementButton.clicked.connect(self.handle_increment)
        self.decrementButton.clicked.connect(self.handle_decrement)
        self.resetButton.clicked.connect(self.handle_reset)
        self.listWidget.itemSelectionChanged.connect(self.OnItemSelectionChanged)
        self.listWidget.itemClicked.connect(self.open_tasbih_entry_dialog)
        self.resetAllButton.clicked.connect(self.handle_reset_all)
        self.deleteAllButton.clicked.connect(self.handle_delete_all)
        self.closeButton.clicked.connect(self.reject)

        # Connect controller signals to dialog slots.
        self.controller.entrieAdded.connect(self.handle_entry_added)
        self.controller.entrieUpdated.connect(self.handle_entry_updated)
        # Populate the list with existing entries.
        self.populate_list()
        self.set_shortcuts()

    def set_shortcuts(self):
        shortcuts = {
            self.incrementButton: "Ctrl+C",
            self.decrementButton: "Ctrl+D",
            self.deleteAllButton: "Ctrl+Delete",
            self.resetAllButton: "Ctrl+Shift+R",
            self.delete_button: "Delete",
            self.addButton: "Ctrl+A",
            self.openButton: "Ctrl+O",
            self.resetButton: "Ctrl+R"
        }
        
        for widget, shortcut in shortcuts.items():
            widget.setShortcut(QKeySequence(shortcut))
            
    def open_tasbih_entry_dialog(self):
        selected_item = self.listWidget.currentItem()
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        tasbih_entry = self.controller.get_entry(entry_id)
        dialog = TasbihEntryDialog(self, self.controller, tasbih_entry)
        UniversalSpeech.say(F"مرحبا بك في المِسْبَحَة، الذِكر: {tasbih_entry.name}، العدد: {tasbih_entry.counter}. استخدم المفاتيح التالية لزيادة العداد: Space, Enter, +,أو C. لإنقاص العداد: D, Ctrl+Space, -, أو Backspace. لإعادة تعيين العداد: Ctrl+R. للمعلومات: V للعدد، T للذِكر، I للكل.")
        dialog.exec()
        
    def OnItemSelectionChanged(self):    
        status = bool(self.listWidget.selectedItems())
        self.openButton.setEnabled(status)
        self.incrementButton.setEnabled(status)
        self.decrementButton.setEnabled(status)
        self.resetButton.setEnabled(status)
        self.delete_button.setEnabled(status)
        self.resetAllButton.setEnabled(status)
        self.deleteAllButton.setEnabled(status)
        
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
        dialog = QInputDialog(self)
        dialog.setWindowTitle("إضافة تسبيح")
        dialog.setLabelText("أدخل اسم التسبيح:")
        dialog.setOkButtonText("حفظ")
        dialog.setCancelButtonText("إلغاء")

        if dialog.exec() == QDialog.Accepted:
            new_name = dialog.textValue().strip()
            if new_name:
                self.controller.add_entry(new_name)
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
        
    def handle_decrement(self):
        """Decrement the counter for the selected entry."""
        selected_item = self.listWidget.currentItem()
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        self.controller.decrement_entry_counter(entry_id)
        
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
    
    def handle_reset_all(self):
        """
        Reset the counter for all entries.
        Displays a confirmation dialog, and if confirmed, calls the controller's reset_all_entries method.
        Afterwards, the UI list is refreshed and focus is set to the last focused index.
        """
        # Save the index of the currently focused item.
        last_focused_index = self.listWidget.currentRow()
    
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("تأكيد إعادة التعيين")
        msg_box.setText("هل أنت متأكد من إعادة تعيين العداد لكل التسابيح؟")

        yes_button = msg_box.addButton("نعم", QMessageBox.ButtonRole.AcceptRole)
        no_button = msg_box.addButton("لا", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            self.controller.reset_all_entries()
            # Refresh the UI: clear and repopulate the list widget.
            self.listWidget.clear()
            self.populate_list()        
            if 0 <= last_focused_index < self.listWidget.count():
                self.listWidget.setCurrentRow(last_focused_index)
            self.listWidget.setFocus()

    def handle_delete_all(self):
        """
        Delete all entries.
        Displays a confirmation dialog, and if confirmed, calls the controller's delete_all_entries method.
        Afterwards, the UI list is cleared.
        """
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("تأكيد الحذف")
        msg_box.setText("هل أنت متأكد من حذف جميع التسابيح؟")

        yes_button = msg_box.addButton("نعم", QMessageBox.ButtonRole.AcceptRole)
        no_button = msg_box.addButton("لا", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            self.controller.delete_all_entries()
            # Clear the list widget to update the UI.
            self.listWidget.clear()
            self.populate_list()
            self.listWidget.setFocus()


class TasbihEntryDialog(QDialog):
    def __init__(self, parent, controller: TasbihController, tasbih_entry: TasbihEntry):
        """
        Sub dialog to show and manage details of a specific tasbih entry.        
        """
        super().__init__(parent)
        self.controller = controller
        self.tasbih_entry = tasbih_entry
        self.setWindowTitle(tasbih_entry.name)
        self.resize(300, 200)
        
        # Layout setup.
        self.layout = QVBoxLayout(self)
        
        # Labels for displaying the tasbih details.
        self.name_label = QLabel("Name: ")
        self.counter_label = QLabel("Counter: 0")
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.counter_label)
        
        # Buttons for actions.
        self.increment_button = QPushButton("Increment")
        self.decrement_button = QPushButton("Decrement")
        self.reset_button = QPushButton("Reset")
        self.close_button = QPushButton("Close")
        
        self.layout.addWidget(self.increment_button)
        self.layout.addWidget(self.decrement_button)
        self.layout.addWidget(self.reset_button)
        self.layout.addWidget(self.close_button)
        
        # Disable focus for all widgets.
        for widget in [self.increment_button, self.decrement_button, self.reset_button, self.close_button]:
            widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Connect button signals to handlers.
        self.increment_button.clicked.connect(self.handle_increment)
        self.decrement_button.clicked.connect(self.handle_decrement)
        self.reset_button.clicked.connect(self.handle_reset)
        self.close_button.clicked.connect(self.close)
        self.controller.entrieUpdated.connect(self.handle_entry_updated)
        
        # Set keyboard shortcuts.
        self.set_shortcuts()
        
        # Load details for the specified tasbih.
        self.load_details()

    def load_details(self, tasbih_entry: TasbihEntry = None):
        """Load and display details for the specific tasbih entry."""
        if tasbih_entry is None:
            tasbih_entry = self.tasbih_entry
        
        self.name_label.setText(tasbih_entry.name)
        self.counter_label.setText(str(tasbih_entry.counter))
        
    def handle_entry_updated(self, tasbih_entry: TasbihEntry):
        self.load_details(tasbih_entry)
        UniversalSpeech.say(str(tasbih_entry.counter))
                
    def handle_increment(self):
        """Handle the increment action."""
        self.controller.increment_entry_counter(self.tasbih_entry.id)
        
    def handle_decrement(self):
        """Handle the decrement action."""
        self.controller.decrement_entry_counter(self.tasbih_entry.id)
        
    def handle_reset(self):
        """Handle the reset action."""
        self.controller.reset_entry_counter(self.tasbih_entry.id)
        
    def set_shortcuts(self):
        """Register keyboard shortcuts for actions."""

        shortcuts = {
            self.increment_button: ["Space", "Return", "C", "+", "="],
            self.decrement_button: ["D", "Ctrl+Space", "-", "Backspace"],
            self.reset_button: "Ctrl+R",
            self.close_button: ["Ctrl+W", "Ctrl+F4"]
        }

        #Info shortcuts
        counter_info_shortcut = QShortcut(QKeySequence("V"), self)
        counter_info_shortcut.activated.connect(lambda: UniversalSpeech.say(str(self.counter_label.text())))
        name_info_shortcut = QShortcut(QKeySequence("T"), self)
        name_info_shortcut.activated.connect(lambda: UniversalSpeech.say(str(self.name_label.text())))
        all_info_shortcut = QShortcut(QKeySequence("I"), self)
        all_info_shortcut.activated.connect(lambda: UniversalSpeech.say(f"{self.name_label.text()}، {self.counter_label.text()}"))

        for widget, key_sequence in shortcuts.items():
            key_sequence = [key_sequence] if isinstance(key_sequence, str) else key_sequence
            for key in key_sequence:
                action = QAction(self)  # Create a new action
                action.setShortcut(QKeySequence(key))  # Set the shortcut
                action.triggered.connect(widget.click)  # Simulate button press
            
                self.addAction(action)  # Attach action to the main window/dialog


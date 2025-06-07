from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QListWidget, QPushButton, QInputDialog, 
    QLabel, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QAction
import qtawesome as qta
from core_functions.tasbih import TasbihController
from core_functions.tasbih.model import TasbihEntry
from utils.const import athkar_db_path
from utils.universal_speech import UniversalSpeech
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class TasbihDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        logger.debug("Initializing TasbihDialog...")
        self.controller = TasbihController(athkar_db_path)
        self.setWindowTitle("المسبحة")
        self.resize(400, 400)
        
        # Create UI elements.
        self.listWidget = QListWidget()
        self.listWidget.setMinimumHeight(150)  # set list Height
        self.listWidget.setAccessibleName("قائمة التسابيح")


        self.openButton = QPushButton()
        self.openButton.setIcon(qta.icon("fa.folder-open"))
        self.openButton.setToolTip("اختيار التسبيح")
        self.openButton.setAccessibleName("اختيار التسبيح")
        
        self.addButton = QPushButton()
        self.addButton.setIcon(qta.icon("fa.plus"))
        self.addButton.setToolTip("إضافة تسبيح")
        self.addButton.setAccessibleName("إضافة تسبيح")
        
        self.editButton = QPushButton()
        self.editButton.setIcon(qta.icon("fa.edit"))
        self.editButton.setToolTip("تعديل التسبيح")
        self.editButton.setAccessibleName("تعديل التسبيح")
        self.editButton.setEnabled(False)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(qta.icon("fa.trash"))
        self.delete_button.setToolTip("حذف تسبيح")
        self.delete_button.setAccessibleName("حذف تسبيح")
        self.delete_button.setEnabled(False)
        
        self.incrementButton = QPushButton()
        self.incrementButton.setIcon(qta.icon("fa.arrow-up"))
        self.incrementButton.setToolTip("زيادة العداد")
        self.incrementButton.setAccessibleName("زيادة العداد")
        self.incrementButton.setEnabled(False)
        
        self.decrementButton = QPushButton()
        self.decrementButton.setIcon(qta.icon("fa.arrow-down"))
        self.decrementButton.setToolTip("إنقاص العداد")
        self.decrementButton.setAccessibleName("إنقاص العداد")
        self.decrementButton.setEnabled(False)
        
        self.resetButton = QPushButton()
        self.resetButton.setIcon(qta.icon("fa.refresh"))
        self.resetButton.setToolTip("مسح العداد")
        self.resetButton.setAccessibleName("مسح العداد")
        self.resetButton.setEnabled(False)
        
        self.resetAllButton = QPushButton()
        self.resetAllButton.setIcon(qta.icon("fa.undo"))
        self.resetAllButton.setToolTip("إعادة تعيين الكل")
        self.resetAllButton.setAccessibleName("إعادة تعيين الكل")
        self.resetAllButton.setEnabled(False)
        
        self.deleteAllButton = QPushButton()
        self.deleteAllButton.setIcon(qta.icon("fa.trash-o"))
        self.deleteAllButton.setToolTip("حذف الكل")
        self.deleteAllButton.setAccessibleName("حذف الكل")
        self.deleteAllButton.setEnabled(False)
        
        self.close_button = QPushButton()
        self.close_button.setIcon(qta.icon("fa.times"))
        self.close_button.setToolTip("إغلاق")
        self.close_button.setAccessibleName("إغلاق")

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("التسابيح"))
        mainLayout.addWidget(self.listWidget)

        # Buttons layout (2 rows)
        gridLayout = QGridLayout()
        gridLayout.addWidget(self.openButton, 0, 0)
        gridLayout.addWidget(self.addButton, 0, 1)
        gridLayout.addWidget(self.editButton, 0, 3)
        gridLayout.addWidget(self.delete_button, 0, 2)
        gridLayout.addWidget(self.incrementButton, 1, 0)
        gridLayout.addWidget(self.decrementButton, 1, 1)
        gridLayout.addWidget(self.resetButton, 1, 2)
        gridLayout.addWidget(self.resetAllButton, 2, 0)
        gridLayout.addWidget(self.deleteAllButton, 2, 1)
        gridLayout.addWidget(self.close_button, 2, 2)

        mainLayout.addLayout(gridLayout)
        self.setLayout(mainLayout)
        
        # Connect UI button clicks to slots.
        self.openButton.clicked.connect(self.open_tasbih_entry_dialog)
        self.addButton.clicked.connect(self.handle_add_entry)
        self.editButton.clicked.connect(self.handle_edit_entry)
        self.delete_button.clicked.connect(self.handle_delete_entry)
        self.incrementButton.clicked.connect(self.handle_increment)
        self.decrementButton.clicked.connect(self.handle_decrement)
        self.resetButton.clicked.connect(self.handle_reset)
        self.listWidget.itemSelectionChanged.connect(self.OnItemSelectionChanged)
        self.listWidget.itemClicked.connect(self.open_tasbih_entry_dialog)
        self.resetAllButton.clicked.connect(self.handle_reset_all)
        self.deleteAllButton.clicked.connect(self.handle_delete_all)
        self.close_button.clicked.connect(self.reject)

        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)


        # Connect controller signals to dialog slots.
        self.controller.entrieAdded.connect(self.handle_entry_added)
        self.controller.entrieUpdated.connect(self.handle_entry_updated)
        # Populate the list with existing entries.
        self.populate_list()
        self.set_shortcuts()
        logger.debug("TasbihDialog Initialized.")

    def set_shortcuts(self):
        """Register keyboard shortcuts for actions."""
        logger.debug("Setting keyboard shortcuts for TasbihDialog.")
        shortcuts = {
            self.incrementButton: "Ctrl+C",
            self.decrementButton: "Ctrl+D",
            self.deleteAllButton: "Ctrl+Delete",
            self.resetAllButton: "Ctrl+Shift+R",
            self.delete_button: "Delete",
            self.addButton: "Ctrl+A",
            self.openButton: "Ctrl+O",
            self.close_button: "Ctrl+W",
            self.resetButton: "Ctrl+R"
        }
        
        for widget, shortcut in shortcuts.items():
            widget.setShortcut(QKeySequence(shortcut))
            logger.debug(f"Shortcut {shortcut} set for {widget.toolTip()}")
            
    def open_tasbih_entry_dialog(self):
        """Open the Tasbih entry dialog for the selected item."""
        logger.debug("the user clicked on a tasbih entry.")
        selected_item = self.listWidget.currentItem()
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        tasbih_entry = self.controller.get_entry(entry_id)
        logger.info(f"Opening Tasbih entry dialog for: {tasbih_entry.name} (ID: {entry_id}, Count: {tasbih_entry.counter})")
        dialog = TasbihEntryDialog(self, self.controller, tasbih_entry)
        UniversalSpeech.say(F"مرحبا بك في المِسْبَحَة، التسبيح: {tasbih_entry.name}، العدد: {tasbih_entry.counter}. استخدم المفاتيح التالية لزيادة العداد: Space, Enter, +,أو C. لإنقاص العداد استخدم: D, Ctrl+Space, -, أو Backspace. لإعادة تعيين العداد استخدم: Ctrl+R. للمعلومات استخدم: V للعدد، T للذِكر، I للكل.")
        dialog.exec()

    def update_edit_button_state(self):
        selected_item = self.listWidget.currentItem()
        if not selected_item:
            self.editButton.setEnabled(False)
            return

        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        entry = self.controller.get_entry(entry_id)
        if entry and entry.counter > 0:
            self.editButton.setEnabled(False)
        else:
            self.editButton.setEnabled(True)


    def OnItemSelectionChanged(self):    
        status = bool(self.listWidget.selectedItems())
        self.openButton.setEnabled(status)
        self.incrementButton.setEnabled(status)
        self.decrementButton.setEnabled(status)
        self.resetButton.setEnabled(status)
        self.delete_button.setEnabled(status)
        self.resetAllButton.setEnabled(status)
        self.editButton.setEnabled(status)
        self.deleteAllButton.setEnabled(status)
        self.update_edit_button_state()

        logger.debug(f"List item selection status: {status}. Buttons enabled: {status}.")
        
    def populate_list(self):
        """Populate the list widget with all current tasbih entries."""
        logger.debug("Populating Tasbih list widget with entries.")        
        entries = self.controller.get_all_entries()
        for entry in entries:
            self.add_list_item(entry)
        logger.debug("Tasbih list populated.")
        
    def add_list_item(self, entry):
        logger.debug(f"Adding Tasbih entry to list: {entry.name} (ID: {entry.id}, Count: {entry.counter})")
        """Create and add a QListWidgetItem for the given tasbih entry."""
        item_text = f"{entry.name} | {entry.counter}"
        item = QListWidgetItem(item_text)
        # Store the entry id in the item for later reference.
        item.setData(Qt.ItemDataRole.UserRole, entry.id)
        self.listWidget.addItem(item)
        logger.debug(f"Added Tasbih entry to list: {entry.name} (ID: {entry.id}, Count: {entry.counter})")

    def handle_edit_entry(self):
        selected_item = self.listWidget.currentItem()
        if not selected_item:
            return
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        old_entry = self.controller.get_entry(entry_id)

        new_name, ok = QInputDialog.getText(self, "تعديل التسبيح", "أدخل الاسم الجديد:", text=old_entry.name)
        if ok and new_name.strip():
            self.controller.update_entry_name(entry_id, new_name.strip())
            updated_entry = self.controller.get_entry(entry_id)
            item_text = f"{updated_entry.name} | {updated_entry.counter}"
            selected_item.setText(item_text)
            UniversalSpeech.say(f"تم تعديل التسبيح إلى: {updated_entry.name}")

    def handle_add_entry(self):
        """Called when the Add button is clicked.
        
        Opens a QInputDialog to obtain the name for the new tasbih entry.
        If a valid name is entered, it is added to the list and the list is focused.
        """
        logger.debug("Opening Add Tasbih Entry dialog.")
        dialog = QInputDialog(self)
        dialog.setWindowTitle("إضافة تسبيح")
        dialog.setLabelText("أدخل اسم التسبيح:")
        dialog.setOkButtonText("حفظ")
        dialog.setCancelButtonText("إلغاء")

        if dialog.exec() == QDialog.Accepted:
            new_name = dialog.textValue().strip()
            if new_name:
                logger.info(f"Adding new Tasbih entry: {new_name}")
                self.controller.add_entry(new_name)
                self.listWidget.setFocus()
        else:
            logger.warning("Attempted to add a Tasbih entry with an empty name.")

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
        logger.debug(f"Updating Tasbih entry in list: {entry.name} (ID: {entry.id}, New Count: {entry.counter})")
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == entry.id:
                item_text = f"{entry.name} | {entry.counter}"
                item.setText(item_text)
                logger.debug(f"Updated Tasbih entry: {entry.name} (ID: {entry.id}, New Count: {entry.counter})")
                UniversalSpeech.say(item_text)
                break

    def handle_increment(self):
        """Increment the counter for the selected entry."""
        logger.debug("Increment button has been clicked")
        selected_item = self.listWidget.currentItem()
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        logger.debug(f"Incrementing counter for Tasbih entry ID: {entry_id}")
        self.controller.increment_entry_counter(entry_id)
        self.update_edit_button_state()
        
    def handle_decrement(self):
        """Decrement the counter for the selected entry."""
        logger.debug("Decrement button has been clicked")
        selected_item = self.listWidget.currentItem()
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        logger.debug(f"Decrementing counter for Tasbih entry ID: {entry_id}")
        self.controller.decrement_entry_counter(entry_id)
        self.update_edit_button_state()        

    def handle_reset(self):
        """Reset the counter for the selected entry."""
        logger.debug("Reset button has been clicked")
        selected_item = self.listWidget.currentItem()
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        logger.warning(f"Resetting counter for Tasbih entry ID: {entry_id}")
        self.controller.reset_entry_counter(entry_id)
        self.update_edit_button_state()

    def handle_delete_entry(self):
        """Delete the selected entry."""
        logger.debug("Delete button has been clicked")
        selected_item = self.listWidget.currentItem()
        entry_id = selected_item.data(Qt.ItemDataRole.UserRole)
        logger.debug(f"Deleting Tasbih entry ID: {entry_id}")
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
        logger.warning("User requested to reset all Tasbih counters.")
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
            logger.debug("Resetting all Tasbih counters.")
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
        logger.debug("User requested to delete all Tasbih entries.")
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("تأكيد الحذف")
        msg_box.setText("هل أنت متأكد من رغبتك في حذف جميع التسابيح؟\nسيتم حذف التسابيح المضافة يدويًا، وإعادة تعيين العدادات للتسابيح الافتراضية.")

        yes_button = msg_box.addButton("نعم", QMessageBox.ButtonRole.AcceptRole)
        no_button = msg_box.addButton("لا", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            logger.debug("Deleting all Tasbih entries.")
            self.controller.delete_all_entries()
            # Clear the list widget to update the UI.
            self.listWidget.clear()
            logger.debug("All Tasbih entries deleted.")
            self.populate_list()
            self.listWidget.setFocus()

    def reject(self):
        self.deleteLater()

    def closeEvent(self, a0):
        logger.debug("TasbihDialog closed.")
        return super().closeEvent(a0)


class TasbihEntryDialog(QDialog):
    def __init__(self, parent, controller: TasbihController, tasbih_entry: TasbihEntry):
        """
        Sub dialog to show and manage details of a specific tasbih entry.        
        """
        super().__init__(parent)
        self.controller = controller
        self.tasbih_entry = tasbih_entry
        logger.debug(f"Opening TasbihEntryDialog for: {tasbih_entry.name} (ID: {tasbih_entry.id}, Count: {tasbih_entry.counter})")
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
        self.increment_button = QPushButton("زيادة عداد التسبيح")
        self.decrement_button = QPushButton("إنقاص عداد التسبيح")
        self.reset_button = QPushButton("إعادة تعيين عداد التسبيح")
        self.close_button = QPushButton("إغلاق")
        
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
        self.close_button.clicked.connect(self.reject)
        self.controller.entrieUpdated.connect(self.handle_entry_updated)
        
        # Set keyboard shortcuts.
        self.set_shortcuts()
        
        # Load details for the specified tasbih.
        self.load_details()

    def load_details(self, tasbih_entry: TasbihEntry = None):
        """Load and display details for the specific tasbih entry."""
        if tasbih_entry is None:
            tasbih_entry = self.tasbih_entry
        
            logger.debug(f"Loading details for Tasbih entry: {tasbih_entry.name} (ID: {tasbih_entry.id}, Count: {tasbih_entry.counter})")
        self.name_label.setText(tasbih_entry.name)
        self.counter_label.setText(str(tasbih_entry.counter))
        
    def handle_entry_updated(self, tasbih_entry: TasbihEntry):
        self.load_details(tasbih_entry)
        logger.debug(f"Tasbih entry updated: {tasbih_entry.name} (ID: {tasbih_entry.id}, New Count: {tasbih_entry.counter})")
        UniversalSpeech.say(str(tasbih_entry.counter))
                
    def handle_increment(self):
        """Handle the increment action."""
        logger.debug(f"Incrementing Tasbih counter (ID: {self.tasbih_entry.id})")
        self.controller.increment_entry_counter(self.tasbih_entry.id)
        
    def handle_decrement(self):
        """Handle the decrement action."""
        logger.debug(f"Decrementing Tasbih counter (ID: {self.tasbih_entry.id})")
        self.controller.decrement_entry_counter(self.tasbih_entry.id)
        
    def handle_reset(self):
        """Handle the reset action."""
        logger.warning(f"Resetting Tasbih counter (ID: {self.tasbih_entry.id})")
        self.controller.reset_entry_counter(self.tasbih_entry.id)
        
    def set_shortcuts(self):
        """Register keyboard shortcuts for actions."""
        logger.debug("Setting keyboard shortcuts for TasbihEntryDialog.")

        shortcuts = {
            self.increment_button: ["Space", "Return", "Enter", "C", "+", "="],
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
                logger.debug(f"Shortcut {key} set for {widget.toolTip()}")

    def reject(self):
        self.deleteLater()

    def closeEvent(self, a0):
        logger.debug("TasbihEntryDialog closed.")
        return super().closeEvent(a0)

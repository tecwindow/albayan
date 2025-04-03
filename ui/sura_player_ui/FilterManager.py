import re
from typing import List, Dict
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QComboBox
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)



@dataclass
class Item:
    id: int
    text: str
    
    
@dataclass
class Category:
    id: int
    label: str
    items: List[Item]
    widget : QComboBox
    selected_item_text: str = ""
    search_query: str = ""


class FilterManager(QObject):
    filterModeChanged = pyqtSignal(bool)
    activeCategoryChanged = pyqtSignal(str)
    itemSelectionChanged = pyqtSignal(QComboBox, int)
    itemeSelected = pyqtSignal()
    selectOutOfRange = pyqtSignal(int)
    filteredItemsUpdated = pyqtSignal(QComboBox, list, str)
    searchQueryUpdated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        logger.debug("initializing FilterManager...")
        self.categories: List[Category] = []
        self.active = False  
        self.current_category_index = 0
        logger.debug("FilterManager initialized.")


    def set_category(self, id, label: str, items: List[Item], widget: QComboBox) -> None:
        category = Category(id, label, items, widget)
        self.categories.append(category)
        logger.debug(f"Category added: ID={id}, Label={label}, Items={len(items)}.")


    def change_category_items(self, id: int, new_items: List[Item]) -> None:
        for category in self.categories:
            if category.id == id:
                logger.debug(f"Changing items for category ID={id}. New item count: {len(new_items)}.")
                category.items = new_items
                
    def toggle_filter_mode(self) -> None:
        """Toggle filter mode."""
        self.active = not self.active
        self.filterModeChanged.emit(self.active)
        logger.debug(f"Filter mode {'enabled' if self.active else 'disabled'}.")
        if not self.active:
            self.clear_filters()

    def switch_category(self, direction: int) -> None:
        """Switch between categories."""
        if not self.categories:
            logger.warning("No categories available to switch.")
            return
        self.current_category_index = (self.current_category_index + direction) % len(self.categories)
        active_category = self.categories[self.current_category_index]
        self.activeCategoryChanged.emit(active_category.label)
        logger.debug(f"Switched to category: {active_category.label}.")
        self.update_filtered_items()

    def navigate_items(self, direction: int) -> None:
        """Navigate through items in the active category."""
        if not self.categories:
            logger.warning("No categories available for navigation.")
            return
        active_category = self.categories[self.current_category_index]
        combo_box = active_category.widget
        current_index = combo_box.currentIndex()
        new_index = max(0, min(combo_box.count() - 1, current_index + direction))
        self.itemSelectionChanged.emit(combo_box, new_index)
        logger.debug(f"Navigated to item index {new_index} in category {active_category.label}.")
        if current_index + direction in (-1, combo_box.count()):
            self.selectOutOfRange.emit(current_index + direction)
            logger.debug(f"Selection out of range: {current_index + direction}.")


    def filter_items(self, char: str):
        """Filter items in the active category based on the search query."""
        active_category = self.categories[self.current_category_index]
        active_category.search_query += char
        self.searchQueryUpdated.emit(active_category.search_query)
        logger.debug(f"Filtering with query: {active_category.search_query}.")
        self.update_filtered_items()

    def delete_last_char(self):
        """Delete the last character from the search query."""
        active_category = self.categories[self.current_category_index]
        if active_category.search_query:
            active_category.search_query = active_category.search_query[:-1]
            self.searchQueryUpdated.emit(active_category.search_query)
            logger.debug(f"Updated search query after deletion: {active_category.search_query}.")
            self.update_filtered_items()

    def update_filtered_items(self):
        """Update the items in the active category based on the search query."""
        active_category = self.categories[self.current_category_index]
        combo_box = active_category.widget
        all_items = active_category.items
        #active_category.selected_item_text = combo_box.currentText()
        filtered_items = [item for item in all_items if item.text.startswith(active_category.search_query)]
        self.filteredItemsUpdated.emit(combo_box, filtered_items, combo_box.currentText())
        logger.debug(f"Filtered items updated for category {active_category.label}. "
                     f"Query: {active_category.search_query}, Matches: {len(filtered_items)}.")


    def clear_filters(self):
        """Clear all search filters."""
        for category in self.categories:
            category.search_query = ""
            combo_box = category.widget
            self.filteredItemsUpdated.emit(combo_box, category.items, combo_box.currentText())
        logger.debug("All filters cleared.")


    def handle_key_press(self, event: QKeyEvent) -> bool:
        """Handle key press events."""
        #logger.debug(f"Key pressed: {event.text()} (KeyCode: {event.key()})")
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_F:
            logger.debug("Ctrl+F detected, toggling filter mode.")
            self.toggle_filter_mode()
            return True
        elif self.active:
            logger.debug("Filter mode is active, processing key events.")
            if event.key() == Qt.Key.Key_Left:
                logger.debug("Left arrow key detected, switching to previous category.")
                self.switch_category(-1)
                return True
            elif event.key() == Qt.Key.Key_Right:
                logger.debug("Right arrow key detected, switching to next category.")
                self.switch_category(1)
                return True
            elif event.key() == Qt.Key.Key_Up:
                logger.debug("Up arrow key detected, navigating up in the item list.")
                self.navigate_items(-1)
                return True
            elif event.key() == Qt.Key.Key_Down:
                logger.debug("Down arrow key detected, navigating down in the item list.")
                self.navigate_items(1)
                return True
            elif event.key() == Qt.Key.Key_Home:
                logger.debug("Home key detected, jumping to the first item in the list.")
                self.navigate_items(-1000)
                return True
            elif event.key() == Qt.Key.Key_End:
                logger.debug("End key detected, jumping to the last item in the list.")
                self.navigate_items(1000)
                return True
            elif event.key() == Qt.Key.Key_PageUp:
                logger.debug("Page Up key detected, jumping up 10 items.")
                self.navigate_items(-10)
                return True
            elif event.key() == Qt.Key.Key_PageDown:
                logger.debug("Page Down key detected, jumping down 10 items.")
                self.navigate_items(10)
                return True
            elif event.key() == Qt.Key.Key_Backspace:
                logger.debug("Backspace key detected, deleting last character from search query.")
                self.delete_last_char()
                return True
            elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                logger.debug("Enter/Return key detected, selecting item and exiting filter mode.")
                self.itemeSelected.emit()
                self.toggle_filter_mode()
                return True
            elif event.key() == Qt.Key.Key_Escape:
                logger.debug("Escape key detected, toggling filter mode off.")
                self.toggle_filter_mode()
                return True
            elif re.search(r"[أ-يئءؤآ]", event.text()):
                logger.debug(f"Arabic character detected: {event.text()}, filtering items.")
                self.filter_items(event.text())
                return True
        #logger.debug("Key event did not match any conditions, returning False.")
        return False

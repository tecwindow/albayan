import re
from typing import List, Dict
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QComboBox


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
        self.categories: List[Category] = []
        self.active = False  
        self.current_category_index = 0

    def set_category(self, id, label: str, items: List[Item], widget: QComboBox) -> None:
        category = Category(id, label, items, widget)
        self.categories.append(category)

    def change_category_items(self, id: int, new_items: List[Item]) -> None:
        for category in self.categories:
            if category.id == id:
                category.items = new_items
                
    def toggle_filter_mode(self) -> None:
        """Toggle filter mode."""
        self.active = not self.active
        self.filterModeChanged.emit(self.active)
        if not self.active:
            self.clear_filters()

    def switch_category(self, direction: int) -> None:
        """Switch between categories."""
        self.current_category_index = (self.current_category_index + direction) % len(self.categories)
        active_category = self.categories[self.current_category_index]
        self.activeCategoryChanged.emit(active_category.label)
        self.update_filtered_items()

    def navigate_items(self, direction: int) -> None:
        """Navigate through items in the active category."""
        active_category = self.categories[self.current_category_index]
        combo_box = active_category.widget
        current_index = combo_box.currentIndex()
        new_index = max(0, min(combo_box.count() - 1, current_index + direction))
        self.itemSelectionChanged.emit(combo_box, new_index)
        if current_index + direction in (-1, combo_box.count()):
            self.selectOutOfRange.emit(current_index + direction)

    def filter_items(self, char: str):
        """Filter items in the active category based on the search query."""
        active_category = self.categories[self.current_category_index]
        active_category.search_query += char
        self.searchQueryUpdated.emit(active_category.search_query)
        self.update_filtered_items()

    def delete_last_char(self):
        """Delete the last character from the search query."""
        active_category = self.categories[self.current_category_index]
        if active_category.search_query:
            active_category.search_query = active_category.search_query[:-1]
            self.searchQueryUpdated.emit(active_category.search_query)
            self.update_filtered_items()

    def update_filtered_items(self):
        """Update the items in the active category based on the search query."""
        active_category = self.categories[self.current_category_index]
        combo_box = active_category.widget
        all_items = active_category.items
        #active_category.selected_item_text = combo_box.currentText()
        filtered_items = [item for item in all_items if item.text.startswith(active_category.search_query)]
        self.filteredItemsUpdated.emit(combo_box, filtered_items, combo_box.currentText())

    def clear_filters(self):
        """Clear all search filters."""
        for category in self.categories:
            category.search_query = ""
            combo_box = category.widget
            self.filteredItemsUpdated.emit(combo_box, category.items, combo_box.currentText())

    def handle_key_press(self, event: QKeyEvent) -> bool:
        """Handle key press events."""
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_F:
            self.toggle_filter_mode()
            return True
        elif self.active:
            if event.key() == Qt.Key.Key_Left:
                self.switch_category(-1)
                return True
            elif event.key() == Qt.Key.Key_Right:
                self.switch_category(1)
                return True
            elif event.key() == Qt.Key.Key_Up:
                self.navigate_items(-1)
                return True
            elif event.key() == Qt.Key.Key_Down:
                self.navigate_items(1)
                return True
            elif event.key() == Qt.Key.Key_Home:
                self.navigate_items(-1000)
                return True
            elif event.key() == Qt.Key.Key_End:
                self.navigate_items(1000)
                return True
            elif event.key() == Qt.Key.Key_PageUp:
                self.navigate_items(-10)
                return True
            elif event.key() == Qt.Key.Key_PageDown:
                self.navigate_items(10)
                return True
            elif event.key() == Qt.Key.Key_Backspace:
                self.delete_last_char()
                return True
            elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.itemeSelected.emit()
                self.toggle_filter_mode()
                return True
            elif event.key() == Qt.Key.Key_Escape:
                self.toggle_filter_mode()
                return True
            elif re.search(r"[أ-يئءؤآ]", event.text()):
                self.filter_items(event.text())
                return True

        return False

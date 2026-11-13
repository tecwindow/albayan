"""
Shortcuts Dialog for Albayan.
Allows users to view, add, edit, delete, and disable keyboard shortcuts,
with conflict detection, and reset to defaults.
"""
from typing import Optional, List
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeView,
    QAbstractItemView,
    QLineEdit,
    QMessageBox,
    QInputDialog,
    QFrame,
    QKeySequenceEdit,
)
from PySide6.QtGui import (
    QKeySequence,
    QFont,
    QShortcut,
    QStandardItemModel,
    QStandardItem,
)
from PySide6.QtCore import Qt, Signal, QModelIndex
from utils.shortcuts_manager import ShortcutsManager, DEFAULT_SHORTCUTS
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ShortcutCaptureDialog(QDialog):
    """
    Modal dialog that allows the user to set a key combination
    using standard QKeySequenceEdit and default Qt keyboard navigation.
    """

    def __init__(self, parent=None, action_label: str = "", current_shortcut: str = ""):
        super().__init__(parent)
        self.action_label = action_label
        self.captured_shortcut: Optional[str] = None

        self.setWindowTitle("تسجيل الاختصار")
        self.setModal(True)
        self.resize(420, 200)

        self._init_ui(current_shortcut)

    def _init_ui(self, current_shortcut: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title_label = QLabel(f"الإجراء: {self.action_label}")
        font = title_label.font()
        font.setPointSize(11)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        hint_label = QLabel(
            "اضغط داخل حقل الاختصار ثم اضغط المفاتيح المطلوبة على لوحة المفاتيح:"
        )
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)

        self.key_sequence_edit = QKeySequenceEdit(self)
        if current_shortcut:
            self.key_sequence_edit.setKeySequence(QKeySequence(current_shortcut))
        self.key_sequence_edit.setAccessibleName("حقل إدخال الاختصار")
        layout.addWidget(self.key_sequence_edit)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_button = QPushButton("حفظ")
        self.save_button.setAccessibleName("حفظ الاختصار المدخل")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self._on_save)

        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setAccessibleName("إلغاء تسجيل الاختصار والعودة")
        self.cancel_button.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)

    def _on_save(self):
        seq = self.key_sequence_edit.keySequence()
        seq_str = seq.toString(QKeySequence.SequenceFormat.PortableText).strip()
        if not seq_str or seq.isEmpty():
            QMessageBox.information(
                self,
                "تنبيه",
                "لم يتم إدخال أي اختصار. يرجى إدخال اختصار أولاً أو الضغط على إلغاء.",
            )
            return

        self.captured_shortcut = seq_str
        self.accept()

    def get_shortcut(self) -> Optional[str]:
        return self.captured_shortcut


ROLE_ITEM_TYPE = Qt.ItemDataRole.UserRole
ROLE_ACTION_ID = Qt.ItemDataRole.UserRole + 1
ROLE_SHORTCUT = Qt.ItemDataRole.UserRole + 2
ROLE_ACTION_LABEL = Qt.ItemDataRole.UserRole + 3


class ShortcutsDialog(QDialog):
    """
    Dedicated dialog for managing Albayan shortcuts.
    Displays a categorized list of all actions, with buttons to Add, Edit,
    Delete/Disable, and Reset shortcuts, with full conflict resolution.
    """

    shortcuts_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إدارة اختصارات لوحة المفاتيح")
        self.resize(820, 600)
        self.setModal(True)

        self._init_ui()
        self._populate_tree()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("بحث:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("ابحث عن إجراء أو اختصار...")
        self.search_box.setAccessibleName("البحث في اختصارات لوحة المفاتيح")
        self.search_box.textChanged.connect(self._filter_tree)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # Shortcuts Tree (Pure single-column hierarchy: Category -> Action -> Shortcut)
        self.tree = QTreeView()
        self.tree.setObjectName("shortcutsTree")
        self.tree.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.tree.setAccessibleName("شجرة اختصارات لوحة المفاتيح")
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        #self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        #self.tree.setTabKeyNavigation(False)
        #self.tree.setRootIsDecorated(True)
        #self.tree.setAlternatingRowColors(True)
        #self.tree.setUniformRowHeights(True)
        #self.tree.setHeaderHidden(True)

        self.model = QStandardItemModel(self)
        self.model.setColumnCount(1)
        self.tree.setModel(self.model)
        self.tree.doubleClicked.connect(self._on_item_double_clicked)

        # Shortcuts strictly for actions on the tree (no shortcuts for navigation)
        del_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self.tree)
        del_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        del_shortcut.activated.connect(self._on_tree_delete)

        edit_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F2), self.tree)
        edit_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        edit_shortcut.activated.connect(self._on_edit)

        enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self.tree)
        enter_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        enter_shortcut.activated.connect(self._on_tree_enter)

        add_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Insert), self.tree)
        add_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        add_shortcut.activated.connect(self._on_add)

        layout.addWidget(self.tree)

        # Main Action Buttons Row
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("إضافة اختصار")
        self.add_btn.setAccessibleName("إضافة اختصار جديد للإجراء المحدد")
        self.add_btn.clicked.connect(self._on_add)
        btn_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("تعديل الاختصار")
        self.edit_btn.setAccessibleName("تعديل الاختصار المحدد")
        self.edit_btn.clicked.connect(self._on_edit)
        btn_layout.addWidget(self.edit_btn)

        self.remove_btn = QPushButton("حذف الاختصار")
        self.remove_btn.setAccessibleName("حذف الاختصار المحدد أو تعطيل الإجراء")
        self.remove_btn.clicked.connect(self._on_remove)
        btn_layout.addWidget(self.remove_btn)

        self.toggle_disable_btn = QPushButton("تعطيل / تفعيل")
        self.toggle_disable_btn.setAccessibleName("تبديل حالة تفعيل أو تعطيل الاختصار للإجراء المحدد")
        self.toggle_disable_btn.clicked.connect(self._on_toggle_disable)
        btn_layout.addWidget(self.toggle_disable_btn)

        self.reset_one_btn = QPushButton("استعادة الافتراضي للإجراء")
        self.reset_one_btn.setAccessibleName("استعادة الاختصارات الافتراضية للإجراء المحدد")
        self.reset_one_btn.clicked.connect(self._on_reset_one)
        btn_layout.addWidget(self.reset_one_btn)

        layout.addLayout(btn_layout)

        # Bottom row: Reset All and Close
        bottom_layout = QHBoxLayout()

        self.reset_all_btn = QPushButton("استعادة كافة الاختصارات الافتراضية")
        self.reset_all_btn.setAccessibleName("إعادة تعيين كافة اختصارات البرنامج إلى الوضع الافتراضي")
        self.reset_all_btn.clicked.connect(self._on_reset_all)
        bottom_layout.addWidget(self.reset_all_btn)

        bottom_layout.addStretch()

        self.close_btn = QPushButton("إغلاق")
        self.close_btn.setAccessibleName("إغلاق نافذة إدارة الاختصارات")
        self.close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(self.close_btn)

        layout.addLayout(bottom_layout)

    def _populate_tree(self, filter_text: str = ""):
        """Fill tree with clean classic 3 levels: Category -> Action -> Shortcut."""
        self.model.clear()
        self.model.setColumnCount(1)
        filter_lower = filter_text.strip().lower()

        for category, actions in DEFAULT_SHORTCUTS.items():
            cat_item = QStandardItem(category)
            cat_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            cat_item.setData("category", ROLE_ITEM_TYPE)
            cat_item.setAccessibleText(f"فئة {category}")
            font = cat_item.font()
            font.setBold(True)
            cat_item.setFont(font)

            has_children = False
            for action_id, info in actions.items():
                label = info["label"]
                current_shortcuts = ShortcutsManager.get(action_id)

                if filter_lower:
                    all_sc = " ".join(current_shortcuts)
                    searchable = f"{label} {all_sc} {category}".lower()
                    if filter_lower not in searchable:
                        continue

                # Level 2: Action item (clean label only)
                item_action = QStandardItem(label)
                item_action.setData("action", ROLE_ITEM_TYPE)
                item_action.setData(action_id, ROLE_ACTION_ID)
                item_action.setData(label, ROLE_ACTION_LABEL)
                item_action.setAccessibleText(f"إجراء {label}")
                item_action.setEditable(False)

                # Level 3: Shortcut item (only the first/primary shortcut is shown)
                if current_shortcuts:
                    primary_sc = current_shortcuts[0]
                    item_sc = QStandardItem(primary_sc)
                    item_sc.setData("shortcut", ROLE_ITEM_TYPE)
                    item_sc.setData(action_id, ROLE_ACTION_ID)
                    item_sc.setData(label, ROLE_ACTION_LABEL)
                    item_sc.setData(primary_sc, ROLE_SHORTCUT)
                    item_sc.setAccessibleText(f"اختصار {primary_sc}")
                    item_sc.setEditable(False)
                    item_action.appendRow(item_sc)
                else:
                    item_empty = QStandardItem("بلا اختصار")
                    item_empty.setData("placeholder", ROLE_ITEM_TYPE)
                    item_empty.setData(action_id, ROLE_ACTION_ID)
                    item_empty.setData(label, ROLE_ACTION_LABEL)
                    item_empty.setForeground(Qt.GlobalColor.gray)
                    item_empty.setAccessibleText(f"الإجراء {label} بلا اختصار")
                    item_empty.setEditable(False)
                    item_action.appendRow(item_empty)

                cat_item.appendRow(item_action)
                has_children = True

            if has_children:
                self.model.appendRow(cat_item)


    def _filter_tree(self, text: str):
        self._populate_tree(text)

    def _get_selection_info(self) -> Optional[dict]:
        """
        Return info about currently selected item:
        {
            "type": "category" | "action" | "shortcut" | "placeholder",
            "action_id": str or None,
            "action_label": str or None,
            "shortcut": str or None,
        }
        """
        selection_model = self.tree.selectionModel()
        if not selection_model:
            return None
        indexes = selection_model.selectedRows(0)
        if not indexes:
            return None
        item = self.model.itemFromIndex(indexes[0])
        if not item:
            return None

        item_type = item.data(ROLE_ITEM_TYPE)
        action_id = item.data(ROLE_ACTION_ID)
        action_label = item.data(ROLE_ACTION_LABEL)

        if item_type in ("shortcut", "placeholder"):
            shortcut_str = item.data(ROLE_SHORTCUT)
            return {
                "type": item_type,
                "action_id": action_id,
                "action_label": action_label,
                "shortcut": shortcut_str,
            }
        elif item_type == "action":
            return {
                "type": "action",
                "action_id": action_id,
                "action_label": action_label,
                "shortcut": None,
            }
        elif item_type == "category":
            return {
                "type": "category",
                "action_id": None,
                "action_label": None,
                "shortcut": None,
            }
        return None

    def _get_selected_action_id(self) -> Optional[tuple[str, str]]:
        """Return (action_id, action_label) of currently selected action/shortcut, or None."""
        info = self._get_selection_info()
        if not info or not info["action_id"]:
            return None
        return (info["action_id"], info["action_label"])

    def _on_item_double_clicked(self, index: QModelIndex):
        info = self._get_selection_info()
        if not info or not info["action_id"]:
            return
        if info["type"] == "placeholder":
            self._on_add()
        elif info["type"] in ("action", "shortcut"):
            self._on_edit()

    def _on_tree_delete(self):
        info = self._get_selection_info()
        if info and info["action_id"]:
            self._on_remove()

    def _on_tree_enter(self):
        info = self._get_selection_info()
        if not info or not info["action_id"]:
            return
        if info["type"] == "placeholder":
            self._on_add()
        elif info["type"] in ("action", "shortcut"):
            self._on_edit()

    def _handle_conflict(self, shortcut: str, target_action_id: str) -> bool:
        """
        Check if shortcut conflicts with another action.
        If conflict exists, prompt user to reassign.
        Returns True if resolved and safe to proceed, False if user cancelled.
        """
        conflict = ShortcutsManager.find_conflict(shortcut, exclude_action_id=target_action_id)
        if not conflict:
            return True

        conflicting_id, conflicting_label = conflict
        target_label = ShortcutsManager.get_action_label(target_action_id)

        reply = QMessageBox.question(
            self,
            "تعارض في الاختصار",
            f"الاختصار '{shortcut}' مستخدم بالفعل للإجراء '{conflicting_label}'.\n\n"
            f"هل ترغب في إزالته من '{conflicting_label}' وتعيينه للإجراء '{target_label}'؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            ShortcutsManager.remove_shortcut(conflicting_id, shortcut)
            logger.info(f"Removed conflicting shortcut '{shortcut}' from '{conflicting_id}'.")
            return True
        return False

    def _on_add(self):
        """Add or set shortcut for the selected action."""
        info = self._get_selection_info()
        if not info or not info["action_id"]:
            QMessageBox.information(self, "تنبيه", "يرجى تحديد إجراء أو اختصار من القائمة أولاً.")
            return
        action_id = info["action_id"]
        label = info["action_label"]

        dlg = ShortcutCaptureDialog(self, action_label=label)
        if dlg.exec():
            new_shortcut = dlg.get_shortcut()
            if not new_shortcut:
                return

            if not self._handle_conflict(new_shortcut, action_id):
                return

            current_shortcuts = ShortcutsManager.get(action_id)
            if new_shortcut in current_shortcuts:
                return

            # Set new shortcut as primary at the beginning
            updated = [new_shortcut] + [s for s in current_shortcuts if s != new_shortcut]
            ShortcutsManager.set(action_id, updated)
            self._populate_tree(self.search_box.text())
            self.shortcuts_changed.emit()
            logger.info(f"Added shortcut '{new_shortcut}' to '{action_id}'.")

    def _on_edit(self):
        """Edit the primary shortcut for the selected action."""
        info = self._get_selection_info()
        if not info or not info["action_id"]:
            QMessageBox.information(self, "تنبيه", "يرجى تحديد إجراء أو اختصار من القائمة أولاً.")
            return

        action_id = info["action_id"]
        label = info["action_label"]

        current_shortcuts = ShortcutsManager.get(action_id)
        if not current_shortcuts:
            self._on_add()
            return

        old_shortcut = current_shortcuts[0]

        dlg = ShortcutCaptureDialog(self, action_label=label, current_shortcut=old_shortcut)
        if dlg.exec():
            new_shortcut = dlg.get_shortcut()
            if not new_shortcut or new_shortcut == old_shortcut:
                return

            if not self._handle_conflict(new_shortcut, action_id):
                return

            # Replace primary shortcut, preserve any background alternatives
            updated = [new_shortcut] + [s for s in current_shortcuts[1:] if s != new_shortcut]
            ShortcutsManager.set(action_id, updated)
            self._populate_tree(self.search_box.text())
            self.shortcuts_changed.emit()
            logger.info(f"Edited shortcut for '{action_id}': {old_shortcut} -> {new_shortcut}")

    def _on_remove(self):
        """Delete shortcut from the selected action."""
        info = self._get_selection_info()
        if not info or not info["action_id"]:
            QMessageBox.information(self, "تنبيه", "يرجى تحديد إجراء أو اختصار من القائمة أولاً.")
            return

        action_id = info["action_id"]
        label = info["action_label"]

        current_shortcuts = ShortcutsManager.get(action_id)
        if not current_shortcuts:
            QMessageBox.information(self, "تنبيه", f"الإجراء '{label}' ليس له أي اختصار حالياً.")
            return

        primary_shortcut = current_shortcuts[0]
        reply = QMessageBox.question(
            self,
            "تأكيد الحذف",
            f"هل تريد حذف الاختصار '{primary_shortcut}' للإجراء '{label}'؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ShortcutsManager.clear_action(action_id)
            self._populate_tree(self.search_box.text())
            self.shortcuts_changed.emit()
            logger.info(f"Cleared shortcuts for '{action_id}'.")

    def _on_toggle_disable(self):
        """Toggle action between disabled (no shortcuts) and default/custom enabled."""
        selected = self._get_selected_action_id()
        if not selected:
            QMessageBox.information(self, "تنبيه", "يرجى تحديد إجراء من القائمة أولاً.")
            return
        action_id, label = selected

        if ShortcutsManager.is_disabled(action_id):
            ShortcutsManager.reset_action(action_id)
            logger.info(f"Re-enabled action '{action_id}'.")
        else:
            ShortcutsManager.clear_action(action_id)
            logger.info(f"Disabled action '{action_id}'.")

        self._populate_tree(self.search_box.text())
        self.shortcuts_changed.emit()

    def _on_reset_one(self):
        """Reset selected action to default shortcuts."""
        selected = self._get_selected_action_id()
        if not selected:
            QMessageBox.information(self, "تنبيه", "يرجى تحديد إجراء من القائمة أولاً.")
            return
        action_id, label = selected

        defaults = ShortcutsManager.get_default(action_id)
        primary_default = defaults[0] if defaults else "بلا اختصار"

        reply = QMessageBox.question(
            self,
            "استعادة الافتراضي",
            f"هل تريد استعادة الاختصار الافتراضي للإجراء '{label}'؟\n\nالافتراضي: {primary_default}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ShortcutsManager.reset_action(action_id)
            self._populate_tree(self.search_box.text())
            self.shortcuts_changed.emit()
            logger.info(f"Reset action '{action_id}' to defaults.")

    def _on_reset_all(self):
        """Reset all application shortcuts to default."""
        reply = QMessageBox.question(
            self,
            "تأكيد استعادة الكل",
            "هل أنت متأكد من رغبتك في إعادة تعيين كافة اختصارات البرنامج إلى الوضع الافتراضي؟\n"
            "سيتم فقدان جميع التخصيصات التي قمت بها.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ShortcutsManager.reset_all()
            self._populate_tree(self.search_box.text())
            self.shortcuts_changed.emit()
            logger.info("All shortcuts reset to defaults by user.")

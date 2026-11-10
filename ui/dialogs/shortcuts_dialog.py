"""
Shortcuts Dialog for Albayan.
Allows users to view, add, edit, delete, and disable keyboard shortcuts,
with key capture on release, conflict detection, and reset to defaults.
"""
from typing import Optional, List
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QLineEdit,
    QMessageBox,
    QInputDialog,
    QFrame,
)
from PySide6.QtGui import QKeySequence, QKeyEvent, QFont
from PySide6.QtCore import Qt, Signal, QEvent
from utils.shortcuts_manager import ShortcutsManager, DEFAULT_SHORTCUTS
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ShortcutCaptureDialog(QDialog):
    """
    Modal dialog that waits for the user to press a key combination
    and saves/accepts it as soon as the keys are released.
    """

    def __init__(self, parent=None, action_label: str = "", current_shortcut: str = ""):
        super().__init__(parent)
        self.action_label = action_label
        self.captured_shortcut: Optional[str] = None
        self._pending_sequence: Optional[str] = None
        self._non_modifier_pressed = False

        self.setWindowTitle("تسجيل الاختصار")
        self.setModal(True)
        self.resize(460, 220)

        self._init_ui(current_shortcut)

    def _init_ui(self, current_shortcut: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title_label = QLabel(f"الإجراء: {self.action_label}")
        font = title_label.font()
        font.setPointSize(12)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        hint_label = QLabel(
            "اضغط على مفاتيح الاختصار المطلوبة معاً، وعند رفع يدك سيتم حفظ الاختصار تلقائياً.\n"
            "(اضغط مفتاح Escape بمفرده للإلغاء)"
        )
        hint_label.setWordWrap(True)
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)

        # Status frame
        self.status_frame = QFrame()
        self.status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.status_frame.setStyleSheet(
            "QFrame { background-color: #2b2b2b; border: 2px solid #555; border-radius: 6px; padding: 10px; }"
        )
        frame_layout = QVBoxLayout(self.status_frame)

        self.status_label = QLabel(
            f"الاختصار الحالي: {current_shortcut}" if current_shortcut else "بانتظار ضغط المفاتيح..."
        )
        status_font = QFont()
        status_font.setPointSize(14)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setAccessibleName("حالة تسجيل الاختصار")
        frame_layout.addWidget(self.status_label)
        layout.addWidget(self.status_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setAccessibleName("إلغاء تسجيل الاختصار والعودة")
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)

    def event(self, event: QEvent) -> bool:
        """Intercept KeyPress and KeyRelease to prevent Qt focus navigation from swallowing keys."""
        if event.type() == QEvent.Type.KeyPress:
            self.keyPressEvent(event)
            return True
        elif event.type() == QEvent.Type.KeyRelease:
            self.keyReleaseEvent(event)
            return True
        return super().event(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        key = event.key()

        # If Escape is pressed with no modifiers, cancel dialog
        if key == Qt.Key.Key_Escape and event.modifiers() == Qt.KeyboardModifier.NoModifier:
            logger.debug("Shortcut capture cancelled via Escape.")
            self.reject()
            return

        # Check if key is modifier-only
        is_modifier = key in (
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
            Qt.Key.Key_AltGr,
        )

        mods = int(event.modifiers().value) & (
            Qt.KeyboardModifier.ControlModifier.value
            | Qt.KeyboardModifier.ShiftModifier.value
            | Qt.KeyboardModifier.AltModifier.value
            | Qt.KeyboardModifier.MetaModifier.value
        )

        if is_modifier:
            mod_texts = []
            if mods & Qt.KeyboardModifier.ControlModifier.value:
                mod_texts.append("Ctrl")
            if mods & Qt.KeyboardModifier.AltModifier.value:
                mod_texts.append("Alt")
            if mods & Qt.KeyboardModifier.ShiftModifier.value:
                mod_texts.append("Shift")
            if mods & Qt.KeyboardModifier.MetaModifier.value:
                mod_texts.append("Meta")
            self.status_label.setText(" + ".join(mod_texts) + " + ...")
            self._pending_sequence = None
            return

        # Normal key with or without modifiers
        combo = mods | key
        seq = QKeySequence(combo)
        seq_str = seq.toString(QKeySequence.SequenceFormat.PortableText)

        if seq_str:
            self._pending_sequence = seq_str
            self._non_modifier_pressed = True
            msg = f"تم التقاط: {seq_str} (ارفع يدك للحفظ)"
            self.status_label.setText(msg)
            self.status_label.setAccessibleName(msg)
            logger.debug(f"Shortcut key pressed: {seq_str}")

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        # As soon as keys start being released after a valid non-modifier combination was entered:
        if self._pending_sequence and self._non_modifier_pressed:
            logger.info(f"Captured shortcut on key release: {self._pending_sequence}")
            self.captured_shortcut = self._pending_sequence
            self.accept()
            return

        super().keyReleaseEvent(event)

    def get_shortcut(self) -> Optional[str]:
        return self.captured_shortcut


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

        # Shortcuts Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["الإجراء", "الاختصارات الحالية", "الحالة", "الافتراضية"])
        self.tree.setColumnWidth(0, 240)
        self.tree.setColumnWidth(1, 230)
        self.tree.setColumnWidth(2, 90)
        self.tree.setColumnWidth(3, 200)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAccessibleName("شجرة اختصارات البرنامج")
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
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
        """Fill tree with actions grouped by categories."""
        self.tree.clear()
        all_info = ShortcutsManager.get_all_with_info()
        categories = ShortcutsManager.get_categories()
        filter_lower = filter_text.strip().lower()

        for category in categories:
            cat_item = QTreeWidgetItem([category, "", "", ""])
            cat_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = cat_item.font(0)
            font.setBold(True)
            cat_item.setFont(0, font)

            has_children = False
            for action_id, info in all_info.items():
                if info["category"] != category:
                    continue

                label = info["label"]
                shortcuts_list = info["shortcuts"]
                default_list = info["default_shortcuts"]

                current_text = ", ".join(shortcuts_list) if shortcuts_list else "معطل (بلا اختصار)"
                default_text = ", ".join(default_list)

                # Determine status text
                if not shortcuts_list:
                    status_text = "معطل"
                elif shortcuts_list != default_list:
                    status_text = "معدل"
                else:
                    status_text = "افتراضي"

                # Filter condition
                if filter_lower:
                    searchable = f"{label} {current_text} {status_text} {default_text} {category}".lower()
                    if filter_lower not in searchable:
                        continue

                action_item = QTreeWidgetItem([label, current_text, status_text, default_text])
                action_item.setData(0, Qt.ItemDataRole.UserRole, action_id)
                action_item.setToolTip(1, current_text)
                action_item.setToolTip(3, default_text)

                # Color formatting
                if status_text == "معطل":
                    action_item.setForeground(2, Qt.GlobalColor.red)
                elif status_text == "معدل":
                    action_item.setForeground(2, Qt.GlobalColor.cyan)

                cat_item.addChild(action_item)
                has_children = True

            if has_children or not filter_lower:
                self.tree.addTopLevelItem(cat_item)
                cat_item.setExpanded(True)

    def _filter_tree(self, text: str):
        self._populate_tree(text)

    def _get_selected_action_id(self) -> Optional[tuple[str, str]]:
        """Return (action_id, action_label) of the currently selected item, or None."""
        selected = self.tree.selectedItems()
        if not selected:
            return None
        item = selected[0]
        action_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not action_id:
            return None
        return (action_id, item.text(0))

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        action_id = item.data(0, Qt.ItemDataRole.UserRole)
        if action_id:
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
        target_info = DEFAULT_SHORTCUTS.get(target_action_id, {})
        target_label = target_info.get("label", target_action_id)

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
        """Add a new shortcut to the selected action."""
        selected = self._get_selected_action_id()
        if not selected:
            QMessageBox.information(self, "تنبيه", "يرجى تحديد إجراء من القائمة أولاً.")
            return
        action_id, label = selected

        dlg = ShortcutCaptureDialog(self, action_label=label)
        if dlg.exec():
            new_shortcut = dlg.get_shortcut()
            if not new_shortcut:
                return

            if not self._handle_conflict(new_shortcut, action_id):
                return

            ShortcutsManager.add_shortcut(action_id, new_shortcut)
            self._populate_tree(self.search_box.text())
            self.shortcuts_changed.emit()
            logger.info(f"Added shortcut '{new_shortcut}' to '{action_id}'.")

    def _on_edit(self):
        """Edit an existing shortcut for the selected action."""
        selected = self._get_selected_action_id()
        if not selected:
            QMessageBox.information(self, "تنبيه", "يرجى تحديد إجراء من القائمة أولاً.")
            return
        action_id, label = selected

        current_shortcuts = ShortcutsManager.get(action_id)

        # If action has no shortcuts, treat edit like Add
        if not current_shortcuts:
            self._on_add()
            return

        # If action has 1 shortcut, edit it directly
        if len(current_shortcuts) == 1:
            old_shortcut = current_shortcuts[0]
            dlg = ShortcutCaptureDialog(self, action_label=label, current_shortcut=old_shortcut)
            if dlg.exec():
                new_shortcut = dlg.get_shortcut()
                if not new_shortcut or new_shortcut == old_shortcut:
                    return

                if not self._handle_conflict(new_shortcut, action_id):
                    return

                ShortcutsManager.set(action_id, [new_shortcut])
                self._populate_tree(self.search_box.text())
                self.shortcuts_changed.emit()
                logger.info(f"Edited shortcut for '{action_id}': {old_shortcut} -> {new_shortcut}")
            return

        # If action has multiple shortcuts, let user choose which one to edit
        chosen_shortcut, ok = QInputDialog.getItem(
            self,
            "اختر الاختصار المراد تعديله",
            f"يحتوي الإجراء '{label}' على أكثر من اختصار، اختر الاختصار المراد تعديله:",
            current_shortcuts,
            0,
            False,
        )
        if not ok or not chosen_shortcut:
            return

        dlg = ShortcutCaptureDialog(self, action_label=label, current_shortcut=chosen_shortcut)
        if dlg.exec():
            new_shortcut = dlg.get_shortcut()
            if not new_shortcut or new_shortcut == chosen_shortcut:
                return

            if not self._handle_conflict(new_shortcut, action_id):
                return

            # Replace chosen with new
            updated = [new_shortcut if s == chosen_shortcut else s for s in current_shortcuts]
            ShortcutsManager.set(action_id, updated)
            self._populate_tree(self.search_box.text())
            self.shortcuts_changed.emit()
            logger.info(f"Edited shortcut in list for '{action_id}': {chosen_shortcut} -> {new_shortcut}")

    def _on_remove(self):
        """Delete a shortcut from the selected action."""
        selected = self._get_selected_action_id()
        if not selected:
            QMessageBox.information(self, "تنبيه", "يرجى تحديد إجراء من القائمة أولاً.")
            return
        action_id, label = selected

        current_shortcuts = ShortcutsManager.get(action_id)
        if not current_shortcuts:
            QMessageBox.information(self, "تنبيه", f"الإجراء '{label}' معطل بالفعل ولا يمتلك أي اختصار.")
            return

        if len(current_shortcuts) == 1:
            reply = QMessageBox.question(
                self,
                "تأكيد الحذف",
                f"هل تريد حذف الاختصار '{current_shortcuts[0]}' وتعطيل الإجراء '{label}'؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                ShortcutsManager.clear_action(action_id)
                self._populate_tree(self.search_box.text())
                self.shortcuts_changed.emit()
                logger.info(f"Cleared shortcuts for '{action_id}'.")
            return

        # If multiple shortcuts exist, offer choice: delete one or all
        items = current_shortcuts + ["حذف كافة الاختصارات (تعطيل الإجراء)"]
        chosen, ok = QInputDialog.getItem(
            self,
            "حذف اختصار",
            f"اختر الاختصار المراد حذفه من الإجراء '{label}':",
            items,
            0,
            False,
        )
        if not ok or not chosen:
            return

        if chosen == "حذف كافة الاختصارات (تعطيل الإجراء)":
            ShortcutsManager.clear_action(action_id)
        else:
            ShortcutsManager.remove_shortcut(action_id, chosen)

        self._populate_tree(self.search_box.text())
        self.shortcuts_changed.emit()
        logger.info(f"Removed shortcut '{chosen}' from '{action_id}'.")

    def _on_toggle_disable(self):
        """Toggle action between disabled (no shortcuts) and default/custom enabled."""
        selected = self._get_selected_action_id()
        if not selected:
            QMessageBox.information(self, "تنبيه", "يرجى تحديد إجراء من القائمة أولاً.")
            return
        action_id, label = selected

        if ShortcutsManager.is_disabled(action_id):
            # Currently disabled, re-enable with defaults
            ShortcutsManager.reset_action(action_id)
            logger.info(f"Re-enabled action '{action_id}'.")
        else:
            # Currently enabled, disable it
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
        defaults_text = ", ".join(defaults) if defaults else "بلا اختصار"

        reply = QMessageBox.question(
            self,
            "استعادة الافتراضي",
            f"هل تريد استعادة الاختصارات الافتراضية للإجراء '{label}'؟\n\nالافتراضية: {defaults_text}",
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

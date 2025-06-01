
from enum import IntFlag
from typing import  Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox,
    QPushButton, QShortcut
)
from PyQt6.QtGui import QKeySequence
import qtawesome as qta

from utils.const import Globals
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class GoToMode(IntFlag):
    NUMERIC_FIELD = 1
    COMBO_FIELD = 2


class GoToDialog(QDialog):
    def __init__(
        self,
        parent,
        title: str,
        initial_value: int,
        min_value: int,
        max_value: int,
        mode: GoToMode,
        combo_data: Optional[dict] = None
    ):
        super().__init__(parent)

        self.mode = mode
        self.combo_data = combo_data or {}

        self.setWindowTitle(title)
        self.setGeometry(100, 100, 350, 180)

        main_layout = QVBoxLayout()

        # Combo Field
        if self.mode & GoToMode.COMBO_FIELD:
            self.combo_label = QLabel("اختر")
            main_layout.addWidget(self.combo_label)

            self.combo_box = QComboBox(self)
            self.combo_box.setAccessibleName(self.combo_label.text())
            for item_id, data in self.combo_data.items():
                item_label = data.get("label") if isinstance(data, dict) else str(data)
                self.combo_box.addItem(item_label, item_id)
            self.combo_box.currentIndexChanged.connect(self._validate_input)
            main_layout.addWidget(self.combo_box)

        # Numeric Field
        if self.mode & GoToMode.NUMERIC_FIELD:
            self.spin_label = QLabel("أدخل الرقم:")
            main_layout.addWidget(self.spin_label)

            self.spin_box = QSpinBox(self)
            self.spin_box.setAccessibleName(self.spin_label.text())
            self.spin_box.setMinimum(min_value)
            self.spin_box.setMaximum(max_value)
            self.spin_box.setValue(initial_value)
            self.spin_box.valueChanged.connect(self._validate_input)
            main_layout.addWidget(self.spin_box)

            if self.mode == (GoToMode.NUMERIC_FIELD | GoToMode.COMBO_FIELD):
                self.combo_box.currentIndexChanged.connect(self._update_spinbox_range_from_combo)
                self._update_spinbox_range_from_combo()

        # Buttons
        button_layout = QHBoxLayout()

        self.go_to_button = QPushButton(self)
        self.go_to_button.setIcon(qta.icon("fa.location-arrow"))
        self.go_to_button.setAccessibleName("اذهب")
        self.go_to_button.setDefault(True)
        self.go_to_button.clicked.connect(self.accept)
        self.go_to_button.clicked.connect(lambda: Globals.effects_manager.play("move"))
        button_layout.addWidget(self.go_to_button)

        self.cancel_button = QPushButton(self)
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))
        self.cancel_button.setIcon(qta.icon("fa.times"))
        self.cancel_button.setAccessibleName("إلغاء")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        QShortcut(QKeySequence("Ctrl+F4"), self).activated.connect(self.reject)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        logger.debug("GoToDialog initialized successfully.")

    def _update_spinbox_range_from_combo(self):
        """Updates spinbox min/max when combo changes (only in COMBO+NUMERIC mode)."""
        if not (self.mode & GoToMode.COMBO_FIELD and self.mode & GoToMode.NUMERIC_FIELD):
            return

        item_id = self.combo_box.currentData()
        item_data = self.combo_data.get(item_id, {})

        min_val = item_data.get("min", 1)
        max_val = item_data.get("max", 1)

        self.spin_box.setMinimum(min_val)
        self.spin_box.setMaximum(max_val)
        self.spin_box.setValue(min_val)

        logger.debug(f"Spinbox range updated: min={min_val}, max={max_val} for item_id={item_id}")

    def _validate_input(self):
        """Enable/disable go_to_button based on input validity."""
        is_valid = True

        if self.mode & GoToMode.COMBO_FIELD:
            current_index = self.combo_box.currentIndex()
            if current_index < 0:
                is_valid = False

        if self.mode & GoToMode.NUMERIC_FIELD:
            if not (self.spin_box.minimum() <= self.spin_box.value() <= self.spin_box.maximum()):
                is_valid = False

        self.go_to_button.setEnabled(is_valid)

    def get_input_value(self):
        """Returns selected values depending on mode."""
        if self.mode == GoToMode.NUMERIC_FIELD:
            return self.spin_box.value()
        elif self.mode == GoToMode.COMBO_FIELD:
            return self.combo_box.currentData()
        elif self.mode == (GoToMode.NUMERIC_FIELD | GoToMode.COMBO_FIELD):
            item_id = self.combo_box.currentData()
            value = self.spin_box.value()
            return {"item_id": item_id, "value": value}

    def set_combo_label(self, label: str):
        """Sets the label for the combo box."""
        if self.mode & GoToMode.COMBO_FIELD:
            self.combo_label.setText(label)
            self.combo_box.setAccessibleName(label)
            logger.debug(f"Combo label set to: {label}")
    
    def set_spin_label(self, label: str):
        """Sets the label for the spin box."""
        if self.mode & GoToMode.NUMERIC_FIELD:
            self.spin_label.setText(label)
            self.spin_box.setAccessibleName(label)
            logger.debug(f"Spin label set to: {label}")
    
    def reject(self):
        self.deleteLater()

    def closeEvent(self, event):
        logger.debug("GoToDialog closed.")
        return super().closeEvent(event)

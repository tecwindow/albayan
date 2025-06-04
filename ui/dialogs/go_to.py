
from enum import IntFlag
from typing import Optional, Union, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QSpinBox, QComboBox, QPushButton
)
from PyQt6.QtGui import QKeySequence, QShortcut
import qtawesome as qta

from ui.widgets.spin_box import SpinBox
from utils.const import Globals
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class GoToStyle(IntFlag):
    NUMERIC_FIELD = 1
    COMBO_FIELD = 2


class GoToDialog(QDialog):
    def __init__(
        self,
        parent,
        title: str,
        initial_value: int = 1,
        min_value: int = 1,
        max_value: int = 1,
        style: GoToStyle = GoToStyle.NUMERIC_FIELD,
        combo_data: Optional[dict] = None
    ):
        super().__init__(parent)

        self.initial_value = initial_value
        self.style = style
        self.combo_data = combo_data or {}

        self.setWindowTitle(title)
        self.setGeometry(100, 100, 350, 180)

        main_layout = QVBoxLayout()

        self.info_label = QLabel("")
        main_layout.addWidget(self.info_label)
        if self.has_combo_field:
            self.combo_label = QLabel("اختر")
            main_layout.addWidget(self.combo_label)

            self.combo_box = QComboBox(self)
            self.combo_box.setAccessibleName(self.combo_label.text())
            for item_id, data in self.combo_data.items():
                label = data.get("label") if isinstance(data, dict) else str(data)
                self.combo_box.addItem(label, item_id)
            self.combo_box.currentIndexChanged.connect(self._validate_input)
            main_layout.addWidget(self.combo_box)



        if self.has_numeric_field:
            self.spin_label = QLabel("أدخل الرقم:")
            main_layout.addWidget(self.spin_label)

            self.spin_box = SpinBox(self)
            self.spin_box.setAccessibleName(self.spin_label.text())
            self.spin_box.setMinimum(min_value)
            self.spin_box.setMaximum(max_value)
            self.spin_box.valueChanged.connect(self._validate_input)
            self.spin_box.setFocus()
            main_layout.addWidget(self.spin_box)

            if self.has_both_fields:
                self.combo_box.currentIndexChanged.connect(self._update_spinbox_range_from_combo)
                self._update_spinbox_range_from_combo()

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
        self._set_current_value()

        logger.debug("GoToDialog initialized successfully.")

    @property
    def has_combo_field(self) -> bool:
        return bool(self.style & GoToStyle.COMBO_FIELD)

    @property
    def has_numeric_field(self) -> bool:
        return bool(self.style & GoToStyle.NUMERIC_FIELD)

    @property
    def has_both_fields(self) -> bool:
        return self.has_combo_field and self.has_numeric_field

    def _set_current_value(self):
        if self.has_both_fields or not self.has_numeric_field:
            self.combo_box.setCurrentText(str(self.initial_value))
        elif self.has_numeric_field:
            self.spin_box.setValue(self.initial_value)

    def _update_spinbox_range_from_combo(self):
        if not self.has_both_fields:
            return

        item_id = self.combo_box.currentData()
        item_data = self.combo_data.get(item_id, {})

        min_val = item_data.get("min", 1)
        max_val = item_data.get("max", 1)
        initial_value = item_data.get("initial_value", 1)

        self.spin_box.setMinimum(min_val)
        self.spin_box.setMaximum(max_val)
        self.spin_box.setValue(initial_value)
        
        logger.debug(f"Spinbox range updated: min={min_val}, max={max_val} for item_id={item_id}")

    def _validate_input(self):
        is_valid = True

        if self.has_combo_field and self.combo_box.currentIndex() < 0:
            is_valid = False

        if self.has_numeric_field and not (
            self.spin_box.minimum() <= self.spin_box.value() <= self.spin_box.maximum()
        ):
            is_valid = False

        if hasattr(self, "go_to_button"):
            self.go_to_button.setEnabled(is_valid)

    def get_input_value(self) -> Union[int, str, Tuple[str, int]]:
        if self.has_both_fields:
            return self.combo_box.currentData(), self.spin_box.value()
        if self.has_combo_field:
            return self.combo_box.currentData()
        if self.has_numeric_field:
            return self.spin_box.value()

    def set_combo_label(self, label: str):
        if self.has_combo_field:
            self.combo_label.setText(label)
            self.combo_box.setAccessibleName(label)
            logger.debug(f"Combo label set to: {label}")

    def set_spin_label(self, label: str):
        if self.has_numeric_field:
            self.spin_label.setText(label)
            self.spin_box.setAccessibleName(label)
            logger.debug(f"Spin label set to: {label}")

    def set_info_label(self, text: str):
        self.info_label.setText(text)
        self.info_label.setAccessibleName(text)
        logger.debug(f"Info label set to: {text}")


    def reject(self):
        self.deleteLater()

    def closeEvent(self, event):
        logger.debug("GoToDialog closed.")
        return super().closeEvent(event)

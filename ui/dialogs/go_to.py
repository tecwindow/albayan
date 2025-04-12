from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QSpinBox, QDialog, QLabel
from PyQt6.QtGui import QKeySequence, QShortcut
from utils.const import Globals
import qtawesome as qta
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class GoToDialog(QDialog):
    def __init__(self, parent, current_position: int, max: int, category_label: str):
        super().__init__(parent)        
        logger.debug(f"Initializing GoToDialog with current_position={current_position}, max={max}, category_label={category_label}.")
        
        self.setWindowTitle('الذهاب إلى')
        self.setGeometry(100, 100, 300, 150)
        
        layout = QVBoxLayout()
        
        self.label = QLabel('أدخل رقم ال{}:'.format(category_label))
        logger.debug(f"Label created with text: {self.label.text()}")
        layout.addWidget(self.label)
        
        self.input_field = QSpinBox(self)
        self.input_field.setAccessibleName(self.label.text())
        self.input_field.setMinimum(1)
        self.input_field.setMaximum(max)
        self.input_field.setValue(current_position)
        self.input_field.selectAll()
        logger.debug(f"SpinBox initialized with range (1, {max}) and value {current_position}.")
        layout.addWidget(self.input_field)
        
        button_layout = QHBoxLayout()
        
        self.go_to_button = QPushButton('اذهب', self)
        self.go_to_button.setIcon(qta.icon("fa.location-arrow"))
        self.go_to_button.setDefault(True)
        self.go_to_button.clicked.connect(self.accept)
        self.go_to_button.clicked.connect(lambda: Globals.effects_manager.play("move"))
        button_layout.addWidget(self.go_to_button)
        
        self.cancel_button = QPushButton('إغلاق', self)
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))
        self.cancel_button.setIcon(qta.icon("fa.times"))
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)

        layout.addLayout(button_layout)        
        self.setLayout(layout)
    
        logger.info("GoToDialog initialized successfully.")

    def get_input_value(self):
        value = self.input_field.value()
        logger.debug(f"User selected value: {value}")
        return value

    def reject(self):
        self.deleteLater()
        
    def closeEvent(self, a0):
        logger.debug("GoToDialog closed.")
        return super().closeEvent(a0)

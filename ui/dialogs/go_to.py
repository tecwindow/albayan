from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QSpinBox, QDialog, QLabel

class GoToDialog(QDialog):
    def __init__(self, parent, current_position: int, max: int, category_label: str):
        super().__init__(parent)
        
        self.setWindowTitle('الذهاب إلى')
        self.setGeometry(100, 100, 300, 150)
        
        layout = QVBoxLayout()
        
        self.label = QLabel('أدخل رقم ال{}:'.format(category_label))
        layout.addWidget(self.label)
        
        self.input_field = QSpinBox(self)
        self.input_field.setAccessibleName(self.label.text())
        self.input_field.setMinimum(1)
        self.input_field.setMaximum(max)
        self.input_field.setValue(current_position)
        self.input_field.selectAll()
        layout.addWidget(self.input_field)
        
        button_layout = QHBoxLayout()
        
        self.go_to_button = QPushButton('اذهب', self)
        self.go_to_button.setDefault(True)
        self.go_to_button.clicked.connect(self.accept)
        button_layout.addWidget(self.go_to_button)
        
        self.cancel_button = QPushButton('إغلاق', self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_input_value(self):
        return self.input_field.value()

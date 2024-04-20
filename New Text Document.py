import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("نافذة بسيطة")
        
        layout = QVBoxLayout()
        
        self.label = QLabel("مرحباً بالعالم!")
        layout.addWidget(self.label)
        
        self.button = QPushButton("انقر هنا")
        layout.addWidget(self.button)
        self.button.clicked.connect(self.button_clicked)
        
        self.setLayout(layout)
        
    def button_clicked(self):
        self.label.setText("لقد قمت بالنقر!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())

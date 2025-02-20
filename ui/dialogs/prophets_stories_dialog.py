import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QApplication
)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt, QTimer, QEvent
from ui.widgets.qText_edit import ReadOnlyTextEdit
from utils.universal_speech import UniversalSpeech
from utils.const import albayan_documents_dir, Globals
from utils.const import Globals, data_folder
import qtawesome as qta

class ProphetsStoriesDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("قصص الأنبياء")
        self.resize(500, 400)
        Globals.effects_manager.play("open")
        
        self.layout = QVBoxLayout(self)
        
        self.label = QLabel("اختر النبي:", self)
        self.layout.addWidget(self.label)
        
        self.combo_box = QComboBox(self)
        self.layout.addWidget(self.combo_box)
        
        self.text_edit = ReadOnlyTextEdit(self)
        self.layout.addWidget(self.text_edit)
        
        self.button_layout = QHBoxLayout()
        
        self.copy_button = QPushButton("نسخ القصة")
        self.copy_button.setIcon(qta.icon("fa.copy"))
        self.copy_button.setShortcut(QKeySequence("Shift+C"))
        self.copy_button.clicked.connect(self.copy_content)
        self.button_layout.addWidget(self.copy_button)
        
        self.save_button = QPushButton("حفظ القصة")
        self.save_button.setIcon(qta.icon("fa.save"))
        self.save_button.setShortcut(QKeySequence("Ctrl+S"))
        self.save_button.clicked.connect(self.save_content)
        self.button_layout.addWidget(self.save_button)
        
        self.close_button = QPushButton("إغلاق")
        self.close_button.setIcon(qta.icon("fa.times"))
        self.close_button.setShortcut(QKeySequence("Ctrl+W"))
        self.close_button.clicked.connect(self.reject)
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)


        self.button_layout.addWidget(self.close_button)
        
        self.layout.addLayout(self.button_layout)
        
        self.load_stories()
        self.combo_box.currentIndexChanged.connect(self.display_story)
        self.combo_box.currentIndexChanged.connect(lambda: Globals.effects_manager.play("move"))
        
        # Call display_story() after loading stories
        if self.combo_box.count() > 0:
            self.combo_box.setCurrentIndex(0)  # Select the first item
            self.display_story()  # Display the first story
        
        self.setFocus()
        QTimer.singleShot(300, self.combo_box.setFocus)
        self.combo_box.installEventFilter(self)


    def load_stories(self):
        try:
            file_path = data_folder/"prophets_stories/stories.json"
            
            with open(file_path, "r", encoding="utf-8") as file:
                self.stories = json.load(file)
            
            for story in self.stories:
                self.combo_box.addItem(story["name"], story)
        except Exception as e:
            self.text_edit.setText(f"خطأ في تحميل القصص: {e}")

    
    def display_story(self):
        selected_story = self.combo_box.currentData()
        if selected_story:
            story_text = f"{selected_story['name']}.\n"
            for event in selected_story["data"]:
                story_text += f"{event['title']}:\n{event['data']}\n"
            self.text_edit.setText(story_text.strip())



    def copy_content(self):
        copied_content = self.text_edit.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(copied_content)
        UniversalSpeech.say("تم نسخ القصة.")
        Globals.effects_manager.play("copy")
    
    def save_content(self):
        prophet_name = self.combo_box.currentText()
        file_name = os.path.join(albayan_documents_dir, f"{prophet_name}.txt")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ القصة", file_name, "Text files (*.txt)",
        )
        
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.text_edit.toPlainText())

    def eventFilter(self, obj, event):
        if obj == self.combo_box and event.type() == event.KeyPress:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                self.text_edit.setFocus()
                return True
        return super().eventFilter(obj, event)

    def reject(self):
        Globals.effects_manager.play("clos")
        self.deleteLater()

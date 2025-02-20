from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QCheckBox, QComboBox, QPushButton, QGroupBox
)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt
from core_functions.athkar.athkar_db_manager import AthkarDBManager
from core_functions.athkar.models import AthkarCategory
from core_functions.athkar.athkar_scheduler import AthkarScheduler
from utils.const import user_db_path, data_folder, athkar_db_path, default_athkar_path

class AthkarDialog(QDialog):
    athkar_scheduler = AthkarScheduler(athkar_db_path, default_athkar_path, data_folder/"athkar/text_athkar.json")
    athkar_scheduler.start()

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("الأذكار")
        self.resize(400, 350)
        self.athkar_db = AthkarDBManager(athkar_db_path)

        self.interval_options_dict = {
            5: "5 دقيقة",
            10: "10 دقيقة",
            15: "15 دقيقة",
            30: "30 دقيقة",
            60: "ساعة"
        }

        self.init_ui()
        self.connect_signals()
        self.load_categories()
        
    def init_ui(self):
        main_layout = QVBoxLayout()

        section_label = QLabel("القسم:")
        self.section_list = QListWidget()
        self.section_list.setAccessibleName(section_label.text())
        main_layout.addWidget(section_label)
        main_layout.addWidget(self.section_list)

        self.audio_athkar_enable_checkbox = QCheckBox("تفعيل الأذكار الصوتية")
        self.text_athkar_enable_checkbox = QCheckBox("تفعيل الأذكار النصية")
        main_layout.addWidget(self.audio_athkar_enable_checkbox)
        main_layout.addWidget(self.text_athkar_enable_checkbox)

        # Duration setup
        duration_group = QGroupBox("مدة التشغيل")
        duration_layout = QHBoxLayout()
        from_label = QLabel("من:")
        self.from_combobox = self.create_time_combobox()
        self.from_combobox.setAccessibleName(from_label.text())
        to_label = QLabel("إلى:")
        self.to_combobox = self.create_time_combobox()
        self.to_combobox.setAccessibleName(to_label.text())

        duration_layout.addWidget(from_label)
        duration_layout.addWidget(self.from_combobox)
        duration_layout.addWidget(to_label)
        duration_layout.addWidget(self.to_combobox)
        duration_group.setLayout(duration_layout)
        main_layout.addWidget(duration_group)

        # Interval setup
        interval_label = QLabel("التكرار كل:")
        self.interval_combobox = QComboBox()
        self.interval_combobox.setAccessibleName(interval_label.text())
        self.interval_combobox.addItems(self.interval_options_dict.values())
        main_layout.addWidget(interval_label)
        main_layout.addWidget(self.interval_combobox)

        # Buttons
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("إعادة ضبط الخيارات")
        self.save_button = QPushButton("حفظ")
        self.save_button.setDefault(True)
        self.cancel_button = QPushButton("إغلاق")
        self.cancel_button.setShortcut(QKeySequence("Ctrl+W"))
        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)

        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def create_time_combobox(self) -> QComboBox:
        combobox = QComboBox()
        time_options = [f"{hour:02d}:00" for hour in range(24)]
        combobox.addItems(time_options)
        return combobox

    def connect_signals(self):
        self.reset_button.clicked.connect(self.reset_settings)
        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.reject)
        self.section_list.currentItemChanged.connect(self.update_ui_based_on_selection)

    def load_categories(self):
        for category in self.athkar_db.get_all_categories():
            category_name = category.name if category.name != "default" else "الافتراضي"
            item = QListWidgetItem(category_name)
            item.setData(Qt.ItemDataRole.UserRole, category)
            self.section_list.addItem(item)
        self.section_list.setCurrentRow(0)
        self.update_ui_based_on_selection()

    def get_selected_category(self) -> Optional[AthkarCategory]:
        selected_item = self.section_list.currentItem()
        if selected_item:
            return selected_item.data(Qt.ItemDataRole.UserRole)
        return None

    def update_ui_based_on_selection(self):
        selected_category = self.get_selected_category()
        if selected_category:
            self.audio_athkar_enable_checkbox.setChecked(selected_category.audio_athkar_enabled)
            self.text_athkar_enable_checkbox.setChecked(selected_category.text_athkar_enabled)
            self.from_combobox.setCurrentText(selected_category.from_time)
            self.to_combobox.setCurrentText(selected_category.to_time)
            interval_text = self.interval_options_dict.get(
                selected_category.play_interval, "5 دقيقة"
            )
            self.interval_combobox.setCurrentText(interval_text)

    def reset_settings(self):
        self.audio_athkar_enable_checkbox.setChecked(False)
        self.text_athkar_enable_checkbox.setChecked(False)
        self.from_combobox.setCurrentIndex(0)
        self.to_combobox.setCurrentIndex(self.to_combobox.count() - 1)
        self.interval_combobox.setCurrentIndex(0)

    def on_save(self) -> None:
        selected_category = self.get_selected_category()
        if not selected_category:
            return
        
        play_interval_text = self.interval_combobox.currentText()
        play_interval = next(
            (key for key, value in self.interval_options_dict.items() if value == play_interval_text), 
            5
        )
        
        self.athkar_db.update_category(
            category_id=selected_category.id,
            from_time=self.from_combobox.currentText(),
            to_time=self.to_combobox.currentText(),
            play_interval=play_interval,
            audio_athkar_enabled=int(self.audio_athkar_enable_checkbox.isChecked()),
            text_athkar_enabled=int(self.text_athkar_enable_checkbox.isChecked())
        )
        self.athkar_scheduler.refresh()
        self.accept()
        self.deleteLater()


    def reject(self):
        self.deleteLater()
        
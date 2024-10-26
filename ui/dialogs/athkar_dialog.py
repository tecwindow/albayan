from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QCheckBox, QComboBox, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt
from core_functions.athkar.athkar_db_manager import AthkarDBManager
from core_functions.athkar.models import AthkarCategory
from core_functions.athkar.athkar_scheduler import AthkarScheduler
from utils.const import user_db_path

class AthkarDialog(QDialog):
    athkar_Scheduler = AthkarScheduler(user_db_path, "Audio/adkar")
    athkar_Scheduler.start()

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("الأذكار")
        self.resize(400, 350)
        self.athkar_db = AthkarDBManager(user_db_path)
        
        main_layout = QVBoxLayout()

        section_label = QLabel("القسم:")
        self.section_list = QListWidget()
        self.section_list.setAccessibleName(section_label.text())
        main_layout.addWidget(section_label)
        main_layout.addWidget(self.section_list)

        for category in self.athkar_db.get_all_categories():
            category_name  = category.name if category.name != "default" else "الافتراضي"
            item = QListWidgetItem(category_name)
            item.setData(Qt.ItemDataRole.UserRole, category)
            self.section_list.addItem(item)
        self.section_list.setCurrentRow(0)

        self.enable_checkbox = QCheckBox("تفعيل القسم")
        selected_category = self.get_selected_category()
        self.enable_checkbox.setChecked(selected_category.status)
        main_layout.addWidget(self.enable_checkbox)

        duration_group = QGroupBox("مدة التشغيل")
        duration_layout = QHBoxLayout()
        from_label = QLabel("من:")
        self.from_combobox = QComboBox()
        self.from_combobox.setAccessibleName(from_label.text())
        to_label = QLabel("إلى:")
        self.to_combobox = QComboBox()
        self.to_combobox.setAccessibleName(to_label.text())
    
        time_options = [f"{hour:02d}:00" for hour in range(24)]
        self.from_combobox.addItems(time_options)
        self.to_combobox.addItems(time_options)
        self.from_combobox.setCurrentText(selected_category.from_time)
        self.to_combobox.setCurrentText(selected_category.to_time)

        duration_layout.addWidget(from_label)
        duration_layout.addWidget(self.from_combobox)
        duration_layout.addWidget(to_label)
        duration_layout.addWidget(self.to_combobox)
        duration_group.setLayout(duration_layout)
        main_layout.addWidget(duration_group)

        interval_label = QLabel("التكرار كل:")
        self.interval_combobox = QComboBox()
        self.interval_combobox.setAccessibleName(interval_label.text())
        interval_options = [f"{minutes}د" for minutes in range(1, 61, 2) if 60 % minutes == 0]
        self.interval_combobox.addItems(interval_options)
        self.interval_combobox.setCurrentText(f"{selected_category.play_interval}د")
        main_layout.addWidget(interval_label)
        main_layout.addWidget(self.interval_combobox)

        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("إعادة ضبط الخيارات")
        self.save_button = QPushButton("حفظ")
        self.save_button.setDefault(True)
        self.cancel_button = QPushButton("إغلاق")
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.reset_button.clicked.connect(self.reset_settings)
        self.save_button.clicked.connect(self.Onsave)
        self.cancel_button.clicked.connect(self.reject)

    def get_selected_category(self) -> AthkarCategory:
        selected_item = self.section_list.selectedItems()
        if  selected_item:
            selected_item = selected_item[0]
            category = selected_item.data(Qt.ItemDataRole.UserRole)
            return category

    def reset_settings(self):
        self.enable_checkbox.setChecked(False)
        self.from_combobox.setCurrentIndex(0)
        self.to_combobox.setCurrentIndex(self.to_combobox.count() - 1)
        self.interval_combobox.setCurrentIndex(0)

    def Onsave(self) -> None:
        selected_category = self.get_selected_category()
        self.athkar_db.update_category(
            category_id=selected_category.id,
            from_time= self.from_combobox.currentText(),
            to_time= self.to_combobox.currentText(),
            play_interval=self.interval_combobox.currentText().replace("د", ""),
            status=int(self.enable_checkbox.isChecked())
        )
        self.athkar_Scheduler.refresh()
        self.accept()



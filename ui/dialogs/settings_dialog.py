from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QComboBox,
    QRadioButton,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QButtonGroup,
    QMessageBox,
    QSlider,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
    QSpinBox,
    QStackedWidget
)
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import Qt
from core_functions.Reciters import RecitersManager
from utils.const import data_folder, program_english_name
from utils.settings import SettingsManager
from utils.audio_player import AthkarPlayer, AyahPlayer, SoundEffectPlayer
from utils.Startup import StartupManager


class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("الإعدادات")
        self.resize(600, 450)
        self.reciters_manager = RecitersManager(data_folder / "quran" / "reciters.db")
        self.init_ui()
        self.set_current_settings()


    def init_ui(self):
        main_layout = QVBoxLayout()
        taps_layout = QHBoxLayout()

        # Tree widget for navigation
        tree_widget = QTreeWidget()
        tree_widget.setHeaderHidden(True)
        tree_widget.setMinimumWidth(200)
        tree_widget.setStyleSheet("QTreeWidget { font-size: 14px; }")
        
        # Adding items to the tree
        general_item = QTreeWidgetItem(["الإعدادات العامة"])
        audio_item = QTreeWidgetItem(["الصوت"])
        listening_item = QTreeWidgetItem(["الاستماع"])
        reading_item = QTreeWidgetItem(["القراءة"])
        search_item = QTreeWidgetItem(["البحث"])
        
        # Adding top-level items
        tree_widget.addTopLevelItem(general_item)
        tree_widget.addTopLevelItem(audio_item)
        tree_widget.addTopLevelItem(listening_item)
        tree_widget.addTopLevelItem(reading_item)
        tree_widget.addTopLevelItem(search_item)
        
        # Stacked widget to switch views
        self.stacked_widget = QStackedWidget()
        
        # General settings
        self.group_general = QGroupBox("الإعدادات العامة")
        self.group_general_layout = QVBoxLayout()
        self.run_in_background_checkbox = QCheckBox("تشغيل البرنامج في الخلفية")
        self.start_on_system_start_checkbox = QCheckBox("تشغيل عند بدء تشغيل النظام")
        self.auto_save_position_checkbox = QCheckBox("حفظ الموضع الحالي تلقائيًا عند إغلاق البرنامج")
        self.update_checkbox = QCheckBox("التحقق من التحديثات")
        self.log_checkbox = QCheckBox("تمكين تسجيل الأخطاء")
        self.reset_button = QPushButton("استعادة الإعدادات الافتراضية")
        self.reset_button.clicked.connect(self.OnReset)
        
        self.group_general_layout.addWidget(self.run_in_background_checkbox)
        self.group_general_layout.addWidget(self.start_on_system_start_checkbox)
        self.group_general_layout.addWidget(self.auto_save_position_checkbox)
        self.group_general_layout.addWidget(self.update_checkbox)
        self.group_general_layout.addWidget(self.log_checkbox)
        self.group_general_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.group_general_layout.addWidget(self.reset_button)
        self.group_general.setLayout(self.group_general_layout)

        self.run_in_background_checkbox.toggled.connect(self.updateStartCheckboxState)
        self.start_on_system_start_checkbox.toggled.connect(self.updateBackgroundCheckboxState)


        self.group_audio = QGroupBox("إعدادات الصوت")
        self.group_audio_layout = QVBoxLayout()
        self.volume_label = QLabel("مستوى صوت البرنامج")
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.valueChanged.connect(self.OnVolume)
        self.volume.setAccessibleName(self.volume_label.text())
        self.volume.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.ayah_volume_label = QLabel("مستوى صوت الآيات")
        self.ayah_volume = QSlider(Qt.Orientation.Horizontal)
        self.ayah_volume.setRange(0, 100)
        self.ayah_volume.valueChanged.connect(self.OnAyahVolume)
        self.ayah_volume.setAccessibleName(self.ayah_volume_label.text())
        self.ayah_volume.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.athkar_volume_label = QLabel("مستوى صوت الأذكار")
        self.athkar_volume = QSlider(Qt.Orientation.Horizontal)
        self.athkar_volume.setRange(0, 100)
        self.athkar_volume.valueChanged.connect(self.OnAthkarVolume)
        self.athkar_volume.setAccessibleName(self.athkar_volume_label.text())
        self.athkar_volume.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.sound_checkbox = QCheckBox("تفعيل المؤثرات الصوتية")
        self.basmala_checkbox = QCheckBox("تفعيل البسملة مع فتح البرنامج")
        self.speech_checkbox = QCheckBox("نطق الإجرائات")

        self.group_audio_layout.addWidget(self.volume_label)
        self.group_audio_layout.addWidget(self.volume)
        self.group_audio_layout.addWidget(self.ayah_volume_label)
        self.group_audio_layout.addWidget(self.ayah_volume)
        self.group_audio_layout.addWidget(self.athkar_volume_label)
        self.group_audio_layout.addWidget(self.athkar_volume)
        self.group_audio_layout.addWidget(self.sound_checkbox)
        self.group_audio_layout.addWidget(self.basmala_checkbox)
        self.group_audio_layout.addWidget(self.speech_checkbox)
        self.group_audio_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.group_audio.setLayout(self.group_audio_layout)
        
        self.group_listening = QGroupBox("إعدادات الاستماع")
        self.group_listening_layout = QVBoxLayout()

        self.reciters_label = QLabel("القارئ:")
        self.reciters_combo = QComboBox()
        reciters = self.reciters_manager.get_reciters()
        self.reciters_combo.setAccessibleName(self.reciters_label.text())
        for  row in reciters:
            display_text = f"{row['name']} - {row['rewaya']} - {row['type']} - ({row['bitrate']} kbps)"
            self.reciters_combo.addItem(display_text, row["id"])

        self.action_label = QLabel("الإجراء بعد الاستماع:")
        self.action_combo = QComboBox()
        items_with_ids = [("إيقاف", 0), ("تكرار", 1), ("الانتقال إلى الآية التالية", 2)]
        [self.action_combo.addItem(text, id) for text, id in items_with_ids]
        self.action_combo.setAccessibleName(self.action_label.text())

        self.duration_label = QLabel("مدة التقديم والترجيع (بالثواني):")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setAccessibleName(self.duration_label.text())        
        self.duration_spinbox.setRange(2, 15)
        self.duration_spinbox.setSingleStep(1)


        self.group_listening_layout.addWidget(self.reciters_label)
        self.group_listening_layout.addWidget(self.reciters_combo)
        self.group_listening_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))  # مسافة نتوسطة
        self.group_listening_layout.addWidget(self.action_label)
        self.group_listening_layout.addWidget(self.action_combo)
        self.group_listening_layout.addWidget(self.duration_label)
        self.group_listening_layout.addWidget(self.duration_spinbox)
        self.group_listening.setLayout(self.group_listening_layout)
        self.group_listening_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.group_reading = QGroupBox("إعدادات القراءة")
        self.group_reading_layout = QVBoxLayout()
        self.font_type_label = QLabel("نوع الخط:")
        self.font_type_combo = QComboBox()
        items_with_ids_list = [("الخط الحديث", 0), ("الخط العثماني", 1)]
        [self.font_type_combo.addItem(text, id) for text, id in items_with_ids_list]
        self.font_type_combo.setAccessibleName(self.font_type_label.text())

        self.turn_pages_checkbox = QCheckBox("قلب الصفحات تلقائيا")

        self.group_reading_layout.addWidget(self.font_type_label)
        self.group_reading_layout.addWidget(self.font_type_combo)
        self.group_reading_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))  # مسافة أكبر
        self.group_reading_layout.addWidget(self.turn_pages_checkbox)
        self.group_reading_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.group_reading.setLayout(self.group_reading_layout)


        self.group_search = QGroupBox("إعدادات البحث")
        self.group_search_layout = QVBoxLayout()
        self.ignore_tashkeel_checkbox = QCheckBox("تجاهل التشكيل")
        self.ignore_hamza_checkbox = QCheckBox("تجاهل الهمزات")
        self.match_whole_word_checkbox = QCheckBox("تطابق الكلمة بأكملها")

        self.group_search_layout.addWidget(self.ignore_tashkeel_checkbox)
        self.group_search_layout.addWidget(self.ignore_hamza_checkbox)
        self.group_search_layout.addWidget(self.match_whole_word_checkbox)
        self.group_search_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.group_search.setLayout(self.group_search_layout)


        # Adding to the stacked widget        
        self.stacked_widget.addWidget(self.group_general)
        self.stacked_widget.addWidget(self.group_audio)
        self.stacked_widget.addWidget(self.group_listening)
        self.stacked_widget.addWidget(self.group_reading)
        self.stacked_widget.addWidget(self.group_search)
        
#        tree_widget.currentItemChanged.connect(lambda current, previous: self.stacked_widget.setCurrentIndex(tree_widget.indexOfTopLevelItem(current)))

        # Linking tree widget with stacked widget
        tree_widget.currentItemChanged.connect(
            lambda current, previous: self.stacked_widget.setCurrentIndex(
                tree_widget.indexOfTopLevelItem(current)
            )
        )


        # Layout adjustments
        taps_layout.addWidget(tree_widget, stretch=1)
        taps_layout.addWidget(self.stacked_widget, stretch=2)
        
        main_layout.addLayout(taps_layout)

        # Buttons at the bottom
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("حفظ")
        save_button.clicked.connect(self.save_settings)
        save_button.setDefault(True)
        close_button = QPushButton("إغلاق")
        close_button.setShortcut(QKeySequence("Ctrl+W"))
        close_button.clicked.connect(self.close)

        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(close_button)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def OnAyahVolume(self) -> None:
        for instance in AyahPlayer.instances:
            instance.set_volume(self.ayah_volume.value())

    def OnAthkarVolume(self) -> None:
        for instance in AthkarPlayer.instances:
            instance.set_volume(self.athkar_volume.value())

    def OnVolume(self) -> None:
        for instance in SoundEffectPlayer.instances:
            instance.set_volume(self.volume.value())

    def updateBackgroundCheckboxState(self):
        # Check if 'start_on_system_start_checkbox' is checked
        if self.start_on_system_start_checkbox.isChecked():
            # If 'start_on_system_start_checkbox' is checked, automatically check 'run_in_background_checkbox'
            self.run_in_background_checkbox.setChecked(True)

    def updateStartCheckboxState(self):

        # Check if 'run_in_background_checkbox' is unchecked, then uncheck 'start_on_system_start_checkbox'
        if not self.run_in_background_checkbox.isChecked():
            self.start_on_system_start_checkbox.setChecked(False)

    def save_settings(self):

        if SettingsManager.current_settings["general"]["auto_start_enabled"] != self.start_on_system_start_checkbox.isChecked():
            if self.start_on_system_start_checkbox.isChecked():
                StartupManager.add_to_startup(program_english_name)
            else:
                StartupManager.remove_from_startup(program_english_name)

        if SettingsManager.current_settings["reading"]["font_type"] != self.font_type_combo.currentData():
            self.parent.quran_view.setText(self.parent.quran.reload_quran(self.font_type_combo.currentData()))

        general_settings = {
            "run_in_background_enabled": self.run_in_background_checkbox.isChecked(),
            "auto_start_enabled": self.start_on_system_start_checkbox.isChecked(),
            "auto_save_position_enabled": self.auto_save_position_checkbox.isChecked(),
            "check_update_enabled": self.update_checkbox.isChecked(),
            "logging_enabled": self.log_checkbox.isChecked()
        }

        audio_settings = {
            "sound_effect_enabled": self.sound_checkbox.isChecked(),
            "start_with_basmala_enabled": self.basmala_checkbox.isChecked(),
            "speak_actions_enabled": self.speech_checkbox.isChecked(),
            "volume_level": self.volume.value(),
            "ayah_volume_level": self.ayah_volume.value(),
            "athkar_volume_level": self.athkar_volume.value()
        }

        listening_settings = {
            "reciter": self.reciters_combo.currentData(),
            "action_after_listening": self.action_combo.currentData(),
            "forward_time": self.duration_spinbox.value()
        }

        reading_settings = {
            "font_type": self.font_type_combo.currentData(),
            "auto_page_turn": self.turn_pages_checkbox.isChecked()
        }

        search_settings = {
            "ignore_tashkeel": self.ignore_tashkeel_checkbox.isChecked(),
            "ignore_hamza": self.ignore_hamza_checkbox.isChecked(),
            "match_whole_word": self.match_whole_word_checkbox.isChecked()
        }

        SettingsManager.write_settings({
            "general": general_settings,
            "audio": audio_settings,
            "listening": listening_settings,
            "reading": reading_settings,
            "search": search_settings
        })
        self.accept()
        self.deleteLater()

    def OnReset(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("تحذير")
        msg_box.setText("هل أنت متأكد من إعادة تعيين الإعدادات إلى الإعدادات الافتراضية؟")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        yes_button = msg_box.addButton("نعم", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("لا", QMessageBox.ButtonRole.NoRole)
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            SettingsManager.reset_settings()
            self.set_current_settings()

    def set_current_settings(self):
        current_settings = SettingsManager.current_settings    
        self.sound_checkbox.setChecked(current_settings["audio"]["sound_effect_enabled"])
        self.basmala_checkbox.setChecked(current_settings["audio"]["start_with_basmala_enabled"])
        self.speech_checkbox.setChecked(current_settings["audio"]["speak_actions_enabled"])
        self.volume.setValue(current_settings["audio"]["volume_level"])
        self.athkar_volume.setValue(current_settings["audio"]["athkar_volume_level"])
        self.ayah_volume.setValue(current_settings["audio"]["ayah_volume_level"])
        self.run_in_background_checkbox.setChecked(current_settings["general"]["run_in_background_enabled"])
        self.turn_pages_checkbox.setChecked(current_settings["reading"]["auto_page_turn"])
        self.start_on_system_start_checkbox.setChecked(current_settings["general"]["auto_start_enabled"])
        self.auto_save_position_checkbox.setChecked(current_settings["general"]["auto_save_position_enabled"])
        self.update_checkbox.setChecked(current_settings["general"]["check_update_enabled"])
        self.duration_spinbox.setValue(current_settings["listening"]["forward_time"])
        self.log_checkbox.setChecked(current_settings["general"]["logging_enabled"])
        self.ignore_tashkeel_checkbox.setChecked(current_settings["search"]["ignore_tashkeel"])
        self.ignore_hamza_checkbox.setChecked(current_settings["search"]["ignore_hamza"])
        self.match_whole_word_checkbox.setChecked(current_settings["search"]["match_whole_word"])
        # Update the reciter ComboBox
        reciter_id = current_settings["listening"]["reciter"]
        for index in range(self.reciters_combo.count()):
            if self.reciters_combo.itemData(index) == reciter_id:
                self.reciters_combo.setCurrentIndex(index)
                break

        stored_id = current_settings["listening"]["action_after_listening"]
        index = self.action_combo.findData(stored_id)
        if index != -1:
            self.action_combo.setCurrentIndex(index)

        stored_id = current_settings["reading"]["font_type"]
        index = self.font_type_combo.findData(stored_id)
        if index != -1:
            self.font_type_combo.setCurrentIndex(index)

    def reject(self):
        self.deleteLater()
        

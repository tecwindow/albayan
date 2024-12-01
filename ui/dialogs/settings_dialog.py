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
    QStackedWidget
)
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import Qt
from core_functions.Reciters import RecitersManager
from utils.const import data_folder
from utils.settings import SettingsManager
from utils.audio_player import AthkarPlayer, AyahPlayer, SoundEffectPlayer


class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("الإعدادات")
        self.resize(500, 400)
        self.reciters_manager = RecitersManager(data_folder / "quran" / "reciters.db")
        self.init_ui()
        self.set_current_settings()


    def init_ui(self):
        main_layout = QVBoxLayout()
        taps_layout = QHBoxLayout()

        tree_widget = QTreeWidget()
        tree_widget.setHeaderHidden(True)
        
        general_item = QTreeWidgetItem(["الإعدادات العامة"])
        audio_item = QTreeWidgetItem(["الصوت"])
        listening_item = QTreeWidgetItem(["الاستماع"])
        search_item = QTreeWidgetItem(["البحث"])
        
        tree_widget.addTopLevelItem(general_item)
        tree_widget.addTopLevelItem(audio_item)
        tree_widget.addTopLevelItem(listening_item)
        tree_widget.addTopLevelItem(search_item)
        
        self.stacked_widget = QStackedWidget()
        
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
        self.volume_label = QLabel("مستوى الصوت")
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
        self.basmala_checkbox = QCheckBox("تشغيل المؤثرات الصوتية مع فتح البرنامج")
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

        self.reciters_label = QLabel("القارئ")
        self.reciters_combo = QComboBox()
        reciters = self.reciters_manager.get_reciters()
        self.reciters_combo.setAccessibleName(self.reciters_label.text())
        for  row in reciters:
            display_text = f"{row['name']} - {row['rewaya']} - {row['type']} - ({row['bitrate']} kbps)"
            self.reciters_combo.addItem(display_text, row["id"])

        self.action_label = QLabel("الإجراء بعد الاستماع")
        self.action_combo = QComboBox()
        items_with_ids = [("إيقاف", 0), ("تكرار", 1), ("الانتقال إلى الآية التالية", 2)]
        [self.action_combo.addItem(text, id) for text, id in items_with_ids]
        self.action_combo.setAccessibleName(self.action_label.text())

        self.group_listening_layout.addWidget(self.reciters_label)
        self.group_listening_layout.addWidget(self.reciters_combo)
        self.group_listening_layout.addWidget(self.action_combo)
        self.group_listening_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.group_listening.setLayout(self.group_listening_layout)

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
        
        self.stacked_widget.addWidget(self.group_general)
        self.stacked_widget.addWidget(self.group_audio)
        self.stacked_widget.addWidget(self.group_listening)
        self.stacked_widget.addWidget(self.group_search)
        
        tree_widget.currentItemChanged.connect(lambda current, previous: self.stacked_widget.setCurrentIndex(tree_widget.indexOfTopLevelItem(current)))

        taps_layout.addWidget(tree_widget, stretch=1)
        taps_layout.addWidget(self.stacked_widget, stretch=2)
        
        main_layout.addLayout(taps_layout)

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
        general_settings = {
            "run_in_background_enabled": self.run_in_background_checkbox.isChecked(),
            "start_on_system_starts_enabled": self.start_on_system_start_checkbox.isChecked(),
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
            "action_after_listening": self.action_combo.currentData()
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
            "search": search_settings
        })
        self.accept()

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
        self.start_on_system_start_checkbox.setChecked(current_settings["general"]["start_on_system_starts_enabled"])
        self.auto_save_position_checkbox.setChecked(current_settings["general"]["auto_save_position_enabled"])
        self.update_checkbox.setChecked(current_settings["general"]["check_update_enabled"])
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


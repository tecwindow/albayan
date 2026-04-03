from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
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
    QLineEdit,
    QStackedWidget
)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt
from ui.widgets.spin_box import SpinBox
from core_functions.quran.types import QuranFontType, MarksType
from core_functions.Reciters import AyahReciter
from utils.const import program_english_name, Globals
from utils.paths import paths
from utils.settings import Config
from utils.logger import LogLevel, LoggerManager
from utils.audio_player import bass_initializer, AthkarPlayer, AyahPlayer, SurahPlayer, SoundEffectPlayer
from utils.Startup import StartupManager
import qtawesome as qta

logger = LoggerManager.get_logger(__name__)

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("الإعدادات")
        self.resize(750, 650)
        self.reciters_manager = AyahReciter(paths.data_folder / "quran" / "reciters.db")
        self.init_ui()
        self.set_current_settings()


    def init_ui(self):
        main_layout = QVBoxLayout()
        taps_layout = QHBoxLayout()

        # Tree widget for navigation
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setMinimumWidth(200)
        self.tree_widget.setStyleSheet("QTreeWidget { font-size: 14px; }")
        
        # Adding items to the tree with icons
        general_item = QTreeWidgetItem(["الإعدادات العامة"])
        general_item.setIcon(0, qta.icon("fa5s.cogs"))

        audio_item = QTreeWidgetItem(["الصوت"])
        audio_item.setIcon(0, qta.icon("fa5s.volume-up"))

        self.listening_item = QTreeWidgetItem(["الاستماع"])
        self.listening_item.setIcon(0, qta.icon("fa5s.headphones"))

        reading_item = QTreeWidgetItem(["القراءة"])
        reading_item.setIcon(0, qta.icon("fa5s.book"))

        surah_player_item = QTreeWidgetItem(["مشغل السور"])
        surah_player_item.setIcon(0, qta.icon("fa5s.play"))

        downloading_item = QTreeWidgetItem(["التنزيل"])
        downloading_item.setIcon(0, qta.icon("fa5s.download"))
 

        search_item = QTreeWidgetItem(["البحث"])
        search_item.setIcon(0, qta.icon("fa5s.search"))
        
        # Adding top-level items
        self.tree_widget.addTopLevelItem(general_item)
        self.tree_widget.addTopLevelItem(audio_item)
        self.tree_widget.addTopLevelItem(self.listening_item)
        self.tree_widget.addTopLevelItem(reading_item)
        self.tree_widget.addTopLevelItem(surah_player_item)
        self.tree_widget.addTopLevelItem(downloading_item)
        self.tree_widget.addTopLevelItem(search_item)
        
        # Stacked widget to switch views
        self.stacked_widget = QStackedWidget()
        
        # General settings
        self.group_general = QGroupBox("الإعدادات العامة")
        self.group_general_layout = QVBoxLayout()
        self.run_in_background_checkbox = QCheckBox("تشغيل البرنامج في الخلفية")
        self.start_on_system_start_checkbox = QCheckBox("تشغيل عند بدء تشغيل النظام")
        self.auto_save_position_checkbox = QCheckBox("حفظ الموضع الحالي تلقائيًا عند إغلاق البرنامج")
        self.auto_restore_position_checkbox = QCheckBox("استعادة الموضع الحالي عند فتح البرنامج")
        self.update_checkbox = QCheckBox("التحقق من التحديثات")
        self.log_levels_label = QLabel(self, text="مستوى السجل:")
        self.log_levels_combo = QComboBox(self)
        self.log_levels_combo.setAccessibleName(self.log_levels_label.text())
        for level in LogLevel:
            self.log_levels_combo.addItem(level.label, level.name)
        self.reset_button = QPushButton("استعادة الإعدادات الافتراضية")
        self.reset_button.clicked.connect(self.OnReset)
        
        self.group_general_layout.addWidget(self.run_in_background_checkbox)
        self.group_general_layout.addWidget(self.start_on_system_start_checkbox)
        self.group_general_layout.addWidget(self.auto_save_position_checkbox)
        self.group_general_layout.addWidget(self.auto_restore_position_checkbox)
        self.group_general_layout.addWidget(self.update_checkbox)
        self.group_general_layout.addWidget(self.log_levels_label)
        self.group_general_layout.addWidget(self.log_levels_combo)
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
        self.volume_device_label = QLabel("كرت الصوت لتشغيل أصوات البرنامج:")
        self.volume_device_combo = QComboBox(self)
        self.volume_device_combo .setAccessibleName(self.volume_device_label.text())
        self.ayah_volume_label = QLabel("مستوى صوت الآيات")
        self.ayah_volume = QSlider(Qt.Orientation.Horizontal)
        self.ayah_volume.setRange(0, 100)
        self.ayah_volume.valueChanged.connect(self.OnAyahVolume)
        self.ayah_volume.setAccessibleName(self.ayah_volume_label.text())
        self.ayah_volume.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.ayah_device_label = QLabel("كرت الصوت لتشغيل الآيات:")
        self.ayah_device_combo = QComboBox(self)
        self.ayah_device_combo.setAccessibleName(self.ayah_device_label.text())
        self.surah_volume_label = QLabel("مستوى صوت السور")
        self.surah_volume = QSlider(Qt.Orientation.Horizontal)
        self.surah_volume.setRange(0, 100)
        self.surah_volume.valueChanged.connect(self.OnSurahVolume)
        self.surah_volume.setAccessibleName(self.surah_volume_label.text())
        self.surah_volume.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.surah_device_label = QLabel("كرت الصوت لتشغيل السور:")
        self.surah_device_combo = QComboBox(self)
        self.surah_device_combo.setAccessibleName(self.surah_device_label.text())
        self.athkar_volume_label = QLabel("مستوى صوت الأذكار")
        self.athkar_volume = QSlider(Qt.Orientation.Horizontal)
        self.athkar_volume.setRange(0, 100)
        self.athkar_volume.valueChanged.connect(self.OnAthkarVolume)
        self.athkar_volume.setAccessibleName(self.athkar_volume_label.text())
        self.athkar_volume.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.athkar_device_label = QLabel("كرت الصوت لتشغيل الأذكار:")
        self.athkar_device_combo = QComboBox(self)
        self.athkar_device_combo.setAccessibleName(self.athkar_device_label.text())

        for device in bass_initializer.get_sound_cards():
            logger.info(f"Detected sound device: {device.name} (Index: {device.index})")
            self.volume_device_combo .addItem(device.name, device.index)
            self.ayah_device_combo.addItem(device.name, device.index)
            self.surah_device_combo.addItem(device.name, device.index)
            self.athkar_device_combo.addItem(device.name, device.index)

        self.sound_checkbox = QCheckBox("تفعيل المؤثرات الصوتية")
        self.basmala_checkbox = QCheckBox("تفعيل البسملة مع فتح البرنامج")
        self.speech_checkbox = QCheckBox("نطق الإجرائات")

        self.group_audio_layout.addWidget(self.volume_label)
        self.group_audio_layout.addWidget(self.volume)
        self.group_audio_layout.addWidget(self.volume_device_label)
        self.group_audio_layout.addWidget(self.volume_device_combo)
        self.group_audio_layout.addWidget(self.ayah_volume_label)
        self.group_audio_layout.addWidget(self.ayah_volume)
        self.group_audio_layout.addWidget(self.ayah_device_label)
        self.group_audio_layout.addWidget(self.ayah_device_combo)
        self.group_audio_layout.addWidget(self.surah_volume_label)
        self.group_audio_layout.addWidget(self.surah_volume)
        self.group_audio_layout.addWidget(self.surah_device_label)
        self.group_audio_layout.addWidget(self.surah_device_combo)
        self.group_audio_layout.addWidget(self.athkar_volume_label)
        self.group_audio_layout.addWidget(self.athkar_volume)
        self.group_audio_layout.addWidget(self.athkar_device_label)
        self.group_audio_layout.addWidget(self.athkar_device_combo)
        self.group_audio_layout.addWidget(self.sound_checkbox)
        self.group_audio_layout.addWidget(self.basmala_checkbox)
        self.group_audio_layout.addWidget(self.speech_checkbox)
        self.group_audio_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.group_audio.setLayout(self.group_audio_layout)
        
        self.group_listening = QGroupBox("إعدادات الاستماع")
        self.group_listening_layout = QVBoxLayout()

        self.reciters_label = QLabel("القارئ:")
        self.reciters_combo = QComboBox()
        self.reciters_combo.setAccessibleName(self.reciters_label.text())


        self.secondary_reciter_label = QLabel("القارئ الثانوي:")
        self.secondary_reciter_combo = QComboBox()
        self.secondary_reciter_combo.setAccessibleName(self.secondary_reciter_label.text())


        reciters = self.reciters_manager.get_reciters()
        for row in reciters:
            display_text = f"{row['name']} - {row['rewaya']} - {row['type']} - ({row['bitrate']} kbps)"
            self.reciters_combo.addItem(display_text, row["id"])
        self.secondary_reciter_combo.addItem("معطل", 0)
        for row in reciters:
            display_text = f"{row['name']} - {row['rewaya']} - {row['type']} - ({row['bitrate']} kbps)"
            self.secondary_reciter_combo.addItem(display_text, row["id"])


        self.sswitch_when_moving_checkbox = QCheckBox("تبديل القارئ عند الانتقال إلى الآية التالية تلقائيًا")

        self.sswitch_when_repeating_checkbox = QCheckBox("تبديل القارئ عند تكرار الآية تلقائيًا")



        self.repeat_limit_label = QLabel("عدد مرات تشغيل وتكرار الآية:")
        self.repeat_limit_spinbox = SpinBox(self)
        self.repeat_limit_spinbox.setAccessibleName(self.repeat_limit_label.text())        
        self.repeat_limit_spinbox.setRange(1, 10)
        self.repeat_limit_spinbox.setSingleStep(1)

        self.action_label = QLabel("الإجراء بعد الاستماع لكل آية:")
        self.action_combo = QComboBox()
        items_with_ids = [("إيقاف", 0), ("تكرار الآية بلا نهاية", 1), ("الانتقال إلى الآية التالية", 2)]
        for text, id in sorted(items_with_ids, key=lambda x: x[1]==1): self.action_combo.addItem(text, id)
        self.action_combo.setAccessibleName(self.action_label.text())



        self.text_repeat_label = QLabel("عدد مرات تشغيل وتكرار النص:")
        self.text_repeat_spinbox = SpinBox(self)
        self.text_repeat_spinbox.setAccessibleName(self.text_repeat_label.text())
        self.text_repeat_spinbox.setRange(1, 10)
        self.text_repeat_spinbox.setSingleStep(1)


        self.action_after_text_label = QLabel("الإجراء بعد نهاية النص:")
        self.action_after_text_combo = QComboBox()
        items_after_text = [("إيقاف", 0), ("تكرار النص الحالي بلا نهاية", 1), ("تنبيه صوتي", 2), ("الانتقال إلى التالي", 3)]
        for text, id in sorted(items_after_text, key=lambda x: x[1]==1): self.action_after_text_combo.addItem(text, id)
        self.action_after_text_combo.setAccessibleName(self.action_after_text_label.text())

        self.duration_label = QLabel("مدة التقديم والترجيع (بالثواني):")
        self.duration_spinbox = SpinBox(self)
        self.duration_spinbox.setAccessibleName(self.duration_label.text())        
        self.duration_spinbox.setRange(2, 15)
        self.duration_spinbox.setSingleStep(1)


        self.auto_move_focus_checkbox = QCheckBox("نقل المؤشر تلقائيًا إلى الآية التي يتم تشغيلها")

        self.auto_play_checkbox = QCheckBox("تشغيل الآية تلقائيًا عند الذهاب إليها من الذهاب إلى")

        self.group_listening_layout.addWidget(self.reciters_label)
        self.group_listening_layout.addWidget(self.reciters_combo)
        self.group_listening_layout.addWidget(self.secondary_reciter_label)
        self.group_listening_layout.addWidget(self.secondary_reciter_combo)
        self.group_listening_layout.addWidget(self.sswitch_when_moving_checkbox)
        self.group_listening_layout.addWidget(self.sswitch_when_repeating_checkbox)
        self.group_listening_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))  # مسافة نتوسطة
        self.group_listening_layout.addWidget(self.repeat_limit_label)
        self.group_listening_layout.addWidget(self.repeat_limit_spinbox)
        self.group_listening_layout.addWidget(self.action_label)
        self.group_listening_layout.addWidget(self.action_combo)
        self.group_listening_layout.addWidget(self.text_repeat_label)
        self.group_listening_layout.addWidget(self.text_repeat_spinbox)
        self.group_listening_layout.addWidget(self.action_after_text_label)
        self.group_listening_layout.addWidget(self.action_after_text_combo)
        self.group_listening_layout.addWidget(self.duration_label)
        self.group_listening_layout.addWidget(self.duration_spinbox)
        self.group_listening_layout.addWidget(self.auto_move_focus_checkbox)
        self.group_listening_layout.addWidget(self.auto_play_checkbox)
        self.group_listening.setLayout(self.group_listening_layout)
        self.group_listening_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


        self.repeat_limit_spinbox.valueChanged.connect(self.update_action_combo_label)
        self.action_combo.currentIndexChanged.connect(self.update_repeat_limit_state)
        self.text_repeat_spinbox.valueChanged.connect(self.update_action_after_text_combo_label)
        self.action_after_text_combo.currentIndexChanged.connect(self.update_text_repeat_state)



        self.group_reading = QGroupBox("إعدادات القراءة")
        self.group_reading_layout = QVBoxLayout()
        self.font_type_label = QLabel("نوع الخط:")
        self.font_type_combo = QComboBox()
        items_with_ids_list = [("الخط الحديث", QuranFontType.DEFAULT), ("الخط العثماني", QuranFontType.UTHMANI)]
        [self.font_type_combo.addItem(text, font_type) for text, font_type in items_with_ids_list]
        self.font_type_combo.setAccessibleName(self.font_type_label.text())

        self.marks_type_label = QLabel("نوع علامات الوقف:")
        self.marks_type_combo = QComboBox()
        marks_options = [("الافتراضي", MarksType.DEFAULT), ("النصي", MarksType.TEXT), ("برايل", MarksType.ACCESSIBLE)]
        [self.marks_type_combo.addItem(text, id) for text, id in marks_options]
        self.marks_type_combo.setAccessibleName(self.marks_type_label.text())

        self.turn_pages_checkbox = QCheckBox("قلب الصفحات تلقائيا")

        self.group_reading_layout.addWidget(self.font_type_label)
        self.group_reading_layout.addWidget(self.font_type_combo)
        self.group_reading_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))  # مسافة أكبر
        self.group_reading_layout.addWidget(self.marks_type_label)
        self.group_reading_layout.addWidget(self.marks_type_combo)
        self.group_reading_layout.addWidget(self.turn_pages_checkbox)
        self.group_reading_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.group_reading.setLayout(self.group_reading_layout)

        self.group_surah_player = QGroupBox("إعدادات مشغل السور")
        self.group_surah_player_layout = QVBoxLayout()

        self.repeat_surah_label = QLabel("عدد مرات تشغيل وتكرار السورة:")
        self.repeat_surah_spinbox = SpinBox(self)
        self.repeat_surah_spinbox.setAccessibleName(self.repeat_surah_label.text())
        self.repeat_surah_spinbox.setRange(1, 10)


        self.action_after_surah_label = QLabel("الإجراء بعد نهاية السورة:")
        self.action_after_surah_combo = QComboBox()
        items_surah = [("إيقاف", 0), ("تكرار السورة بلا نهاية", 1), ("الانتقال إلى السورة التالية", 2)]
        for text, id in sorted(items_surah, key=lambda x: x[1]==1): self.action_after_surah_combo.addItem(text, id)
        self.action_after_surah_combo.setAccessibleName(self.action_after_surah_label.text())

        self.player_in_background_checkbox = QCheckBox("تشغيل السور في الخلفية")


        self.group_surah_player_layout.addWidget(self.repeat_surah_label)
        self.group_surah_player_layout.addWidget(self.repeat_surah_spinbox)
        self.group_surah_player_layout.addWidget(self.action_after_surah_label)
        self.group_surah_player_layout.addWidget(self.action_after_surah_combo)
        self.group_surah_player_layout.addWidget(self.player_in_background_checkbox)
        self.group_surah_player_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.group_surah_player.setLayout(self.group_surah_player_layout)


        self.action_after_surah_combo.currentIndexChanged.connect(self.update_repeat_surah_state)
        self.repeat_surah_spinbox.valueChanged.connect(self.update_action_after_surah_combo_label)

        self.group_downloading = QGroupBox("إعدادات التنزيل")
        self.group_downloading_layout = QVBoxLayout()

        self.files_to_download_at_the_same_time_label = QLabel("عدد الملفات التي يمكن تنزيلها في نفس الوقت:")
        self.files_to_download_at_the_same_time_combo = QComboBox()
        items_files = [("ملف 1", 1), ("ملفين", 2), ("3 ملفات", 3), ("4 ملفات", 4), ("5 ملفات", 5)]
        [self.files_to_download_at_the_same_time_combo.addItem(text, id) for text, id in items_files]
        self.files_to_download_at_the_same_time_combo.setAccessibleName(self.files_to_download_at_the_same_time_label.text())



        self.download_path_label = QLabel("مسار التنزيل الحالي:")
        self.download_path_edit = QLineEdit()
        self.download_path_edit.setReadOnly(True)
        self.download_path_edit.setText(str(Config.downloading.download_path))
        self.download_path_edit.setAccessibleName(self.download_path_label.text())


        self.change_download_path_button = QPushButton("تغيير المسار")

        self.offline_playback_checkbox = QCheckBox("تشغيل السور والآيات التي تم تنزيلها دون إنترنت")

        self.show_incomplete_download_warning_checkbox = QCheckBox("إظهار تحذير عند إغلاق البيان  في حال وجود ملفات لم يكتمل تنزيلها")

        self.auto_refresh_downloads_lists_checkbox = QCheckBox("تحديث قوائم التنزيلات تلقائيا")

        self.group_downloading_layout.addWidget(self.files_to_download_at_the_same_time_label)  
        self.group_downloading_layout.addWidget(self.files_to_download_at_the_same_time_combo)
        self.group_downloading_layout.addWidget(self.download_path_label)
        self.group_downloading_layout.addWidget(self.download_path_edit)
        self.group_downloading_layout.addWidget(self.change_download_path_button)
        self.group_downloading_layout.addWidget(self.offline_playback_checkbox)
        self.group_downloading_layout.addWidget(self.show_incomplete_download_warning_checkbox)
        self.group_downloading_layout.addWidget(self.auto_refresh_downloads_lists_checkbox)
        self.group_downloading_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.group_downloading.setLayout(self.group_downloading_layout)

        self.change_download_path_button.clicked.connect(self.change_download_path)

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
        self.stacked_widget.addWidget(self.group_surah_player)
        self.stacked_widget.addWidget(self.group_downloading)
        self.stacked_widget.addWidget(self.group_search)
        
#        self.tree_widget.currentItemChanged.connect(lambda current, previous: self.stacked_widget.setCurrentIndex(self.tree_widget.indexOfTopLevelItem(current)))

        # Linking tree widget with stacked widget
        self.tree_widget.currentItemChanged.connect(
            lambda current, previous: self.stacked_widget.setCurrentIndex(
                self.tree_widget.indexOfTopLevelItem(current)
            )
        )


        # Layout adjustments
        taps_layout.addWidget(self.tree_widget, stretch=1)
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

        close_shortcut = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut.activated.connect(self.reject)

        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(close_button)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

        self.update_action_combo_label(self.repeat_limit_spinbox.value())
        self.update_action_after_text_combo_label(self.text_repeat_spinbox.value())
        self.update_action_after_surah_combo_label(self.repeat_surah_spinbox.value())



    def update_repeat_surah_state(self):
        """Disable or enable repeat_surah_spinbox based on action_after_surah_combo selection."""
        current_id = self.action_after_surah_combo.currentData()
        self.repeat_surah_spinbox.setEnabled(current_id != 1)

    def update_repeat_limit_state(self):
        current_id = self.action_combo.currentData()
        if current_id == 1:
            self.repeat_limit_spinbox.setEnabled(False)
        else:
            self.repeat_limit_spinbox.setEnabled(True)


    def update_text_repeat_state(self):
        current_id = self.action_after_text_combo.currentData()
        if current_id == 1:
            self.text_repeat_spinbox.setEnabled(False)
        else:
            self.text_repeat_spinbox.setEnabled(True)





    def update_action_combo_label(self, value: int):
        forms = {1: "مرة واحدة", 2: "مرتين"}
        times_text = forms.get(value, f"{value} مرات")


        templates = {
            0: "تشغيل الآية {} ثم إيقاف",
            2: "تشغيل الآية {} ثم الانتقال إلى الآية التالية",
        }

        for i in range(self.action_combo.count()):
            id = self.action_combo.itemData(i)
            if id in templates:
                self.action_combo.setItemText(i, templates[id].format(times_text))

    def update_action_after_surah_combo_label(self, value: int):

        templates = {
            0: "تشغيل السورة {} ثم إيقاف",
            2: "تشغيل السورة {} ثم الانتقال إلى السورة التالية",
        }


        forms = {1: "مرة واحدة", 2: "مرتين"}
        times_text = forms.get(value, f"{value} مرات")

        for i in range(self.action_after_surah_combo.count()):
            id = self.action_after_surah_combo.itemData(i)
            if id in templates:
                self.action_after_surah_combo.setItemText(i, templates[id].format(times_text))


    def update_action_after_text_combo_label(self, value: int):
        forms = {1: "مرة واحدة", 2: "مرتين"}
        times_text = forms.get(value, f"{value} مرات")

        templates = {
            0: "تشغيل {} ثم إيقاف",
            2: "تشغيل {} ثم تنبيه صوتي",
            3: "تشغيل {} ثم الانتقال إلى التالي",
        }

        for i in range(self.action_after_text_combo.count()):
            id = self.action_after_text_combo.itemData(i)
            if id in templates:
                self.action_after_text_combo.setItemText(i, templates[id].format(times_text))



    def change_download_path(self):
        logger.debug("Changing download path.")
        new_path = QFileDialog.getExistingDirectory(self, "اختر مجلد التنزيل", "")
        if new_path:
            self.download_path_edit.setText(new_path)
            logger.debug(f"Download path changed to: {new_path}")
 

    def OnSurahVolume(self) -> None:
        volume = self.surah_volume.value()
        logger.debug(f"Surah volume changed to {volume}.")
        for instance in SurahPlayer.instances:
            instance.set_volume(volume)

    def OnAyahVolume(self) -> None:
        volume = self.ayah_volume.value()
        logger.debug(f"Ayah volume changed to {volume}.")
        for instance in AyahPlayer.instances:
            instance.set_volume(volume)

    def OnAthkarVolume(self) -> None:
        volume = self.athkar_volume.value()
        logger.debug(f"Athkar volume changed to {volume}.")
        for instance in AthkarPlayer.instances:
            instance.set_volume(volume)

    def OnVolume(self) -> None:
        volume = self.volume.value()
        logger.debug(f"Sound effects volume changed to {volume}.")
        for instance in SoundEffectPlayer.instances:
            instance.set_volume(volume)

    def updateBackgroundCheckboxState(self):
        # Check if 'start_on_system_start_checkbox' is checked
        if self.start_on_system_start_checkbox.isChecked():
            # If 'start_on_system_start_checkbox' is checked, automatically check 'run_in_background_checkbox'
            self.run_in_background_checkbox.setChecked(True)
            logger.debug("Enabled 'Run in Background' as 'Start on System Startup' is checked.")

    def updateStartCheckboxState(self):

        # Check if 'run_in_background_checkbox' is unchecked, then uncheck 'start_on_system_start_checkbox'
        if not self.run_in_background_checkbox.isChecked():
            self.start_on_system_start_checkbox.setChecked(False)
            logger.debug("'Run in Background' is unchecked, disabled 'Start on System Startup'.")

    def save_settings(self):
        logger.debug("Saving user settings.")
        # Apply new sound cards
        SurahPlayer.apply_new_sound_card(self.surah_device_combo.currentData())
        AyahPlayer.apply_new_sound_card(self.ayah_device_combo.currentData())
        AthkarPlayer.apply_new_sound_card(self.athkar_device_combo.currentData())
        SoundEffectPlayer.apply_new_sound_card(self.volume_device_combo.currentData())

        #apply new log level
        log_level = LogLevel.from_name(self.log_levels_combo.currentData())
        LoggerManager.change_log_level(log_level)

        if Config.general.auto_start_enabled != self.start_on_system_start_checkbox.isChecked():
            if self.start_on_system_start_checkbox.isChecked():
                StartupManager.add_to_startup(program_english_name)
            else:
                StartupManager.remove_from_startup(program_english_name)

        if Config.reading.font_type != self.font_type_combo.currentData().value:
            new_font_type = self.font_type_combo.currentData()
            logger.info(f"Font type changed from {QuranFontType.from_int(Config.reading.font_type)} to {new_font_type}. Reloading Quran text.")
            self.parent.quran_manager.get_surahs.cache_clear()
            self.parent.quran_manager.font_type = new_font_type
            self.parent.quran_view.setText(self.parent.quran_manager.get_current_content())
            Globals.effects_manager.play("change")
        if Config.reading.marks_type != self.marks_type_combo.currentData().value:
            new_marks_type = self.marks_type_combo.currentData()
            self.parent.quran_manager.formatter_options.marks_type = new_marks_type
            logger.info(f"Marks type changed from {MarksType.from_int(Config.reading.marks_type)} to {new_marks_type}. Reloading Quran text.")
            self.parent.quran_view.setText(self.parent.quran_manager.get_current_content())
            Globals.effects_manager.play("change")
        if Config.reading.auto_page_turn != self.turn_pages_checkbox.isChecked():
            self.parent.quran_manager.formatter_options.auto_page_turn = self.turn_pages_checkbox.isChecked()
            self.parent.quran_view.setText(self.parent.quran_manager.get_current_content())
                
        # Update settings in Config
        Config.general.run_in_background_enabled = self.run_in_background_checkbox.isChecked()
        Config.general.auto_start_enabled = self.start_on_system_start_checkbox.isChecked()
        Config.general.auto_save_position_enabled = self.auto_save_position_checkbox.isChecked()
        Config.general.auto_restore_position_enabled = self.auto_restore_position_checkbox.isChecked()
        Config.general.check_update_enabled = self.update_checkbox.isChecked()
        Config.general.log_level = self.log_levels_combo.currentData()

        Config.audio.sound_effect_enabled = self.sound_checkbox.isChecked()
        Config.audio.start_with_basmala_enabled = self.basmala_checkbox.isChecked()
        Config.audio.speak_actions_enabled = self.speech_checkbox.isChecked()
        Config.audio.volume_level = self.volume.value()
        Config.audio.volume_device = self.volume_device_combo.currentData()
        Config.audio.ayah_volume_level = self.ayah_volume.value()
        Config.audio.ayah_device = self.ayah_device_combo.currentData()
        Config.audio.surah_volume_level = self.surah_volume.value()
        Config.audio.surah_device = self.surah_device_combo.currentData()
        Config.audio.athkar_volume_level = self.athkar_volume.value()
        Config.audio.athkar_device = self.athkar_device_combo.currentData()

        Config.listening.reciter = self.reciters_combo.currentData()
        Config.listening.secondary_reciter = self.secondary_reciter_combo.currentData()
        Config.listening.use_secondary_reciter_when_moving = self.sswitch_when_moving_checkbox.isChecked()
        Config.listening.use_secondary_reciter_when_repeating = self.sswitch_when_repeating_checkbox.isChecked()
        Config.listening.action_after_listening = self.action_combo.currentData()
        Config.listening.forward_time = self.duration_spinbox.value()
        Config.listening.ayah_repeat_count = self.repeat_limit_spinbox.value()
        Config.listening.action_after_text = self.action_after_text_combo.currentData()
        Config.listening.text_repeat_count = self.text_repeat_spinbox.value()
        Config.listening.auto_move_focus = self.auto_move_focus_checkbox.isChecked()
        Config.listening.auto_play_ayah_after_go_to = self.auto_play_checkbox.isChecked()

        Config.reading.font_type = self.font_type_combo.currentData().value
        Config.reading.auto_page_turn = self.turn_pages_checkbox.isChecked()
        Config.reading.marks_type = self.marks_type_combo.currentData().value

        Config.surah_player.action_after_surah = self.action_after_surah_combo.currentData()
        Config.surah_player.surah_repeat_count = self.repeat_surah_spinbox.value()
        Config.surah_player.play_surah_in_background_enabled = self.player_in_background_checkbox.isChecked()

        Config.downloading.files_to_download_at_the_same_time = self.files_to_download_at_the_same_time_combo.currentData()
        Config.downloading.download_path = self.download_path_edit.text()
        Config.downloading.show_incomplete_download_warning = self.show_incomplete_download_warning_checkbox.isChecked()
        Config.downloading.offline_playback = self.offline_playback_checkbox.isChecked()
        Config.downloading.auto_refresh_downloads_lists = self.auto_refresh_downloads_lists_checkbox.isChecked()


        Config.search.ignore_tashkeel = self.ignore_tashkeel_checkbox.isChecked()
        Config.search.ignore_hamza = self.ignore_hamza_checkbox.isChecked()
        Config.search.match_whole_word = self.match_whole_word_checkbox.isChecked()

        # Save settings to file
        logger.debug("Saving settings to configuration file.")
        new_settings = "\n".join([str(section_obj) for section_obj in Config.sections().values()])
        logger.debug(new_settings)
        Config.save_settings()

        self.accept()
        self.deleteLater()

    def OnReset(self):
        logger.warning("User requested settings reset.")
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("تحذير")
        msg_box.setText("هل أنت متأكد من إعادة تعيين الإعدادات إلى الإعدادات الافتراضية؟")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        yes_button = msg_box.addButton("نعم", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("لا", QMessageBox.ButtonRole.NoRole)
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            logger.debug("Resetting settings to default values.")
            Config.reset_settings()
            self.set_current_settings()

    def set_current_settings(self):
        logger.debug("Applying current settings to UI elements.")
        self.sound_checkbox.setChecked(Config.audio.sound_effect_enabled)
        self.basmala_checkbox.setChecked(Config.audio.start_with_basmala_enabled)
        self.speech_checkbox.setChecked(Config.audio.speak_actions_enabled)
        self.volume.setValue(Config.audio.volume_level)
        self.athkar_volume.setValue(Config.audio.athkar_volume_level)
        self.ayah_volume.setValue(Config.audio.ayah_volume_level)
        self.surah_volume.setValue(Config.audio.surah_volume_level)
        self.run_in_background_checkbox.setChecked(Config.general.run_in_background_enabled)
        self.turn_pages_checkbox.setChecked(Config.reading.auto_page_turn)
        self.start_on_system_start_checkbox.setChecked(Config.general.auto_start_enabled)
        self.auto_save_position_checkbox.setChecked(Config.general.auto_save_position_enabled)
        self.auto_restore_position_checkbox.setChecked(Config.general.auto_restore_position_enabled)
        self.update_checkbox.setChecked(Config.general.check_update_enabled)
        self.duration_spinbox.setValue(Config.listening.forward_time)
        self.repeat_limit_spinbox.setValue(Config.listening.ayah_repeat_count)
        self.text_repeat_spinbox.setValue(Config.listening.text_repeat_count)
        self.repeat_surah_spinbox.setValue(Config.surah_player.surah_repeat_count)
        self.player_in_background_checkbox.setChecked(Config.surah_player.play_surah_in_background_enabled)
        self.auto_move_focus_checkbox.setChecked(Config.listening.auto_move_focus)
        self.auto_play_checkbox.setChecked(Config.listening.auto_play_ayah_after_go_to)
        self.sswitch_when_moving_checkbox.setChecked(Config.listening.use_secondary_reciter_when_moving)
        self.sswitch_when_repeating_checkbox.setChecked(Config.listening.use_secondary_reciter_when_repeating)
        self.download_path_edit.setText(Config.downloading.download_path)
        self.show_incomplete_download_warning_checkbox.setChecked(Config.downloading.show_incomplete_download_warning)
        self.offline_playback_checkbox.setChecked(Config.downloading.offline_playback)
        self.auto_refresh_downloads_lists_checkbox.setChecked(Config.downloading.auto_refresh_downloads_lists)
        self.ignore_tashkeel_checkbox.setChecked(Config.search.ignore_tashkeel)
        self.ignore_hamza_checkbox.setChecked(Config.search.ignore_hamza)
        self.match_whole_word_checkbox.setChecked(Config.search.match_whole_word)

        combo_config = [
            (self.log_levels_combo, Config.general.log_level),
            (self.reciters_combo, Config.listening.reciter),
            (self.secondary_reciter_combo, Config.listening.secondary_reciter),
            (self.action_combo, Config.listening.action_after_listening),
        (self.action_after_text_combo    , Config.listening.action_after_text),
            (self.font_type_combo, QuranFontType.from_int(Config.reading.font_type)),
    (self.marks_type_combo, MarksType.from_int(Config.reading.marks_type)),
    (self.files_to_download_at_the_same_time_combo, Config.downloading.files_to_download_at_the_same_time),
    (self.action_after_surah_combo, Config.surah_player.action_after_surah),
            (self.ayah_device_combo, Config.audio.ayah_device),
            (self.surah_device_combo, Config.audio.surah_device),
            (        self.volume_device_combo, Config.audio.volume_device),
            (self.athkar_device_combo, Config.audio.athkar_device)
        ]

        for combo, value in combo_config:
            index = combo.findData(value)
            if index != -1:
                combo.setCurrentIndex(index)
        
    def open_listening_tab_and_focus_reciter(self):
        self.tree_widget.setCurrentItem(self.listening_item)
        self.reciters_combo.setFocus()

    def open_listening_tab_and_focus_action(self):
        self.tree_widget.setCurrentItem(self.listening_item)
        self.action_combo.setFocus()

    def open_listening_tab_and_focus_repeat_limit(self):
        self.tree_widget.setCurrentItem(self.listening_item)    
        self.repeat_limit_spinbox.setFocus()


    def open_listening_tab_and_focus_text_repeat(self):
        self.tree_widget.setCurrentItem(self.listening_item)
        self.text_repeat_spinbox.setFocus()


    def open_listening_tab_and_focus_action_after_text(self):
        self.tree_widget.setCurrentItem(self.listening_item)
        self.action_after_text_combo.setFocus()

    def reject(self):
        self.deleteLater()
    
    def closeEvent(self, a0):
        logger.debug("Settings dialog closed.")
        return super().closeEvent(a0)
    

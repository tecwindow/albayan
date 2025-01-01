import os
import qtawesome as qta
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QGroupBox, QSlider, QWidget, QMainWindow
)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt
from core_functions.Reciters import SurahReciter
from utils.const import data_folder


class SuraPlayerWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("مشغل القرآن")
        self.resize(600, 400)

        # Dropdown menus for reciters and surahs
        self.reciters = SurahReciter(data_folder / "quran" / "reciters.db")
        self.surahs = [str(i) for i in range(1, 115)]

        # Set up central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Status bar for info display
        self.statusBar().showMessage("مرحبًا بك في مشغل القرآن")

        # Dropdowns for reciters and surahs
        self.selection_group = QGroupBox("التحديدات")
        selection_layout = QHBoxLayout()

        self.reciter_label = QLabel("القارئ:")
        self.reciter_combo = QComboBox()
        self.reciter_combo.setAccessibleName(self.reciter_label.text())
        for row in self.reciters.get_reciters():
            display_text = f"{row['name']} - {row['rewaya']} - ({row['bitrate']} kbps)"
            self.reciter_combo.addItem(display_text, row["id"])

        self.surah_label = QLabel("السورة:")
        self.surah_combo = QComboBox()
        self.surah_combo.setAccessibleName(self.surah_label.text())
        self.surah_combo.addItems(self.surahs)

        selection_layout.addWidget(self.reciter_label)
        selection_layout.addWidget(self.reciter_combo)
        selection_layout.addWidget(self.surah_label)
        selection_layout.addWidget(self.surah_combo)
        self.selection_group.setLayout(selection_layout)

        # Control buttons
        control_layout = QHBoxLayout()
        self.rewind_button = QPushButton(qta.icon("fa.backward"), "")
        self.rewind_button.setAccessibleName("ترجيع")
        self.play_pause_button = QPushButton(qta.icon("fa.play"), "")
        self.play_pause_button.setAccessibleName("تشغيل")
        self.forward_button = QPushButton(qta.icon("fa.forward"), "")
        self.forward_button.setAccessibleName("تقديم")
        self.previous_surah_button = QPushButton(qta.icon("fa.step-backward"), "")
        self.previous_surah_button.setAccessibleName("السورة السابقة")
        self.next_surah_button = QPushButton(qta.icon("fa.step-forward"), "")
        self.next_surah_button.setAccessibleName("السورة التالية")
        self.volume_down_button = QPushButton(qta.icon("fa.volume-down"), "")
        self.volume_down_button.setAccessibleName("خفض الصوت")
        self.volume_up_button = QPushButton(qta.icon("fa.volume-up"), "")
        self.volume_up_button.setAccessibleName("رفع الصوت")
        
        control_layout.addWidget(self.volume_down_button)
        control_layout.addWidget(self.previous_surah_button)
        control_layout.addWidget(self.rewind_button)
        control_layout.addWidget(self.play_pause_button)
        control_layout.addWidget(self.forward_button)
        control_layout.addWidget(self.next_surah_button)
        control_layout.addWidget(self.volume_up_button)

        # Sliders for progress and volume
        self.progress_group = QGroupBox("شريط التقدم")
        progress_layout = QVBoxLayout()
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setAccessibleName("TimeSlider")
        self.time_slider.setRange(0, 100)
        self.time_slider.setValue(0)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setAccessibleName("VolumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)

        self.elapsed_time_label = QLabel("0:00")
        self.remaining_time_label = QLabel("0:00")
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.elapsed_time_label)
        time_layout.addWidget(self.remaining_time_label)

        progress_layout.addWidget(self.time_slider)
        progress_layout.addWidget(QLabel("الصوت:"))
        progress_layout.addWidget(self.volume_slider)
        progress_layout.addLayout(time_layout)
        self.progress_group.setLayout(progress_layout)

        # Add elements to the main layout
        layout.addWidget(self.selection_group)
        layout.addLayout(control_layout)
        layout.addWidget(self.progress_group)

        # Connect signals to events
        self.reciter_combo.currentIndexChanged.connect(self.update_current_reciter)
        self.surah_combo.currentIndexChanged.connect(self.update_current_surah)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.volume_slider.valueChanged.connect(self.update_volume)
        self.time_slider.sliderMoved.connect(self.update_time)

        # Disable focus on elements
        self.disable_focus()

        # Set up keyboard shortcuts
        self.setup_shortcuts()

    def disable_focus(self):
        """Disable focus on all elements."""
        widgets = [
            self.rewind_button,
            self.play_pause_button,
            self.forward_button,
            self.previous_surah_button,
            self.next_surah_button,
            self.volume_up_button,
            self.volume_down_button,
            self.reciter_combo,
            self.surah_combo,
            self.time_slider,
            self.volume_slider
        ]
        for widget in widgets:
            widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        #QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.forward)
        #QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.rewind)
        #QShortcut(QKeySequence(Qt.Key.Key_Up), self, self.volume_up)
        #QShortcut(QKeySequence(Qt.Key.Key_Down), self, self.volume_down)
        QShortcut(QKeySequence("N"), self, self.next_surah)
        QShortcut(QKeySequence("B"), self, self.previous_surah)
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.toggle_play_pause)

    def update_current_reciter(self):
        """Update the currently selected reciter."""
        current_reciter = self.reciter_combo.currentText()
        self.statusBar().showMessage(f"القارئ الحالي: {current_reciter}")

    def update_current_surah(self):
        """Update the currently selected surah."""
        current_surah = self.surah_combo.currentText()
        self.statusBar().showMessage(f"السورة الحالية: {current_surah}")

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.play_pause_button.icon().name() == "fa.play":
            self.play_pause_button.setIcon(qta.icon("fa.pause"))
            self.statusBar().showMessage("تشغيل")
        else:
            self.play_pause_button.setIcon(qta.icon("fa.play"))
            self.statusBar().showMessage("إيقاف مؤقت")

    def forward(self):
        """Skip forward."""
        self.statusBar().showMessage("تخطي للأمام")

    def rewind(self):
        """Skip backward."""
        self.statusBar().showMessage("تخطي للخلف")

    def next_surah(self):
        """Go to the next surah."""
        self.statusBar().showMessage("السورة التالية")

    def previous_surah(self):
        """Go to the previous surah."""
        self.statusBar().showMessage("السورة السابقة")

    def update_volume(self):
        """Update the volume based on slider position."""
        volume = self.volume_slider.value()
        self.statusBar().showMessage(f"الصوت: {volume}%")

    def update_time(self, position):
        """Update the time slider position."""
        self.statusBar().showMessage(f"تحديد الوقت: {position}%")


import os
import qtawesome as qta
from PyQt6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QGroupBox,
    QProgressBar,
    QWidget
)
from PyQt6.QtGui import QGuiApplication, QWindow, QShortcut, QKeySequence
from PyQt6.QtCore import Qt


class SuraPlayerDialog(QWindow):
    def __init__(self, title, reciters, surahs):
        super().__init__()
        self.setTitle(title)
        self.resize(600, 400)

        # Dropdown menus for reciters and surahs
        self.reciters = reciters
        self.surahs = surahs

        # Set up the interface container
        self.container = QWidget.createWindowContainer(self)
        layout = QVBoxLayout(self.container)

        # Playback information
        self.info_group = QGroupBox("Playback Status")
        info_layout = QVBoxLayout()
        self.current_reciter_label = QLabel("Reciter: Not Selected")
        self.current_surah_label = QLabel("Surah: Not Selected")
        info_layout.addWidget(self.current_reciter_label)
        info_layout.addWidget(self.current_surah_label)
        self.info_group.setLayout(info_layout)

        # Dropdowns for reciters and surahs
        self.selection_group = QGroupBox("Selections")
        selection_layout = QHBoxLayout()
        self.reciter_combo = QComboBox()
        self.reciter_combo.addItems(self.reciters)
        self.surah_combo = QComboBox()
        self.surah_combo.addItems(self.surahs)
        selection_layout.addWidget(QLabel("Reciter:"))
        selection_layout.addWidget(self.reciter_combo)
        selection_layout.addWidget(QLabel("Surah:"))
        selection_layout.addWidget(self.surah_combo)
        self.selection_group.setLayout(selection_layout)

        # Control buttons
        control_layout = QHBoxLayout()
        self.rewind_button = QPushButton(qta.icon("fa.backward"), "")
        self.play_pause_button = QPushButton(qta.icon("fa.play"), "")
        self.forward_button = QPushButton(qta.icon("fa.forward"), "")
        self.previous_surah_button = QPushButton(qta.icon("fa.step-backward"), "")
        self.next_surah_button = QPushButton(qta.icon("fa.step-forward"), "")
        self.volume_down_button = QPushButton(qta.icon("fa.volume-down"), "")
        self.volume_up_button = QPushButton(qta.icon("fa.volume-up"), "")
        control_layout.addWidget(self.volume_down_button)
        control_layout.addWidget(self.previous_surah_button)
        control_layout.addWidget(self.rewind_button)
        control_layout.addWidget(self.play_pause_button)
        control_layout.addWidget(self.forward_button)
        control_layout.addWidget(self.next_surah_button)
        control_layout.addWidget(self.volume_up_button)

        # Progress bar
        self.progress_group = QGroupBox("Progress Bar")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.elapsed_time_label = QLabel("0:00")
        self.remaining_time_label = QLabel("0:00")
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.elapsed_time_label)
        time_layout.addWidget(self.remaining_time_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addLayout(time_layout)
        self.progress_group.setLayout(progress_layout)

        # Add elements to the main layout
        layout.addWidget(self.info_group)
        layout.addWidget(self.selection_group)
        layout.addLayout(control_layout)
        layout.addWidget(self.progress_group)

        # Connect signals to events
        self.reciter_combo.currentIndexChanged.connect(self.update_current_reciter)
        self.surah_combo.currentIndexChanged.connect(self.update_current_surah)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.volume_up_button.clicked.connect(self.volume_up)
        self.volume_down_button.clicked.connect(self.volume_down)

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
            self.progress_bar
        ]
        for widget in widgets:
            widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.forward)
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.rewind)
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, self.volume_up)
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, self.volume_down)
        QShortcut(QKeySequence("N"), self, self.next_surah)
        QShortcut(QKeySequence("B"), self, self.previous_surah)
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.toggle_play_pause)

    def update_current_reciter(self):
        """Update the currently selected reciter."""
        current_reciter = self.reciter_combo.currentText()
        self.current_reciter_label.setText(f"Reciter: {current_reciter}")

    def update_current_surah(self):
        """Update the currently selected surah."""
        current_surah = self.surah_combo.currentText()
        self.current_surah_label.setText(f"Surah: {current_surah}")

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.play_pause_button.icon().name() == "fa.play":
            self.play_pause_button.setIcon(qta.icon("fa.pause"))
        else:
            self.play_pause_button.setIcon(qta.icon("fa.play"))

    def forward(self):
        """Skip forward."""
        print("Skipped forward")

    def rewind(self):
        """Skip backward."""
        print("Skipped backward")

    def next_surah(self):
        """Go to the next surah."""
        print("Next surah")

    def previous_surah(self):
        """Go to the previous surah."""
        print("Previous surah")

    def volume_up(self):
        """Increase volume."""
        print("Volume increased")

    def volume_down(self):
        """Decrease volume."""
        print("Volume decreased")


# Run the interface as a test
if __name__ == "__main__":
    import sys

    app = QGuiApplication(sys.argv)

    reciters = ["Abdul Basit", "Mishary Alafasy", "Saad Al Ghamdi"]
    surahs = ["Al-Fatiha", "Al-Baqarah", "Al-Imran", "An-Nisa"]

    player = SuraPlayerDialog("Quran Player", reciters, surahs)
    player.show()
    sys.exit(app.exec())

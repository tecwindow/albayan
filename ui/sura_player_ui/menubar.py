from typing import List
from PyQt6.QtWidgets import QMenuBar, QApplication
from PyQt6.QtGui import QAction, QKeyEvent, QKeySequence
from PyQt6.QtCore import Qt, QEvent


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFocus()
        
        # Create Player Menu
        main_menu = self.addMenu("القائمة الرئيسية(&M)")
        player_menu = self.addMenu("مشغل القرآن(&P)")
        
        # Create Actions for Player Menu
        self.play_pause_action = QAction("تشغيل", self)  # "Play"
        self.stop_action = QAction("إيقاف", self)  # "Stop"
        self.forward_action = QAction("تقديم", self)  # "Forward"
        self.rewind_action = QAction("إرجاع", self)  # "Rewind"
        self.up_volume_action = QAction("رفع الصوت", self)
        self.down_volume_action = QAction("خفض الصوت", self)
        
        # Add Actions to Menu
        player_menu.addAction(self.play_pause_action)
        player_menu.addAction(self.stop_action)
        player_menu.addAction(self.forward_action)
        player_menu.addAction(self.rewind_action)
        player_menu.addAction(self.up_volume_action)
        player_menu.addAction(self.down_volume_action)
        
        # Create Actions for Main Menu
        self.close_window_action = QAction("إغلاق النافذة", self) 
        self.close_window_action .triggered.connect(self.parent.OnClose)
        self.close_program_action = QAction("إغلاق البرنامج", self)
        self.close_program_action.triggered.connect(QApplication.exit)

        # Add Actions to Menu    
        main_menu.addAction(self.close_window_action)
        main_menu.addAction(self.close_program_action)
        self.installEventFilter(self)

    def get_player_actions(self) -> List[QAction]:
        return [self.play_pause_action, self.stop_action, self.forward_action, self.rewind_action, self.up_volume_action, self.down_volume_action]

    def eventFilter(self, obj, event: QEvent):
        if obj == self:
            if (event.type() == QKeyEvent.Type.KeyPress and event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Enter)) or (event.type() in (QEvent.Type.Close, QEvent.Type.Hide)):
                self.clearFocus()
                self.parent.setFocus()
            event.accept()
        return super().eventFilter(obj, event)
    
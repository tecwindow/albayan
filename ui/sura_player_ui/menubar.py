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
        loop_menu = self.addMenu("التكرار(&R)")
        
                # Create Actions for Main Menu
        self.close_window_action = QAction("إغلاق النافذة", self) 
        self.close_window_action .triggered.connect(self.parent.OnClose)
        self.close_program_action = QAction("إغلاق البرنامج", self)
        self.close_program_action.triggered.connect(QApplication.exit)

        # Add Actions to Menu    
        main_menu.addAction(self.close_window_action)
        main_menu.addAction(self.close_program_action)        
        
        # Create Actions for Player Menu
        self.play_pause_action = QAction("تشغيل", self)  # "Play"
        self.stop_action = QAction("إيقاف", self)  # "Stop"
        self.forward_action = QAction("تقديم", self)  # "Forward"
        self.rewind_action = QAction("ترجيع", self)  # "Rewind"
        self.replay_action = QAction("إعادة", self)  # "Replay"
        self.up_volume_action = QAction("رفع الصوت", self)
        self.down_volume_action = QAction("خفض الصوت", self)
        self.next_surah_action = QAction("السورة التالية", self)
        self.previous_surah_action = QAction("السورة السابقة", self)
        self.next_reciter_action = QAction("القارئ التالي", self)
        self.previous_reciter_action = QAction("القارئ السابق", self)
        
        # Add Actions to Menu
        player_menu.addAction(self.play_pause_action)
        player_menu.addAction(self.stop_action)
        player_menu.addAction(self.forward_action)
        player_menu.addAction(self.rewind_action)
        player_menu.addAction(self.replay_action)
        player_menu.addAction(self.up_volume_action)
        player_menu.addAction(self.down_volume_action)
        player_menu.addAction(self.next_surah_action)
        player_menu.addAction(self.previous_surah_action)
        player_menu.addAction(self.next_reciter_action)
        player_menu.addAction(self.previous_reciter_action)
        
        self.set_start_action = QAction("تحديد نقطة البداية", self)
        self.set_end_action = QAction("تحديد نقطة النهاية", self)
        self.toggle_loop_action = QAction("تشغيل/إيقاف التكرار", self)
        self.return_to_start_action = QAction("تشغيل بداية التحديد", self)
        self.clear_loop_action = QAction("تجاهل التحديد", self)


        loop_menu.addActions([
            self.set_start_action, self.set_end_action, self.return_to_start_action, self.clear_loop_action,
            self.toggle_loop_action
        ])        
        self.installEventFilter(self)

    def get_player_actions(self) -> List[QAction]:
        return [self.play_pause_action, self.stop_action, self.forward_action, self.rewind_action, self.replay_action, self.up_volume_action, self.down_volume_action, self.next_surah_action, self.previous_surah_action, self.next_reciter_action, self.previous_reciter_action, self.set_start_action, self.set_end_action, self.return_to_start_action, self.clear_loop_action, self.toggle_loop_action]

    def eventFilter(self, obj, event: QEvent):
        if obj == self:
            if (event.type() == QKeyEvent.Type.KeyPress and event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Enter)) or (event.type() in (QEvent.Type.Close, QEvent.Type.Hide)):
                self.clearFocus()
                self.parent.setFocus()
            event.accept()
        return super().eventFilter(obj, event)
    
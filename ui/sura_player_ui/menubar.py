from PyQt6.QtWidgets import QMenuBar, QApplication
from PyQt6.QtGui import QAction, QKeyEvent
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
        play_action = QAction("تشغيل", self)  # "Play"
        stop_action = QAction("إيقاف", self)  # "Stop"
        forward_action = QAction("تقديم", self)  # "Forward"
        rewind_action = QAction("إرجاع", self)  # "Rewind"
        
        # Add Actions to Menu
        player_menu.addAction(play_action)
        player_menu.addAction(stop_action)
        player_menu.addAction(forward_action)
        player_menu.addAction(rewind_action)

        # Create Actions for Main Menu
        close_window_action = QAction("إغلاق النافذة", self) 
        close_window_action .triggered.connect(self.parent.OnClose)
        close_program_action = QAction("إغلاق البرنامج", self)
        close_program_action.triggered.connect(QApplication.exit)

        # Add Actions to Menu    
        main_menu.addAction(close_window_action)
        main_menu.addAction(close_program_action)
        self.installEventFilter(self)

    def eventFilter(self, obj, event: QEvent):
        if obj == self:
            if (event.type() == QKeyEvent.Type.KeyPress and event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Enter)) or (event.type() in (QEvent.Type.Close, QEvent.Type.Hide)):
                self.clearFocus()
                self.parent.setFocus()
            event.accept()
        return super().eventFilter(obj, event)
    
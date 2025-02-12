from PyQt6.QtCore import QTimer
from utils.audio_player import SurahPlayer
from utils.universal_speech import UniversalSpeech

class AudioLooper:
    """
    Manages looping functionality in the Quran player.
    
    When loop is active, a timer periodically checks the player's current position.
    If the position exceeds the loop end point, the playback is restarted from the loop start point
    after a specified delay.
    """
    
    def __init__(self, parent, player: SurahPlayer, loop_check_interval: int = 100):
        """
        Initializes the AudioLooper.
        
        :param player: Reference to the main player for controlling playback.
        :param loop_check_interval: Interval (in milliseconds) to check the player's position.
        """

        self.parent = parent
        self.player = player
        self.loop_start = 0 # Start point (A)
        self.loop_end = 0 # End point (B)
        self.loop_active = False  # Loop state
        self.loop_delay = 100   # Delay (in milliseconds) before restarting the loop
        
        # Timer to monitor the player's current position.
        self.monitor_timer = QTimer()
        self.monitor_timer.setInterval(loop_check_interval)
        self.monitor_timer.timeout.connect(self.check_loop)
    
    def set_loop_start(self):
        """Set the start point (A) for the repeat loop."""
        self.loop_start = self.player.get_position()
        if self.loop_start > self.loop_end:
            self.loop_end = self.player.get_length()
        UniversalSpeech.say(f"تم تحديد البداية عند: {self.parent.format_time(self.loop_start)}.")
    
    def set_loop_end(self):
        """Set the end point (B) for the repeat loop."""
        self.loop_end = self.player.get_position()
        if self.loop_end < self.loop_start:
            self.loop_start = 0
        UniversalSpeech.say(f"تم تحديد النهاية عند: {self.parent.format_time(self.loop_end)}.")
    
    def toggle_loop(self):
        """
        Toggle loop playback between start (A) and end (B).
        If loop points are not set, informs the user.
        """
        if not self.loop_start  and  not self.loop_end:
            UniversalSpeech.say("لم يتم تحديد البداية والنهاية.")
            return

        self.loop_active = not self.loop_active
        if self.loop_active:
            UniversalSpeech.say(f"بدأ التكرار من {self.parent.format_time(self.loop_start)} إلى {self.parent.format_time(self.loop_end)}.")
            # Start playback from the loop start and start the monitor timer.
            self.player.set_position(self.loop_start)
            self.player.play()
            self.monitor_timer.start()
        else:
            UniversalSpeech.say("تم إيقاف التكرار.")
            self.monitor_timer.stop()

        return self.loop_active

    def check_loop(self):
        """
        Checks the player's current position.
        If the position exceeds loop_end, restarts the loop after the specified delay.
        """
        current_position = self.player.get_position()
        if current_position >= self.loop_end or current_position < self.loop_start:
            # Stop the monitor timer to avoid multiple triggers.
            self.monitor_timer.stop()
            QTimer.singleShot(self.loop_delay, self.restart_loop)
    
    def restart_loop(self):
        """
        Restarts the loop by setting the player's position to loop_start,
        resuming playback, and restarting the monitor timer.
        """
        if self.loop_active:
            self.player.set_position(self.loop_start)
            self.player.play()
            self.monitor_timer.start()

    def resume(self):
        """
        Resume the looping playback if it was paused.
        
        This method will start the player's playback and restart the monitor timer if it is not active,
        """
        if self.loop_active:
            self.player.play()
            if not self.monitor_timer.isActive():
                self.monitor_timer.start()    

    def return_to_start(self):
        """Return playback to the loop start point."""
        if self.loop_start == 0:
            UniversalSpeech.say("لم يتم تحديد البداية.")
            return

        self.player.set_position(self.loop_start)
        UniversalSpeech.say(f"يتم التشغيل من: {self.parent.format_time(self.loop_start)}.")

    def clear_loop(self):
        """Clear the loop points and stop the loop."""
        self.loop_start = 0
        self.loop_end = 0
        self.loop_active = False
        if  self.monitor_timer.isActive():
            self.monitor_timer.stop()
        #UniversalSpeech.say(F"تم مسح البداية والنهاية وإيقاف التكرار.")


    def set_loop_delay(self, delay: int):
        """
        Set the delay time (in milliseconds) before restarting the loop.
        
        :param delay: Delay in milliseconds.
        """
        self.loop_delay = delay
        UniversalSpeech.say(f"Loop delay set to {self.loop_delay} milliseconds.")

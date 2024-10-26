import os
import utils.const as const
from random import choice
from core_functions.athkar.athkar_db_manager import AthkarDBManager
from core_functions.athkar.models import AudioAthkar
from utils.sound_Manager import AudioPlayerBase
from utils.logger import Logger



class AthkarPlayer(AudioPlayerBase):
    def __init__(self, athkar_db: AthkarDBManager, folder: str, category_id: int) -> None:
        self.athkar_db = athkar_db
        self.category_id = category_id
        super().__init__(folder)

    def load_all_sounds(self) -> None:
        try:
            for file in self.athkar_db.get_audio_athkar(self.category_id):
                sound_path = os.path.join(self.folder, file.audio_file_name)
                if os.path.exists(sound_path):
                    self.load_sound(file.id, sound_path)
                else:
                    Logger.error(f"Sound file not found: {sound_path}")
        except Exception as e:
            Logger.error(f"Failed to load sounds for category {self.category_id}: {str(e)}")
            
    def play(self) -> None:

        if not self.sounds:
            Logger.error("No sounds are loaded to play.")
            return

        random_sound = choice(list(self.sounds.keys()))
        if const.tray_icon is not None:
            current_file = self.athkar_db._get_by_id(AudioAthkar, random_sound)
            const.tray_icon.showMessage("الأذكار", current_file.description,msecs=5000)

        return super().play(random_sound)

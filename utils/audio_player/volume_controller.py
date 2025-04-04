from utils.settings import Config
from utils.universal_speech import UniversalSpeech
from utils.audio_player import AyahPlayer, SoundEffectPlayer, AthkarPlayer, SurahPlayer
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class VolumeController:
    """Handles volume control for different categories with custom handling."""
    def __init__(self) -> None:
        self.categories = self._load_categories()
        self.current_category_index = Config.audio.current_volume_category
        logger.debug(f"Initialized VolumeController. Current category index: {self.current_category_index}")

    def _load_categories(self) -> dict:
        """Load categories with their custom handling methods."""
        return {
            "athkar_volume_level": {"label": "مستوى صوت الأذكار", "custom_volume_handler": None, "instances": AthkarPlayer.instances},
            "ayah_volume_level": {"label": "مستوى صوت استماع الآيات", "custom_volume_handler": None, "instances": AyahPlayer.instances},
            "surah_volume_level": {"label": "مستوى صوت استماع السور", "custom_volume_handler": None, "instances": SurahPlayer.instances},
            "volume_level": {"label": "مستوى  صوت البرنامج", "custom_volume_handler": None, "instances": SoundEffectPlayer.instances},
        }

    def _get_volume(self, category: str) -> int:
        """Retrieve the volume for the given category from the settings."""
        volume = Config.audio.get_value(category)
        logger.debug(f"Retrieved volume for {category}: {volume}%")
        return volume

    def switch_category(self, direction: str) -> None:
        """Switch between categories in the specified direction ('next' or 'previous')."""
        categories = list(self.categories.keys())
        prev_category = self.get_current_category()
        if direction == 'next':
            self.current_category_index = (self.current_category_index + 1) % len(categories)  
        elif direction == 'previous':
            self.current_category_index = (self.current_category_index - 1) % len(categories)  

        current_category = self.get_current_category()  # Get the current category key
        current_label = self.categories[current_category]["label"]  # Access label
        current_volume = self._get_volume(current_category)  # Get current volume

        Config.audio.set_value("current_volume_category", self.current_category_index)
        UniversalSpeech.say(f"{current_label}: {current_volume}%")
        logger.info(f"Switched category from {prev_category} to {current_category}. New volume: {current_volume}%")

    def adjust_volume(self, change: int) -> None:
        """Adjust the volume for the current category with special handling if needed."""
        current_category = self.get_current_category()
        current_volume = self._get_volume(current_category)
        new_volume = max(0, min(100, current_volume + change))
        current_label = self.categories[current_category]["label"]
        UniversalSpeech.say(f"{new_volume}%: {current_label}")
        Config.audio.set_value(current_category, new_volume)
        logger.info(f"Adjusted volume for {current_category} from {current_volume}% to {new_volume}%")

        # Apply the custom volume handler if it exists for the current category
        handling_method = self.categories[current_category].get("custom_volume_handler")
        if handling_method:
            try:
                handling_method(new_volume)
                logger.debug(f"Applied custom handler for {current_category}")
            except Exception as e:
                logger.warning(f"Error applying custom volume handler for {current_category}: {e}")


        instances = self.categories[current_category].get("instances")
        if instances:
            for instance in instances:
                try:
                    instance.set_volume(new_volume)
                    logger.debug(f"Set volume for instance {instance} in {current_category} to {new_volume}%")
                except Exception as e:
                    logger.warning(f"Failed to set volume for {instance} in {current_category}: {e}")

    def get_category_info(self):
        """Retrieve the information for the current category."""
        current_category = self.get_current_category()
        logger.debug(f"Retrieved info for category: {current_category}")
        return self.categories[current_category]

    def get_current_category(self) -> str:
        """Return the name of the current category based on the index."""
        categories = list(self.categories.keys())
        return categories[self.current_category_index]

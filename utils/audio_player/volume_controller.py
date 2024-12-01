from utils.settings import SettingsManager
from utils.universal_speech import UniversalSpeech
from utils.audio_player import AyahPlayer, SoundEffectPlayer, AthkarPlayer


class VolumeController:
    """Handles volume control for different categories with custom handling."""
    
    def __init__(self) -> None:
        self.categories = self._load_categories()
        self.current_category_index = 0 

    def _load_categories(self) -> dict:
        """Load categories with their custom handling methods."""
        return {
            "athkar_volume_level": {"label": "مستوى صوت الأذكار", "custom_volume_handler": None, "instances": AthkarPlayer.instances},
            "ayah_volume_level": {"label": "مستوى صوت استماع الآيات", "custom_volume_handler": None, "instances": AyahPlayer.instances},
            "volume_level": {"label": "مستوى  صوت البرنامج", "custom_volume_handler": None, "instances": SoundEffectPlayer.instances},
        }

    def _get_volume(self, category: str) -> int:
        """Retrieve the volume for the given category from the settings."""
        return SettingsManager.current_settings["audio"].get(category, 50) 

    def switch_category(self, direction: str) -> None:
        """Switch between categories in the specified direction ('next' or 'previous')."""
        categories = list(self.categories.keys())
        if direction == 'next':
            self.current_category_index = (self.current_category_index + 1) % len(categories)  # Move to the next category
        elif direction == 'previous':
            self.current_category_index = (self.current_category_index - 1) % len(categories)  # Move to the previous category

        current_category = self.get_category_info()
        UniversalSpeech.say(current_category["label"])

    def adjust_volume(self, change: int) -> None:
        """Adjust the volume for the current category with special handling if needed."""
        current_category = self.get_current_category()
        current_volume = self._get_volume(current_category)
        new_volume = max(0, min(100, current_volume + change))
        UniversalSpeech.say(f"{new_volume}%")
        SettingsManager.write_settings({"audio": {current_category: new_volume}})

        # Apply the custom volume handler if it exists for the current category
        handling_method = self.categories[current_category].get("custom_volume_handler")
        if handling_method:
            handling_method(new_volume)

        instances = self.categories[current_category].get("instances")
        if instances:
            for instance in instances:
                instance.set_volume(new_volume)

    def get_category_info(self):
        """Retrieve the information for the current category."""
        current_category = self.get_current_category()
        return self.categories[current_category]

    def get_current_category(self) -> str:
        """Return the name of the current category based on the index."""
        categories = list(self.categories.keys())
        return categories[self.current_category_index]

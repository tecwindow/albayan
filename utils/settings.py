import os
import configparser
from utils.const import albayan_folder


class SettingsManager:
    path = os.path.join(albayan_folder, "Settingss.ini")
    config = configparser.ConfigParser()

    default_settings = {
        "general": {
            "language": "Arabic",
            "sound_effect_enabled": True,
            "speak_actions_enabled": True,
            "auto_save_position_enabled": False,
            "check_update_enabled": True,
            "logging_enabled": False
        },
        "search": {
            "ignore_tashkeel": True,
            "ignore_hamza": True,
        },
        "preferences": {
            "theme": "default"
        }
        }

    @classmethod
    def write_settings(cls, new_settings:dict, is_reading:bool=False) -> None:
        try:
            cls.config.read_dict(new_settings)
            with open(cls.path, "w", encoding='utf-8') as config_file:
                cls.config.write(config_file)
            if not is_reading:
                cls._current_settings = cls.read_settings()
        except Exception as e:
            print(e)

    @classmethod
    def read_settings(cls) -> dict:
        try:
            cls.config.read(cls.path, encoding='utf-8')
        except configparser.Error as e:
            print(e)

        current_settings = {}
        for section in cls.default_settings:
            current_settings[section] = {}
            for setting, default_value in cls.default_settings[section].items():
                try:
                    if isinstance(default_value, bool):
                        current_settings[section][setting] = cls.config.getboolean(section, setting)
                    elif isinstance(default_value, int):
                        current_settings[section][setting] = cls.config.getint(section, setting)
                    else:
                        current_settings[section][setting] = cls.config.get(section, setting)
                except Exception as e:
                    print(e)
                    cls.write_settings({section: {setting: default_value}}, is_reading=True)
                    current_settings[section][setting] = default_value

        return current_settings

    @classmethod
    def reset_settings(cls) -> None:
        cls.write_settings(cls.default_settings)

    @classmethod
    @property
    def current_settings(cls) -> dict:
        if not hasattr(cls, "_current_settings"):
            cls._current_settings = cls.read_settings()
        return cls._current_settings
    

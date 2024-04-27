import os
import configparser
from utils.const import albayan_folder


class SettingsManager:
    path = os.path.join(albayan_folder, "Settingss.ini")
    config = configparser.ConfigParser()

    default_settings = {
        "general": {
            "check_update_enabled": True,
            "is_logging_enabled": False
        }}

    @classmethod
    def write_settings(cls, new_settings) -> None:
        try:
            cls.config.read_dict(new_settings)
            with open(cls.path, "w", encoding='utf-8') as config_file:
                cls.config.write(config_file)
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
                    cls.write_settings({section: {setting: default_value}})
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
    

import os
import configparser
import logging
from dataclasses import dataclass, asdict
from abc import ABC
from typing import Any, Dict, Tuple, ClassVar
from utils.const import CONFIG_PATH
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class BaseSection(ABC):
    def get_value(self, key: str) -> Any:
        if key in self.__dataclass_fields__:
            value = getattr(self, key)
            logger.debug(f"Retrieved '{key}' from section '{self.__class__.SECTION_NAME}': {value}")
            return value
        else:
            logger.warning(f"Attempted to access invalid key '{key}' in section '{self.__class__.SECTION_NAME}'")
            raise KeyError(f"Key '{key}' not found in section '{self.__class__.SECTION_NAME}'")

    def set_value(self, key: str, value: Any) -> None:
        if key in self.__dataclass_fields__:
            setattr(self, key, value)
            logger.debug(f"Updated '{key}' in section '{self.__class__.SECTION_NAME}' to: {value}")
            Config.save_settings()
        else:
            logger.warning(f"Attempted to set invalid key '{key}' in section '{self.__class__.SECTION_NAME}'")
            raise KeyError(f"Key '{key}' not found in section '{self.__class__.SECTION_NAME}'")

    def items(self) -> Tuple[str, Any]:
        return asdict(self).items()

@dataclass
class GeneralSettings(BaseSection):
    SECTION_NAME: ClassVar[str] = "general"
    language: str = "Arabic"
    run_in_background_enabled: bool = False
    auto_start_enabled: bool = False
    auto_save_position_enabled: bool = False
    check_update_enabled: bool = True
    log_level: str = "ERROR"

@dataclass
class AudioSettings(BaseSection):
    SECTION_NAME: ClassVar[str] = "audio"
    sound_effect_enabled: bool = True
    start_with_basmala_enabled: bool = True
    speak_actions_enabled: bool = True
    volume_level: int = 75
    volume_device: int = 1
    ayah_volume_level: int = 100
    ayah_device: int = 1
    surah_volume_level: int = 100
    surah_device: int = 1
    athkar_volume_level: int = 50
    athkar_device: int = 1
    current_volume_category: int = 0

@dataclass
class ListeningSettings(BaseSection):
    SECTION_NAME: ClassVar[str] = "listening"
    reciter: int = 58
    action_after_listening: int = 0
    forward_time: int = 5
    auto_move_focus: bool = True

@dataclass
class SearchSettings(BaseSection):
    SECTION_NAME: ClassVar[str] = "search"
    ignore_tashkeel: bool = True
    ignore_hamza: bool = True
    match_whole_word: bool = False

@dataclass
class ReadingSettings(BaseSection):
    SECTION_NAME: ClassVar[str] = "reading"
    font_type: int = 0
    auto_page_turn: bool = False
    marks_type: int = 0

@dataclass
class PreferencesSettings(BaseSection):
    SECTION_NAME: ClassVar[str] = "preferences"
    theme: str = "FlatDark"

class Config:
    """
    Singleton configuration manager using dataclasses.
    All methods are class methods so that settings can be accessed directly via:
      Config.general, Config.audio, etc.
    """
    _config_parser = configparser.ConfigParser()    
    # Define settings sections as class-level attributes.
    general: GeneralSettings = GeneralSettings()
    audio: AudioSettings = AudioSettings()
    listening: ListeningSettings = ListeningSettings()
    search: SearchSettings = SearchSettings()
    reading: ReadingSettings = ReadingSettings()
    preferences: PreferencesSettings = PreferencesSettings()

    @classmethod
    def ensure_section(cls, section: str) -> None:
        """
        Ensures that the given section exists in the config parser.
        If the section does not exist, it is created.
        """
        if section not in cls._config_parser:
            cls._config_parser[section] = {}
            logger.debug(f"Created missing section '{section}' in config file.")

    @classmethod
    def sections(cls) -> Dict[str, BaseSection]:
        """
        Returns a dictionary mapping section names to their corresponding dataclass instances
        by iterating over the class annotations.
        """
        sections_dict = {}
        for attr_name in cls.__annotations__:
            attr = getattr(cls, attr_name, None)
            if isinstance(attr, BaseSection):
                section_name = getattr(attr.__class__, "SECTION_NAME", None)
                if section_name:
                    sections_dict[section_name] = attr
        return sections_dict

    @classmethod
    def _get_value(cls, section: str, key: str, default_value: Any) -> Any:
        """
        Helper function to retrieve a value from the config file based on the type of the default value.
        This reduces repetition in the load section method.
        """
        try:
            if isinstance(default_value, bool):
                return cls._config_parser.getboolean(section, key, fallback=default_value)
            elif isinstance(default_value, int):
                return cls._config_parser.getint(section, key, fallback=default_value)
            elif isinstance(default_value, float):
                return cls._config_parser.getfloat(section, key, fallback=default_value)
            else:
                return cls._config_parser.get(section, key, fallback=default_value)
        except Exception as e:
            logger.warning(f"Error retrieving value for {section}:{key}; using default ({e})")
            return default_value

    @classmethod
    def _load_section(cls, section: str, section_obj: Any) -> None:
        """
        Loads a specific section from the config file into the corresponding dataclass.
        """
        cls.ensure_section(section)
        updated = False

        for field_name, default_value in section_obj.items():
            value = cls._get_value(section, field_name, default_value)
            setattr(section_obj, field_name, value)
            if cls._config_parser[section].get(field_name) is None:
                updated = True
                        
        if updated:
            cls._save_section(section, section_obj)
            cls._write_config()
                            
    @classmethod
    def _save_section(cls, section: str, section_obj: Any) -> None:
        """
        Saves the values of a dataclass section to the config file.
        """
        cls.ensure_section(section)
        for field_name, value in section_obj.items():
            if not cls._config_parser[section].get(field_name):
                logger.info(f"Creating new setting '{field_name}' in section '{section}'")
            cls._config_parser[section][field_name] = str(value)

    @classmethod
    def load_settings(cls) -> None:
        """
        Loads all settings from the configuration file by iterating over all sections.
        If the config file cannot be read or is missing, it will save the default settings.
        """
        try:
            if not cls._config_parser.read(CONFIG_PATH, encoding='utf-8'):
                logger.warning(f"Config file '{CONFIG_PATH}' not found or empty. Saving default settings.")
                cls.save_settings()
        except configparser.Error as e:
            logger.error(f"Failed to read config file: {e}. Reverting to default settings.", exc_info=True)
            cls.save_settings()            

        for section, instance in cls.sections().items():
            cls._load_section(section, instance)

    @classmethod
    def save_settings(cls) -> None:
        """
        Saves all settings to the configuration file by iterating over all sections.
        """
        for section, instance in cls.sections().items():
            cls._save_section(section, instance)
            logger.debug(f"Saving section '{section}' with values: {asdict(instance)}")
        cls._write_config()

    @classmethod
    def _write_config(cls) -> None:
        """Writes the current configuration to the config file."""
        logger.debug(f"Writing configuration to '{CONFIG_PATH}'")
        try:
            with open(CONFIG_PATH, "w", encoding='utf-8') as config_file:
                cls._config_parser.write(config_file)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Error writing config file: {e}", exc_info=True)

    @classmethod
    def reset_settings(cls) -> None:
        """
        Dynamically resets all settings to their default values by iterating over class
        annotations and reinitializing any attribute that is an instance of BaseSection.
        """
        for attr_name in cls.__annotations__:
            attr = getattr(cls, attr_name, None)
            if isinstance(attr, BaseSection):
                setattr(cls, attr_name, type(attr)())
        cls.save_settings()
        logger.info("All settings have been reset to default values.")
        
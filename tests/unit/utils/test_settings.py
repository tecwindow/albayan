import configparser
import pytest
from utils.settings import Config, GeneralSettings, AudioSettings, BaseSection


class TestBaseSection:
    def test_get_value_valid_and_invalid(self):
        general = GeneralSettings()
        assert general.get_value("language") == "Arabic"
        assert general.get_value("check_update_enabled") is True

        with pytest.raises(KeyError, match="Key 'nonexistent' not found"):
            general.get_value("nonexistent")

    def test_set_value_valid_and_invalid(self, temp_paths, monkeypatch):
        # Mock Config.save_settings to test section in isolation
        saved = False
        monkeypatch.setattr(Config, "save_settings", lambda: None)

        general = GeneralSettings()
        general.set_value("language", "English")
        assert general.language == "English"

        with pytest.raises(KeyError, match="Key 'bad_key' not found"):
            general.set_value("bad_key", "value")

    def test_items_dict(self):
        audio = AudioSettings()
        items = dict(audio.items())
        assert "volume_level" in items
        assert items["volume_level"] == 75
        assert items["sound_effect_enabled"] is True


class TestConfig:
    def test_sections_dict(self):
        sections = Config.sections()
        assert "general" in sections
        assert "audio" in sections
        assert "listening" in sections
        assert "search" in sections
        assert "reading" in sections
        assert "surah_player" in sections
        assert "downloading" in sections
        assert "preferences" in sections
        assert len(sections) == 8

    def test_ensure_section(self):
        Config.ensure_section("custom_test_section")
        assert "custom_test_section" in Config._config_parser

    def test_get_value_type_conversions(self):
        parser = configparser.ConfigParser()
        parser.add_section("test_types")
        parser.set("test_types", "b_true", "true")
        parser.set("test_types", "b_false", "no")
        parser.set("test_types", "num_int", "42")
        parser.set("test_types", "num_float", "3.14")
        parser.set("test_types", "str_val", "hello")

        Config._config_parser = parser

        assert Config._get_value("test_types", "b_true", False) is True
        assert Config._get_value("test_types", "b_false", True) is False
        assert Config._get_value("test_types", "num_int", 0) == 42
        assert Config._get_value("test_types", "num_float", 0.0) == 3.14
        assert Config._get_value("test_types", "str_val", "") == "hello"

        # Fallback on missing key
        assert Config._get_value("test_types", "missing", "default_val") == "default_val"

    def test_save_and_load_settings_roundtrip(self, temp_paths):
        # Set custom settings
        Config.general.language = "Français"
        Config.audio.volume_level = 88
        Config.reading.font_type = 1
        Config.save_settings()

        # Verify config file was written to disk
        config_file = temp_paths["config_file"]
        assert config_file.exists()

        # Reset to defaults in memory, then load from disk
        Config.general.language = "Arabic"
        Config.audio.volume_level = 75
        Config.load_settings()

        assert Config.general.language == "Français"
        assert Config.audio.volume_level == 88
        assert Config.reading.font_type == 1

    def test_reset_settings(self, temp_paths):
        Config.general.language = "CustomLanguage"
        Config.audio.volume_level = 10
        Config.save_settings()

        Config.reset_settings()

        # Defaults restored
        assert Config.general.language == "Arabic"
        assert Config.audio.volume_level == 75

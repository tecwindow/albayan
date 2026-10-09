from datetime import time
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from core_functions.athkar.athkar_scheduler import AthkarScheduler


@pytest.fixture
def mock_tray(monkeypatch):
    from utils.const import Globals
    tray = MagicMock()
    monkeypatch.setattr(Globals, "TRAY_ICON", tray)
    monkeypatch.setattr("core_functions.athkar.athkar_scheduler.QIcon", MagicMock())
    return tray


class TestAthkarScheduler:
    def test_parse_time(self):
        t1 = AthkarScheduler._parse_time("08:30")
        assert t1 == time(8, 30)

        t2 = AthkarScheduler._parse_time("00:00")
        assert t2 == time(0, 0)

        t3 = AthkarScheduler._parse_time("23:59")
        assert t3 == time(23, 59)

    def test_create_triggers_normal_day_range(self):
        scheduler = AthkarScheduler.__new__(AthkarScheduler)
        from_t = time(9, 0)
        to_t = time(17, 0)

        triggers = scheduler._create_triggers(from_t, to_t, play_interval=30)
        assert len(triggers) == 1
        trigger = triggers[0]
        # APScheduler CronTrigger fields
        fields_str = str(trigger)
        assert "hour='9-17'" in fields_str
        assert "minute='*/30'" in fields_str

    def test_create_triggers_midnight_wrap_around(self):
        scheduler = AthkarScheduler.__new__(AthkarScheduler)
        from_t = time(22, 0)
        to_t = time(4, 0)

        triggers = scheduler._create_triggers(from_t, to_t, play_interval=60)
        # Should create 2 triggers for the wrap-around
        assert len(triggers) == 2
        t1_str = str(triggers[0])
        t2_str = str(triggers[1])
        assert "hour='22-23'" in t1_str
        assert "hour='0-4'" in t2_str
        assert "minute='0'" in t1_str
        assert "minute='0'" in t2_str

    def test_add_jobs(self):
        scheduler = AthkarScheduler.__new__(AthkarScheduler)
        scheduler.scheduler = MagicMock()
        scheduler.audio_athkar_job = MagicMock()
        scheduler.text_athkar_job = MagicMock()

        category = MagicMock()
        category.id = 1
        category.audio_path = "/audio"
        category.audio_athkar_enabled = 1
        category.text_athkar_enabled = 1

        mock_trigger = MagicMock()
        scheduler._add_jobs(category, mock_trigger)

        assert scheduler.scheduler.add_job.call_count == 2

    def test_text_athkar_job_short_text(self, mock_tray):
        scheduler = AthkarScheduler.__new__(AthkarScheduler)
        scheduler.db_manager = MagicMock()
        mock_item = MagicMock(text="سبحان الله وبحمده")
        scheduler.db_manager.get_text_athkar.return_value = [mock_item]

        scheduler.text_athkar_job(category_id=1)

        mock_tray.showMessage.assert_called_once()
        title, desc, icon, duration = mock_tray.showMessage.call_args[0]
        assert title == "البيان"
        assert desc == "سبحان الله وبحمده"
        assert duration == 5000

    def test_text_athkar_job_long_text(self, mock_tray):
        scheduler = AthkarScheduler.__new__(AthkarScheduler)
        scheduler.db_manager = MagicMock()
        # Text exceeding 256 characters
        long_words = [f"كلمة{i}" for i in range(50)]
        long_text = " ".join(long_words)
        assert len(long_text) > 256

        mock_item = MagicMock(text=long_text)
        scheduler.db_manager.get_text_athkar.return_value = [mock_item]

        scheduler.text_athkar_job(category_id=1)

        mock_tray.showMessage.assert_called_once()
        title, desc, icon, duration = mock_tray.showMessage.call_args[0]
        # Title takes first 10 words, description takes remainder
        expected_title = " ".join(long_words[:10])
        expected_desc = " ".join(long_words[10:])
        assert title == expected_title
        assert desc == expected_desc

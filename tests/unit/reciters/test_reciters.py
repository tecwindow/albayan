import os
import sqlite3
import pytest
from unittest.mock import MagicMock

from core_functions.Reciters import SurahReciter, AyahReciter
from exceptions.database import DBNotFoundError
from core_functions.downloader.status import DownloadStatus


@pytest.fixture
def test_reciters_db(tmp_path):
    db_file = tmp_path / "reciters.db"
    conn = sqlite3.connect(str(db_file))
    conn.execute("""
        CREATE TABLE moshaf (
            id INTEGER PRIMARY KEY,
            name TEXT,
            rewaya TEXT,
            type TEXT,
            bitrate INTEGER,
            url TEXT,
            available_suras TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE reciters (
            id INTEGER PRIMARY KEY,
            name TEXT,
            rewaya TEXT,
            type TEXT,
            bitrate INTEGER,
            url TEXT
        )
    """)
    # Seed sample moshaf
    conn.execute("""
        INSERT INTO moshaf VALUES 
        (1, 'مشاري العفاسي', 'حفص عن عاصم', 'مرتل', 128, 'https://server.com/afasy/', '114,1,2'),
        (2, 'عبد الباسط', 'مجود', 'مجود', 48, 'https://server.com/basit/', '1,2'),
        (3, 'محمود خليل الحصري', 'حفص', 'معلم', 192, 'https://server.com/hosary/', '1')
    """)
    # Seed sample ayah reciters
    conn.execute("""
        INSERT INTO reciters VALUES 
        (1, 'العفاسي آيات', 'حفص', 'مرتل', 128, 'https://everyayah.com/data/Alafasy_128kbps/')
    """)
    conn.commit()
    conn.close()
    return str(db_file)


class TestReciters:
    def test_missing_db_raises_db_not_found(self, temp_paths):
        with pytest.raises(DBNotFoundError):
            reciter = SurahReciter("/nonexistent/path/reciters.db")
            reciter.get_reciters()

    def test_surah_reciter_quality_and_available_suras(self, temp_paths, test_reciters_db):
        sr = SurahReciter(test_reciters_db)
        reciters = sr.get_reciters()
        assert len(reciters) == 3

        # Reciter 1: bitrate 128 -> Medium
        r1 = next(r for r in reciters if r["id"] == 1)
        assert r1["quality"] == "Medium"
        assert r1["available_suras"] == [1, 2, 114]  # parsed and sorted
        assert "مشاري العفاسي" in r1["display_text"]

        # Reciter 2: bitrate 48 -> Low
        r2 = next(r for r in reciters if r["id"] == 2)
        assert r2["quality"] == "Low"

        # Reciter 3: bitrate 192 -> High
        r3 = next(r for r in reciters if r["id"] == 3)
        assert r3["quality"] == "High"

    def test_surah_reciter_get_reciter_by_id(self, temp_paths, test_reciters_db):
        sr = SurahReciter(test_reciters_db)
        r = sr.get_reciter(1)
        assert r["id"] == 1
        assert r["available_suras"] == [1, 2, 114]

        # Non-existent ID returns empty dict
        r_none = sr.get_reciter(999)
        assert r_none == {}

    def test_surah_reciter_get_url(self, temp_paths, test_reciters_db):
        sr = SurahReciter(test_reciters_db)
        url = sr.get_url(reciter_id=1, surah_number=1)
        assert url == "https://server.com/afasy/001.mp3"

        url_surah114 = sr.get_url(reciter_id=1, surah_number=114)
        assert url_surah114 == "https://server.com/afasy/114.mp3"

    def test_surah_reciter_offline_playback(self, temp_paths, test_reciters_db, tmp_path):
        sr = SurahReciter(test_reciters_db)

        # Mock check_local_file returning an existing local file
        local_audio = tmp_path / "001.mp3"
        local_audio.touch()

        sr.download_db = MagicMock()
        mock_record = MagicMock(folder_path=str(tmp_path), filename="001.mp3")
        sr.download_db.find_one.return_value = mock_record

        # Offline playback returns local file
        url = sr.get_url(reciter_id=1, surah_number=1, offline_playback=True)
        assert url == str(local_audio)

    def test_ayah_reciter_get_url(self, temp_paths, test_reciters_db):
        ar = AyahReciter(test_reciters_db)
        url = ar.get_url(reciter_id=1, surah_number=1, ayah_number=1)
        assert url == "https://everyayah.com/data/Alafasy_128kbps/001001.mp3"

        url_ayah7 = ar.get_url(reciter_id=1, surah_number=1, ayah_number=7)
        assert url_ayah7 == "https://everyayah.com/data/Alafasy_128kbps/001007.mp3"

    def test_ayah_reciter_offline_playback(self, temp_paths, test_reciters_db, tmp_path):
        ar = AyahReciter(test_reciters_db)

        local_audio = tmp_path / "001001.mp3"
        local_audio.touch()

        ar.download_db = MagicMock()
        mock_record = MagicMock(folder_path=str(tmp_path), filename="001001.mp3")
        ar.download_db.find_one.return_value = mock_record

        url = ar.get_url(reciter_id=1, surah_number=1, ayah_number=1, offline_playback=True)
        assert url == str(local_audio)

        # Fallback to web URL when local file not found
        ar.download_db.find_one.return_value = None
        fallback_url = ar.get_url(reciter_id=1, surah_number=1, ayah_number=1, offline_playback=True)
        assert fallback_url == "https://everyayah.com/data/Alafasy_128kbps/001001.mp3"

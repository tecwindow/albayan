import os
import sqlite3
import pytest
from unittest.mock import MagicMock

from core_functions.search import SearchCriteria, QuranSearchManager
from exceptions.database import (
    DBNotFoundError,
    DatabaseConnectionError,
    InvalidCriteriaError,
    InvalidSearchTextError,
)


class TestSearchCriteria:
    def test_valid_criteria(self):
        assert SearchCriteria.is_valid("page") is True
        assert SearchCriteria.is_valid("sura_number") is True
        assert SearchCriteria.is_valid("hizb") is True
        assert SearchCriteria.is_valid("juz") is True
        assert SearchCriteria.is_valid("hizbQuarter") is True
        assert SearchCriteria.is_valid("invalid_criteria") is False

    def test_arabic_criteria_mapping(self):
        assert SearchCriteria.get_criteria_by_arabic_name("صفحة") == "page"
        assert SearchCriteria.get_criteria_by_arabic_name("سورة") == "sura_number"
        assert SearchCriteria.get_criteria_by_arabic_name("الحزب") == "hizb"
        assert SearchCriteria.get_criteria_by_arabic_name("الجزء") == "juz"
        assert SearchCriteria.get_criteria_by_arabic_name("الربع") == "hizbQuarter"
        assert SearchCriteria.get_criteria_by_arabic_name("غير معروف") is None

    def test_get_arabic_criteria_list(self):
        arabic_list = SearchCriteria.get_arabic_criteria()
        assert "صفحة" in arabic_list
        assert "سورة" in arabic_list


@pytest.fixture
def test_search_db(tmp_path):
    db_file = tmp_path / "Verses.DB"
    conn = sqlite3.connect(str(db_file))
    conn.execute("""
        CREATE TABLE quran (
            number INTEGER PRIMARY KEY,
            text TEXT,
            sura_name TEXT,
            sura_number INTEGER,
            numberInSurah INTEGER,
            juz INTEGER,
            hizb INTEGER,
            page INTEGER,
            hizbQuarter INTEGER
        )
    """)
    conn.executemany(
        "INSERT INTO quran VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", "الفاتحة", 1, 1, 1, 1, 1, 1),
            (2, "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", "الفاتحة", 1, 2, 1, 1, 1, 1),
            (3, "الرَّحْمَٰنِ الرَّحِيمِ", "الفاتحة", 1, 3, 1, 1, 1, 1),
            (4, "مَالِكِ يَوْمِ الدِّينِ", "الفاتحة", 1, 4, 1, 1, 1, 1),
            (5, "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ", "الفاتحة", 1, 5, 1, 1, 1, 1),
            (8, "الم", "البقرة", 2, 1, 1, 1, 2, 1),
        ],
    )
    conn.commit()
    conn.close()
    return str(db_file)


@pytest.fixture
def search_manager(test_search_db, monkeypatch):
    monkeypatch.setattr(os.path, "isfile", lambda path: True)
    original_connect = sqlite3.connect

    def mock_connect(*args, **kwargs):
        return original_connect(test_search_db)

    monkeypatch.setattr(sqlite3, "connect", mock_connect)
    sm = QuranSearchManager()
    return sm


class TestQuranSearchManager:
    def test_missing_db_raises_db_not_found(self, monkeypatch):
        monkeypatch.setattr(os.path, "isfile", lambda path: False)
        with pytest.raises(DBNotFoundError):
            QuranSearchManager()

    def test_invalid_criteria_raises_error(self, search_manager):
        with pytest.raises(InvalidCriteriaError):
            search_manager.set(criteria="nonexistent_criteria")

    def test_set_and_surah_name_resolution(self, search_manager):
        search_manager.set(
            criteria=SearchCriteria.sura,
            _from="الفاتحة",
            _to="البقرة",
        )
        assert search_manager._from == 1
        assert search_manager._to == 2

    def test_set_boundary_clamping(self, search_manager):
        # _from < 1 clamped to 1
        # _to < _from clamped to _from
        search_manager.set(criteria=SearchCriteria.page, _from=-5, _to=-1)
        assert search_manager._from == 1
        assert search_manager._to == 1

    def test_invalid_search_text_type_raises(self, search_manager):
        search_manager.set(criteria=SearchCriteria.page, _from=1, _to=604)
        with pytest.raises(InvalidSearchTextError):
            search_manager.search(12345)

    def test_empty_search_text_returns_none(self, search_manager):
        search_manager.set(criteria=SearchCriteria.page, _from=1, _to=604)
        assert search_manager.search("") is None

    def test_search_partial_match(self, search_manager):
        search_manager.set(criteria=SearchCriteria.page, _from=1, _to=1)
        results = search_manager.search("الرَّحْمَٰنِ")
        assert len(results) == 2  # Ayah 1 and Ayah 3

    def test_search_no_tashkil(self, search_manager):
        search_manager.set(
            no_tashkil=True,
            criteria=SearchCriteria.page,
            _from=1,
            _to=1,
        )
        # Search without tashkil for "الحمد"
        results = search_manager.search("الحمد")
        assert len(results) == 1
        assert results[0]["number"] == 2

    def test_search_no_hamza(self, search_manager):
        search_manager.set(
            no_hamza=True,
            no_tashkil=True,
            criteria=SearchCriteria.page,
            _from=1,
            _to=1,
        )
        # Search with regular alef for "اياك" (original has "إِيَّاكَ")
        results = search_manager.search("اياك")
        assert len(results) == 1
        assert results[0]["number"] == 5

    def test_search_match_whole_word(self, search_manager):
        search_manager.set(
            match_whole_word=True,
            criteria=SearchCriteria.page,
            _from=1,
            _to=2,
        )
        results = search_manager.search("الم")
        assert len(results) == 1
        assert results[0]["number"] == 8

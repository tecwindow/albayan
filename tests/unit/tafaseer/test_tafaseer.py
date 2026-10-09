import os
import sqlite3
import pytest
from core_functions.tafaseer import Category, TafaseerManager
from exceptions.database import DBNotFoundError


class TestCategory:
    def test_category_validation(self):
        assert Category.is_valid("katheer") is True
        assert Category.is_valid("muyassar") is True
        assert Category.is_valid("sa3dy") is True
        assert Category.is_valid("invalid_category") is False

    def test_arabic_mapping(self):
        assert Category.get_category_by_arabic_name("ابن كثير") == "katheer"
        assert Category.get_category_by_arabic_name("الميسر") == "muyassar"
        assert Category.get_category_by_arabic_name("غير موجود") is None

    def test_get_categories_in_arabic(self):
        categories = Category.get_categories_in_arabic()
        assert len(categories) == 7
        assert "ابن كثير" in categories
        assert "السعدي" in categories


@pytest.fixture
def test_tafsir_db(tmp_path):
    db_file = tmp_path / "katheer.db"
    conn = sqlite3.connect(str(db_file))
    conn.execute("CREATE TABLE tafsir_1 (number INTEGER PRIMARY KEY, text TEXT)")
    conn.execute(
        "INSERT INTO tafsir_1 VALUES (1, 'أبدأ باسم الله. وهو الرحمن الرحيم. المستحق للحمد.')"
    )
    conn.commit()
    conn.close()
    return str(db_file)


class TestTafaseerManager:
    def test_invalid_category_raises_assertion(self):
        mgr = TafaseerManager()
        with pytest.raises(AssertionError):
            mgr.set("unknown_tafseer")

    def test_missing_db_raises_db_not_found(self, monkeypatch):
        monkeypatch.setattr(os.path, "isfile", lambda path: False)
        mgr = TafaseerManager()
        with pytest.raises(DBNotFoundError):
            mgr.set(Category.katheer)

    def test_get_tafaseer_bounds_assertions(self, test_tafsir_db, monkeypatch):
        monkeypatch.setattr(os.path, "isfile", lambda path: True)
        orig_connect = sqlite3.connect
        monkeypatch.setattr(sqlite3, "connect", lambda path: orig_connect(test_tafsir_db))

        mgr = TafaseerManager()
        mgr.set(Category.katheer)

        with pytest.raises(AssertionError, match="Out of surah range"):
            mgr.get_tafaseer(0, 1)

        with pytest.raises(AssertionError, match="Out of surah range"):
            mgr.get_tafaseer(115, 1)

        with pytest.raises(AssertionError, match="Out of ayah range"):
            mgr.get_tafaseer(1, 0)

    def test_get_tafaseer_and_text_formatting(self, test_tafsir_db, monkeypatch):
        monkeypatch.setattr(os.path, "isfile", lambda path: True)
        original_connect = sqlite3.connect

        def mock_connect(*args, **kwargs):
            return original_connect(test_tafsir_db)

        monkeypatch.setattr(sqlite3, "connect", mock_connect)

        mgr = TafaseerManager()
        mgr.set(Category.katheer)

        text = mgr.get_tafaseer(1, 1)
        assert "أبدأ باسم الله." in text
        assert "وهو الرحمن الرحيم." in text
        # Verify sentences separated by newline
        assert "\n" in text

    def test_get_text_empty_or_none(self):
        mgr = TafaseerManager()
        assert mgr.get_text(None) == ""
        assert mgr.get_text({"text": ""}) == ""

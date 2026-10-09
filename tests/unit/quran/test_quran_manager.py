import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import sessionmaker

from core_functions.quran.quran_manager import QuranManager
from core_functions.quran.types import QuranFontType, NavigationMode


@pytest.fixture
def quran_manager(in_memory_quran_engine, monkeypatch):
    def fake_create_engine(self):
        self.engine = in_memory_quran_engine
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    monkeypatch.setattr(QuranManager, "_create_engine_and_session", fake_create_engine)
    qm = QuranManager(QuranFontType.DEFAULT, NavigationMode.PAGE)
    return qm


class TestQuranManager:
    def test_navigation_max_limits(self):
        assert QuranManager.get_max_for_navigation(NavigationMode.PAGE) == 604
        assert QuranManager.get_max_for_navigation(NavigationMode.SURAH) == 114
        assert QuranManager.get_max_for_navigation(NavigationMode.JUZ) == 30
        assert QuranManager.get_max_for_navigation(NavigationMode.HIZB) == 60
        assert QuranManager.get_max_for_navigation(NavigationMode.QUARTER) == 240

    def test_navigation_mode_setter_updates_max_position(self, quran_manager):
        quran_manager.navigation_mode = NavigationMode.SURAH
        assert quran_manager.navigation_mode == NavigationMode.SURAH
        assert quran_manager.max_position == 114

        quran_manager.navigation_mode = NavigationMode.PAGE
        assert quran_manager.max_position == 604

    def test_get_surahs(self, quran_manager):
        surahs = quran_manager.get_surahs()
        assert len(surahs) >= 2
        fatiha = surahs[0]
        assert fatiha.number == 1
        assert "الفاتحة" in fatiha.name
        assert fatiha.ayah_count == 7
        assert fatiha.first_ayah_number == 1
        assert fatiha.last_ayah_number == 7

    def test_get_page(self, quran_manager):
        content = quran_manager.get_page(1)
        assert quran_manager.current_position == 1
        assert "الفاتحة" in content
        assert "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ" in content

    def test_get_surah(self, quran_manager):
        content = quran_manager.get_surah(1)
        assert quran_manager.navigation_mode == NavigationMode.SURAH
        assert quran_manager.current_position == 1
        assert "الفاتحة" in content

    def test_get_juz_and_hizb_and_quarter(self, quran_manager):
        juz_content = quran_manager.get_juz(1)
        assert quran_manager.navigation_mode == NavigationMode.JUZ
        assert "الفاتحة" in juz_content

        hizb_content = quran_manager.get_hizb(1)
        assert quran_manager.navigation_mode == NavigationMode.HIZB
        assert "الفاتحة" in hizb_content

        quarter_content = quran_manager.get_quarter(1)
        assert quran_manager.navigation_mode == NavigationMode.QUARTER
        assert "الفاتحة" in quarter_content

    def test_navigation_next_back_clamping(self, quran_manager):
        quran_manager.navigation_mode = NavigationMode.PAGE
        quran_manager.current_position = 1

        # back() should clamp to 1
        quran_manager.back()
        assert quran_manager.current_position == 1

        # next() advances
        quran_manager.next()
        assert quran_manager.current_position == 2

        # go_to clamping
        quran_manager.go_to(0)
        assert quran_manager.current_position == 1

        quran_manager.go_to(9999)
        assert quran_manager.current_position == quran_manager.max_position

    def test_get_range(self, quran_manager):
        # Range across Al-Fatiha
        content = quran_manager.get_range(from_surah=1, from_ayah=1, to_surah=1, to_ayah=3)
        assert "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ" in content
        assert "ٱلرَّحْمَٰنِ ٱلرَّحِيمِ" in content

    def test_get_by_ayah_number(self, quran_manager):
        quran_manager.navigation_mode = NavigationMode.PAGE
        content = quran_manager.get_by_ayah_number(1)
        assert "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ" in content
        assert quran_manager.current_position == 1

        # Nonexistent ayah number returns empty string
        invalid_content = quran_manager.get_by_ayah_number(99999)
        assert invalid_content == ""

    def test_font_type_change_triggers_recreate(self, in_memory_quran_engine, monkeypatch):
        recreated = False

        def fake_create(self):
            nonlocal recreated
            recreated = True
            self.engine = in_memory_quran_engine
            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()

        monkeypatch.setattr(QuranManager, "_create_engine_and_session", fake_create)
        qm = QuranManager(QuranFontType.DEFAULT, NavigationMode.PAGE)
        recreated = False

        qm.font_type = QuranFontType.UTHMANI
        assert recreated is True
        assert qm.font_type == QuranFontType.UTHMANI

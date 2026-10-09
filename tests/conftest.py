import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from PyQt6.QtCore import QCoreApplication

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core_functions.quran.models import QuranBase, AyahMapBase, Quran, AyahViewMap
from core_functions.tasbih.model import Base as TasbihBase, TasbihEntry
from core_functions.athkar.models import Base as AthkarBase, AthkarCategory, TextAthkar, AudioAthkar
from core_functions.downloader.models import Base as DownloaderBase, DownloadSurahs, DownloadAyahs
from utils.paths import paths


@pytest.fixture(scope="session")
def qapp():
    """Shared QCoreApplication for tests that interact with QObject signals/threads."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


@pytest.fixture
def mock_globals(monkeypatch):
    """Mocks Globals.effects_manager and Globals.TRAY_ICON to avoid external side-effects."""
    from utils.globals import Globals
    mock_effects = MagicMock()
    mock_tray = MagicMock()
    monkeypatch.setattr(Globals, "effects_manager", mock_effects)
    monkeypatch.setattr(Globals, "TRAY_ICON", mock_tray)
    return {"effects_manager": mock_effects, "tray_icon": mock_tray}


@pytest.fixture
def temp_paths(tmp_path, monkeypatch):
    """Monkeypatches paths attributes to point to an isolated tmp_path directory."""
    app_dir = tmp_path / "app_folder"
    app_dir.mkdir(parents=True, exist_ok=True)
    audio_dir = app_dir / "audio" / "athkar"
    audio_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir = tmp_path / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(paths, "_app_folder", app_dir)
    monkeypatch.setattr(paths, "_user_db", app_dir / "user_data.db")
    monkeypatch.setattr(paths, "_config_file", app_dir / "config.ini")
    monkeypatch.setattr(paths, "_download_db_path", app_dir / "download_data.db")
    monkeypatch.setattr(paths, "_athkar_db", app_dir / "athkar.db")
    monkeypatch.setattr(paths, "_athkar_audio", audio_dir)
    monkeypatch.setattr(paths, "download_folder", downloads_dir)

    return {
        "app_folder": app_dir,
        "config_file": app_dir / "config.ini",
        "user_db": app_dir / "user_data.db",
        "athkar_db": app_dir / "athkar.db",
        "download_db": app_dir / "download_data.db",
        "downloads_dir": downloads_dir,
    }


@pytest.fixture
def in_memory_quran_engine():
    """Creates an in-memory SQLite database populated with sample Quran ayahs for testing."""
    engine = create_engine("sqlite:///:memory:")
    QuranBase.metadata.create_all(engine)
    AyahMapBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    sample_ayahs = [
        Quran(
            number=1,
            text="بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
            sura_name="الفاتحة",
            sura_number=1,
            numberInSurah=1,
            juz=1,
            hizb=1,
            page=1,
            hizbQuarter=1,
            sajda=0,
            sajdaObligation=0,
        ),
        Quran(
            number=2,
            text="ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ",
            sura_name="الفاتحة",
            sura_number=1,
            numberInSurah=2,
            juz=1,
            hizb=1,
            page=1,
            hizbQuarter=1,
            sajda=0,
            sajdaObligation=0,
        ),
        Quran(
            number=3,
            text="ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
            sura_name="الفاتحة",
            sura_number=1,
            numberInSurah=3,
            juz=1,
            hizb=1,
            page=1,
            hizbQuarter=1,
            sajda=0,
            sajdaObligation=0,
        ),
        Quran(
            number=4,
            text="مَٰلِكِ يَوْمِ ٱلدِّينِ",
            sura_name="الفاتحة",
            sura_number=1,
            numberInSurah=4,
            juz=1,
            hizb=1,
            page=1,
            hizbQuarter=1,
            sajda=0,
            sajdaObligation=0,
        ),
        Quran(
            number=5,
            text="إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
            sura_name="الفاتحة",
            sura_number=1,
            numberInSurah=5,
            juz=1,
            hizb=1,
            page=1,
            hizbQuarter=1,
            sajda=0,
            sajdaObligation=0,
        ),
        Quran(
            number=6,
            text="ٱهْدِنَا ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ",
            sura_name="الفاتحة",
            sura_number=1,
            numberInSurah=6,
            juz=1,
            hizb=1,
            page=1,
            hizbQuarter=1,
            sajda=0,
            sajdaObligation=0,
        ),
        Quran(
            number=7,
            text="صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ",
            sura_name="الفاتحة",
            sura_number=1,
            numberInSurah=7,
            juz=1,
            hizb=1,
            page=1,
            hizbQuarter=1,
            sajda=0,
            sajdaObligation=0,
        ),
        # Ayah from Surah 2 for multi-surah tests
        Quran(
            number=8,
            text="الم",
            sura_name="البقرة",
            sura_number=2,
            numberInSurah=1,
            juz=1,
            hizb=1,
            page=2,
            hizbQuarter=1,
            sajda=0,
            sajdaObligation=0,
        ),
        # Ayah with sajda
        Quran(
            number=1160,
            text="إِنَّ ٱلَّذِينَ عِندَ رَبِّكَ لَا يَسْتَكْبِرُونَ عَنْ عِبَادَتِهِۦ وَيُسَبِّحُونَهُۥ وَلَهُۥ يَسْجُدُونَ",
            sura_name="الأعراف",
            sura_number=7,
            numberInSurah=206,
            juz=9,
            hizb=18,
            page=176,
            hizbQuarter=72,
            sajda=1,
            sajdaObligation=1,
        ),
    ]

    with Session() as session:
        session.add_all(sample_ayahs)
        session.commit()

    return engine


@pytest.fixture
def in_memory_tasbih_engine():
    """Creates an in-memory SQLite engine for TasbihEntry."""
    engine = create_engine("sqlite:///:memory:")
    TasbihBase.metadata.create_all(engine)
    return engine


@pytest.fixture
def in_memory_athkar_engine():
    """Creates an in-memory SQLite engine for AthkarCategory, TextAthkar, AudioAthkar."""
    engine = create_engine("sqlite:///:memory:")
    AthkarBase.metadata.create_all(engine)
    return engine


@pytest.fixture
def in_memory_download_engine():
    """Creates an in-memory SQLite engine for DownloadSurahs and DownloadAyahs."""
    engine = create_engine("sqlite:///:memory:")
    DownloaderBase.metadata.create_all(engine)
    return engine

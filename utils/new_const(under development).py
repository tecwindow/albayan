from pathlib import Path
import os

class Paths:
    """Class for managing application paths."""
    TECWINDOW_FOLDER = Path(os.getenv("AppData")) / "tecwindow"
    ALBAYAN_FOLDER = TECWINDOW_FOLDER / "albayan"
    USER_DB_PATH = ALBAYAN_FOLDER / "user_data.db"
    ATHKAR_DB_PATH = ALBAYAN_FOLDER / "athkar.db"
    DEFAULT_ATHKAR_PATH = ALBAYAN_FOLDER / "audio" / "athkar"
    TEST_ATHKAR_PATH = Path("audio/athkar")
    DATA_FOLDER = Path("database")

    TEMP_FOLDER = Path(os.getenv("TEMP")) / "albayan"
    DOCUMENTS_DIR = Path(os.path.expanduser("~")) / "Documents" / "Albayan"

    @staticmethod
    def initialize_directories():
        """Ensure necessary directories exist."""
        Paths.ALBAYAN_FOLDER.mkdir(parents=True, exist_ok=True)
        Paths.TEMP_FOLDER.mkdir(parents=True, exist_ok=True)
        Paths.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

class ProgramInfo:
    """Class for managing program metadata."""
    NAME = "البيان"
    ENGLISH_NAME = "Albayan"
    VERSION = "1.3.0"
    ICON = "icon.webp"
    WEBSITE = "https://tecwindow.net/"

class Globals:
    """Class for managing global shared objects."""
    TRAY_ICON = None
    effects_manager = None

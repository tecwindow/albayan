import os
import sys
from pathlib import Path

# Import the registry class from registry library
from .registry import registry, RegistryError
from .const import program_english_name, author
from utils.logger import LoggerManager

# The AppId defined in InnoSetup script
APP_ID = "{5BDDE425-E22F-4A82-AF2F-72AF71301D3F}"

logger = LoggerManager.get_logger(__name__)
logger.debug("Logger initialized for PathManager module.")

try:
    from winrt.windows.storage import ApplicationData
    logger.debug("winrt.windows.storage.ApplicationData imported successfully.")
except ImportError:
    ApplicationData = None
    logger.debug("winrt.windows.storage.ApplicationData not available, using fallback.")


def get_current_app_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(sys.argv[0]))


def is_installed(app_id: str = APP_ID) -> bool:
    current_path = os.path.normcase(os.path.normpath(get_current_app_dir()))
    inno_key = f"{app_id}_is1"

    registry_paths = [
        f"HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{inno_key}",
        f"HKLM\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{inno_key}",
        f"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{inno_key}",
        f"HKCU\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{inno_key}"
    ]

    for path in registry_paths:
        install_dir = None
        try:
            install_dir = registry.read(path, "Inno Setup: App Path")
            if not install_dir:
                install_dir = registry.read(path, "InstallLocation")
        except RegistryError:
            continue
        except Exception:
            continue

        if install_dir:
            install_dir = os.path.normcase(os.path.normpath(str(install_dir)))
            if current_path == install_dir or current_path.startswith(install_dir + os.sep):
                return True

    return False


def is_portable(app_id: str = APP_ID) -> bool:
    return not is_installed(app_id)


class PathManager:
    def __init__(self, app_name, author):
        self.app_name = app_name
        self.author = author
        logger.debug(f"Initializing PathManager with app_name='{app_name}' and author='{author}'.")

        # detect initial operating mode
        self.is_portable_mode = is_portable()
        logger.debug(f"Initial portable mode check: {self.is_portable_mode}")

        # detect environment (MSIX vs external vs portable)
        self._base_dir = self._detect_base_dir()

        # check permissions if in portable mode to prevent crashes in read-only locations
        if self.is_portable_mode:
            if not self._check_write_permission(self._base_dir):
                logger.warning(f"No write permission in {self._base_dir}. Falling back to AppData paths.")
                self.is_portable_mode = False
                # Re-detect the base directory now that we are forcing installed mode behavior
                self._base_dir = self._detect_base_dir()

        # main app folder
        if self.is_portable_mode:
            self._app_folder = self._base_dir / "User Data"
        else:
            self._app_folder = self._base_dir / self.author / app_name
            
        self._app_folder.mkdir(parents=True, exist_ok=True)
        logger.debug(f"App folder created/existing: {self._app_folder}")

        # bundled data folder
        self._data_folder = Path("database")  # bundled data

        # create athkar audio folder
        self._athkar_audio = self._app_folder / "audio" / "athkar"
        self._athkar_audio.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Athkar audio folder created/existing: {self._athkar_audio}")

        # temp folder
        self._temp_folder = Path(os.getenv("TEMP", "/tmp")) / app_name
            
        self._temp_folder.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Temp folder created/existing: {self._temp_folder}")

        # documents folder
        self._documents_dir = Path.home() / "Documents" / app_name
        self._documents_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Documents folder created/existing: {self._documents_dir}")

        # standard paths
        self._user_db = self._app_folder / "user_data.db"
        self._download_db_path = self._app_folder / "download_data.db"
        self._config_file = self._app_folder / "config.ini"
        self._log_file = self._app_folder / f"{app_name.lower()}.log"
        self._reciters_db = self._data_folder / "quran" / "reciters.db"
        self._athkar_db = self._app_folder / "athkar.db"

        logger.debug("Standard DB/config/log paths initialized.")

    def _check_write_permission(self, target_dir: Path) -> bool:
        """Silently tests if the application can write to the target directory."""
        test_file = target_dir / ".write_test"
        try:
            # Attempt to write and immediately delete a temp file
            test_file.touch(exist_ok=True)
            test_file.unlink()
            logger.debug(f"Write permission confirmed for: {target_dir}")
            return True
        except Exception as e:
            logger.debug(f"Write permission check failed for {target_dir} | Error: {e}")
            return False

    def _detect_base_dir(self) -> Path:
        """Detects base directory depending on app context."""
        logger.debug("Detecting base directory...")
        
        if self.is_portable_mode:
            path = Path(get_current_app_dir())
            logger.debug(f"Portable environment detected, base folder: {path}")
            return path
            
        if ApplicationData:
            try:
                path = Path(ApplicationData.current.local_folder.path)
                logger.debug(f"MSIX environment detected, base folder: {path}")
                return path
            except Exception as e:
                logger.debug(f"Failed to get MSIX base folder, error: {e}")
                
        fallback_path = Path(os.getenv("APPDATA", Path.home()))
        logger.debug(f"Fallback base folder: {fallback_path}")
        return fallback_path

    # Properties with debug

    @property
    def base_dir(self):
        logger.debug(f"Accessed base_dir: {self._base_dir}")
        return self._base_dir

    @property
    def app_folder(self):
        logger.debug(f"Accessed app_folder: {self._app_folder}")
        return self._app_folder

    @property
    def user_db(self):
        logger.debug(f"Accessed user_db path: {self._user_db}")
        return self._user_db

    @property
    def download_db_path(self):
        logger.debug(f"Accessed download_db_path: {self._download_db_path}")
        return self._download_db_path

    @property
    def config_file(self):
        logger.debug(f"Accessed config_file path: {self._config_file}")
        return self._config_file

    @property
    def log_file(self):
        logger.debug(f"Accessed log_file path: {self._log_file}")
        return self._log_file

    @property
    def data_folder(self):
        logger.debug(f"Accessed data_folder: {self._data_folder}")
        return self._data_folder

    @property
    def reciters_db(self):
        logger.debug(f"Accessed reciters_db path: {self._reciters_db}")
        return self._reciters_db

    @property
    def athkar_db(self):
        logger.debug(f"Accessed athkar_db path: {self._athkar_db}")
        return self._athkar_db

    @property
    def athkar_audio(self):
        logger.debug(f"Accessed athkar_audio folder: {self._athkar_audio}")
        return self._athkar_audio

    @property
    def temp_folder(self):
        logger.debug(f"Accessed temp_folder: {self._temp_folder}")
        return self._temp_folder

    @property
    def documents_dir(self):
        logger.debug(f"Accessed documents_dir: {self._documents_dir}")
        return self._documents_dir

    def __repr__(self):
        paths = {
            "PortableMode": self.is_portable_mode,
            "BaseDir": self.base_dir,
            "AppFolder": self.app_folder,
            "UserDB": self.user_db,
            "Config": self.config_file,
            "Log": self.log_file,
            "AthkarDB": self.athkar_db,
            "AthkarAudio": self.athkar_audio,
            "Temp": self.temp_folder,
            "Documents": self.documents_dir,
        }
        lines = [f"<PathManager app='{self.app_name}'>"]
        lines += [f"  {key}: {val}" for key, val in paths.items()]
        logger.debug(f"PathManager representation: {lines}")
        return "\n".join(lines)


# Singleton instance

paths = PathManager(program_english_name, author)
logger.debug("Singleton PathManager instance created.")
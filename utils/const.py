import os
from pathlib import Path
from PyQt6.QtWidgets import QSystemTrayIcon
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

logger.debug("Initializing folder paths.")
tecwindow_folder = os.path.join(os.getenv("AppData"), "tecwindow")
albayan_folder = os.path.join(tecwindow_folder, "albayan")
os.makedirs(albayan_folder, exist_ok=True)
logger.debug(f"Created albayan folder at {albayan_folder}")
user_db_path = os.path.join(albayan_folder, "user_data.db")
logger.debug(f"User database path: {user_db_path}")
CONFIG_PATH = os.path.join(albayan_folder, "config.ini")
logger.debug(f"Config path: {CONFIG_PATH}")
LOG_PATH = os.path.join(albayan_folder, "albayan.log")
logger.debug(f"Log path: {LOG_PATH}")
data_folder = Path("database")
logger.debug(f"Data folder path: {data_folder}")


#athkar
logger.debug("Initializing athkar paths.")
athkar_db_path = Path(albayan_folder) / "athkar.db"
logger.debug(f"Athkar database path: {athkar_db_path}")
default_athkar_path = Path(albayan_folder) / "audio" / "athkar"
logger.debug(f"Default athkar path: {default_athkar_path}")
test_athkar_path = Path("audio/athkar")

# albayan folder in temp
logger
temp_folder = os.path.join(os.getenv("TEMP"), "albayan")
os.makedirs(temp_folder, exist_ok=True)
logger.debug(f"Temporary folder path: {temp_folder}")

# Get the path to the Documents directory
logger.debug("Initializing Documents directory.")
albayan_documents_dir = os.path.join(os.path.expanduser("~"), "Documents", "Albayan")
os.makedirs(albayan_documents_dir, exist_ok=True)
logger

# program information
logger.debug("Initializing program information.")
program_name = "البيان"
program_english_name = "Albayan"
program_version = "4.0.0"
dev_mode = False
program_icon = "Albayan.ico"
website = "https://tecwindow.net/"
logger.debug(f"Program Info: {program_name}, {program_english_name}, Version: {program_version}, Website: {website}")

class Globals:
    """Class for managing global shared objects."""
    TRAY_ICON = None
    effects_manager = None

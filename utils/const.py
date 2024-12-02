import os
from pathlib import Path
from PyQt6.QtWidgets import QSystemTrayIcon

tecwindow_folder = os.path.join(os.getenv("AppData"), "tecwindow")
albayan_folder = os.path.join(tecwindow_folder, "albayan")
os.makedirs(albayan_folder, exist_ok=True)
user_db_path = os.path.join(albayan_folder, "user_data.db")
data_folder = Path("database")

#athkar
athkar_db_path = Path(albayan_folder) / "athkar.db"
default_athkar_path = Path(albayan_folder) / "audio" / "athkar"
test_athkar_path = Path("audio/athkar")

# albayan folder in temp
temp_folder = os.path.join(os.getenv("TEMP"), "albayan")
os.makedirs(temp_folder, exist_ok=True)

# Get the path to the Documents directory
albayan_documents_dir = os.path.join(os.path.expanduser("~"), "Documents", "Albayan")
os.makedirs(albayan_documents_dir, exist_ok=True)

# program information
program_name = "البيان"
program_english_name = "Albayan"
program_version = "1.3.0"
program_icon = "icon.webp"
website = "https://tecwindow.net/"


class Globals:
    """Class for managing global shared objects."""
    TRAY_ICON = None
    effects_manager = None

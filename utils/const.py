import os
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QSystemTrayIcon

tecwindow_folder = os.path.join(os.getenv("AppData"), "tecwindow")
albayan_folder = os.path.join(tecwindow_folder, "albayan")
os.makedirs(albayan_folder, exist_ok=True)
user_db_path = os.path.join(albayan_folder, "user_data.db")
athkar_db_path = Path(albayan_folder)/"athkar.db"
data_folder = Path("database")

# albayan folder in temp
temp_folder = os.path.join(os.getenv("TEMP"), "albayan")
os.makedirs(temp_folder, exist_ok=True)

# Get the path to the Documents directory
albayan_documents_dir = os.path.join(os.path.expanduser("~"), "Documents", "Albayan")
os.makedirs(albayan_documents_dir, exist_ok=True)

# program information
program_name = "البيان"
program_version = "1.2.4"
program_icon = "icon.webp"
tray_icon: Optional[QSystemTrayIcon] = None
website = "https://tecwindow.net/"

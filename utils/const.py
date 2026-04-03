import os
from pathlib import Path
from PyQt6.QtWidgets import QSystemTrayIcon
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)



# program information
logger.debug("Initializing program information.")
program_name = "البيان"
program_english_name = "Albayan"
program_version = "6.1.0"
author= "Tecwindow"
dev_mode = False
program_icon = "Albayan.ico"
website = "https://tecwindow.net/"
logger.debug(f"Program Info: {program_name}, {program_english_name}, Version: {program_version}, Website: {website}, author, {author}.")

class Globals:
    """Class for managing global shared objects."""
    TRAY_ICON = None
    effects_manager = None

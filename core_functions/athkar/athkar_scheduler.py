from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QSystemTrayIcon
import os
import json
from datetime import datetime, time
from pathlib import Path
from typing import Dict, Optional, Union
from random import choice
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.exc import IntegrityError
from .athkar_db_manager import AthkarDBManager
from .athkar_refresher import AthkarRefresher
from utils.audio_player import AthkarPlayer
from utils.const import Globals, program_icon
from utils.logger import LoggerManager
from exceptions.base import ErrorMessage

logger = LoggerManager.get_logger(__name__)

class AthkarScheduler:
    def __init__(self, athkar_db_folder: Union[Path, str], default_category_path: Optional[Union[Path, str]] = None, text_athkar_path: Optional[Union[Path, str]] = None, default_category_settings: Optional[Dict[str, int]] = None) -> None:
        self.default_category_path = Path(default_category_path) if isinstance(default_category_path, str) else default_category_path
        self.text_athkar_path = Path(text_athkar_path) if isinstance(text_athkar_path, str) else text_athkar_path
        self.default_category_settings = default_category_settings if default_category_settings is not None else {}
        self.categories = None
        self.db_manager = AthkarDBManager(athkar_db_folder)
        self.scheduler = BackgroundScheduler()
        self.setup()

    def setup(self) -> None:
        logger.info("Initializing AthkarScheduler.")
        if self.default_category_path:
            logger.debug(f"Ensuring category folder exists: {self.default_category_path}")
            self.default_category_path.mkdir(parents=True, exist_ok=True)
            try:
                category_id = self.db_manager.create_category("default", str(self.default_category_path), **self.default_category_settings)
                logger.debug(f"Default category created with ID {category_id}")
                if self.text_athkar_path and self.text_athkar_path.exists():
                    with open(self.text_athkar_path, encoding="UTF-8") as f:
                        text_data = json.load(f)
                        self.db_manager.add_text_athkar(text_data, category_id)
                        logger.debug(f"Loaded {len(text_data)} text athkar into default category")
            except IntegrityError:
                logger.warning("Default category already exists, skipping creation.")
                pass

        self.categories = self.db_manager.get_all_categories()
        logger.debug(f"Loaded {len(self.categories)} categories from database.")
        for category in self.categories:
            refresher = AthkarRefresher(self.db_manager, category.audio_path, category.id)
            refresher.refresh_data()

    def audio_athkar_job(self, category_id: int, audio_path: str) -> None:
        logger.debug(f"Starting audio athkar for category ID {category_id} using {audio_path}")
        with AthkarPlayer(audio_path, self.db_manager.get_audio_athkar(category_id)) as player:
            player.play()

    def text_athkar_job(self, category_id: int) -> None:
        logger.info(f"Displaying text athkar for category ID {category_id}")
        random_text_athkar = choice(self.db_manager.get_text_athkar(category_id))
        text = random_text_athkar.text

        if len(text) > 256:
            title = " ".join(text.split()[:10])
            description = " ".join(text.split()[10:])
        else:
            title = "البيان"
            description = text


        icon_path = "Albayan.ico"

        Globals.TRAY_ICON.showMessage(title, description, QIcon(icon_path), 5000)

    @staticmethod
    def _parse_time(time_str: str) -> time:
        return datetime.strptime(time_str, "%H:%M").time()

    def _create_triggers(self, from_time: time, to_time: time, play_interval: int):
        minute = "0" if play_interval == 60 else f"*/{play_interval}"

        if from_time < to_time:
            return [CronTrigger(minute=minute, hour=f"{from_time.hour}-{to_time.hour}")]
        else:
            return [
                CronTrigger(minute=minute, hour=f"{from_time.hour}-23"),
                CronTrigger(minute=minute, hour=f"0-{to_time.hour}")
            ]

    def _add_jobs(self, category, trigger):
        if category.audio_athkar_enabled:
            self.scheduler.add_job(
                self.audio_athkar_job,
                trigger,
                args=[category.id, category.audio_path],
                id=f"audio_athkar_{category.id}_{trigger}"
            )
        if category.text_athkar_enabled:
            self.scheduler.add_job(
                self.text_athkar_job,
                trigger,
                args=[category.id],
                id=f"text_athkar_{category.id}_{trigger}"
            )

    def start(self) -> None:
        logger.info("Starting AthkarScheduler...")
        for category in self.categories:
            try:
                from_time = self._parse_time(category.from_time)
                to_time = self._parse_time(category.to_time)
                triggers = self._create_triggers(from_time, to_time, category.play_interval)
                for trigger in triggers:
                    self._add_jobs(category, trigger)
                    logger.debug(f"Scheduled athkar jobs for category {category.id} from {category.from_time} to {category.to_time}")
            except Exception as e:
                logger.error(f"Error scheduling category {category.id}: {e}", exc_info=True)

        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("AthkarScheduler started successfully.")


    def refresh(self) -> None:
        logger.info("Refreshing AthkarScheduler...")
        if self.scheduler is not None:
            self.scheduler.remove_all_jobs()

        self.setup()
        self.start()
        logger.info("AthkarScheduler refreshed successfully.")

        
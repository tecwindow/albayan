import os
import json
import utils.const as const
from datetime import datetime, time
from pathlib import Path
from typing import Dict, Optional, Union
from random import choice
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.exc import IntegrityError 
from .athkar_db_manager import AthkarDBManager
from .athkar_refresher import AthkarRefresher
from .athkar_player import AthkarPlayer

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

        if self.default_category_path:
            self.default_category_path.mkdir(parents=True, exist_ok=True)
            try:
                category_id = self.db_manager.create_category("default", str(self.default_category_path), **self.default_category_settings)
                if self.text_athkar_path and self.text_athkar_path.exists():
                    with open(self.text_athkar_path, encoding="UTF-8") as f:
                        self.db_manager.add_text_athkar(json.load(f), category_id)
            except IntegrityError as e:
                pass

        self.categories = self.db_manager.get_all_categories()
        for category in self.categories:
            refresher = AthkarRefresher(self.db_manager, category.audio_path, category.id)
            refresher.refresh_data()

    def audio_athkar_job(self, player: AthkarPlayer) -> None:
        player.play()

    def text_athkar_job(self, category_id: int) -> None:
        random_text_athkar = choice(self.db_manager.get_text_athkar(category_id))
        const.tray_icon.showMessage("البيان", random_text_athkar.text,msecs=5000)

    @staticmethod
    def _parse_time(time_str: str) -> time:
        time_ob = datetime.strptime(time_str, "%H:%M")
        return time_ob

    def start(self,) -> None:
        for category in self.categories:
            from_time = self._parse_time(category.from_time)
            to_time = self._parse_time(category.to_time)
            minute = "0" if category.play_interval == 60 else f"*/{category.play_interval}"
            trigger = CronTrigger(minute=minute, hour=f"{from_time.hour}-{to_time.hour}")
            if category.audio_athkar_enabled :
                player = AthkarPlayer(self.db_manager, category.audio_path, category.id)
                self.scheduler.add_job(self.audio_athkar_job, trigger, args=[player])
            if category.text_athkar_enabled:
                self.scheduler.add_job(self.text_athkar_job, trigger, args=[category.id])

        if not self.scheduler.running:
            self.scheduler.start()

    def refresh(self) -> None:

        if self.scheduler is not None:
            self.scheduler.remove_all_jobs()

        self.setup()
        self.start()

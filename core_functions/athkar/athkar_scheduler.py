import os
from datetime import datetime, time
from typing import Dict, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.exc import IntegrityError 
from .athkar_db_manager import AthkarDBManager
from .athkar_refresher import AthkarRefresher
from utils.sound_Manager import BasmalaManager

class AthkarScheduler:
    def __init__(self, athkar_db_folder: str, default_category_path: Optional[str] = None, default_category_settings: Optional[Dict[str, int]] = None) -> None:
        self.default_category_path = default_category_path
        self.default_category_settings = default_category_settings if default_category_settings is not None else {}
        self.categories = None
        self.db_manager = AthkarDBManager(athkar_db_folder)
        self.scheduler = BackgroundScheduler() 
        self.setup()

    def setup(self) -> None:

        if self.default_category_path:
            os.makedirs(self.default_category_path, exist_ok=True)
            try:
                self.db_manager.create_category("default", self.default_category_path, **self.default_category_settings)
            except IntegrityError as e:
                pass

        self.categories = self.db_manager.get_all_categories()
        for category in self.categories:
            refresher = AthkarRefresher(self.db_manager, category.audio_path, category.id)
            refresher.refresh_data()

    def job(self, audio_path: str) -> None:
        BasmalaManager(audio_path).play()

    @staticmethod
    def _parse_time(time_str: str) -> time:
        time_ob = datetime.strptime(time_str, "%H:%M")
        return time_ob

    def start(self,) -> None:
        for category in self.categories:
            if not category.status:
                continue
            from_time = self._parse_time(category.from_time)
            to_time = self._parse_time(category.to_time)
            trigger = CronTrigger(minute=f"*/{category.play_interval}", hour=f"{from_time.hour}-{to_time.hour}")
            self.scheduler.add_job(self.job, trigger, args=[category.audio_path])

        if not self.scheduler.running:
            self.scheduler.start()

    def refresh(self) -> None:

        if self.scheduler is not None:
            self.scheduler.remove_all_jobs()

        self.setup()
        self.start()

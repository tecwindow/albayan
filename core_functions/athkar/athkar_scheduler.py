import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.exc import IntegrityError 
from typing import Dict, Optional
from .athkar_db_manager import AthkarDBManager
from .athkar_refresher import AthkarRefresher
from utils.sound_Manager import BasmalaManager

class AthkarScheduler:
    def __init__(self, athkar_db_folder: str, default_category_path: Optional[str] = None, default_category_settings: Optional[Dict[str, int]] = None) -> None:
        self.default_category_path = default_category_path
        self.default_category_settings = default_category_settings
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

        for category in self.db_manager.get_all_categories():
            refresher = AthkarRefresher(self.db_manager, category.audio_path, category.id)
            refresher.refresh_data()

    def job(self, audio_path: str) -> None:
        BasmalaManager(audio_path).play()

    def start(self) -> None:
        for category in self.db_manager.get_all_categories():
            trigger = CronTrigger(minute=f"*/{category.play_interval}", hour=f"{category.from_time}-{category.to_time}")
            self.scheduler.add_job(self.job, trigger, args=[category.audio_path])
        self.scheduler.start()

import os
from typing import List, Dict, Optional
from sqlalchemy.orm import sessionmaker
from .models import AthkarCategory, TextAthkar, AudioAthkar
from . import init_db
from utils.logger import LoggerManager
logger = LoggerManager.get_logger(__name__)


class AthkarDBManager:
    def __init__(self, db_file_path: str):
        logger.debug(f"Initializing database manager with file path: {db_file_path}")
        self.engine = init_db(db_file_path)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"Database engine created and session factory initialized.")


    def _add_to_db(self, instance) -> int:
        with self.Session() as session:
            session.add(instance)
            session.commit()
            logger.debug(f"Added {instance.__class__.__name__} to database with ID: {instance.id}")
            return instance.id

    def _update_in_db(self, instance, **kwargs):
        with self.Session() as session:
            for key, value in kwargs.items():
                logger.debug(f"Updating {key} to {value} for {instance.__class__.__name__} with ID: {instance.id}")
                setattr(instance, key, value)
                session.merge(instance)
            session.commit()
            logger.info(f"Updated {instance.__class__.__name__} with ID: {instance.id} using {kwargs}")

    def _delete_from_db(self, instance):
        with self.Session() as session:
            session.delete(instance)
            session.commit()
            logger.info(f"Deleted {instance.__class__.__name__} with ID: {instance.id}")

    def _get_by_id(self, model, item_id):
        with self.Session() as session:
            instance = session.query(model).filter_by(id=item_id).first()
            if instance:
                logger.debug(f"Found {model.__name__} with ID: {item_id}")
            else:
                logger.warning(f"{model.__name__} with ID: {item_id} not found")
            return instance


    def create_category(self, 
                        name: str,
                        audio_path: Optional[str] = None,
                        from_time: str = "00:00",
                        to_time: str = "23:00",
                        play_interval: int =30,
                        audio_athkar_enabled: int = 0,
                        text_athkar_enabled: int = 0
                        ) -> int:
        logger.debug(f"Creating category with name: {name}, from_time: {from_time}, to_time: {to_time}, "
                     f"play_interval: {play_interval}, audio_athkar_enabled: {audio_athkar_enabled}, "
                     f"text_athkar_enabled: {text_athkar_enabled}")
        new_category = AthkarCategory(
            name=name,
            audio_path=audio_path,
            from_time=from_time,
            to_time=to_time,
            play_interval=play_interval,
            audio_athkar_enabled=audio_athkar_enabled,
            text_athkar_enabled=text_athkar_enabled
        )
        return self._add_to_db(new_category)

    def update_category(self, category_id: int, **kwargs) -> None:
        logger.debug(f"Updating category with ID: {category_id} using {kwargs}")
        category = self._get_by_id(AthkarCategory, category_id)
        if category:
            self._update_in_db(category, **kwargs)
        else:
            logger.warning(f"Category with ID: {category_id} not found for update")

    def delete_category(self, category_id: int) -> None:
        logger.debug(f"Deleting category with ID: {category_id}")
        category = self._get_by_id(AthkarCategory, category_id)
        if category:
            self._delete_from_db(category)
        else:
            logger.warning(f"Category with ID: {category_id} not found for deletion")


    def get_all_categories(self) -> List[AthkarCategory]:
        logger.debug("Fetching all categories from database")
        with self.Session() as session:
            categories = session.query(AthkarCategory).all()
            logger.info(f"Found {len(categories)} categories in database")
            return categories


    def add_text_athkar(self, athkar_list: List[Dict[str, str]], category_id: int) -> None:
        logger.debug(f"Adding text athkars for category ID: {category_id}")
        new_athkar_list = [
            TextAthkar(name=athkar.get("name"), text=athkar.get("text"), category_id=category_id)
            for athkar in athkar_list
        ]
        with self.Session() as session:
            session.bulk_save_objects(new_athkar_list)
            session.commit()
            logger.info(f"Added {len(new_athkar_list)} text athkars for category ID: {category_id}")

    def update_text_athkar(self, athkar_id: int, **kwargs) -> None:
        logger.debug(f"Updating text athkar with ID: {athkar_id} using {kwargs}")
        text_athkar = self._get_by_id(TextAthkar, athkar_id)
        if text_athkar:
            self._update_in_db(text_athkar, **kwargs)
        else:
            logger.warning(f"Text athkar with ID: {athkar_id} not found for update")    


    def delete_text_athkar(self, athkar_id: int) -> None:
        logger.debug(f"Deleting text athkar with ID: {athkar_id}")
        text_athkar = self._get_by_id(TextAthkar, athkar_id)
        if text_athkar:
            self._delete_from_db(text_athkar)
        else:
            logger.warning(f"Text athkar with ID: {athkar_id} not found for deletion")

    def get_text_athkar(self, category_id: int) -> List[TextAthkar]:
        logger.debug(f"Fetching text athkars for category ID: {category_id}")
        with self.Session() as session:
            text_athkars = session.query(TextAthkar).filter(TextAthkar.category_id == category_id).all()
            logger.info(f"Found {len(text_athkars)} text athkars for category ID: {category_id}")
            return text_athkars

    def add_audio_athkar(self, audio_files, category_id: int) -> None:
        logger.debug(f"Adding audio athkars for category ID: {category_id}")
        new_athkar_list = [
            AudioAthkar(audio_file_name=audio_file, category_id=category_id)
            for audio_file in audio_files
        ]
        with self.Session() as session:
            session.bulk_save_objects(new_athkar_list)
            session.commit()
            logger.info(f"Added {len(new_athkar_list)} audio athkars for category ID: {category_id}")


    def update_audio_athkar(self, athkar_id: int, **kwargs) -> None:
        logger.debug(f"Updating audio athkar with ID: {athkar_id} using {kwargs}")
        audio_athkar = self._get_by_id(AudioAthkar, athkar_id)
        if audio_athkar:
            self._update_in_db(audio_athkar, **kwargs)
        else:
            logger.warning(f"Audio athkar with ID: {athkar_id} not found for update")


    def delete_audio_athkar(self, athkar_ids: List[int]) -> None:
        logger.debug(f"Deleting audio athkars with IDs: {athkar_ids}")
        with self.Session() as session:
            session.query(AudioAthkar).filter(AudioAthkar.id.in_(athkar_ids)).delete(synchronize_session='fetch')
            session.commit()
            logger.info(f"Deleted audio athkars with IDs: {athkar_ids}")


    def get_audio_athkar(self, category_id: int) -> List[AudioAthkar]:
        logger.debug(f"Fetching audio athkars for category ID: {category_id}")
        with self.Session() as session:
            audio_athkars = session.query(AudioAthkar).filter(AudioAthkar.category_id == category_id).all()
            logger.info(f"Found {len(audio_athkars)} audio athkars for category ID: {category_id}")
            return audio_athkars
        

        
import os
from typing import List, Dict, Optional
from sqlalchemy.orm import sessionmaker
from .models import AthkarCategory, TextAthkar, AudioAthkar
from . import init_db

class AthkarDBManager:
    def __init__(self, db_file_path: str):
        self.engine = init_db(db_file_path)
        self.Session = sessionmaker(bind=self.engine)

    def _add_to_db(self, instance) -> int:
        with self.Session() as session:
            session.add(instance)
            session.commit()
            return instance.id

    def _update_in_db(self, instance, **kwargs):
        with self.Session() as session:
            for key, value in kwargs.items():
                setattr(instance, key, value)
                session.merge(instance)
            session.commit()

    def _delete_from_db(self, instance):
        with self.Session() as session:
            session.delete(instance)
            session.commit()

    def _get_by_id(self, model, item_id):
        with self.Session() as session:
            return session.query(model).filter_by(id=item_id).first()

    def create_category(self, 
                        name: str,
                        audio_path: Optional[str] = None,
                        from_time: str = "00:00",
                        to_time: str = "23:00",
                        play_interval: int =5,
                        audio_athkar_enabled: int = 0,
                        text_athkar_enabled: int = 0
                        ) -> int:
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
        category = self._get_by_id(AthkarCategory, category_id)
        if category:
            self._update_in_db(category, **kwargs)

    def delete_category(self, category_id: int) -> None:
        category = self._get_by_id(AthkarCategory, category_id)
        if category:
            self._delete_from_db(category)

    def get_all_categories(self) -> List[AthkarCategory]:
        with self.Session() as session:
            return session.query(AthkarCategory).all()

    def add_text_athkar(self, athkar_list: List[Dict[str, str]], category_id: int) -> None:
        new_athkar_list = [
            TextAthkar(name=athkar.get("name"), text=athkar.get("text"), category_id=category_id)
            for athkar in athkar_list
        ]
        with self.Session() as session:
            session.bulk_save_objects(new_athkar_list)
            session.commit()

    def update_text_athkar(self, athkar_id: int, **kwargs) -> None:
        text_athkar = self._get_by_id(TextAthkar, athkar_id)
        if text_athkar:
            self._update_in_db(text_athkar, **kwargs)

    def delete_text_athkar(self, athkar_id: int) -> None:
        text_athkar = self._get_by_id(TextAthkar, athkar_id)
        if text_athkar:
            self._delete_from_db(text_athkar)

    def get_text_athkar(self, category_id: int) -> List[TextAthkar]:
        with self.Session() as session:
            return session.query(TextAthkar).filter(TextAthkar.category_id == category_id).all()
        
    def add_audio_athkar(self, audio_files, category_id: int) -> None:
        new_athkar_list = [
            AudioAthkar(audio_file_name=audio_file, category_id=category_id)
            for audio_file in audio_files
        ]
        with self.Session() as session:
            session.bulk_save_objects(new_athkar_list)
            session.commit()

    def update_audio_athkar(self, athkar_id: int, **kwargs) -> None:
        audio_athkar = self._get_by_id(AudioAthkar, athkar_id)
        if audio_athkar:
            self._update_in_db(audio_athkar, **kwargs)

    def delete_audio_athkar(self, athkar_ids: List[int]) -> None:
        with self.Session() as session:
            session.query(AudioAthkar).filter(AudioAthkar.id.in_(athkar_ids)).delete(synchronize_session='fetch')
            session.commit()

    def get_audio_athkar(self, category_id: int) -> List[AudioAthkar]:
        with self.Session() as session:
            return session.query(AudioAthkar).filter(AudioAthkar.category_id == category_id).all()
        
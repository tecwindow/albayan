import os
from sqlalchemy.orm import sessionmaker
from models import AthkarCategory, TextAthkar, AudioAthkar
from . import init_db

class AthkarDBManager:
    def __init__(self, db_folder: str):
        self.engine = init_db(os.path.join(db_folder, "athkar.db"))
        self.Session = sessionmaker(bind=self.engine)

    def _add_to_db(self, instance):
        with self.Session() as session:
            session.add(instance)
            session.commit()

    def _update_in_db(self, instance, **kwargs):
        with self.Session() as session:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            session.commit()

    def _delete_from_db(self, instance):
        with self.Session() as session:
            session.delete(instance)
            session.commit()

    def _get_by_id(self, model, item_id):
        with self.Session() as session:
            return session.query(model).filter_by(id=item_id).first()

    def create_category(self, name, audio_path=None, from_time=None, to_time=None, play_interval=None, status=1):
        new_category = AthkarCategory(
            name=name,
            audio_path=audio_path,
            from_time=from_time,
            to_time=to_time,
            play_interval=play_interval,
            status=status
        )
        self._add_to_db(new_category)

    def update_category(self, category_id, **kwargs):
        category = self._get_by_id(AthkarCategory, category_id)
        if category:
            self._update_in_db(category, **kwargs)

    def delete_category(self, category_id):
        category = self._get_by_id(AthkarCategory, category_id)
        if category:
            self._delete_from_db(category)

    def get_all_categories(self):
        with self.Session() as session:
            return session.query(AthkarCategory).all()

    def create_text_athkar(self, name, text, category_id):
        new_text_athkar = TextAthkar(name=name, text=text, category_id=category_id)
        self._add_to_db(new_text_athkar)

    def update_text_athkar(self, athkar_id, **kwargs):
        text_athkar = self._get_by_id(TextAthkar, athkar_id)
        if text_athkar:
            self._update_in_db(text_athkar, **kwargs)

    def delete_text_athkar(self, athkar_id):
        text_athkar = self._get_by_id(TextAthkar, athkar_id)
        if text_athkar:
            self._delete_from_db(text_athkar)

    def get_all_text_athkars(self):
        with self.Session() as session:
            return session.query(TextAthkar).all()

    def create_audio_athkar(self, audio_file_name, description, category_id):
        new_audio_athkar = AudioAthkar(audio_file_name=audio_file_name, description=description, category_id=category_id)
        self._add_to_db(new_audio_athkar)

    def update_audio_athkar(self, athkar_id, **kwargs):
        audio_athkar = self._get_by_id(AudioAthkar, athkar_id)
        if audio_athkar:
            self._update_in_db(audio_athkar, **kwargs)

    def delete_audio_athkar(self, athkar_id):
        audio_athkar = self._get_by_id(AudioAthkar, athkar_id)
        if audio_athkar:
            self._delete_from_db(audio_athkar)

    def get_all_audio_athkars(self):
        with self.Session() as session:
            return session.query(AudioAthkar).all()

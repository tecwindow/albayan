from PyQt6.QtCore import QObject, pyqtSignal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
from .model import Base, TasbihEntry
from utils.logger import Logger


class TasbihController(QObject):
    # Signal emitted whenever the list of tasbih entries is updated.
    entrieAdded = pyqtSignal(TasbihEntry)
    entrieUpdated = pyqtSignal(TasbihEntry)

    def __init__(self, db_path: str):
        super().__init__()
        db_url = f'sqlite:///{db_path}'
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist.
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self._initialize_default_entries()

    def _initialize_default_entries(self):
        """Insert a list of default tasbih entries if they are not already in the database."""
        default_entries = [
            "سبحان الله",
            "الحمد لله",
            "الله أكبر",
            "لا إله إلا الله"
        ]
        for entry in default_entries:
            self.add_entry(entry)

    def get_all_entries(self) -> list[TasbihEntry]:
        """Return all tasbih entries as a list of TasbihEntrie."""
        with self.Session() as session:
            items = session.query(TasbihEntry).all()
            return items

    def add_entry(self, name):
        """Add a new tasbih entry provided by the user."""
        try:
            with self.Session() as session:
                new_entry = TasbihEntry(name=name)
                session.add(new_entry)
                session.commit()
                self.entrieAdded.emit(self.get_entry(new_entry.id))
        except IntegrityError as e:
            Logger.error(e)
        except Exception as e:
            Logger.error(e)

    def get_entry(self, entry_id) -> TasbihEntry:
        """Return a specific tasbih entry by its ID."""
        with self.Session() as session:
            return session.query(TasbihEntry).get(entry_id)

    def update_entry(self, tasbih_entry: TasbihEntry):
        with self.Session() as session:
            session.merge(tasbih_entry)
            session.commit()
            self.entrieUpdated.emit(tasbih_entry)

    def increment_entry_counter(self, entry_id):
        """Increment the counter for a specific tasbih entry."""
        item = self.get_entry(entry_id)
        if item:
            item.counter += 1
            self.update_entry(item)

    def reset_entry_counter(self, entry_id):
        """Reset the counter for a specific tasbih entry."""
        item = self.get_entry(entry_id)
        if item:
            item.counter = 0
            self.update_entry(item)
            
    def delete_entry(self, entry_id):
        """Delete a specific tasbih entry by its ID."""
        with self.Session() as session:
            entry = session.get(TasbihEntry, entry_id)
            if entry:
                session.delete(entry)
                session.commit()

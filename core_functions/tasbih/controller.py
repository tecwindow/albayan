from PyQt6.QtCore import QObject, pyqtSignal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
from .model import Base, TasbihEntry
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class TasbihController(QObject):
    # Signal emitted whenever the list of tasbih entries is updated.
    entrieAdded = pyqtSignal(TasbihEntry)
    entrieUpdated = pyqtSignal(TasbihEntry)

    def __init__(self, db_path: str):
        super().__init__()
        logger.debug(f"Initializing TasbihController with database path: {db_path}")
        db_url = f'sqlite:///{db_path}'
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist.
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self._initialize_default_entries()
        logger.debug("Database initialized successfully.")

    def _initialize_default_entries(self):
        """Check if default tasbih entries exist, and insert them if not."""
        logger.debug("Checking for default tasbih entries in the database.")
        
        default_entries = [
            "سبحان الله",
            "الحمد لله",
            "أستغفر الله",
            "لا حول ولا قوة إلا بالله",
            "الله أكبر",
            "لا إله إلا الله"
        ]

        for entry in default_entries:
            self.add_entry(entry)

    def get_all_entries(self) -> list[TasbihEntry]:
        """Retrieve all tasbih entries."""
        try:
            with self.Session() as session:
                entries = session.query(TasbihEntry).all()
                logger.info(f"Retrieved {len(entries)} tasbih entries from the database.")
                return entries
        except Exception as e:
            logger.error(f"Error retrieving tasbih entries: {e}", exc_info=True)
            return []

    def add_entry(self, name):
        """Add a new tasbih entry provided by the user."""
        try:
            with self.Session() as session:
                new_entry = TasbihEntry(name=name)
                session.add(new_entry)
                session.commit()
                self.entrieAdded.emit(self.get_entry(new_entry.id))
                logger.info(f"Added new tasbih entry: {name}")
        except IntegrityError as e:
            logger.debug(f"Entry '{name}' already exists in the database.")
        except Exception as e:
            logger.error(f"Error adding tasbih entry '{name}': {e}", exc_info=True)

    def get_entry(self, entry_id: int) -> TasbihEntry:
        """Retrieve a tasbih entry by ID."""
        try:
            with self.Session() as session:
                entry = session.get(TasbihEntry, entry_id)
                if entry:
                    logger.debug(f"Retrieved entry: {entry.name} (ID: {entry_id})")
                else:
                    logger.warning(f"Entry with ID {entry_id} not found.")
                return entry
        except Exception as e:
            logger.error(f"Error retrieving tasbih entry with ID {entry_id}: {e}", exc_info=True)
            return None

    def update_entry(self, tasbih_entry: TasbihEntry):
        """Update an existing tasbih entry."""
        try:
            with self.Session() as session:
                session.merge(tasbih_entry)
                session.commit()
                self.entrieUpdated.emit(tasbih_entry)
                logger.info(f"Updated tasbih entry: {tasbih_entry.name} (ID: {tasbih_entry.id}) (counter: {tasbih_entry.counter})")
        except Exception as e:
            logger.error(f"Error updating tasbih entry ID {tasbih_entry.id}: {e}", exc_info=True)

    def increment_entry_counter(self, entry_id: int):
        """Increment the counter for a specific tasbih entry."""
        item = self.get_entry(entry_id)
        if item:
            item.counter += 1
            self.update_entry(item)
            logger.debug(f"Incremented counter for entry ID {entry_id}. New count: {item.counter}")

    def decrement_entry_counter(self, entry_id: int):
        """Decrement the counter for a specific tasbih entry."""
        item = self.get_entry(entry_id)
        if item:
            item.counter = max(0, item.counter - 1)
            self.update_entry(item)
            logger.debug(f"Decremented counter for entry ID {entry_id}. New count: {item.counter}")

    def reset_entry_counter(self, entry_id: int):
        """Reset the counter for a specific tasbih entry."""
        item = self.get_entry(entry_id)
        if item:
            item.counter = 0
            self.update_entry(item)
            logger.info(f"Reset counter for entry ID {entry_id}.")

    def delete_entry(self, entry_id: int):
        """Delete a specific tasbih entry by its ID."""
        try:
            with self.Session() as session:
                entry = session.get(TasbihEntry, entry_id)
                if entry:
                    session.delete(entry)
                    session.commit()
                    logger.info(f"Deleted tasbih entry: {entry.name} (ID: {entry_id})")
                else:
                    logger.warning(f"Entry with ID {entry_id} not found for deletion.")
        except Exception as e:
            logger.error(f"Error deleting tasbih entry ID {entry_id}: {e}", exc_info=True)

    def reset_all_entries(self):
        """Reset the counter for all tasbih entries."""
        try:
            with self.Session() as session:
                session.query(TasbihEntry).update({TasbihEntry.counter: 0})
                session.commit()
                logger.info("All tasbih entry counters have been reset.")
        except Exception as e:
            logger.error(f"Error resetting all tasbih counters: {e}", exc_info=True)

    def delete_all_entries(self):
        """Delete all tasbih entries."""
        try:
            with self.Session() as session:
                session.query(TasbihEntry).delete()
                session.commit()
                logger.info("All tasbih entries deleted. Reinitializing default entries.")
            self._initialize_default_entries()
        except Exception as e:
            logger.error(f"Error deleting all tasbih entries: {e}", exc_info=True) 


    def update_entry_name(self, entry_id: int, new_name: str):
        """update tasbih entrie."""
        logger.debug(f"Updating name of tasbih entry ID {entry_id} to '{new_name}'")
        entry = self.get_entry(entry_id)
        if entry:
            old_name = entry.name
            entry.name = new_name
            self.update_entry(entry)
            self.entrieUpdated.emit(entry)
            logger.info(f"Updated tasbih name from '{old_name}' to '{new_name}' (ID: {entry_id})")

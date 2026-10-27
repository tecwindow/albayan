import sqlite3
from typing import List, Optional
from exceptions.database import DBNotFoundError
from utils.logger import LoggerManager
from .models import Category

logger = LoggerManager.get_logger(__name__)


class TafaseerManager:
    """
    Manages active SQLite database connections to Tafaseer databases
    and retrieves tafsir text for specific Surah and Ayah numbers.
    """

    _active_instances: List["TafaseerManager"] = []

    def __init__(self) -> None:
        logger.debug("Initializing TafaseerManager...")
        self._tafaseer_category: Optional[str] = None
        self._conn: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
        self._db_path: Optional[str] = None
        TafaseerManager._active_instances.append(self)
        logger.debug("TafaseerManager initialized.")

    @classmethod
    def close_all_instances_for(cls, category: str) -> None:
        """Closes connections on any manager instances that have this category open."""
        for inst in list(cls._active_instances):
            if inst._tafaseer_category == category:
                inst.close_connection()

    def set(self, tafaseer_category: str) -> None:
        logger.debug(f"Setting tafaseer category: {tafaseer_category}")
        if not Category.is_valid(tafaseer_category):
            logger.error(f"Invalid tafaseer category: {tafaseer_category}")
            raise ValueError(f"Invalid tafaseer category: {tafaseer_category}")

        self._tafaseer_category = tafaseer_category
        logger.info(f"Set tafaseer category to: {tafaseer_category}")
        self._connect_to_database()

    def _connect_to_database(self) -> None:
        assert self._tafaseer_category is not None, "You must set tafaseer category."
        file_path = Category.find_tafsir_db_path(self._tafaseer_category)
        logger.debug(f"Connecting to database at {file_path} for {self._tafaseer_category}...")

        if file_path is None or not file_path.is_file():
            logger.error(f"Database file not found: {file_path}")
            raise DBNotFoundError(str(file_path or self._tafaseer_category))

        self.close_connection()
        self._conn = sqlite3.connect(str(file_path))
        self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()
        self._db_path = str(file_path)
        logger.info(f"Database connection established successfully: {file_path}.")

    def close_connection(self) -> None:
        """Explicitly close database connection if currently open."""
        if self._conn is not None:
            try:
                self._conn.close()
                logger.debug(f"Closed database connection for {self._tafaseer_category}.")
            except Exception as e:
                logger.warning(f"Error closing tafaseer db connection: {e}")
            finally:
                self._conn = None
                self._cursor = None
                self._db_path = None

    def get_tafaseer(self, surah_number: int, ayah_number: int) -> str:
        """Fetch tafseer text for a specific Surah and Ayah."""
        logger.debug(f"Fetching tafseer for Surah {surah_number}, Ayah {ayah_number}...")
        assert self._conn is not None, "You must connect to database first."
        assert 1 <= surah_number <= 114, "Out of surah range."
        assert 1 <= ayah_number, "Out of ayah range."

        query = "SELECT text FROM tafsir_{} WHERE number = ?".format(surah_number)
        try:
            self._cursor.execute(query, [ayah_number])
            result = self._cursor.fetchone()
            logger.info(f"Fetched tafseer for Surah {surah_number}, Ayah {ayah_number}.")
            return self.get_text(result)
        except sqlite3.Error as e:
            logger.error(f"Error fetching tafseer: {e}", exc_info=True)
            return ""

    def get_text(self, row) -> str:
        """Process and format tafseer text from database row."""
        logger.debug("Processing tafseer text...")
        if row:
            text = row["text"].replace(".", ". \n").strip()
        else:
            logger.warning("No text found in the result row.")
            return ""

        # Remove empty lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

    def __str__(self) -> str:
        return f"Category: {self._tafaseer_category}"

    def __del__(self):
        """Close database connection when manager object is destroyed."""
        try:
            if self in TafaseerManager._active_instances:
                TafaseerManager._active_instances.remove(self)
        except Exception:
            pass
        self.close_connection()

import os
import sqlite3
from typing import List, Dict, Optional
from functools import lru_cache
from abc import ABC, abstractmethod
from exceptions.database import DBNotFoundError
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class RecitersManager(ABC):
    def __init__(self, db_path: str, table_name: str) -> None:
        """Initializes the RecitersManager with the database path and table name."""
        logger.debug(f"Initializing {self.__class__.__name__} with database: {db_path}, table: {table_name}")
        self.db_path = db_path
        self.table_name = table_name
        logger.debug(f"{self.__class__.__name__} initialized.")

    def _connect(self) -> sqlite3.Connection:
        """Establishes a connection to the SQLite database."""
        logger.debug(f"Connecting to database at: {self.db_path} in {self.__class__.__name__}")
        if not os.path.isfile(self.db_path):
            logger.error(f"Database file not found: {self.db_path}")
            raise DBNotFoundError(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        logger.debug(f"Database connection established successfully to {self.db_path} in {self.__class__.__name__}")
        return conn

    def get_reciters(self) -> List[sqlite3.Row]:
        """Fetches all reciters from the database."""
        logger.debug(f"Fetching all reciters from table: {self.table_name}")
        with self._connect() as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT *,
                    CASE
                        WHEN bitrate < 64 THEN 'Low'
                        WHEN bitrate BETWEEN 64 AND 128 THEN 'Medium'
                        ELSE 'High'
                    END AS quality
                FROM {self.table_name}
                ORDER BY name, bitrate;
            """
            cursor.execute(query)
            result = cursor.fetchall()
            logger.info(f"Fetched {len(result)} reciters from the database.")
            return result
            return cursor.fetchall()

    def get_reciter(self, id: int) -> sqlite3.Row:
        """Fetches a specific reciter by ID."""
        logger.debug(f"Fetching reciter with ID: {id}")
        with self._connect() as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM {self.table_name} WHERE id = ?;"
            cursor.execute(query, (id,))
            result = cursor.fetchone()
            if result:
                logger.debug(f"Fetched reciter: {result['name']} (ID: {id})")
            else:
                logger.warning(f"No reciter found with ID: {id}")
            return result

    @lru_cache(maxsize=1)
    def _get_base_url(self, reciter_id: int) -> Optional[str]:
        """Fetches the base URL for a specific reciter ID."""
        logger.debug(f"Fetching base URL for reciter ID: {reciter_id}")
        with self._connect() as conn:
            cursor = conn.cursor()
            query = f"SELECT url FROM {self.table_name} WHERE id = ?"
            cursor.execute(query, (reciter_id,))
            result = cursor.fetchone()
            if result:
                logger.debug(f"Fetched base URL for reciter ID {reciter_id}: {result['url']}")
                return result["url"]
            else:
                logger.warning(f"No base URL found for reciter ID: {reciter_id}")
        return None

    @abstractmethod
    def get_url(self, reciter_id: int, surah_number: int) -> Optional[str]:
        pass


class SurahReciter(RecitersManager):
    def __init__(self, db_path: str, table_name: str ="moshaf"):
        super().__init__(db_path, table_name)

    def get_url(self, reciter_id: int, surah_number: int) -> Optional[str]:
        """Fetches the URL for a specific reciter and surah number."""
        logger.debug(f"Getting URL for reciter ID: {reciter_id}, surah number: {surah_number}")
        base_url = self._get_base_url(reciter_id)
        if base_url:
            url = f"{base_url}/{surah_number:03}.mp3"
            logger.debug(f"Generated URL: {url}")
            return url
        logger.warning(f"Base URL for reciter ID: {reciter_id} is not available.")
        return None
    

class AyahReciter(RecitersManager):
    def __init__(self, db_path: str, table_name: str ="reciters"):
        super().__init__(db_path, table_name)

    def get_url(self, reciter_id: int, surah_number: int, aya_number: int) -> Optional[str]:
        """Fetches the URL for a specific reciter, surah number, and ayah number."""
        logger.debug(f"Getting URL for reciter ID: {reciter_id}, surah number: {surah_number}, ayah number: {aya_number}")
        base_url = self._get_base_url(reciter_id)
        if base_url:
            url = f"{base_url}{surah_number:03}{aya_number:03}.mp3"
            logger.debug(f"Generated URL: {url}")
            return url
        logger.warning(f"Base URL for reciter ID: {reciter_id} is not available.")
        return None
    
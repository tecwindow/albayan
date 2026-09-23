import os
import sqlite3
from typing import List, Dict, Optional
from functools import lru_cache
from abc import ABC, abstractmethod
from exceptions.database import DBNotFoundError
from utils.logger import LoggerManager
from core_functions.downloader.db import DownloadDB
from core_functions.downloader.models import DownloadSurahs, DownloadAyahs
from core_functions.downloader.status import DownloadStatus
from utils.paths import paths

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

    def get_reciters(self) -> List[dict]:
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
                    END AS quality,
                                    name || ' - ' || rewaya || ' - (' || type || ') - (' || bitrate || ' kbps)' AS display_text
                FROM {self.table_name}
                ORDER BY name, bitrate;
            """
            cursor.execute(query)
            result = cursor.fetchall()
            logger.info(f"Fetched {len(result)} reciters from the database.")
            return [dict(row) for row in result]

    @lru_cache(maxsize=32)
    def get_reciter(self, id: int) -> dict:
        """Fetches a specific reciter by ID."""
        logger.debug(f"Fetching reciter with ID: {id}")
        with self._connect() as conn:
            cursor = conn.cursor()
            query = f"""
            SELECT *, 
            name || ' - ' || rewaya || ' - (' || type || ') - (' || bitrate || ' kbps)' AS display_text 
            FROM {self.table_name}
            WHERE id = ?;
            """
            cursor.execute(query, (id,))
            result = cursor.fetchone()
            if result:
                logger.debug(f"Fetched reciter: {result['name']} (ID: {id})")
                return dict(result)
            else:
                logger.warning(f"No reciter found with ID: {id}")
                return {}

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
    def check_local_file(self, reciter_id: int, surah_number: int, ayah_number: Optional[int] = None) -> Optional[str]:
        pass

    @abstractmethod
    def get_url(self, reciter_id: int, surah_number: int) -> Optional[str]:
        pass


class SurahReciter(RecitersManager):
    def __init__(self, db_path: str, table_name: str ="moshaf"):
        super().__init__(db_path, table_name)
        self.download_db = DownloadDB(f"sqlite:///{paths.download_db_path}", DownloadSurahs)

    def get_reciters(self):
        reciters = super().get_reciters()
        for reciter in reciters:
            reciter["available_suras"] = sorted(map(int, reciter["available_suras"].split(",")))
        return reciters

    @lru_cache(maxsize=32)    
    def get_reciter(self, id: int) -> dict:
        reciter_data = super().get_reciter(id)
        if reciter_data and isinstance(reciter_data["available_suras"], str):
            reciter_data["available_suras"] = sorted(map(int, reciter_data["available_suras"].split(",")))
        return reciter_data

    def check_local_file(self, reciter_id: int, surah_number: int, ayah_number: Optional[int] = None) -> Optional[str]:
        """Checks for a local file for the given reciter and surah number."""
        logger.debug(f"Checking local file for reciter ID: {reciter_id}, surah number: {surah_number}")
        try:
            local_file = self.download_db.find_one(reciter_id=reciter_id, surah_number=surah_number, status=DownloadStatus.COMPLETED)
            if local_file and os.path.exists(os.path.join(local_file.folder_path, local_file.filename)):
                file_path = os.path.join(local_file.folder_path, local_file.filename)
                logger.debug(f"Found local file: {file_path}")
                return file_path
            else:
                logger.debug(f"No local file found for reciter ID: {reciter_id}, surah number: {surah_number}")
        except Exception as e:
            logger.error(f"Error checking for local surah file: {e}")
        return None
    
    def get_url(self, reciter_id: int, surah_number: int, offline_playback: bool = False) -> Optional[str]:
        """Fetches the URL for a specific reciter and surah number."""
        logger.debug(f"Getting URL for reciter ID: {reciter_id}, surah number: {surah_number}")

        if offline_playback:
            # Check for local file first
            local_file = self.check_local_file(reciter_id, surah_number)
            if local_file:
                return local_file
            
        base_url = self._get_base_url(reciter_id)
        if base_url:
            base_url = base_url.rstrip('/')
            url = f"{base_url}/{surah_number:03}.mp3"
            logger.debug(f"Generated URL: {url}")
            return url
        logger.warning(f"Base URL for reciter ID: {reciter_id} is not available.")
        return None
    

class AyahReciter(RecitersManager):
    def __init__(self, db_path: str, table_name: str ="reciters"):
        super().__init__(db_path, table_name)
        self.download_db = DownloadDB(f"sqlite:///{paths.download_db_path}", DownloadAyahs)

    def check_local_file(self, reciter_id, surah_number, ayah_number = None):
        """Checks for a local file for the given reciter, surah, and ayah number."""
        logger.debug(f"Checking local file for reciter ID: {reciter_id}, surah number: {surah_number}, ayah number: {ayah_number}")
        try:
            local_file = self.download_db.find_one(reciter_id=reciter_id, surah_number=surah_number, ayah_number=ayah_number, status=DownloadStatus.COMPLETED)
            if local_file and os.path.exists(os.path.join(local_file.folder_path, local_file.filename)):
                file_path = os.path.join(local_file.folder_path, local_file.filename)
                logger.debug(f"Found local file: {file_path}")
                return file_path
            else:
                logger.debug(f"No local file found for reciter ID: {reciter_id}, surah number: {surah_number}, ayah number: {ayah_number}")
        except Exception as e:
            logger.error(f"Error checking for local ayah file: {e}")
        return None

    def get_url(self, reciter_id: int, surah_number: int, ayah_number: int, offline_playback: bool = False) -> Optional[str]:
        """Fetches the URL for a specific reciter, surah number, and ayah number."""
        logger.debug(f"Getting URL for reciter ID: {reciter_id}, surah number: {surah_number}, ayah number: {ayah_number}")

        if offline_playback:
            # Check for local file first
            local_file = self.check_local_file(reciter_id, surah_number, ayah_number)
            if local_file:
                return local_file
            
        base_url = self._get_base_url(reciter_id)
        if base_url:
            url = f"{base_url}{surah_number:03}{ayah_number:03}.mp3"
            logger.debug(f"Generated URL: {url}")
            return url
        logger.warning(f"Base URL for reciter ID: {reciter_id} is not available.")
        return None
    
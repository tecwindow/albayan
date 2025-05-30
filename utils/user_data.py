import sqlite3
import os
import datetime
from typing import Dict, Union, Optional
from pathlib import Path
from utils.logger import LoggerManager
from exceptions.database import DatabaseConnectionError

logger = LoggerManager.get_logger(__name__)

class PreferencesManager:
    def __init__(self, db_path: Union[Path, str]):
        self.db_path = db_path
        logger.debug(f"Initializing PreferencesManager with database path: {db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()
        logger.debug("PreferencesManager initialized")

    def create_table(self) -> None:
        """Create the preferences table if it does not exist."""
        try:
            logger.debug("Creating preferences table if it does not exist.")
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            self.conn.commit()
            logger.debug("Preferences table created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating preferences table: {e}", exc_info=True)

    def set_preference(self, key: str, value: str) -> None:
        """
        Insert or update a preference.
        Uses SQLite's UPSERT (ON CONFLICT) clause.
        """
        try:
            logger.debug(f"Setting preference: {key} = {value}")
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO preferences (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            ''', (key, value))
            self.conn.commit()
            logger.debug(f"Preference set successfully: {key} = {value}")
        except sqlite3.Error as e:
                        logger.error(f"Error setting preference '{key}': {e}", exc_info=True)

    def set_preferences(self, preferences: Dict[str, str]) -> None:
        """Insert or update multiple preferences."""
        for key, value in preferences.items():
            self.set_preference(key, value)

    def get(self, key: str, default_value: Optional[str] = None) -> str:
        """Retrieve a preference value by key."""
        try:
            logger.debug(f"Fetching preference for key: {key}")
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            value = row[0] if row else default_value
            logger.info(f"Preference retrieved: {key} = {value}")
            return value
        except sqlite3.Error as e:
            logger.error(f"Error retrieving preference '{key}': {e}")

            return default_value

    def get_int(self, key: str, default_value: Optional[int] = None) -> int:
        return int(self.get(key, default_value))

    def get_float(self, key: str, default_value: Optional[float] = None) -> float:
        return float(self.get(key, default_value or -1))

    def get_bool(self, key: str, default_value: Optional[bool] = None) -> bool:
        return self.get(key, default_value) == "True"

    def close(self):
        logger.debug("Closing preferences database connection.")
        self.conn.close()
        logger.info("Preferences database connection closed.")


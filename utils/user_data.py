import sqlite3
import os
import datetime
from typing import Union, Optional
from pathlib import Path
from utils.logger import LoggerManager
from exceptions.database import DatabaseConnectionError

logger = LoggerManager.get_logger(__name__)

class UserDataManager:
    def __init__(self, db_path: Union[Path, str]) -> None:
        """Initialize the database connection and create table if not exists."""
        self.db_path = db_path
        logger.debug(f"Initializing UserDataManager with database path: {db_path}")
        self.connect()
        self.create_table()
        logger.debug("UserDataManager initialized")

    def connect(self):
        """Connect to the SQLite database."""
        logger.debug(f"Connecting to database at {self.db_path}")
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.debug("Database connection established successfully,at {self.db_path}.")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}", exc_info=True)
            raise DatabaseConnectionError(f"Error connecting to database", e)

    def create_table(self):
        """Create the user position table if it does not exist."""
        try:
            logger.debug("Creating user_position table if it does not exist.")
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_position(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ayah_number INTEGER NOT NULL,
                    criteria_number INTEGER NOT NULL,
                    position INTEGER NOT NULL
                )
            ''')
            self.conn.commit()
            logger.debug("user_position table created successfully.")    
        except sqlite3.Error as e:
            logger.error(f"Error creating table: {e}", exc_info=True)
            raise RuntimeError(f"Error creating table: {e}")

    def save_position(self, ayah_number: int, criteria_number: int, position: int) -> None:
        """Save the current position of the user."""

        try:
            logger.debug(f"Saving user position: Ayah {ayah_number}, Criteria {criteria_number}, Position {position}")
            self.cursor.execute('''
                UPDATE user_position 
                                SET 
                    ayah_number = ?, 
                    criteria_number = ?, 
                    position = ?
                WHERE id = 1
            ''', (ayah_number, criteria_number, position))

            if self.cursor.rowcount == 0:  
                logger.debug("No rows updated, inserting new record.")
                # If no rows were updated, insert a new record
                self.cursor.execute('''
                    INSERT INTO user_position(id, ayah_number, criteria_number, position)
                    VALUES (1, ?, ?, ?)
                ''', (ayah_number, criteria_number, position))
            self.conn.commit()
            logger.debug("User position saved successfully.")    
        except sqlite3.Error as e:
            logger.error(f"Error saving user position: {e}", exc_info=True)
            raise RuntimeError(f"Error saving user position: {e}")

    def get_last_position(self) -> dict:
        """Retrieve the last saved position of the user."""
        try:
            logger.debug("Fetching last saved position.")
            self.cursor.execute('''
                SELECT * FROM user_position WHERE id = 1
            ''')
            result = self.cursor.fetchone()
            position_data = self.convert_to_dict(result)
            if position_data:
                logger.debug(f"Retrieved last position: {position_data}")
            else:
                logger.warning("No previous position found in database.")
            return position_data
        except sqlite3.Error as e:
            logger.error(f"Error retrieving user position: {e}", exc_info=True)
            raise RuntimeError(f"Error retrieving user position: {e}")
        
    @staticmethod
    def convert_to_dict(result: sqlite3.Row) -> dict:
        if result is None:
            return {}
        return dict(result)

    def close_connection(self):
        """Close the database connection."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logger.info("Database connection closed.")

    def __del__(self):
        """Destructor to ensure database connection is closed."""
        logger.debug("Destructor called, closing database connection.")
        self.close_connection()


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
        except sqlite3.IntegrityError as e:
                        logger.warning(f"Failed to set preference '{key}': {e}")

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
        return int(self.get(key, default_value or -1))

    def get_float(self, key: str, default_value: Optional[float] = None) -> float:
        return float(self.get(key, default_value or -1))

    def get_bool(self, key: str, default_value: Optional[bool] = None) -> bool:
        return self.get(key, default_value) == "True"

    def close(self):
        logger.debug("Closing preferences database connection.")
        self.conn.close()
        logger.info("Preferences database connection closed.")


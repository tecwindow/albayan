import sqlite3
import logging
import os
import datetime
from typing import Union, Optional
from pathlib import Path

class UserDataManager:
    def __init__(self, db_path: Union[Path, str]) -> None:
        """Initialize the database connection and create table if not exists."""
        self.db_path = db_path
        self.connect()
        self.create_table()

    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error connecting to database: {e}")

    def create_table(self):
        """Create the user position table if it does not exist."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_position(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ayah_number INTEGER NOT NULL,
                    criteria_number INTEGER NOT NULL,
                    position INTEGER NOT NULL
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error creating table: {e}")

    def save_position(self, ayah_number: int, criteria_number: int, position: int) -> None:
        """Save the current position of the user."""

        try:

            self.cursor.execute('''
                UPDATE user_position 
                                SET 
                    ayah_number = ?, 
                    criteria_number = ?, 
                    position = ?
                WHERE id = 1
            ''', (ayah_number, criteria_number, position))

            if self.cursor.rowcount == 0:  
                # If no rows were updated, insert a new record
                self.cursor.execute('''
                    INSERT INTO user_position(id, ayah_number, criteria_number, position)
                    VALUES (1, ?, ?, ?)
                ''', (ayah_number, criteria_number, position))
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error saving user position: {e}")

    def get_last_position(self) -> dict:
        """Retrieve the last saved position of the user."""
        try:
            self.cursor.execute('''
                SELECT * FROM user_position WHERE id = 1
            ''')
            result = self.cursor.fetchone()
            return self.convert_to_dict(result)
        except sqlite3.Error as e:
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

    def __del__(self):
        """Destructor to ensure database connection is closed."""
        self.close_connection()


class PreferencesManager:
    def __init__(self, db_path: Union[Path, str]):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def set_preference(self, key: str, value: str) -> None:
        """
        Insert or update a preference.
        Uses SQLite's UPSERT (ON CONFLICT) clause.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO preferences (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            ''', (key, value))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            logging.warning(f"Failed to sett preference: {e}")

    def get(self, key: str, default_value: Optional[str] = None) -> str:
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default_value

    def get_int(self, key: str, default_value: Optional[int] = None) -> int:
        return int(self.get(key, default_value or -1))

    def get_float(self, key: str, default_value: Optional[float] = None) -> float:
        return float(self.get(key, default_value or -1))

    def get_bool(self, key: str, default_value: Optional[bool] = None) -> bool:
        return self.get(key, default_value) == "True"

    def close(self):
        self.conn.close()


import sqlite3
import os
import datetime
from utils.const import albayan_folder

class UserDataManager:
    def __init__(self) -> None:
        """Initialize the database connection and create table if not exists."""
        self.db_path = os.path.join(albayan_folder, "user_data.db")
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

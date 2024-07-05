import sqlite3
import os
import datetime
from PyQt6.QtWidgets import QMessageBox
from utils.logger import Logger
from utils.const import albayan_folder
from utils.exceptions import DuplicateEntryError


class BookmarkManager:
    def __init__(self) -> None:
        self.file_path = os.path.join(albayan_folder, "bookmark.db")
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        self.create_table()

    def connect(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.file_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            Logger.error(str(e))

    def create_table(self) -> None:

        query = """
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY,
                name TEXT,
                ayah_number INTEGER UNIQUE,
                ayah_number_in_surah INTEGER,
                surah_number INTEGER,
                surah_name TEXT,
                criteria_number INTEGER,
                date TEXT
            )
        """

        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            Logger.error(str(e))

    def insert_bookmark(self, name: str, ayah_number: int, ayah_number_in_surah: int, surah_number: int, surah_name: str, criteria_number: int) -> None:

        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """
            INSERT INTO bookmarks (
                name, ayah_number, ayah_number_in_surah, surah_number, surah_name, criteria_number, date
                )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?
                )
        """ 

        try:
            self.cursor.execute(query, (name, ayah_number, ayah_number_in_surah, surah_number, surah_name, criteria_number, date))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            # Unique constraint
            Logger.error(str(e))
            raise DuplicateEntryError(e)
        except Exception as e:
            print(e)
            Logger.error(str(e))

    def get_bookmarks(self) -> list:

        returned_data = []
        try:
            self.cursor.execute("SELECT * FROM bookmarks")
            returned_data = self.cursor.fetchall()
        except Exception as e:
            Logger.error(str(e))

        return returned_data
    
    def delete_bookmark(self, bookmark_id: int) -> None:
        try:
            self.cursor.execute("DELETE FROM bookmarks WHERE id=?", (bookmark_id,))
            self.conn.commit()
        except Exception as e:
            Logger.error(str(e))

    def update_bookmark(self, bookmark_id: int, new_name: str) -> None:

        query = """
            UPDATE bookmarks
            SET 
            name=?
            WHERE 
            id=?
        """

        try:
            self.cursor.execute(query, (new_name, bookmark_id))
            self.conn.commit()
        except Exception as e:
            Logger.error(str(e))

    def search_bookmarks(self, search_text: str) -> list:

        returned_data = []
        query = """
            SELECT * FROM bookmarks
            WHERE name LIKE ?
        """

        try:
            self.cursor.execute(query, ('%' + search_text + '%',))
            returned_data = self.cursor.fetchall()
        except Exception as e:
            Logger.error(str(e))

        return returned_data
    
    def __str__(self) -> str:
        return "Connecting to {}.".format(self.file_path)

    def __del__(self):
        if self.conn:
            self.conn.close()


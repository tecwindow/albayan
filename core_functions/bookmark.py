import sqlite3
import os
import datetime
from PyQt6.QtWidgets import QMessageBox
from utils.logger import LoggerManager
from utils.const import albayan_folder

logger = LoggerManager.get_logger(__name__)

class BookmarkManager:
    def __init__(self) -> None:
        logger.info("Initializing BookmarkManager...")
        self.file_path = os.path.join(albayan_folder, "bookmark.db")
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        self.create_table()
        logger.info(f"BookmarkManager initialized. Database file: {self.file_path}.")


    def connect(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.file_path)
            conn.row_factory = sqlite3.Row
            logger.debug(f"Connected to bookmark database: {self.file_path}.")
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}", exc_info=True)

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
            logger.debug("Bookmarks table checked/created successfully.")
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating bookmarks table: {str(e)}", exc_info=True)

    def insert_bookmark(self, name: str, ayah_number: int, ayah_number_in_surah: int, surah_number: int, surah_name: str, criteria_number: int) -> None:
        if self.is_exist(ayah_number):
            logger.warning(f"Bookmark already exists for Ayah number: {ayah_number}")
            return

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
            logger.info(f"Inserted bookmark: {name} (Ayah: {ayah_number}, Surah: {surah_number})")
        except Exception as e:
            logger.error(f"Error inserting bookmark: {str(e)}", exc_info=True)

    def get_bookmarks(self) -> list:

        returned_data = []
        try:
            self.cursor.execute("SELECT * FROM bookmarks")
            bookmarks = self.cursor.fetchall()
            logger.debug(f"Fetched {len(bookmarks)} bookmarks.")
            return bookmarks
        except Exception as e:
            logger.error(f"Error fetching bookmarks: {str(e)}", exc_info=True)

        return returned_data
    
    def delete_bookmark(self, bookmark_id: int) -> None:
        try:
            self.cursor.execute("DELETE FROM bookmarks WHERE id=?", (bookmark_id,))
            self.conn.commit()
            logger.info(f"Deleted bookmark with ID: {bookmark_id}")
        except Exception as e:
            logger.error(f"Error deleting bookmark (ID: {bookmark_id}): {str(e)}", exc_info=True)

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
            logger.info(f"Updated bookmark ID {bookmark_id} with new name: {new_name}")
        except Exception as e:
            logger.error(f"Error updating bookmark (ID: {bookmark_id}): {str(e)}", exc_info=True)

    def search_bookmarks(self, search_text: str) -> list:

        returned_data = []
        query = """
            SELECT * FROM bookmarks
            WHERE name LIKE ?
        """

        try:
            self.cursor.execute(query, ('%' + search_text + '%',))
            results = self.cursor.fetchall()
            logger.debug(f"Search query '{search_text}' returned {len(results)} results.")
            return results
        except Exception as e:
            logger.error(f"Error searching bookmarks: {str(e)}", exc_info=True)

            return []
    
    def __str__(self) -> str:
        return "Connecting to {}.".format(self.file_path)

    def __del__(self):
        if self.conn:
            self.conn.close()
            logger.info("Closed database connection.")


    def is_exist(self, ayah_number: int) -> bool:
        query = "SELECT 1 FROM bookmarks WHERE ayah_number = ?"
        try:
            self.cursor.execute(query, (ayah_number,))
            result = self.cursor.fetchone()
            exists = result is not None
            logger.debug(f"Checked existence of Ayah {ayah_number}: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking existence of Ayah {ayah_number}: {str(e)}", exc_info=True)
            return False


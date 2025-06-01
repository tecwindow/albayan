import sqlite3
import os
import datetime
from PyQt6.QtWidgets import QMessageBox
from utils.logger import LoggerManager
from utils.const import albayan_folder

logger = LoggerManager.get_logger(__name__)

class BookmarkManager:
    def __init__(self) -> None:
        logger.debug("Initializing BookmarkManager...")
        self.file_path = os.path.join(albayan_folder, "bookmark.db")
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        self.create_table()
        logger.debug(f"BookmarkManager initialized. Database file: {self.file_path}.")

    def connect(self) -> sqlite3.Connection:
        """Connect to the SQLite database."""        
        logger.debug(f"Connecting to database at {self.file_path}...")
        try:
            conn = sqlite3.connect(self.file_path)
            conn.row_factory = sqlite3.Row
            logger.info(f"Connected to bookmark database: {self.file_path}.")
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}", exc_info=True)

    def create_table(self) -> None:
        """Create the bookmarks table if it doesn't exist."""
        logger.debug("Creating bookmarks table if it doesn't exist...")

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
        """Insert a new bookmark into the database."""
        logger.debug(f"Inserting bookmark: {name} (Ayah: {ayah_number}, Surah: {surah_number})...")
    
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
        """Fetch all bookmarks from the database."""
        logger.debug("Fetching all bookmarks from the database...")

        bookmarks = []
        try:
            self.cursor.execute("SELECT * FROM bookmarks")
            bookmarks = self.cursor.fetchall()
            logger.info(f"Fetched {len(bookmarks)} bookmarks.")
        except Exception as e:
            logger.error(f"Error fetching bookmarks: {str(e)}", exc_info=True)

        return bookmarks
    
    def delete_bookmark(self, bookmark_id: int) -> None:
        """Delete a bookmark by its ID."""
        logger.debug(f"Deleting bookmark with ID: {bookmark_id}...")
        try:
            self.cursor.execute("DELETE FROM bookmarks WHERE id=?", (bookmark_id,))
            self.conn.commit()
            logger.info(f"Deleted bookmark with ID: {bookmark_id}")
        except Exception as e:
            logger.error(f"Error deleting bookmark (ID: {bookmark_id}): {str(e)}", exc_info=True)



    def delete_all_bookmarks(self) -> None:
        """Delete all bookmarks from the database."""
        logger.debug("Deleting all bookmarks from the database...")
        try:
            self.cursor.execute("DELETE FROM bookmarks")
            self.conn.commit()
            logger.info("All bookmarks have been deleted successfully.")
        except Exception as e:
            logger.error(f"Error deleting all bookmarks: {str(e)}", exc_info=True)


    def update_bookmark(self, bookmark_id: int, new_name: str) -> None:
        """Update a bookmark's name by its ID."""
        logger.debug(f"Updating bookmark ID {bookmark_id} with new name: {new_name}...")

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
        """Search for bookmarks by name."""
        logger.debug(f"Searching bookmarks with text: {search_text}...")

        bookmarks = []
        query = """
            SELECT * FROM bookmarks
            WHERE name LIKE ?
        """

        try:
            self.cursor.execute(query, ('%' + search_text + '%',))
            bookmarks = self.cursor.fetchall()
            logger.debug(f"Search query '{search_text}' returned {len(bookmarks)} results.")
        except Exception as e:
            logger.error(f"Error searching bookmarks: {str(e)}", exc_info=True)

            return bookmarks

    def is_exist(self, ayah_number: int) -> bool:
        """Check if a bookmark exists for the given Ayah number."""
        logger.debug(f"Checking existence of Ayah {ayah_number} in bookmarks...")
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
    
    def __str__(self) -> str:
        return "Connecting to {}.".format(self.file_path)

    def __del__(self):
        """Close the database connection."""
        logger.debug("Deleting BookmarkManager object and closing connection.")
        if self.conn:
            self.conn.close()
            logger.info("Deleted BookmarkManager object and Database connection closed.")

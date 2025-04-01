import sqlite3
import os
from exceptions.database import DBNotFoundError
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class Category:
    baghawy = "baghawy"
    jalalayn = "jalalayn"
    katheer = "katheer"
    muyassar = "muyassar"
    qortoby = "qortoby"
    sa3dy = "sa3dy"
    tabary = "tabary"

    _category_in_arabic = {
        "البغوي": baghawy,
        "الجلالين": jalalayn,
        "ابن كثير": katheer,
        "الميسر": muyassar,
        "القرطبي": qortoby,
        "السعدي": sa3dy,
        "الطبري": tabary
    }

    @classmethod
    def is_valid(cls, category: str) -> bool:
        return category in cls._category_in_arabic.values()

    @classmethod
    def get_category_by_arabic_name(cls, arabic_name: str) -> str:
        return cls._category_in_arabic.get(arabic_name, None)

    @classmethod
    def get_categories_in_arabic(cls) -> list:
        return list(cls._category_in_arabic.keys())

class TafaseerManager:
    def __init__(self) -> None:
        logger.info("Initializing TafaseerManager...")
        self._tafaseer_category = None
        self._conn = None  
        logger.info("TafaseerManager initialized.")


    def set(self, tafaseer_category: str) -> None:
        assert Category.is_valid(tafaseer_category), "Invalid tafaseer category."
        logger.debug(f"Setting tafaseer category: {tafaseer_category}")
        if not Category.is_valid(tafaseer_category):
            logger.error(f"Invalid tafaseer category: {tafaseer_category}")
            raise ValueError("Invalid tafaseer category.")
        
        self._tafaseer_category = tafaseer_category
        logger.info(f"Setting tafaseer category to: {tafaseer_category}")
        self._connect_to_database()


    def _connect_to_database(self) -> None:
        assert self._tafaseer_category is not None, "You must set tafaseer category."
        file_path = os.path.join("database", "tafaseer", self._tafaseer_category + ".db")
        logger.debug(f"Connecting to database at {file_path}...")
        if not os.path.isfile(file_path):
            logger.error(f"Database file not found at: {file_path}")
            raise DBNotFoundError(file_path)
        logger.info(f"Database file found. Connecting to the database...")
        self._conn = sqlite3.connect(file_path)
        self._conn.row_factory = sqlite3.Row 
        self._cursor = self._conn.cursor()
        logger.info("Database connection established successfully.")


    def get_tafaseer(self, surah_number, ayah_number) -> str:
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
        logger.debug("Processing tafseer text...")
        if row:
                    text = row["text"].replace(".", ". \n").strip()
        else:
            logger.warning("No text found in the result.")
            return ""

        # Remove empty lines.
        logger.debug("Removing empty lines...")
        lines = text.split("\n")
        lines = list(filter(lambda x: x.strip(), lines))
        text = "\n".join(lines)
        logger.debug("Tafseer text processed successfully.")
        return text


    def __str__(self) -> str:
        return "Category: {}".format(self._tafaseer_category)

    def __del__(self):
        if self._conn:
            logger.info("Closing database connection...")
            self._conn.close()
            logger.info("Database connection closed.")          

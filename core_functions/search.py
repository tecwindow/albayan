import sqlite3
import re
import os
from exceptions.database import DBNotFoundError, DatabaseConnectionError, InvalidSearchTextError, InvalidCriteriaError
from utils.logger import LoggerManager
logger = LoggerManager.get_logger(__name__)

class SearchCriteria:
    page = "page"
    sura = "sura_number"
    hizb = "hizb"
    juz = "juz"
    quarter = "hizbQuarter"
    _arabic_criteria_dict = {
        "صفحة": page,
        "سورة": sura,
        "الحزب": hizb,
        "الجزء": juz,
        "الربع": quarter
    }    

    @classmethod
    def is_valid(cls, criteria) -> bool:
        return criteria in cls._arabic_criteria_dict.values()

    @classmethod
    def get_criteria_by_arabic_name(cls, arabic_criteria) -> str:
        return cls._arabic_criteria_dict.get(arabic_criteria)

    @classmethod    
    def get_arabic_criteria(cls) -> list:
        return list(cls._arabic_criteria_dict.keys())


class QuranSearchManager:
    def __init__(self):
        logger.info("Initializing QuranSearchManager...")
        self.no_tashkil = False
        self.no_hamza = False
        self.match_whole_word = False
        self._criteria = None
        self._from = None
        self._to = None
        self._from_ayah = None
        self._to_ayah = None
        self._conn = None
        self._cursor = None
        self._connect()
        logger.info("QuranSearchManager initialized.")

    def set(self, no_tashkil:bool=False, no_hamza:bool=False, match_whole_word:bool=False, criteria:str=None, _from:int=None, _to:int=None, from_ayah:int=None, to_ayah:int=None) -> None:
        logger.debug(f"Setting parameters: no_tashkil={no_tashkil}, no_hamza={no_hamza}, match_whole_word={match_whole_word}, criteria={criteria}, _from={_from}, _to={_to}, from_ayah={from_ayah}, to_ayah={to_ayah}")

        if not  SearchCriteria.is_valid(criteria):
            logger.error(f"Invalid criteria: {criteria}")
            raise InvalidCriteriaError(criteria)

        if self._conn is None:
                logger.error("Database connection is None. You must connect to the database first.")
                raise DatabaseConnectionError("QuranSearchManager._conn is None, you must connect to database first.")

        #Get surah number if the input is surah  name
        if  criteria == SearchCriteria.sura and isinstance(_from, str):
            logger.debug(f"Converting surah name '{_from}' to surah number...")
            self._cursor.execute("SELECT DISTINCT sura_number AS 'number' FROM quran WHERE sura_name LIKE '%' || ? || '%';", (_from,))
            _from = self._cursor.fetchone()['number']
        if  criteria == SearchCriteria.sura and isinstance(_to, str):
            logger.debug(f"Converting surah name '{_to}' to surah number...")
            self._cursor.execute("SELECT DISTINCT sura_number AS 'number' FROM quran WHERE sura_name LIKE '%' || ? || '%';", (_to,))
            _to = self._cursor.fetchone()['number']

        if not isinstance(_from, int) or _from < 1:
            logger.warning(f"Invalid 'from' value: {_from}. Setting to 1.")
            _from = 1

        if _to < _from:
            logger.warning(f"Invalid 'to' value: {_to}. Setting 'to' to 'from' value: {_from}.")
            _to = _from

        if not isinstance(_to, int) or _to <1:
            logger.debug(f"Invalid 'to' value: {_to}. Fetching max value for {criteria}.")
            self._cursor.execute(f"SELECT DISTINCT MAX({criteria}) AS 'max' FROM quran;")
            _to = self._cursor.fetchone()["max"]

# Set attributes
        self.no_tashkil = no_tashkil
        self.no_hamza = no_hamza
        self.match_whole_word = match_whole_word
        self._from = _from
        self._to = _to
        self._from_ayah = from_ayah
        self._to_ayah = to_ayah
        self._criteria = criteria
        logger.debug(f"Parameters set: no_tashkil={self.no_tashkil}, no_hamza={self.no_hamza}, match_whole_word={self.match_whole_word}, criteria={self._criteria}, _from={self._from}, _to={self._to}, from_ayah={self._from_ayah}, to_ayah={self._to_ayah}.")


    def _connect(self):
        file_path = os.path.join("database", "quran", 'Verses.DB')
        if not os.path.isfile(file_path):
            logger.error(f"Database file not found: {file_path}")
            raise DBNotFoundError(file_path)
        
        # connect to database
        try:
            logger.info(f"Connecting to database: {file_path}...")
            self._conn = sqlite3.connect(file_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.create_function("REGEXP", 2, lambda expr, item: re.search(expr, item) is not None)
            self._cursor = self._conn.cursor()
            logger.info("Database connection established successfully.")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}", exc_info=True)
            raise DatabaseConnectionError(cause=e)
    
    def search(self, search_text:str) -> list:
        logger.debug(f"Starting search with text: '{search_text}'")
        if  not isinstance(search_text, str):
            logger.error(f"Invalid search text: {search_text}")
            raise InvalidSearchTextError(search_text)

        if not search_text:
            logger.info("Empty search text provided. Returning None.")
            return None

        if self.match_whole_word:
            operator = "REGEXP"
            search_text = rf"\b{search_text}\b"
        else:
            operator = "LIKE"
            search_text = f"%{search_text}%"

        query = f"SELECT * FROM quran WHERE {self._criteria} >= ? AND {self._criteria} <= ? AND text {operator} ?;"
        logger.debug(f"Query constructed: {query}")
        if self.no_tashkil:
            # remove all tashkil from the text to search
            logger.debug("Removing tashkil from the search text...")
            tashkil = ['َ', 'ً', 'ُ', 'ٌ', 'ِ', 'ٍ', 'ْ', 'ّ']
            for char in tashkil:
                search_text = search_text.replace(char, '')
                query = query.replace('AND text', f"AND REPLACE(text, '{char}', '')")
                query = query.replace('REPLACE(text', f"REPLACE(REPLACE(text, '{char}', '')")
        if self.no_hamza:
            # replace all hamzat with 'ا'
            logger.debug("Replacing hamza characters with 'ا'...")
            hamzat = ['أ', 'إ', 'آ', 'ء', 'ؤ']
            for char in hamzat:
                search_text = search_text.replace(char, 'ا')
                # replace all hamzat with 'ا' in the SQL query
                query = query.replace('AND text', f"AND REPLACE(text, '{char}', 'ا')")
                query = query.replace('REPLACE(text', f"REPLACE(REPLACE(text, '{char}', 'ا')")

        logger.debug("Executing query...")
        try:
            self._cursor.execute(query, (self._from, self._to, search_text))
            result = self._cursor.fetchall()
            logger.info(f"Search completed. Found {len(result)} results.")
        except sqlite3.Error as e:
            logger.error(f"Search query execution failed: {e}", exc_info=True)
            return []

        return result


    def __str__(self) -> str:
        return "Quran Search Manager Information:\n" \
            "No Tashkil: {}\n" \
            "No Hamza: {}\n" \
            "Criteria: {}\n" \
            "From: {}\n" \
            "To: {}\n" \
            "From Ayah: {}\n" \
            "To Ayah: {}\n".format(self.no_tashkil, self.no_hamza, self._criteria, self._from, self._to, self._from_ayah, self._to_ayah)

    def __del__(self):
        if self._conn is not None:
            logger.info("Closing database connection...")
            self._conn.close()
            logger.info("Database connection closed.")          


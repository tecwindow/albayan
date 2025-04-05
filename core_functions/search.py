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
        """Initialize the QuranSearchManager class."""
        logger.debug("Initializing QuranSearchManager...")
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
        logger.debug("QuranSearchManager initialized.")

    def set(self, no_tashkil:bool=False, no_hamza:bool=False, match_whole_word:bool=False, criteria:str=None, _from:int=None, _to:int=None, from_ayah:int=None, to_ayah:int=None) -> None:
        """
        Set the parameters for the search.

        :param 
        no_tashkil: If True, ignore tashkil (diacritics) in the search.
        no_hamza: If True, ignore hamza in the search.
        match_whole_word: If True, match the whole word in the search.
        criteria: The criteria for the search (e.g., page, sura_number, hizb, juz, quarter).
        _from: The starting value for the criteria.
        _to: The ending value for the criteria.
        from_ayah: The starting ayah number.
        to_ayah: The ending ayah number.
        """
        logger.debug(f"Setting parameters: no_tashkil={no_tashkil}, no_hamza={no_hamza}, match_whole_word={match_whole_word}, criteria={criteria}, _from={_from}, _to={_to}, from_ayah={from_ayah}, to_ayah={to_ayah}")

        if not  SearchCriteria.is_valid(criteria):
            logger.error(f"Invalid criteria: {criteria}. Must be one of {SearchCriteria.get_arabic_criteria()}.")
            raise InvalidCriteriaError(criteria)

        if self._conn is None:
            logger.error("Database connection is None. Must connect to database first.")
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
        logger.info(f"Parameters set: no_tashkil={self.no_tashkil}, no_hamza={self.no_hamza}, match_whole_word={self.match_whole_word}, criteria={self._criteria}, _from={self._from}, _to={self._to}, from_ayah={self._from_ayah}, to_ayah={self._to_ayah}.")

    def _connect(self):
        """Connect to the Quran database."""
        file_path = os.path.join("database", "quran", 'Verses.DB')
        if not os.path.isfile(file_path):
            logger.error(f"Database file not found: {file_path}")
            raise DBNotFoundError(file_path)
        
        # connect to database
        try:
            logger.debug(f"Connecting to database: {file_path}...")
            self._conn = sqlite3.connect(file_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.create_function("REGEXP", 2, lambda expr, item: re.search(expr, item) is not None)
            self._cursor = self._conn.cursor()
            logger.debug("Database connection established successfully.")
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise DatabaseConnectionError(cause=e)
    
    def search(self, search_text:str) -> list:
        """Search for the given text in the Quran database."""
        logger.debug(f"Starting search with text: '{search_text}'")
        
        if  not isinstance(search_text, str):
            logger.error(f"Invalid search text type: {type(search_text)}. Must be a string.")
            raise InvalidSearchTextError(search_text)

        if not search_text:
            logger.warning("Empty search text provided. Returning None.")
            return None

        if self.match_whole_word:
            operator = "REGEXP"
            search_text = rf"\b{search_text}\b"
            logger.debug(f"Using REGEXP operator for whole word match: {search_text}")
        else:
            operator = "LIKE"
            search_text = f"%{search_text}%"
            logger.debug(f"Using LIKE operator for partial match: {search_text}")

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

        try:
            self._cursor.execute(query, (self._from, self._to, search_text))
            result = self._cursor.fetchall()
            logger.info(f"Search completed. Found {len(result)} results.")
        except sqlite3.Error as e:
            logger.error(f"Search query execution failed: {e}", exc_info=True)
            return []

        return result


    def __str__(self) -> str:
        """Return a string representation of the QuranSearchManager."""
        return "Quran Search Manager Information:\n" \
            "No Tashkil: {}\n" \
            "No Hamza: {}\n" \
            "Criteria: {}\n" \
            "From: {}\n" \
            "To: {}\n" \
            "From Ayah: {}\n" \
            "To Ayah: {}\n".format(self.no_tashkil, self.no_hamza, self._criteria, self._from, self._to, self._from_ayah, self._to_ayah)

    def __del__(self):
        """Destructor for the QuranSearchManager class."""
        logger.debug("Deleting QuranSearchManager object and closing database connection...")
        if self._conn is not None:
            self._conn.close()
            logger.info("Deleted QuranSearchManager object Database connection closed.")          

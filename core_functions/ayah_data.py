import sqlite3
from typing import List, Dict
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class AyahData:
    def __init__(self):
        logger.debug("Initializing AyahData class.")
        self.connect()
        self.create_table()
        logger.debug("AyahData class initialized.")

    def connect(self) -> None:
        """Connect to temporary database to store ayah positions in the text."""
        logger.debug("Connecting to in-memory SQLite database.")
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        logger.info("Connected to in-memory SQLite database.")

    def create_table(self) -> None:
        """Create the table to store ayah data."""
        logger.debug("Creating ayah_data table.")
        self.cursor.execute('''
            CREATE TEMPORARY TABLE IF NOT EXISTS ayah_data (
                ayah_number INTEGER NOT NULL,
                            surah_number INTEGER NOT NULL,
                            ayah_number_in_surah INTEGER NOT NULL,
                first_position INTEGER NOT NULL,
                last_position INTEGER NOT NULL,
                PRIMARY KEY (ayah_number, first_position, last_position)
            )
        ''')
        self.conn.commit()
        logger.info("Table ayah_data created or already exists.")

    def insert(self, ayah_number: int, surah_number: int, ayah_number_in_surah: int, first_position: int, last_position: int):
        """Insert a new ayah into the table."""
        self.cursor.execute('''
            INSERT INTO ayah_data (ayah_number, surah_number, ayah_number_in_surah, first_position, last_position)
            VALUES (?, ?, ?, ?, ?)
        ''', (ayah_number, surah_number, ayah_number_in_surah, first_position, last_position))
        self.conn.commit()
        #logger.debug(f"Inserted ayah number {ayah_number} into the database.")

    def get(self, position: int) -> int:
        """Retrieve ayah number by a specific position."""
        logger.debug(f"Retrieving ayah number for position {position}.")
        self.cursor.execute('''
            SELECT ayah_number FROM ayah_data
            WHERE ? BETWEEN first_position AND last_position
        ''', (position,))        
        result = self.cursor.fetchone()
        
        if result:
            logger.debug(f"Found ayah number {result['ayah_number']} for position {position}.")
            return result['ayah_number']
        else:
            logger.warning(f"No ayah found for position {position}. Trying previous position.")
            if position > 1:
                return self.get(position - 1)
            else:
                logger.error(f"Position {position} is out of range.")
                return None

    def get_position(self, ayah_number: int) -> int:
        """Get position for Specific ayah"""
        logger.debug(f"Retrieving position for ayah number {ayah_number}.")
        self.cursor.execute("SELECT first_position FROM ayah_data WHERE ayah_number = ?;", (ayah_number,))
        result = self.cursor.fetchone()

        if result:
            logger.debug(f"Found first position {result['first_position']} for ayah number {ayah_number}.")
            return result["first_position"]
        else:
            logger.warning(f"No position found for ayah number {ayah_number}.")
            return 0

    def get_ayah_number(self, ayah_number_in_surah: int, surah_number) -> int:
        """Get ayah number by surah number and ayah number in surah."""
        logger.debug(f"Retrieving ayah number for surah number {surah_number}, ayah number in surah {ayah_number_in_surah}.")
        self.cursor.execute("SELECT ayah_number FROM ayah_data WHERE ayah_number_in_surah = ? AND surah_number = ?;", (ayah_number_in_surah, surah_number))
        result = self.cursor.fetchone()

        if result:
            logger.debug(f"Found ayah number {result['ayah_number']} for surah number {surah_number}, ayah number in surah {ayah_number_in_surah}.")
            return result["ayah_number"]
        else:
            logger.warning(f"No ayah found for surah number {surah_number}, ayah number in surah {ayah_number_in_surah}.")
            return None

    def get_ayah_range(self) -> Dict[int, List[sqlite3.Row]]:
        """Fetches the maximum and minimum ayah numbers from the ayah_data table."""
        logger.debug("Fetching maximum and minimum ayah numbers for each surah.")
        self.cursor.execute("""
            SELECT 
                surah_number,
                MAX(ayah_number_in_surah) AS max_ayah,
                MIN(ayah_number_in_surah) AS min_ayah
            FROM ayah_data
            GROUP BY surah_number;
        """)
    
        result = {row["surah_number"]: row for row in self.cursor.fetchall()}
        logger.debug(f"Fetched ayah range: {result}.")
        return result

    def __del__(self):
        """Close the connection when the object is deleted."""
        logger.debug("Deleting AyahData object and closing database connection.")       
        if self.conn:
            self.conn.close()
            logger.info(" Deleted AyahData object Database connection closed.")

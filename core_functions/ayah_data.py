import sqlite3
from typing import List, Dict

class AyahData:
    def __init__(self):
        self.connect()
        self.create_table()
    
    def connect(self) -> None:
        """Connect to temporary database to store ayah positions in the text."""
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_table(self) -> None:
        """Create the table to store ayah data."""
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

    def insert(self, ayah_number: int, surah_number: int, ayah_number_in_surah: int, first_position: int, last_position: int):
        """Insert a new ayah into the table."""

        self.cursor.execute('''
            INSERT INTO ayah_data (ayah_number, surah_number, ayah_number_in_surah, first_position, last_position)
            VALUES (?, ?, ?, ?, ?)
        ''', (ayah_number, surah_number, ayah_number_in_surah, first_position, last_position))
        self.conn.commit()
    
    def get(self, position: int) -> int:
        """Retrieve ayah number by a specific position."""
    
        self.cursor.execute('''
            SELECT ayah_number FROM ayah_data
            WHERE ? BETWEEN first_position AND last_position
        ''', (position,))        
        result = self.cursor.fetchone()
        
        if result:
            return result['ayah_number']
        else:
            if position > 1:
                return self.get(position - 1)
        
    def get_position(self, ayah_number: int) -> int:
        """Get position for Specific ayah"""
        self.cursor.execute("SELECT first_position FROM ayah_data WHERE ayah_number = ?;", (ayah_number,))
        result = self.cursor.fetchone()

        if result:
            return result["first_position"]
        else:
            return 0

    def get_ayah_number(self, ayah_number_in_surah: int, surah_number) -> int:
        """Get ayah number by surah number and ayah number in surah."""
        self.cursor.execute("SELECT ayah_number FROM ayah_data WHERE ayah_number_in_surah = ? AND surah_number = ?;", (ayah_number_in_surah, surah_number))
        result = self.cursor.fetchone()

        if result:
            return result["ayah_number"]
        else:
            return None

    def get_ayah_range(self) -> Dict[int, List[sqlite3.Row]]:
        """Fetches the maximum and minimum ayah numbers from the ayah_data table."""
        self.cursor.execute("""
            SELECT 
                surah_number,
                MAX(ayah_number_in_surah) AS max_ayah,
                MIN(ayah_number_in_surah) AS min_ayah
            FROM ayah_data
            GROUP BY surah_number;
        """)
    
        return {row["surah_number"]: row for row in self.cursor.fetchall()}

    def __del__(self):
        """Close the connection when the object is deleted."""
        if self.conn:
            self.conn.close()

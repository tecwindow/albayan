import sqlite3

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
                first_position INTEGER NOT NULL,
                last_position INTEGER NOT NULL,
                PRIMARY KEY (ayah_number, first_position, last_position)
            )
        ''')
        self.conn.commit()

    def insert(self, ayah_number: int, first_position: int, last_position: int):
        """Insert a new ayah into the table."""

        self.cursor.execute('''
            INSERT INTO ayah_data (ayah_number, first_position, last_position)
            VALUES (?, ?, ?)
        ''', (ayah_number, first_position, last_position))
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
            return None  

    def get_position(self, ayah_number: int) -> int:
        """Get position for Specific ayah"""
        self.cursor.execute("SELECT first_position FROM ayah_data WHERE ayah_number = ?;", (ayah_number,))
        result = self.cursor.fetchone()

        if result:
            return result["first_position"]
        else:
            return 0

    def __del__(self):
        """Close the connection when the object is deleted."""
        if self.conn:
            self.conn.close()

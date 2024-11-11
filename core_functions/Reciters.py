import sqlite3
from typing import List, Optional
from functools import lru_cache

class RecitersManager:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_reciters(self) -> List[sqlite3.Row]:
        """Fetches all reciters from the database."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reciters")
            return cursor.fetchall()

    @lru_cache(maxsize=1)
    def _get_base_url(self, reciter_id: int) -> Optional[str]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM reciters WHERE id = ?", (reciter_id,))
            result = cursor.fetchone()
            if result:
                return result["url"]
        return None

    def get_url(self, reciter_id: int, surah_number: int, aya_number: int) -> Optional[str]:
        base_url = self._get_base_url(reciter_id)
        if base_url:
            return f"{base_url}{surah_number:03}{aya_number:03}.mp3"
        return None
    
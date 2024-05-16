import sqlite3
import os
from abc import ABC, abstractmethod

class Base(ABC):

    def _connect(self, file_path) -> sqlite3.Connection:
        
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"No database found in: {file_path}")

        conn = sqlite3.connect(file_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @property
    @abstractmethod
    def text(self) -> str:
        pass

    def remove_empty_lines(self, text) -> str:
        lines = text.split("\n")
        lines = list(filter(lambda x: x.strip(), lines))
        text = "\n".join(lines)

        return text

    def __del__(self) -> None:
        if self._conn is not None:
            self._conn.close()

        
class E3rab(Base):
    def __init__(self, surah_number: int, ayah_number: int) -> None:
        assert 1 <= surah_number <= 114, "Out of surah number."
        self._surah_number = surah_number
        self._ayah_number = ayah_number
        file_path = os.path.join("database", "other", "e3rab.db")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()

    @property
    def text(self) -> str:
        sql = f"SELECT text FROM e3rab_{self._surah_number} WHERE number = ?;"
        self.cursor.execute(sql, (self._ayah_number,))
        result = self.cursor.fetchone()

        if result:
            return self.remove_empty_lines(result["text"])
        else:
            return ""


class TanzilAyah(Base):
    def __init__(self, ayah_number:int) -> None:
        self._ayah_number = ayah_number
        file_path = os.path.join("database", "other", "tanzil.db")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()

    @property
    def text(self) -> str:
        sql = "SELECT text FROM tanzil WHERE number = ?;"
        self.cursor.execute(sql, (self._ayah_number,))
        result = self.cursor.fetchone()

        if result:
            return self.remove_empty_lines(result["text"])
        else:
            return ""

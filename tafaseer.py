import sqlite3
import os

class Category:
    baghawy = "baghawy"
    jalalayn = "jalalayn"
    katheer = "katheer"
    muyassar = "muyassar"
    qortoby = "qortoby"
    sa3dy = "sa3dy"
    tabary = "tabary"

    @classmethod
    def is_valid(cls, category: str) -> bool:
        return category in [cls.baghawy, cls.jalalayn, cls.katheer, cls.muyassar, cls.qortoby, cls.sa3dy, cls.tabary]


class TafaseerManager:
    def __init__(self) -> None:
        self._tafaseer_category = None
        self._conn = None  

    def set(self, tafaseer_category: str) -> None:
        assert Category.is_valid(tafaseer_category), "Invalid tafaseer category."
        self._tafaseer_category = tafaseer_category
        self._connect_to_database()

    def _connect_to_database(self) -> None:
        assert self._tafaseer_category is not None, "You must set tafaseer category."
        file_path = os.path.join("database", "tafaseer", self._tafaseer_category + ".db")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"There's no file: {self._tafaseer_category}.db")
        self._conn = sqlite3.connect(file_path)
        self._conn.row_factory = sqlite3.Row 
        self._cursor = self._conn.cursor()

    def get_tafaseer(self, surah_number, ayah_number) -> str:
        assert self._conn is not None, "You must connect to database first."
        assert 1 <= surah_number <= 114, "Out of surah range."
        assert 1 <= ayah_number, "Out of ayah range."
        query = "SELECT text FROM tafsir_{} WHERE number = ?".format(surah_number)
        self._cursor.execute(query, [ayah_number])
        result = self._cursor.fetchone()
        if result:
            return result["text"]
        else:
            return ""

    def __str__(self) -> str:
        return "Category: {}".format(self._tafaseer_category)

    def __del__(self):
        if self._conn:
            self._conn.close()


tafaseer_manager = TafaseerManager()
tafaseer_manager.set(Category.baghawy)
result = tafaseer_manager.get_tafaseer(1, 2)
print(result)
import sqlite3
import os
from exceptions.database import DBNotFoundError

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
            raise DBNotFoundError(file_path)
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

        return self.get_text(result)

    def get_text(self, row) -> str:

        if row:
                    text = row["text"].replace(".", ". \n").strip()
        else:
            return ""

        # Remove empty lines.
        lines = text.split("\n")
        lines = list(filter(lambda x: x.strip(), lines))
        text = "\n".join(lines)

        return text


    def __str__(self) -> str:
        return "Category: {}".format(self._tafaseer_category)

    def __del__(self):
        if self._conn:
            self._conn.close()


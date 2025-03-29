import sqlite3
import json
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
    def __init__(self, ayah_number: int) -> None:
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


class AyaInfo(Base):
    def __init__(self, ayah_number: int) -> None:
        self._ayah_number = ayah_number
        file_path = os.path.join("database", "quran", "quran.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()

    @property
    def text(self) -> str:

        sql = """
        SELECT 
        number,
        sura_name,
        sura_number,
          numberInSurah,
          juz,
          hizb, 
          page,
          hizbQuarter,
        CASE 
            WHEN sajda = 1 THEN 'نعم'
            ELSE 'لا'
        END AS sajda,
        CASE 
            WHEN sajdaObligation = 1 THEN 'نعم'
            ELSE 'لا'
        END AS sajdaObligation
        FROM quran 
        WHERE number = ?;
        """

        self.cursor.execute(sql, (self._ayah_number,))
        result = self.cursor.fetchone()

        if result:
            return self.format_text(result)
        else:
            return ""

    @staticmethod
    def format_text(result: dict) -> str:
        text = """|
        <ul>
            <li><strong>رقم الآية:</strong> {}.</li>
            <li><strong>رقم الآية في المصحف:</strong> {}.</li>
            <li><strong>السورة:</strong> {}.</li>
            <li><strong>رقم السورة:</strong> {}.</li>
            <li><strong>رقم الصفحة:</strong> {}.</li>
            <li><strong>رقم الجزء:</strong> {}.</li>
            <li><strong>رقم الحزب:</strong> {}.</li>
            <li><strong>رقم الربع:</strong> {}.</li>
            <li><strong>سجدة:</strong> {}.</li>
            <li><strong>سجدة واجبة:</strong> {}.</li>
        </ul>
        """.format(result["numberInSurah"], result["number"], result["sura_name"], result["sura_number"], result["page"], result["juz"], result["hizb"], result["hizbQuarter"], result["sajda"], result["sajdaObligation"])

        return text

    
class SuraInfo(Base):
    def __init__(self, surah_number: int) -> None:
        assert 1 <= surah_number <= 114, "Out of surah number."
        self._surah_number = surah_number
        file_path = os.path.join("database", "other", "quran_info.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()

    @property
    def text(self) -> str:
        self.cursor.execute("SELECT sura_number, info FROM surah_info WHERE sura_number = ?", (self._surah_number,))
        result = self.cursor.fetchone()

        if result and result[0]:
            info =  json.loads(result["info"])
            info["sura_number"] = result["sura_number"]
            text = self._format(info)
        else:
            text = ""
        
        return text

    def _format(self, data: dict) -> str:

        arabic_labels = {
            "name": "اسم السورة",
            "sura_number": "رقم السورة",
            "english_name": "الاسم بالإنجليزية",
            "revelationType": "نوع السورة",
            "numberOfAyahs": "عدد الآيات",
            "firstAyahNumber": "رقم أول آية في المصحف",
            "lastAyahNumber": "رقم آخر آية في المصحف",
            "start_page": "تبدأ في الصفحة",
            "end_page": "تنتهي في الصفحة",
            "start_hizb": "تبدأ في الحزب",
            "end_hizb": "تنتهي في الحزب",
            "start_juz": "تبدأ في الجزء",
            "end_juz": "تنتهي في الجزء",
            "start_hizb_quarter": "تبدأ في الربع",
            "end_hizb_quarter": "تنتهي في الربع"
        }
        
        text = "<ul>\n"
        for key, label in arabic_labels.items():
            value = data.get(key, "غير متوفر")
            text += f"<li><strong>{label}:</strong> {value}.</li>\n"

        return text + "</ul>"


class JuzInfo(Base):
    def __init__(self, juz_number: int) -> None:
        """Initialize with a specific Juz number"""
        assert 1 <= juz_number <= 30, "❌ Juz number must be between 1 and 30."
        self._juz_number = juz_number
        file_path = os.path.join("database", "quran", "quran.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()

    @property
    def text(self) -> str:

        query = """ 
        SELECT 
            juz AS juz_number,
            MIN(page) AS start_page,
            MAX(page) AS end_page,
            MIN(hizb) AS start_hizb,
            MAX(hizb) AS end_hizb,
            MIN(hizbQuarter) AS start_hizbQuarter,
            MAX(hizbQuarter) AS end_hizbQuarter,
            COUNT(DISTINCT sura_number) AS count_surahs,
            COUNT(number) AS count_ayahs,
            (SELECT numberInSurah FROM quran q2 WHERE q2.juz = q1.juz ORDER BY number LIMIT 1) AS start_ayah_number,
            (SELECT numberInSurah FROM quran q3 WHERE q3.juz = q1.juz ORDER BY number DESC LIMIT 1) AS end_ayah_number,
            (SELECT sura_name FROM quran q4 WHERE q4.juz = q1.juz ORDER BY number LIMIT 1) AS start_sura_name,
            (SELECT sura_name FROM quran q5 WHERE q5.juz = q1.juz ORDER BY number DESC LIMIT 1) AS end_sura_name,
            (SELECT GROUP_CONCAT(REPLACE(sura_name, 'سورة ', ''), ', ') FROM (SELECT DISTINCT sura_name FROM quran WHERE juz = q1.juz)) AS surah_names
        FROM quran q1
        WHERE juz = ?
        GROUP BY juz;
        """

        self.cursor.execute(query, (self._juz_number,))
        result = self.cursor.fetchone()

        if result:
            return self._format(dict(result))
        else:
            return ""

    def _format(self, data: dict) -> str:

        text = f"""
رقم الجزء: {data["juz_number"]}.
        يبدأ الجزء {data["juz_number"]} من الآية {data["start_ayah_number"]} في {data["start_sura_name"]}.
ينتهي الجزء في الآية {data["end_ayah_number"]} من {data["end_sura_name"]}.
يبدأ من الصفحة {data["start_page"]} وينتهي في الصفحة {data["end_page"]}.
يبدأ في الربع {data["start_hizbQuarter"]} وينتهي في الربع {data["end_hizbQuarter"]}.
يبدأ في الحزب {data["start_hizb"]} وينتهي في الحزب {data["end_hizb"]}.
عدد السور في الجزء: {data["count_surahs"]}.
عدد الآيات في الجزء: {data["count_ayahs"]}.
السور الموجودة في الجزء: {data["surah_names"]}.
"""

        return text.strip()


class HizbInfo(Base):
    def __init__(self, hizb_number: int) -> None:
        assert 1 <= hizb_number <= 60, "❌ Hizb number must be between 1 and 60."
        self._hizb_number = hizb_number
        file_path = os.path.join("database", "quran", "quran.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()

    @property
    def text(self) -> str:

        query = """ 
        SELECT 
            hizb AS hizb_number,
            CASE 
                WHEN (hizb % 2) = 1 THEN 'الأول' 
                ELSE 'الثاني' 
            END AS hizb_order_in_juz,
            MIN(juz) AS juz,
            MIN(page) AS start_page,
            MAX(page) end_page,
            MIN(hizbQuarter) AS start_hizbQuarter,
            MAX(hizbQuarter) AS end_hizbQuarter,
            COUNT(DISTINCT sura_number) AS count_surahs,
            COUNT(number) AS count_ayahs,
            (SELECT numberInSurah FROM quran WHERE hizb = q1.hizb ORDER BY number LIMIT 1) AS start_ayah_number,
            (SELECT numberInSurah FROM quran WHERE hizb = q1.hizb ORDER BY number DESC LIMIT 1) AS end_ayah_number,
            (SELECT sura_name FROM quran WHERE hizb = q1.hizb ORDER BY number LIMIT 1) AS start_sura_name,
            (SELECT sura_name FROM quran WHERE hizb = q1.hizb ORDER BY number DESC LIMIT 1) AS end_sura_name,
            (SELECT GROUP_CONCAT(REPLACE(sura_name, 'سورة ', ''), ', ') FROM (SELECT DISTINCT sura_name FROM quran WHERE hizb = q1.hizb)) AS surah_names
        FROM quran q1
        WHERE hizb = ?
        GROUP BY hizb;
        """

        self.cursor.execute(query, (self._hizb_number,))
        result = self.cursor.fetchone()

        if result:
            return self._format(dict(result))
        else:
            return ""

    def _format(self, data: dict) -> str:

        text = f"""
رقم الحزب: {data["hizb_number"]}.
        يبدأ الحزب {data["hizb_number"]} من الآية {data["start_ayah_number"]} في {data["start_sura_name"]}.
ينتهي الحزب في الآية {data["end_ayah_number"]} من {data["end_sura_name"]}.
موضع الحزب في الجزء: الحزب {data["hizb_order_in_juz"]} من الجزء {data["juz"]}.
موضع الحزب في المصحف:
يبدأ من الصفحة {data["start_page"]} وينتهي في الصفحة {data["end_page"]}.
يبدأ في الربع {data["start_hizbQuarter"]} وينتهي في الربع {data["end_hizbQuarter"]}.
عدد السور في الحزب: {data["count_surahs"]}.
عدد الآيات في الحزب: {data["count_ayahs"]}.
السور الموجودة في الحزب: {data["surah_names"]}.
"""

        return text.strip()
    
    
class QuarterInfo(Base):
    def __init__(self, quarter_number: int) -> None:
        assert 1 <= quarter_number <= 240, "❌ Quarter number must be between 1 and 240."
        self._quarter_number = quarter_number
        file_path = os.path.join("database", "quran", "quran.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()

    @property
    def text(self) -> str:

        query = """ 
        SELECT 
            hizbQuarter AS quarter_number,
            CASE 
                WHEN hizbQuarter % 4 = 1 THEN 'الأول'
                WHEN hizbQuarter % 4 = 2 THEN 'الثاني'
                WHEN hizbQuarter % 4 = 3 THEN 'الثالث'
                ELSE 'الرابع'
            END AS quarter_order_in_hizb,
            MIN(hizb) AS hizb,
            MIN(page) AS start_page,
            MAX(page) AS end_page,
            COUNT(DISTINCT sura_number) AS count_surahs,
            COUNT(number) AS count_ayahs,
            (SELECT numberInSurah FROM quran WHERE hizbQuarter = q1.hizbQuarter ORDER BY number LIMIT 1) AS start_ayah_number,
            (SELECT numberInSurah FROM quran WHERE hizbQuarter = q1.hizbQuarter ORDER BY number DESC LIMIT 1) AS end_ayah_number,
            (SELECT sura_name FROM quran WHERE hizbQuarter = q1.hizbQuarter ORDER BY number LIMIT 1) AS start_sura_name,
            (SELECT sura_name FROM quran WHERE hizbQuarter = q1.hizbQuarter ORDER BY number DESC LIMIT 1) AS end_sura_name,
            (SELECT GROUP_CONCAT(REPLACE(sura_name, 'سورة ', ''), ', ') FROM (SELECT DISTINCT sura_name FROM quran WHERE hizbQuarter = q1.hizbQuarter)) AS surah_names
        FROM quran q1
        WHERE hizbQuarter = ?
        GROUP BY hizbQuarter;
        """

        self.cursor.execute(query, (self._quarter_number,))
        result = self.cursor.fetchone()

        if result:
            return self._format(dict(result))
        else:
            return ""

    def _format(self, data: dict) -> str:

        text = f"""
رقم الربع: {data["quarter_number"]}.
        يبدأ الربع {data["quarter_number"]} من الآية {data["start_ayah_number"]} في {data["start_sura_name"]}.
ينتهي الربع في الآية {data["end_ayah_number"]} من {data["end_sura_name"]}.
موضع الربع في الجزء: الربع {data["quarter_order_in_hizb"]} من الحزب {data["hizb"]} في الجزء .
موضع الربع في المصحف:
يبدأ من الصفحة {data["start_page"]} وينتهي في الصفحة {data["end_page"]}.
عدد السور في الربع: {data["count_surahs"]}.
عدد الآيات في الربع: {data["count_ayahs"]}.
السور الموجودة في الربع: {data["surah_names"]}.
"""

        return text.strip()

class PageInfo(Base):
    def __init__(self, page_number: int) -> None:
        assert 1 <= page_number <= 604, "❌ Page number must be between 1 and 604."
        self._page_number = page_number
        file_path = os.path.join("database", "quran", "quran.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()

    @property
    def text(self) -> str:
        
        query = """ 
        SELECT 
            page AS page_number,
            MIN(juz) AS juz_number,
            MIN(hizb) AS hizb_number,
            MIN(hizbQuarter) AS quarter_number,
            COUNT(DISTINCT sura_number) AS count_surahs,
            COUNT(number) AS count_ayahs,
            (SELECT numberInSurah FROM quran WHERE page = q1.page ORDER BY number LIMIT 1) AS start_ayah_number,
            (SELECT numberInSurah FROM quran WHERE page = q1.page ORDER BY number DESC LIMIT 1) AS end_ayah_number,
            (SELECT sura_name FROM quran WHERE page = q1.page ORDER BY number LIMIT 1) AS start_sura_name,
            (SELECT sura_name FROM quran WHERE page = q1.page ORDER BY number DESC LIMIT 1) AS end_sura_name,
            (SELECT GROUP_CONCAT(REPLACE(sura_name, 'سورة ', ''), ', ') FROM (SELECT DISTINCT sura_name FROM quran WHERE page = q1.page)) AS surah_names
        FROM quran q1
        WHERE page = ?
        GROUP BY page;
        """

        self.cursor.execute(query, (self._page_number,))
        result = self.cursor.fetchone()

        if result:
            return self._format(dict(result))
        else:
            return ""

    def _format(self, data: dict) -> str:

        text = f"""
رقم الصفحة:{data["page_number"]}.
توجد في الجزء: {data["juz_number"]}.
توجد في الحزب: {data["hizb_number"]}.
توجد في الربع: {data["quarter_number"]}.
تبدأ الصفحة بالآية {data["start_ayah_number"]} من {data["start_sura_name"]}.
تنتهي الصفحة بالآية {data["end_ayah_number"]} من {data["end_sura_name"]}.
 عدد السور في الصفحة: {data["count_surahs"]}.
عدد الآيات في الصفحة: {data["count_ayahs"]}.
السور الموجودة في الصفحة: {data["surah_names"]}.
"""

        return text.strip()


class MoshafInfo(Base):
    MECCAN_COUNT = 86
    MEDINAN_COUNT = 28

    def __init__(self) -> None:
        file_path = os.path.join("database", "quran", "quran.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()

    @property
    def text(self) -> str:

        query = """ 
        SELECT 
            COUNT(DISTINCT sura_number) AS total_surahs,
            COUNT(number) AS total_ayahs,
            COUNT(DISTINCT juz) AS total_juz,
            COUNT(DISTINCT hizb) AS total_hizb,
            COUNT(DISTINCT hizbQuarter) AS total_hizb_quarters,
            COUNT(DISTINCT page) AS total_pages
        FROM quran;
        """
        
        self.cursor.execute(query)
        result = self.cursor.fetchone()

        if result:
            return self._format(dict(result))
        else:
            return "⚠️ لم يتم العثور على بيانات."

    def _format(self, data: dict) -> str:

        text = f"""
معلومات عامة عن المصحف:
 عدد السور: {data["total_surahs"]} سورة.
عدد السور المكية: {self.MECCAN_COUNT} سورة.
عدد السور المدنية: {self.MEDINAN_COUNT} سورة.
عدد الآيات: {data["total_ayahs"]} آية.
عدد الأجزاء: {data["total_juz"]} جزء.
- عدد الأحزاب: {data["total_hizb"]} حزب 
عدد الأرباع: {data["total_hizb_quarters"]} ربع.
عدد الصفحات: {data["total_pages"]} صفحة.
"""

        return text.strip()


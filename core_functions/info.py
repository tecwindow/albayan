import sqlite3
import json
import os
from abc import ABC, abstractmethod
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class Base(ABC):
    
    def _connect(self, file_path) -> sqlite3.Connection:
        """Connect to the SQLite database and return the connection object."""
        logger.debug(f"Connecting to the database: {file_path}, in instance of {self.__class__.__name__}")
        
        if not os.path.isfile(file_path):
            logger.error(f"No database found in: {file_path}")
            raise FileNotFoundError(f"No database found in: {file_path}")

        conn = sqlite3.connect(file_path)
        conn.row_factory = sqlite3.Row
        logger.info(f"Connected to the database successfully: {file_path}, in instance of {self.__class__.__name__}")
        return conn
    
    @property
    @abstractmethod
    def text(self) -> str:
        pass

    def remove_empty_lines(self, text) -> str:
        """Remove empty lines from the provided text."""
        logger.debug("Removing empty lines from the provided text.")
        lines = text.split("\n")
        lines = list(filter(lambda x: x.strip(), lines))
        text = "\n".join(lines)
        logger.debug(f"Removed empty lines, new text length: {len(text)}.")
        return text

    def __del__(self) -> None:
        """Destructor to close the database connection."""
        logger.debug(f"Deleting {self.__class__.__name__} object and closing database.")
        if self._conn is not None:
            self._conn.close()
            logger.info(f"Deleted {self.__class__.__name__} object and Database connection closed.")
        
class E3rab(Base):
    def __init__(self, surah_number: int, ayah_number: int) -> None:
        logger.debug(f"Initializing E3rab with surah: {surah_number}, ayah: {ayah_number}.")
        assert 1 <= surah_number <= 114, "Out of surah number."
        self._surah_number = surah_number
        self._ayah_number = ayah_number
        file_path = os.path.join("database", "other", "e3rab.db")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()
        logger.debug(f"Initialized E3rab successfully with surah: {surah_number}, ayah: {ayah_number}.")

    @property
    def text(self) -> str:
        """Fetch the E3rab text for the specified Ayah number."""
        logger.debug(f"Fetching E3rab for {self._surah_number}, Ayah {self._ayah_number}.")
        
        query = f"SELECT text FROM e3rab_{self._surah_number} WHERE number = ?;"
        self.cursor.execute(query, (self._ayah_number,))
        result = self.cursor.fetchone()

        if result:
            logger.debug(f"E3rab found for Surah {self._surah_number}, Ayah {self._ayah_number}.")
            return self.remove_empty_lines(result["text"])
        else:
            logger.warning(f"No E3rab found for Surah {self._surah_number}, Ayah {self._ayah_number}. Returning empty string.")
            return ""


class TanzilAyah(Base):
    def __init__(self, ayah_number: int) -> None:
        logger.debug(f"Initializing TanzilAyah with Ayah {ayah_number}.")
        self._ayah_number = ayah_number
        file_path = os.path.join("database", "other", "tanzil.db")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()
        logger.debug(f"Initialized TanzilAyah successfully with Ayah {ayah_number}.")

    @property
    def text(self) -> str:
        """Fetch the tanzilAyah text for the specified Ayah number from the Tanzil database."""
        logger.debug(f"Fetching tanzilAyah for Ayah {self._ayah_number} from Tanzil database.")
        
        query = "SELECT text FROM tanzil WHERE number = ?;"
        self.cursor.execute(query, (self._ayah_number,))
        result = self.cursor.fetchone()

        if result:
            logger.debug(f"TanzilAyah found for Ayah {self._ayah_number}.")
            return self.remove_empty_lines(result["text"])
        else:
            logger.warning(f"No text found for Ayah {self._ayah_number}. Returning empty string.")
            return ""


class AyaInfo(Base):
    def __init__(self, ayah_number: int) -> None:
        logger.debug(f"Initializing AyaInfo with Ayah {ayah_number}.")
        self._ayah_number = ayah_number
        file_path = os.path.join("database", "quran", "quran.DB")
        
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()
        logger.debug(f"Initialized AyaInfo successfully with Ayah {ayah_number}.")


    @property
    def text(self) -> str:
        """Fetch the Aya information for the specified Ayah number."""
        logger.debug(f"Fetching Aya information for Ayah {self._ayah_number}.")
        
        query = """
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

        self.cursor.execute(query, (self._ayah_number,))
        result = self.cursor.fetchone()

        if result:
            logger.debug(f"Aya information found for Ayah {self._ayah_number}.")
            return self.format_text(result)
        else:
            logger.warning(f"No information found for Ayah {self._ayah_number}. Returning empty string.")
            return ""

    @staticmethod
    def format_text(result: dict) -> str:
        """Format the Aya information into a readable string."""
        logger.debug(f"Formatting Aya information for Ayah {result['numberInSurah']}.")
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
        logger.debug(f"Aya information formatted successfully.")

        return text
        
    
class SuraInfo(Base):
    def __init__(self, surah_number: int) -> None:
        logger.debug(f"Initializing SuraInfo for Surah {surah_number}.")
        assert 1 <= surah_number <= 114, "Out of surah number."
        self._surah_number = surah_number
        file_path = os.path.join("database", "other", "quran_info.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()
        logger.debug(f"Initialized SuraInfo successfully for Surah {surah_number}.")

    @property
    def text(self) -> str:
        """Fetch the Surah information for the specified Surah number."""
        logger.debug(f"Fetching information for Surah {self._surah_number}.")
        
        self.cursor.execute("SELECT sura_number, info FROM surah_info WHERE sura_number = ?", (self._surah_number,))
        result = self.cursor.fetchone()

        if result and result[0]:
            info =  json.loads(result["info"])
            info["sura_number"] = result["sura_number"]
            text = self._format(info)
            logger.debug(f"Information fetched successfully for Surah {self._surah_number}.")
        else:
            logger.warning(f"No information found for Surah {self._surah_number}. Returning empty string.")
            text = ""
        
        return text

    def _format(self, data: dict) -> str:
        """Format the Surah information into a readable string."""
        logger.debug(f"Formatting information for Surah {data.get('name', 'Unknown')}.")

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

        logger.debug(f"Formatted information for Surah {data.get('name', 'Unknown')}.")
        return text + "</ul>"


class JuzInfo(Base):
    def __init__(self, juz_number: int) -> None:
        """Initialize with a specific Juz number"""
        logger.debug(f"Initializing JuzInfo for Juz {juz_number}.")
        assert 1 <= juz_number <= 30, "❌ Juz number must be between 1 and 30."
        self._juz_number = juz_number
        file_path = os.path.join("database", "quran", "quran.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()
        logger.debug(f"Initialized JuzInfo successfully for Juz {juz_number}.")

    @property
    def text(self) -> str:
        """Fetch the Juz information for the specified Juz number."""
        logger.debug(f"Fetching information for Juz {self._juz_number}.")
        
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
            logger.debug(f"Information fetched successfully for Juz {self._juz_number}.")
            return self._format(dict(result))
        else:
            logger.warning(f"No information found for Juz {self._juz_number}. Returning empty string.")
            return ""

    def _format(self, data: dict) -> str:
        """Format the Juz information into a readable string."""
        logger.debug(f"Formatting information for Juz {data['juz_number']}.")
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
        logger.debug(f"Formatted information for Juz {data['juz_number']}.")
        return text.strip()


class HizbInfo(Base):
    def __init__(self, hizb_number: int) -> None:
        """Initialize with a specific Hizb number"""
        logger.debug(f"Initializing HizbInfo for Hizb {hizb_number}.")
        assert 1 <= hizb_number <= 60, "❌ Hizb number must be between 1 and 60."
        self._hizb_number = hizb_number
        file_path = os.path.join("database", "quran", "quran.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()
        logger.debug(f"Initialized HizbInfo successfully for Hizb {hizb_number}.")

    @property
    def text(self) -> str:
        """Fetch the Hizb information for the specified Hizb number."""
        logger.debug(f"Fetching information for Hizb {self._hizb_number}.")

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
            logger.debug(f"Information fetched successfully for Hizb {self._hizb_number}.")
            return self._format(dict(result))
        else:
            logger.warning(f"No information found for Hizb {self._hizb_number}. Returning empty string.")
            return ""

    def _format(self, data: dict) -> str:
        """Format the Hizb information into a readable string."""
        logger.debug(f"Formatting information for Hizb {data['hizb_number']}.")
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
        logger.debug(f"Formatted information for Hizb {data['hizb_number']}.")
        return text.strip()
    
    
class QuarterInfo(Base):
    def __init__(self, quarter_number: int) -> None:
        """Initialize with a specific Quarter number"""
        logger.debug(f"Initializing QuarterInfo for Quarter {quarter_number}.")
        assert 1 <= quarter_number <= 240, "❌ Quarter number must be between 1 and 240."
        self._quarter_number = quarter_number
        file_path = os.path.join("database", "quran", "quran.DB")        
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()
        logger.info(f"Initialized QuarterInfo successfully for Quarter {quarter_number}.")

    @property
    def text(self) -> str:
        """Fetch the Quarter information for the specified Quarter number."""
        logger.debug(f"Fetching information for Quarter {self._quarter_number}.")
        
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
            logger.debug(f"Information fetched successfully for Quarter {self._quarter_number}.")
            return self._format(dict(result))
        else:
            logger.warning(f"No information found for Quarter {self._quarter_number}. Returning empty string.")
            return ""

    def _format(self, data: dict) -> str:
        """Format the Quarter information into a readable string."""
        logger.debug(f"Formatting information for Quarter {data['quarter_number']}.")
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
        logger.debug(f"Formatted information for Quarter {data['quarter_number']}.")
        return text.strip()

class PageInfo(Base):
    def __init__(self, page_number: int) -> None:
        """Initialize with a specific Page number"""
        logger.debug(f"Initializing PageInfo for Page {page_number}.")
        assert 1 <= page_number <= 604, "❌ Page number must be between 1 and 604."
        self._page_number = page_number
        file_path = os.path.join("database", "quran", "quran.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()
        logger.debug(f"Initialized PageInfo successfully for Page {page_number}.")

    @property
    def text(self) -> str:
        """Fetch the Page information for the specified Page number."""
        logger.debug(f"Fetching information for Page {self._page_number}.")
        
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
            logger.debug(f"Information fetched successfully for Page {self._page_number}.")
            return self._format(dict(result))
        else:
            logger.warning(f"No information found for Page {self._page_number}. Returning empty string.")
            return ""

    def _format(self, data: dict) -> str:
        """Format the Page information into a readable string."""
        logger.debug(f"Formatting information for Page {data['page_number']}.")
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
        logger.debug(f"Formatted information for Page {data['page_number']}.")
        return text.strip()


class MoshafInfo(Base):
    MECCAN_COUNT = 86
    MEDINAN_COUNT = 28

    def __init__(self) -> None:
        """Initialize the MoshafInfo class."""
        logger.debug(f"Initializing MoshafInfo.")
        file_path = os.path.join("database", "quran", "quran.DB")
        self._conn = self._connect(file_path)
        self.cursor = self._conn.cursor()
        logger.debug(f"Initialized MoshafInfo successfully.")

    @property
    def text(self) -> str:
        """Fetch general information about the Quran."""
        logger.debug("Fetching general information about the Quran.")
        
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
            logger.debug("General information about the Quran fetched successfully.")
            return self._format(dict(result))
        else:
            logger.warning("No general information found about the Quran.")
            return "⚠️ لم يتم العثور على بيانات."

    def _format(self, data: dict) -> str:
        """Format the general information into a readable string."""
        logger.debug("Formatting general information about the Quran.")
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
        logger.debug("General information about the Quran formatted successfully.")
        return text.strip()


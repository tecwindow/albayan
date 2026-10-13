import sqlite3
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from exceptions.database import DBNotFoundError
from utils.paths import paths
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

DEFAULT_BUNDLED_TAFSIR_ID = "muyassar"

PRIMARY_TAFASEER_BASE_URL = "https://albayan.tecwindow.net/tafaseer"
BACKUP_GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/tecwindow/albayan-data/main/tafaseer"
BACKUP_GITHUB_RELEASE_BASE_URL = "https://github.com/tecwindow/albayan-data/releases/download/v1.0"

TAFASEER_CATALOG: Dict[str, Dict[str, Any]] = {
    "muyassar": {
        "id": "muyassar",
        "arabic_name": "الميسر",
        "full_name": "التفسير الميسر",
        "author": "نخبة من العلماء - مجمع الملك فهد لطباعة المصحف الشريف",
        "description": "تفسير ميسر وسلس وموثوق تم إعداده بإشراف مجمع الملك فهد لطباعة المصحف الشريف.",
        "db_filename": "muyassar.db",
        "zip_filename": "muyassar.zip",
        "approx_size_mb": 3.24,
        "download_size_mb": 0.63,
        "is_bundled_default": True,
        "mirrors": [
            f"{PRIMARY_TAFASEER_BASE_URL}/muyassar.zip",
            f"{BACKUP_GITHUB_RAW_BASE_URL}/muyassar.zip",
            f"{BACKUP_GITHUB_RELEASE_BASE_URL}/muyassar.zip",
        ],
    },
    "mukhtasar": {
        "id": "mukhtasar",
        "arabic_name": "المختصر في التفسير",
        "full_name": "المختصر في تفسير القرآن الكريم",
        "author": "مركز تفسير للدراسات القرآنية",
        "description": "كتاب متميز ومحرر أصدره مركز تفسير للدراسات القرآنية، يتميز بوضوح العبارة وذكر مقاصد السور.",
        "db_filename": "mukhtasar.db",
        "zip_filename": "mukhtasar.zip",
        "approx_size_mb": 2.58,
        "download_size_mb": 0.61,
        "is_bundled_default": False,
        "mirrors": [
            f"{PRIMARY_TAFASEER_BASE_URL}/mukhtasar.zip",
            f"{BACKUP_GITHUB_RAW_BASE_URL}/mukhtasar.zip",
            f"{BACKUP_GITHUB_RELEASE_BASE_URL}/mukhtasar.zip",
        ],
    },
    "sa3dy": {
        "id": "sa3dy",
        "arabic_name": "السعدي",
        "full_name": "تيسير الكريم الرحمن في تفسير كلام المنان",
        "author": "الشيخ عبد الرحمن بن ناصر السعدي",
        "description": "من أسهل التفاسير وأكثرها تركيزاً على المعنى الإجمالي وتهذيب الأخلاق والتدبر الإيماني.",
        "db_filename": "sa3dy.db",
        "zip_filename": "sa3dy.zip",
        "approx_size_mb": 7.98,
        "download_size_mb": 1.75,
        "is_bundled_default": False,
        "mirrors": [
            f"{PRIMARY_TAFASEER_BASE_URL}/sa3dy.zip",
            f"{BACKUP_GITHUB_RAW_BASE_URL}/sa3dy.zip",
            f"{BACKUP_GITHUB_RELEASE_BASE_URL}/sa3dy.zip",
        ],
    },
    "baghawy": {
        "id": "baghawy",
        "arabic_name": "البغوي",
        "full_name": "معالم التنزيل في تفسير القرآن",
        "author": "الإمام الحسين بن مسعود البغوي",
        "description": "تفسير أثري جليل ينقل الآثار عن السلف مع اعتناء خاص بصحة الروايات وتجنب الإسرائيليات الضعيفة.",
        "db_filename": "baghawy.db",
        "zip_filename": "baghawy.zip",
        "approx_size_mb": 8.96,
        "download_size_mb": 2.03,
        "is_bundled_default": False,
        "mirrors": [
            f"{PRIMARY_TAFASEER_BASE_URL}/baghawy.zip",
            f"{BACKUP_GITHUB_RAW_BASE_URL}/baghawy.zip",
            f"{BACKUP_GITHUB_RELEASE_BASE_URL}/baghawy.zip",
        ],
    },
    "katheer": {
        "id": "katheer",
        "arabic_name": "ابن كثير",
        "full_name": "تفسير القرآن العظيم",
        "author": "الإمام الحافظ إسماعيل بن عمر بن كثير",
        "description": "من أشهر التفاسير بالمأثور، يفسر القرآن بالقرآن ثم بالسنة النبوية وأقوال الصحابة والتابعين.",
        "db_filename": "katheer.db",
        "zip_filename": "katheer.zip",
        "approx_size_mb": 16.16,
        "download_size_mb": 3.34,
        "is_bundled_default": False,
        "mirrors": [
            f"{PRIMARY_TAFASEER_BASE_URL}/katheer.zip",
            f"{BACKUP_GITHUB_RAW_BASE_URL}/katheer.zip",
            f"{BACKUP_GITHUB_RELEASE_BASE_URL}/katheer.zip",
        ],
    },
    "qortoby": {
        "id": "qortoby",
        "arabic_name": "القرطبي",
        "full_name": "الجامع لأحكام القرآن",
        "author": "الإمام أبو عبد الله محمد بن أحمد القرطبي",
        "description": "موسوعة جامعة في التفسير واستنباط الأحكام الفقهية مع الاستشهاد بمسائل اللغة والقراءات.",
        "db_filename": "qortoby.db",
        "zip_filename": "qortoby.zip",
        "approx_size_mb": 22.52,
        "download_size_mb": 5.38,
        "is_bundled_default": False,
        "mirrors": [
            f"{PRIMARY_TAFASEER_BASE_URL}/qortoby.zip",
            f"{BACKUP_GITHUB_RAW_BASE_URL}/qortoby.zip",
            f"{BACKUP_GITHUB_RELEASE_BASE_URL}/qortoby.zip",
        ],
    },
    "tabary": {
        "id": "tabary",
        "arabic_name": "الطبري",
        "full_name": "جامع البيان عن تأويل آي القرآن",
        "author": "الإمام أبو جعفر محمد بن جرير الطبري",
        "description": "إمام المفسرين وأعظم كتب التفسير بالمأثور وأقدمها، يجمع الروايات بأسانيدها ويوجه الأقوال.",
        "db_filename": "tabary.db",
        "zip_filename": "tabary.zip",
        "approx_size_mb": 36.90,
        "download_size_mb": 7.69,
        "is_bundled_default": False,
        "mirrors": [
            f"{PRIMARY_TAFASEER_BASE_URL}/tabary.zip",
            f"{BACKUP_GITHUB_RAW_BASE_URL}/tabary.zip",
            f"{BACKUP_GITHUB_RELEASE_BASE_URL}/tabary.zip",
        ],
    },
    "jalalayn": {
        "id": "jalalayn",
        "arabic_name": "الجلالين",
        "full_name": "تفسير الجلالين",
        "author": "جلال الدين المحلي وجلال الدين السيوطي",
        "description": "تفسير مختصر جداً يركز على إيضاح معاني المفردات بأسلوب موجز ودقيق.",
        "db_filename": "jalalayn.db",
        "zip_filename": "jalalayn.zip",
        "approx_size_mb": 2.56,
        "download_size_mb": 0.63,
        "is_bundled_default": False,
        "mirrors": [
            f"{PRIMARY_TAFASEER_BASE_URL}/jalalayn.zip",
            f"{BACKUP_GITHUB_RAW_BASE_URL}/jalalayn.zip",
            f"{BACKUP_GITHUB_RELEASE_BASE_URL}/jalalayn.zip",
        ],
    },
}


class Category:
    baghawy = "baghawy"
    jalalayn = "jalalayn"
    katheer = "katheer"
    mukhtasar = "mukhtasar"
    muyassar = "muyassar"
    qortoby = "qortoby"
    sa3dy = "sa3dy"
    tabary = "tabary"

    _category_in_arabic = {
        meta["arabic_name"]: cat_id for cat_id, meta in TAFASEER_CATALOG.items()
    }

    @classmethod
    def is_valid(cls, category: str) -> bool:
        return category in TAFASEER_CATALOG

    @classmethod
    def get_category_by_arabic_name(cls, arabic_name: str) -> Optional[str]:
        return cls._category_in_arabic.get(arabic_name, None)

    @classmethod
    def get_arabic_name_by_category(cls, category: str) -> Optional[str]:
        info = TAFASEER_CATALOG.get(category)
        return info["arabic_name"] if info else None

    @classmethod
    def get_categories_in_arabic(cls) -> list:
        return list(cls._category_in_arabic.keys())

    @classmethod
    def get_tafsir_info(cls, category: str) -> Optional[Dict[str, Any]]:
        return TAFASEER_CATALOG.get(category)

    @classmethod
    def get_all_catalog(cls) -> Dict[str, Dict[str, Any]]:
        return TAFASEER_CATALOG

    @classmethod
    def find_tafsir_db_path(cls, category: str) -> Optional[Path]:
        """
        Locates the tafsir sqlite database using dual-path lookup:
        1. User's writable folder: paths.tafaseer_folder
        2. Application's bundled folder: paths.data_folder / 'tafaseer'
        Returns a Path object if found, or None if not installed.
        """
        logger.debug(f"Locating tafsir database for category: '{category}'...")
        if not cls.is_valid(category):
            logger.warning(f"Invalid tafsir category requested: '{category}'")
            return None

        # Check user data folder first
        candidates_user = [
            paths.tafaseer_folder / f"{category}.db",
            paths.tafaseer_folder / f"{category}.DB",
        ]
        for p in candidates_user:
            if p.is_file():
                logger.debug(f"Found tafsir database in user folder: {p}")
                return p

        # Check bundled folder
        bundled_folder = paths.data_folder / "tafaseer"
        candidates_bundled = [
            bundled_folder / f"{category}.db",
            bundled_folder / f"{category}.DB",
            Path("database") / "tafaseer" / f"{category}.db",
            Path("database") / "tafaseer" / f"{category}.DB",
        ]
        for p in candidates_bundled:
            if p.is_file():
                logger.debug(f"Found tafsir database in bundled folder: {p}")
                return p

        logger.debug(f"Tafsir database not found locally for category: '{category}'")
        return None

    @classmethod
    def is_installed(cls, category: str) -> bool:
        """Checks if a tafsir database exists locally either bundled or downloaded."""
        return cls.find_tafsir_db_path(category) is not None

    @classmethod
    def is_bundled(cls, category: str) -> bool:
        """
        Returns True if the tafsir exists in the bundled read-only database folder.
        Bundled default tafsir cannot be deleted by the user.
        """
        bundled_folder = paths.data_folder / "tafaseer"
        candidates = [
            bundled_folder / f"{category}.db",
            bundled_folder / f"{category}.DB",
            Path("database") / "tafaseer" / f"{category}.db",
            Path("database") / "tafaseer" / f"{category}.DB",
        ]
        for p in candidates:
            if p.is_file():
                return True
        return False

    @classmethod
    def is_deletable(cls, category: str) -> bool:
        """
        A tafsir is deletable only if it is installed in the user folder
        and is NOT the primary bundled default tafsir.
        """
        if category == DEFAULT_BUNDLED_TAFSIR_ID:
            return False

        user_candidates = [
            paths.tafaseer_folder / f"{category}.db",
            paths.tafaseer_folder / f"{category}.DB",
        ]
        return any(p.is_file() for p in user_candidates)

    @classmethod
    def get_installed_categories_arabic(cls) -> List[str]:
        """Returns a list of Arabic names for currently installed/available tafaseer."""
        installed = []
        for arabic_name, cat_id in cls._category_in_arabic.items():
            if cls.is_installed(cat_id):
                installed.append(arabic_name)
        return installed

    @classmethod
    def delete_tafsir(cls, category: str) -> bool:
        """
        Deletes a downloaded tafsir from the user folder.
        Safely closes any active database connections first.
        """
        logger.info(f"Attempting to delete tafsir category: '{category}' from user storage...")
        if not cls.is_valid(category):
            logger.error(f"Cannot delete invalid tafsir category: '{category}'")
            raise ValueError(f"فئة تفسير غير صالحة: {category}")

        if category == DEFAULT_BUNDLED_TAFSIR_ID:
            logger.warning("Attempted to delete the default bundled tafsir (forbidden).")
            raise ValueError("لا يمكن حذف التفسير الأساسي المضمن مع البرنامج.")

        # Close all active connections to prevent Windows file locking
        logger.debug(f"Closing any active connections for tafsir '{category}' prior to file deletion.")
        TafaseerManager.close_all_instances_for(category)

        deleted = False
        user_candidates = [
            paths.tafaseer_folder / f"{category}.db",
            paths.tafaseer_folder / f"{category}.DB",
            paths.tafaseer_folder / f"{category}.zip",
            paths.tafaseer_folder / f"{category}.db.part",
            paths.tafaseer_folder / f"{category}.zip.part",
        ]
        for p in user_candidates:
            if p.exists():
                try:
                    p.unlink()
                    deleted = True
                    logger.info(f"Deleted tafsir file: {p}")
                except Exception as e:
                    logger.error(f"Failed to delete tafsir file {p}: {e}", exc_info=True)
                    raise

        if deleted:
            logger.info(f"Successfully deleted tafsir category: '{category}'.")
        else:
            logger.warning(f"No files found to delete for tafsir category: '{category}'.")

        return deleted


class TafaseerManager:
    _active_instances: List["TafaseerManager"] = []

    def __init__(self) -> None:
        logger.debug("Initializing TafaseerManager...")
        self._tafaseer_category: Optional[str] = None
        self._conn: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
        self._db_path: Optional[str] = None
        TafaseerManager._active_instances.append(self)
        logger.debug("TafaseerManager initialized.")

    @classmethod
    def close_all_instances_for(cls, category: str) -> None:
        """Closes connections on any manager instances that have this category open."""
        for inst in list(cls._active_instances):
            if inst._tafaseer_category == category:
                inst.close_connection()

    def set(self, tafaseer_category: str) -> None:
        logger.debug(f"Setting tafaseer category: {tafaseer_category}")
        if not Category.is_valid(tafaseer_category):
            logger.error(f"Invalid tafaseer category: {tafaseer_category}")
            raise ValueError(f"Invalid tafaseer category: {tafaseer_category}")

        self._tafaseer_category = tafaseer_category
        logger.info(f"Set tafaseer category to: {tafaseer_category}")
        self._connect_to_database()

    def _connect_to_database(self) -> None:
        assert self._tafaseer_category is not None, "You must set tafaseer category."
        file_path = Category.find_tafsir_db_path(self._tafaseer_category)
        logger.debug(f"Connecting to database at {file_path} for {self._tafaseer_category}...")

        if file_path is None or not file_path.is_file():
            logger.error(f"Database file not found: {file_path}")
            raise DBNotFoundError(str(file_path or self._tafaseer_category))

        self.close_connection()
        self._conn = sqlite3.connect(str(file_path))
        self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()
        self._db_path = str(file_path)
        logger.info(f"Database connection established successfully: {file_path}.")

    def close_connection(self) -> None:
        """Explicitly close database connection if currently open."""
        if self._conn is not None:
            try:
                self._conn.close()
                logger.debug(f"Closed database connection for {self._tafaseer_category}.")
            except Exception as e:
                logger.warning(f"Error closing tafaseer db connection: {e}")
            finally:
                self._conn = None
                self._cursor = None
                self._db_path = None

    def get_tafaseer(self, surah_number: int, ayah_number: int) -> str:
        """Fetch tafseer for a specific Surah and Ayah."""
        logger.debug(f"Fetching tafseer for Surah {surah_number}, Ayah {ayah_number}...")
        assert self._conn is not None, "You must connect to database first."
        assert 1 <= surah_number <= 114, "Out of surah range."
        assert 1 <= ayah_number, "Out of ayah range."

        query = "SELECT text FROM tafsir_{} WHERE number = ?".format(surah_number)
        try:
            self._cursor.execute(query, [ayah_number])
            result = self._cursor.fetchone()
            logger.info(f"Fetched tafseer for Surah {surah_number}, Ayah {ayah_number}.")
            return self.get_text(result)
        except sqlite3.Error as e:
            logger.error(f"Error fetching tafseer: {e}", exc_info=True)
            return ""

    def get_text(self, row) -> str:
        """Process the tafseer text from the database row."""
        logger.debug("Processing tafseer text...")
        if row:
            text = row["text"].replace(".", ". \n").strip()
        else:
            logger.warning("No text found in the result.")
            return ""

        # Remove empty lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

    def __str__(self) -> str:
        return f"Category: {self._tafaseer_category}"

    def __del__(self):
        """Close the database connection when the object is deleted."""
        try:
            if self in TafaseerManager._active_instances:
                TafaseerManager._active_instances.remove(self)
        except Exception:
            pass
        self.close_connection()

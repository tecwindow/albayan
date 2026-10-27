from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from utils.paths import paths
from utils.logger import LoggerManager
from .data import TAFASEER_CATALOG, DEFAULT_BUNDLED_TAFSIR_ID

logger = LoggerManager.get_logger(__name__)


@dataclass
class TafsirInfo:
    """Represents catalog metadata for a single Tafsir book."""
    id: str
    arabic_name: str
    full_name: str
    author: str
    description: str
    db_filename: str
    zip_filename: str
    approx_size_mb: float
    download_size_mb: float
    is_bundled_default: bool
    mirrors: List[str]


class Category:
    """
    Model and category catalog resolver for Quranic Tafaseer.
    Provides lookup, file location resolution, and installation status checks.
    """

    baghawy = "baghawy"
    jalalayn = "jalalayn"
    katheer = "katheer"
    mukhtasar = "mukhtasar"
    muyassar = "muyassar"
    qortoby = "qortoby"
    sa3dy = "sa3dy"
    tabary = "tabary"

    _category_in_arabic: Dict[str, str] = {
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
        Locates the tafsir SQLite database using dual-path lookup:
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
            raise ValueError(f"Invalid tafsir category: {category}")

        if category == DEFAULT_BUNDLED_TAFSIR_ID:
            logger.warning("Attempted to delete default bundled tafsir (forbidden).")
            raise ValueError("Cannot delete bundled default tafsir.")

        # Close all active connections to prevent Windows file locking
        from .manager import TafaseerManager
        logger.debug(f"Closing active connections for tafsir '{category}' prior to file deletion.")
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

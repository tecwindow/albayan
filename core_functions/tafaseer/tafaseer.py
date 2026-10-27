"""
Backward-compatibility facade for core_functions.tafaseer.tafaseer.
Re-exports data, models, and manager components.
"""

from .data import (
    DEFAULT_BUNDLED_TAFSIR_ID,
    PRIMARY_TAFASEER_BASE_URL,
    BACKUP_GITHUB_RAW_BASE_URL,
    BACKUP_GITHUB_RELEASE_BASE_URL,
    TAFASEER_CATALOG,
)
from .models import Category, TafsirInfo
from .manager import TafaseerManager

__all__ = [
    "DEFAULT_BUNDLED_TAFSIR_ID",
    "PRIMARY_TAFASEER_BASE_URL",
    "BACKUP_GITHUB_RAW_BASE_URL",
    "BACKUP_GITHUB_RELEASE_BASE_URL",
    "TAFASEER_CATALOG",
    "Category",
    "TafsirInfo",
    "TafaseerManager",
]

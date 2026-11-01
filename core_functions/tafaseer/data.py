import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests
from utils.paths import paths
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

DEFAULT_BUNDLED_TAFSIR_ID = "muyassar"

PRIMARY_TAFASEER_BASE_URL = "https://albayan.tecwindow.net/tafaseer"
BACKUP_GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/tecwindow/albayan-data/main/tafaseer"
BACKUP_GITHUB_RELEASE_BASE_URL = "https://github.com/tecwindow/albayan-data/releases/download/v1.0"

# Ordered list of remote endpoints to fetch latest tafaseer.json
TAFASEER_JSON_REMOTE_URLS: List[str] = [
    "https://albayan.tecwindow.net/tafaseer/tafaseer.json",
    "https://albayan.tecwindow.net/tafaseer.json",
    "https://raw.githubusercontent.com/tecwindow/albayan/albayan_beta/database/tafaseer/tafaseer.json",
    "https://raw.githubusercontent.com/tecwindow/albayan/main/database/tafaseer/tafaseer.json",
    "https://raw.githubusercontent.com/tecwindow/albayan/master/database/tafaseer/tafaseer.json",
    "https://raw.githubusercontent.com/tecwindow/albayan-data/main/tafaseer/tafaseer.json",
]

# Static fallback catalog guaranteed to always be available offline
DEFAULT_CATALOG: Dict[str, Dict[str, Any]] = {
    "muyassar": {
        "id": "muyassar",
        "arabic_name": "الميسر",
        "full_name": "التفسير الميسر لنخبة من العلماء",
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
        "full_name": "المختصر في تفسير القرآن الكريم لمركز تفسير للدراسات القرآنية",
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
        "full_name": "تيسير الكريم الرحمن في تفسير كلام المنان للإمام السعدي",
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
        "full_name": "معالم التنزيل في تفسير القرآن للإمام البغوي",
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
        "full_name": "تفسير القرآن العظيم للإمام ابن كثير",
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
        "full_name": "الجامع لأحكام القرآن للإمام القرطبي",
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
        "full_name": "جامع البيان عن تأويل آي القرآن للإمام الطبري",
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
        "full_name": "تفسير الجلالين للإمامين المحلي والسيوطي",
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


def _validate_catalog(data: Any) -> bool:
    """Validate that the loaded catalog data is a non-empty dictionary of valid tafsir metadata."""
    if not isinstance(data, dict) or not data:
        return False
    for cat_id, info in data.items():
        if not isinstance(cat_id, str) or not isinstance(info, dict):
            return False
        if "arabic_name" not in info or "mirrors" not in info:
            return False
    return True


def get_bundled_json_path() -> Optional[Path]:
    """Find the bundled tafaseer.json if available."""
    candidates = [
        paths.data_folder / "tafaseer" / "tafaseer.json",
        Path(__file__).resolve().parents[2] / "database" / "tafaseer" / "tafaseer.json",
        Path("database") / "tafaseer" / "tafaseer.json",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def get_cached_json_path() -> Path:
    """Return the user cache path for tafaseer.json."""
    return paths.tafaseer_folder / "tafaseer.json"


def load_local_catalog() -> Dict[str, Dict[str, Any]]:
    """
    Load the catalog from local sources:
    1. User cache (downloaded previously)
    2. Bundled json file in database/tafaseer/tafaseer.json
    3. Static DEFAULT_CATALOG fallback
    """
    # 1. Try cache
    cache_path = get_cached_json_path()
    if cache_path.is_file():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if _validate_catalog(data):
                logger.debug(f"Loaded tafaseer catalog from cache: {cache_path}")
                return data
        except Exception as e:
            logger.warning(f"Failed to read cached tafaseer.json: {e}")

    # 2. Try bundled json
    bundled_path = get_bundled_json_path()
    if bundled_path:
        try:
            with open(bundled_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if _validate_catalog(data):
                logger.debug(f"Loaded tafaseer catalog from bundled file: {bundled_path}")
                return data
        except Exception as e:
            logger.warning(f"Failed to read bundled tafaseer.json: {e}")

    # 3. Fallback
    logger.debug("Using built-in DEFAULT_CATALOG fallback for tafaseer.")
    return {k: v.copy() for k, v in DEFAULT_CATALOG.items()}


def save_catalog_to_cache(catalog: Dict[str, Dict[str, Any]]) -> bool:
    """Save the catalog dictionary to user cache as formatted JSON."""
    cache_path = get_cached_json_path()
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        logger.debug(f"Saved updated tafaseer catalog to cache: {cache_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save tafaseer catalog to cache: {e}")
        return False


# The active global catalog instance initialized from local storage
TAFASEER_CATALOG: Dict[str, Dict[str, Any]] = load_local_catalog()


def update_catalog(new_catalog: Dict[str, Dict[str, Any]], save_cache: bool = True) -> bool:
    """Update TAFASEER_CATALOG in-place and optionally save to user cache."""
    if not _validate_catalog(new_catalog):
        logger.error("Invalid catalog format provided to update_catalog.")
        return False

    TAFASEER_CATALOG.clear()
    TAFASEER_CATALOG.update(new_catalog)
    if save_cache:
        save_catalog_to_cache(new_catalog)
    logger.info(f"Tafaseer catalog updated with {len(TAFASEER_CATALOG)} entries.")
    return True


def fetch_remote_catalog(timeout: int = 5) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Fetch the latest tafaseer.json from albayan.tecwindow.net or GitHub.
    Returns the parsed catalog dictionary if successful, or None if unreachable.
    """
    session = requests.Session()
    session.headers.update({"User-Agent": "Albayan-Quran-App"})

    for url in TAFASEER_JSON_REMOTE_URLS:
        try:
            logger.debug(f"Attempting to fetch tafaseer catalog from: {url}")
            resp = session.get(url, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                if _validate_catalog(data):
                    logger.info(f"Successfully fetched tafaseer catalog from: {url}")
                    update_catalog(data, save_cache=True)
                    return data
                else:
                    logger.warning(f"Catalog fetched from {url} was invalid.")
            else:
                logger.debug(f"Fetch from {url} returned status code {resp.status_code}")
        except Exception as e:
            logger.debug(f"Failed to fetch tafaseer catalog from {url}: {e}")

    logger.warning("Could not fetch remote tafaseer catalog from any URL.")
    return None

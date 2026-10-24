import sqlite3
from pathlib import Path
from typing import Optional, Union
from utils.logger import LoggerManager
from utils.paths import paths
from utils.archive import ZipArchive
from core_functions.downloader.manager import DownloadManager
from .tafaseer import Category

logger = LoggerManager.get_logger(__name__)


class TafsirInstaller:
    """
    Stateless service class responsible for scheduling downloads,
    extracting database archives, verifying integrity, and installing Tafaseer.
    """

    @staticmethod
    def start_download(
        manager: DownloadManager,
        tafsir_id: str,
        dest_dir: Optional[Path] = None,
    ) -> Optional[int]:
        """
        Schedules and starts downloading a tafsir archive using DownloadManager directly.
        Returns the assigned download_id.
        """
        info = Category.get_tafsir_info(tafsir_id)
        if not info:
            logger.error(f"Catalog metadata not found for tafsir: {tafsir_id}")
            return None

        mirrors = info.get("mirrors", [])
        if not mirrors:
            logger.error(f"No download mirrors available for tafsir: {tafsir_id}")
            return None

        folder = dest_dir or paths.tafaseer_folder
        folder.mkdir(parents=True, exist_ok=True)

        zip_filename = info.get("zip_filename", f"{tafsir_id}.zip")
        db_filename = info.get("db_filename", f"{tafsir_id}.db")

        download_id = manager.add_download(
            url=mirrors[0],
            download_folder=str(folder),
            filename=zip_filename,
            mirrors=mirrors,
            tafsir_id=tafsir_id,
            db_filename=db_filename,
        )

        if download_id is not None:
            manager.start()
            logger.info(f"Tafsir download scheduled successfully: {tafsir_id} (ID={download_id})")

        return download_id

    @staticmethod
    def install(
        tafsir_id: str,
        zip_path: Union[Path, str],
        dest_dir: Optional[Path] = None,
    ) -> Path:
        """
        Extracts the database from the downloaded zip archive,
        verifies its schema integrity, and deletes the temporary archive.
        Returns the Path to the installed SQLite database.
        """
        archive_path = Path(zip_path)
        target_folder = dest_dir or paths.tafaseer_folder
        target_folder.mkdir(parents=True, exist_ok=True)

        info = Category.get_tafsir_info(tafsir_id)
        db_filename = info.get("db_filename", f"{tafsir_id}.db") if info else f"{tafsir_id}.db"
        dest_db_path = target_folder / db_filename

        logger.info(f"Installing tafsir '{tafsir_id}' from archive: {archive_path}")
        try:
            # 1. Extract database from archive
            ZipArchive.extract_by_extension(
                zip_path=archive_path,
                extension=".db",
                destination_path=dest_db_path,
            )

            # 2. Verify database integrity
            TafsirInstaller.verify(dest_db_path)

            # 3. Clean up zip archive to save disk space
            ZipArchive.remove_archive(archive_path)

            logger.info(f"Tafsir '{tafsir_id}' successfully installed at: {dest_db_path}")
            return dest_db_path

        except Exception as e:
            logger.error(f"Failed to install tafsir '{tafsir_id}' from {archive_path}: {e}", exc_info=True)
            ZipArchive.remove_archive(archive_path)
            raise

    @staticmethod
    def verify(db_path: Union[Path, str]) -> None:
        """
        Validates that the SQLite database file exists and contains the required 'tafsir_1' table.
        """
        path = Path(db_path)
        if not path.is_file():
            logger.error(f"Database file does not exist: {path}")
            raise FileNotFoundError(f"Database file not found: {path}")

        with sqlite3.connect(str(path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='tafsir_1';"
            )
            if cursor.fetchone()[0] == 0:
                logger.error(f"Database schema mismatch: missing required table 'tafsir_1' in {path}")
                raise ValueError("Database schema incompatible: missing 'tafsir_1' table.")


# Functional aliases for backwards-compatibility
start_tafsir_download = TafsirInstaller.start_download
install_tafsir_archive = TafsirInstaller.install
verify_tafsir_database = TafsirInstaller.verify

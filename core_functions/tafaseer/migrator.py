import os
import sys
import shutil
from pathlib import Path
from typing import List, Optional

from utils.logger import LoggerManager
from utils.paths import paths
from .data import TAFASEER_CATALOG, DEFAULT_BUNDLED_TAFSIR_ID
from .installer import TafsirInstaller

logger = LoggerManager.get_logger(__name__)


class LegacyTafaseerMigrator:
    """
    Detects and migrates legacy tafaseer SQLite databases from the application's
    installation directory to the user's data directory (paths.tafaseer_folder).

    - Preserves the bundled default tafsir ('muyassar') in the installation directory.
    - Verifies SQLite schema and integrity before finalizing migration.
    - Handles Windows read-only folder permissions gracefully (copy + optional delete).
    - Preserves repository files when running from source (non-frozen mode).
    - Normalizes filenames to canonical lowercase (e.g., jalalayn.DB -> jalalayn.db).
    """

    _has_run: bool = False

    @classmethod
    def migrate_if_needed(
        cls,
        legacy_dirs: Optional[List[Path]] = None,
        force: bool = False,
    ) -> int:
        """
        Executes legacy tafaseer migration if not previously executed in this session.
        Returns the count of successfully migrated tafaseer.
        """
        if cls._has_run and not force:
            logger.debug("Legacy tafaseer migration already executed for this session.")
            return 0

        cls._has_run = True
        logger.info("Checking for legacy tafaseer databases to migrate...")

        target_dir = paths.tafaseer_folder
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create target tafaseer folder {target_dir}: {e}", exc_info=True)
            return 0

        # Scan candidate legacy directories if not specified
        if legacy_dirs is None:
            candidate_legacy_dirs: List[Path] = [
                paths.data_folder / "tafaseer",
            ]
            db_rel = Path("database") / "tafaseer"
            if db_rel.resolve() != (paths.data_folder / "tafaseer").resolve():
                candidate_legacy_dirs.append(db_rel)
        else:
            candidate_legacy_dirs = legacy_dirs

        # Filter to unique, existing directories that are distinct from target_dir
        valid_legacy_dirs: List[Path] = []
        for d in candidate_legacy_dirs:
            try:
                resolved = d.resolve()
                if resolved.is_dir() and resolved != target_dir.resolve() and resolved not in valid_legacy_dirs:
                    valid_legacy_dirs.append(resolved)
            except Exception:
                if d.is_dir() and d != target_dir and d not in valid_legacy_dirs:
                    valid_legacy_dirs.append(d)

        if not valid_legacy_dirs:
            logger.debug("No legacy tafaseer directories found.")
            return 0

        migrated_count = 0

        for legacy_dir in valid_legacy_dirs:
            logger.debug(f"Scanning legacy directory for tafaseer: {legacy_dir}")
            try:
                files = list(legacy_dir.iterdir())
            except Exception as e:
                logger.warning(f"Unable to read legacy directory {legacy_dir}: {e}")
                continue

            for file_path in files:
                if not file_path.is_file():
                    continue

                # Match .db and .DB extensions
                suffix_lower = file_path.suffix.lower()
                if suffix_lower != ".db":
                    continue

                stem_lower = file_path.stem.lower()

                # Always preserve the bundled default tafsir (e.g. muyassar) in installation folder
                if stem_lower == DEFAULT_BUNDLED_TAFSIR_ID.lower():
                    logger.debug(f"Skipping bundled default tafsir from migration: {file_path.name}")
                    continue

                # Match against catalog metadata
                cat_id = stem_lower
                if cat_id not in TAFASEER_CATALOG:
                    logger.debug(f"Skipping non-catalog db file in legacy folder: {file_path.name}")
                    continue

                dest_file = target_dir / f"{cat_id}.db"

                # If destination file already exists, verify its integrity
                if dest_file.is_file():
                    try:
                        TafsirInstaller.verify(dest_file)
                        logger.debug(f"Tafsir '{cat_id}' already exists and is valid in user folder: {dest_file}")
                        # Destination is healthy, safely attempt to clean up source file
                        cls._safe_delete_legacy_file(file_path)
                        continue
                    except Exception as e:
                        logger.warning(
                            f"Existing tafsir in user folder is corrupt ({dest_file}): {e}. Overwriting with legacy copy."
                        )

                # Verify source file integrity before migrating
                try:
                    TafsirInstaller.verify(file_path)
                except Exception as e:
                    logger.warning(f"Corrupted or invalid legacy tafsir database found at {file_path}: {e}. Skipping.")
                    continue

                # Copy safely using a temporary file
                temp_dest = target_dir / f"{cat_id}.db.migrating"
                try:
                    logger.info(f"Migrating legacy tafsir '{cat_id}' from {file_path} to {dest_file}...")
                    shutil.copy2(str(file_path), str(temp_dest))

                    # Verify copied file
                    TafsirInstaller.verify(temp_dest)

                    # Replace target file atomically
                    if dest_file.exists():
                        dest_file.unlink()
                    temp_dest.replace(dest_file)

                    migrated_count += 1
                    logger.info(f"Successfully migrated legacy tafsir '{cat_id}' to {dest_file}")

                    # Attempt to clean up legacy source file to save disk space
                    cls._safe_delete_legacy_file(file_path)

                except Exception as e:
                    logger.error(
                        f"Failed to migrate legacy tafsir '{cat_id}' from {file_path}: {e}",
                        exc_info=True,
                    )
                    if temp_dest.exists():
                        try:
                            temp_dest.unlink()
                        except Exception:
                            pass

        if migrated_count > 0:
            logger.info(f"Legacy tafaseer migration completed: {migrated_count} tafsir(s) migrated successfully.")
        else:
            logger.debug("Legacy tafaseer migration finished: no files needed migration.")

        return migrated_count

    @classmethod
    def _safe_delete_legacy_file(cls, path: Path) -> bool:
        """
        Attempts to delete a legacy file to free up space in installed / frozen mode.
        Preserves files when running from source to avoid modifying git tracked files.
        Suppresses PermissionError / OSError in read-only installation directories.
        """
        if not getattr(sys, "frozen", False):
            logger.debug(f"Preserving legacy file {path} when running from source code.")
            return False

        try:
            path.unlink()
            logger.info(f"Cleaned up legacy tafsir file: {path}")
            return True
        except (PermissionError, OSError) as e:
            logger.debug(
                f"Could not remove legacy file {path} (read-only installation directory): {e}"
            )
            return False
        except Exception as e:
            logger.warning(f"Unexpected error while removing legacy file {path}: {e}")
            return False

import os
import zipfile
from pathlib import Path
from typing import List, Optional, Union
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ZipArchive:
    """
    Utility class for inspecting, extracting, and managing zip archive files.
    Provides clear, reusable methods for safe archive handling.
    """

    @staticmethod
    def is_valid_archive(zip_path: Union[Path, str]) -> bool:
        """
        Validates if the file exists and is an uncorrupted zip archive.
        """
        path = Path(zip_path)
        if not path.is_file():
            logger.warning(f"Archive file not found: {path}")
            return False

        if not zipfile.is_zipfile(path):
            logger.warning(f"File is not a valid zip archive: {path}")
            return False

        try:
            with zipfile.ZipFile(path, "r") as zf:
                bad_file = zf.testzip()
                if bad_file:
                    logger.error(f"Corrupt file found in zip archive {path}: {bad_file}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error testing zip archive {path}: {e}")
            return False

    @staticmethod
    def list_members(zip_path: Union[Path, str]) -> List[str]:
        """
        Returns the list of filenames inside the zip archive.
        """
        path = Path(zip_path)
        with zipfile.ZipFile(path, "r") as zf:
            return zf.namelist()

    @staticmethod
    def find_member(zip_path: Union[Path, str], extension: str) -> Optional[str]:
        """
        Finds the first member in the archive matching the specified extension (case-insensitive).
        """
        ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        members = ZipArchive.list_members(zip_path)
        for member in members:
            if member.lower().endswith(ext):
                return member
        return None

    @staticmethod
    def extract_member(
        zip_path: Union[Path, str],
        member_name: str,
        destination_path: Union[Path, str],
        chunk_size: int = 1024 * 1024,
    ) -> Path:
        """
        Extracts a single member from the zip archive directly to destination_path.
        """
        src_path = Path(zip_path)
        dest_path = Path(destination_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Extracting member '{member_name}' from {src_path} to {dest_path}")
        with zipfile.ZipFile(src_path, "r") as zf:
            with zf.open(member_name) as source, open(dest_path, "wb") as target:
                while chunk := source.read(chunk_size):
                    target.write(chunk)

        logger.info(f"Successfully extracted '{member_name}' to {dest_path}")
        return dest_path

    @staticmethod
    def extract_by_extension(
        zip_path: Union[Path, str],
        extension: str,
        destination_path: Union[Path, str],
    ) -> Path:
        """
        Finds a member matching the given extension and extracts it to destination_path.
        Raises FileNotFoundError if no matching member is found in the archive.
        """
        member = ZipArchive.find_member(zip_path, extension)
        if not member:
            raise FileNotFoundError(
                f"No member with extension '{extension}' found in archive: {zip_path}"
            )
        return ZipArchive.extract_member(zip_path, member, destination_path)

    @staticmethod
    def extract_all(zip_path: Union[Path, str], destination_dir: Union[Path, str]) -> Path:
        """
        Extracts all files from the zip archive to destination_dir.
        """
        src_path = Path(zip_path)
        dest_dir = Path(destination_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Extracting all members from {src_path} to {dest_dir}")
        with zipfile.ZipFile(src_path, "r") as zf:
            zf.extractall(dest_dir)

        logger.info(f"Extracted archive {src_path} to {dest_dir}")
        return dest_dir

    @staticmethod
    def remove_archive(zip_path: Union[Path, str]) -> bool:
        """
        Safely deletes the archive file from disk.
        """
        path = Path(zip_path)
        if path.exists():
            try:
                path.unlink()
                logger.debug(f"Deleted archive: {path}")
                return True
            except Exception as e:
                logger.warning(f"Failed to delete archive {path}: {e}")
                return False
        return False

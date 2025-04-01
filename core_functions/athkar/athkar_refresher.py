import os
from typing import Dict
from .athkar_db_manager import AthkarDBManager
from utils.logger import LoggerManager
logger = LoggerManager.get_logger(__name__)


class AthkarRefresher:
    def __init__(self, db_manager: AthkarDBManager, folder_path: str, category_id: int) -> None:
        logger.debug(f"Initializing AthkarRefresher with folder path: {folder_path} and category ID: {category_id}")
        self.db_manager = db_manager
        self.folder_path = folder_path
        self.category_id = category_id
        self.audio_extensions = {'.mp3', '.wav', '.ogg', '.flac'}
        logger.debug(f"Initialized AthkarRefresher for category {self.category_id} with folder {self.folder_path}")

    def refresh_data(self) -> None:
        logger.info(f"Refreshing data for category {self.category_id}...")
        existing_files = set(self._get_existing_files())
        logger.debug(f"Found {len(existing_files)} existing audio files in folder: {self.folder_path}")
        db_files = self._get_files_in_db()
        logger.debug(f"Found {len(db_files)} audio files in database for category {self.category_id}")
        new_files = existing_files - set(db_files.keys())
        removed_files = set(db_files.keys()) - existing_files

        if new_files:
            logger.info(f"Found {len(new_files)} new files to add.")
            self.db_manager.add_audio_athkar(new_files, self.category_id)
            logger.info(f"Added {len(new_files)} new audio athkar to database for category {self.category_id}")
        else:
            logger.debug("No new files to add.")
        if removed_files:
            removed_ids = [db_files[file_name] for file_name in removed_files]
            logger.warning(f"Found {len(removed_files)} files to remove from database.")
            removed_ids = [db_files[file_name] for file_name in removed_files]
            self.db_manager.delete_audio_athkar(removed_ids)
            logger.info(f"Removed {len(removed_files)} audio athkar from database for category {self.category_id}")
        else:
            logger.debug("No files to remove.")


    def _get_existing_files(self) -> list:
        logger.debug(f"Scanning directory {self.folder_path} for audio files.")
        return [
            f for f in os.listdir(self.folder_path)
            if os.path.isfile(os.path.join(self.folder_path, f)) and self._is_audio_file(f)
        ]

    def _is_audio_file(self, filename: str) -> bool:
        is_audio = any(filename.lower().endswith(ext) for ext in self.audio_extensions)
        if not is_audio:
            logger.debug(f"File {filename} is not a valid audio file.")
        return is_audio

    def _get_files_in_db(self) -> Dict[str, int]:
        logger.debug(f"Retrieving audio athkar from the database for category {self.category_id}.")
        audio_athkars = self.db_manager.get_audio_athkar(self.category_id)
        logger.debug(f"Found {len(audio_athkars)} audio athkar in the database for category {self.category_id}.")
        return {athkar.audio_file_name: athkar.id for athkar in audio_athkars}
    

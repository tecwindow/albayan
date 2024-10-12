import os
from typing import Dict
from .athkar_db_manager import AthkarDBManager


class AthkarRefresher:
    def __init__(self, db_manager: AthkarDBManager, folder_path: str, category_id: int) -> None:
        self.db_manager = db_manager
        self.folder_path = folder_path
        self.category_id = category_id
        self.audio_extensions = {'.mp3', '.wav', '.ogg', '.flac'}

    def refresh_data(self) -> None:
        existing_files = set(self._get_existing_files())
        db_files = self._get_files_in_db()

        new_files = existing_files - set(db_files.keys())
        removed_files = set(db_files.keys()) - existing_files

        if new_files:
            self.db_manager.add_audio_athkar(new_files, self.category_id)

        if removed_files:
            removed_ids = [db_files[file_name] for file_name in removed_files]
            self.db_manager.delete_audio_athkar(removed_ids)

    def _get_existing_files(self) -> list:
        return [
            f for f in os.listdir(self.folder_path)
            if os.path.isfile(os.path.join(self.folder_path, f)) and self._is_audio_file(f)
        ]

    def _is_audio_file(self, filename: str) -> bool:
        return any(filename.lower().endswith(ext) for ext in self.audio_extensions)

    def _get_files_in_db(self) -> Dict[str, int]:
        audio_athkars = self.db_manager.get_audio_athkar(self.category_id)
        return {athkar.audio_file_name: athkar.id for athkar in audio_athkars}

import pytest
from unittest.mock import MagicMock
from core_functions.athkar.athkar_refresher import AthkarRefresher


class TestAthkarRefresher:
    def test_is_audio_file(self):
        refresher = AthkarRefresher(MagicMock(), "/dummy", 1)
        assert refresher._is_audio_file("morning.mp3") is True
        assert refresher._is_audio_file("evening.WAV") is True
        assert refresher._is_audio_file("athkar.ogg") is True
        assert refresher._is_audio_file("sound.flac") is True
        assert refresher._is_audio_file("document.pdf") is False
        assert refresher._is_audio_file("readme.txt") is False

    def test_refresh_data_adds_new_files(self, tmp_path):
        folder = tmp_path / "audio"
        folder.mkdir()
        (folder / "athkar1.mp3").touch()
        (folder / "athkar2.wav").touch()
        (folder / "notes.txt").touch()  # non-audio ignored

        mock_db = MagicMock()
        # DB starts empty
        mock_db.get_audio_athkar.return_value = []

        refresher = AthkarRefresher(mock_db, str(folder), category_id=1)
        refresher.refresh_data()

        mock_db.add_audio_athkar.assert_called_once()
        added_files = set(mock_db.add_audio_athkar.call_args[0][0])
        assert added_files == {"athkar1.mp3", "athkar2.wav"}
        mock_db.delete_audio_athkar.assert_not_called()

    def test_refresh_data_removes_deleted_files(self, tmp_path):
        folder = tmp_path / "audio"
        folder.mkdir()
        # Only athkar1.mp3 exists on disk
        (folder / "athkar1.mp3").touch()

        mock_db = MagicMock()
        mock_item1 = MagicMock(audio_file_name="athkar1.mp3", id=101)
        mock_item2 = MagicMock(audio_file_name="deleted.mp3", id=102)
        mock_db.get_audio_athkar.return_value = [mock_item1, mock_item2]

        refresher = AthkarRefresher(mock_db, str(folder), category_id=1)
        refresher.refresh_data()

        mock_db.add_audio_athkar.assert_not_called()
        mock_db.delete_audio_athkar.assert_called_once_with([102])

    def test_refresh_data_already_in_sync(self, tmp_path):
        folder = tmp_path / "audio"
        folder.mkdir()
        (folder / "athkar1.mp3").touch()

        mock_db = MagicMock()
        mock_item = MagicMock(audio_file_name="athkar1.mp3", id=101)
        mock_db.get_audio_athkar.return_value = [mock_item]

        refresher = AthkarRefresher(mock_db, str(folder), category_id=1)
        refresher.refresh_data()

        mock_db.add_audio_athkar.assert_not_called()
        mock_db.delete_audio_athkar.assert_not_called()

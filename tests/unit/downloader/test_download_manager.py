import pytest
from unittest.mock import MagicMock
from core_functions.downloader.manager import DownloadManager
from core_functions.downloader.db import DownloadDB
from core_functions.downloader.models import DownloadSurahs
from core_functions.downloader.status import DownloadStatus


@pytest.fixture(autouse=True)
def prevent_real_workers(monkeypatch):
    """Ensure tests never spawn real network DownloadWorker threads on QThreadPool."""
    monkeypatch.setattr(DownloadManager, "_start_download", lambda self, did: None)


@pytest.fixture
def mock_db(tmp_path):
    db_file = tmp_path / "downloads.db"
    db_url = f"sqlite:///{db_file}"
    db = DownloadDB(db_url, DownloadSurahs)
    yield db
    db.engine.dispose()


class TestDownloadManager:
    def test_init_raises_without_db_when_history_enabled(self, qapp):
        with pytest.raises(ValueError, match="DownloadDB instance is required"):
            DownloadManager(save_history=True, download_db=None)

        with pytest.raises(ValueError, match="DownloadDB instance is required"):
            DownloadManager(load_history=True, download_db=None)

    def test_add_new_downloads_validation(self, qapp):
        mgr = DownloadManager()
        with pytest.raises(ValueError, match="must be a list of dictionaries"):
            mgr.add_new_downloads("not a list", "/downloads")

    def test_add_and_get_downloads(self, qapp, tmp_path):
        mgr = DownloadManager()
        added_signal = []
        mgr.downloads_added.connect(added_signal.extend)

        mgr.add_download("https://example.com/001.mp3", str(tmp_path), surah_number=1)

        assert len(mgr.get_downloads()) == 1
        assert len(added_signal) == 1
        item = mgr.get_download(1)
        assert item["filename"] == "001.mp3"
        assert item["status"] == DownloadStatus.PENDING
        assert item["surah_number"] == 1

    def test_status_change_and_database_sync(self, qapp, mock_db, tmp_path):
        mgr = DownloadManager(save_history=True, download_db=mock_db)
        mgr.add_download("https://example.com/002.mp3", str(tmp_path), reciter_id=1, surah_number=2)

        status_events = []
        mgr.status_changed.connect(lambda did, st: status_events.append((did, st)))

        mgr._on_status(1, DownloadStatus.DOWNLOADING)
        assert mgr.get_download(1)["status"] == DownloadStatus.DOWNLOADING
        assert len(status_events) == 1
        assert status_events[0] == (1, DownloadStatus.DOWNLOADING)

        # Verify synced to DB
        db_item = mock_db.get(1)
        assert db_item.status == DownloadStatus.DOWNLOADING

    def test_has_active_downloads(self, qapp, tmp_path):
        mgr = DownloadManager()
        assert mgr.has_active_downloads() is False

        mgr.add_download("https://example.com/001.mp3", str(tmp_path))
        assert mgr.has_active_downloads() is True  # PENDING counts as active

        mgr._on_status(1, DownloadStatus.COMPLETED)
        assert mgr.has_active_downloads() is False

    def test_set_size_text(self, qapp, tmp_path):
        mgr = DownloadManager()
        mgr.add_download("https://example.com/001.mp3", str(tmp_path))

        # Size in KB (< 1MB)
        mgr.set_size_text(1, 512 * 1024)
        assert mgr.get_download(1)["size_text"] == "512.00 KB"

        # Size in MB (>= 1MB)
        mgr.set_size_text(1, 2 * 1024 * 1024)
        assert mgr.get_download(1)["size_text"] == "2.00 MB"

    def test_pause_and_resume_all(self, qapp, tmp_path):
        mgr = DownloadManager()
        mgr.add_download("https://example.com/001.mp3", str(tmp_path))
        mgr.add_download("https://example.com/002.mp3", str(tmp_path))

        mgr.pause_all()
        paused = mgr.get_downloads(DownloadStatus.PAUSED)
        assert len(paused) == 2

        mgr.resume_all()
        resumed = mgr.get_downloads(DownloadStatus.PENDING)
        assert len(resumed) == 2

    def test_cancel_all(self, qapp, tmp_path):
        mgr = DownloadManager()
        mgr.add_download("https://example.com/001.mp3", str(tmp_path))
        mgr.add_download("https://example.com/002.mp3", str(tmp_path))

        cancelled_events = []
        mgr.cancelled_all.connect(lambda: cancelled_events.append(True))
        mgr.cancel_all()
        cancelled = mgr.get_downloads(DownloadStatus.CANCELLED)
        assert len(cancelled) == 2
        assert len(cancelled_events) == 1

    def test_delete_download(self, qapp, tmp_path):
        mgr = DownloadManager()
        file_to_create = tmp_path / "001.mp3"
        file_to_create.write_text("dummy")

        mgr.add_download("https://example.com/001.mp3", str(tmp_path))
        deleted_signals = []
        mgr.download_deleted.connect(deleted_signals.append)

        mgr.delete(1, delete_file=True)
        assert mgr.get_download(1) is None
        assert not file_to_create.exists()
        assert deleted_signals == [1]

    def test_load_history(self, qapp, mock_db, tmp_path):
        mock_db.upsert({
            "url": "https://example.com/history.mp3",
            "filename": "history.mp3",
            "folder_path": str(tmp_path),
            "status": DownloadStatus.COMPLETED,
            "reciter_id": 1,
            "surah_number": 1,
            "downloaded_bytes": 1024,
            "total_bytes": 1024,
        })

        mgr = DownloadManager(load_history=True, save_history=True, download_db=mock_db)
        downloads = mgr.get_downloads()
        assert len(downloads) == 1
        assert downloads[0]["filename"] == "history.mp3"
        assert downloads[0]["status"] == DownloadStatus.COMPLETED

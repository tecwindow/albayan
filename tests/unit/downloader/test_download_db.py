import pytest
from core_functions.downloader.db import DownloadDB
from core_functions.downloader.models import DownloadSurahs
from core_functions.downloader.status import DownloadStatus


@pytest.fixture
def download_db(tmp_path):
    db_file = tmp_path / "downloads.db"
    db_url = f"sqlite:///{db_file}"
    db = DownloadDB(db_url, DownloadSurahs)
    yield db
    db.engine.dispose()


class TestDownloadDB:
    def test_upsert_single_new_and_update(self, download_db):
        data = {
            "url": "https://example.com/1.mp3",
            "filename": "1.mp3",
            "folder_path": "/downloads",
            "status": DownloadStatus.PENDING,
            "reciter_id": 1,
            "surah_number": 1,
        }
        item_id = download_db.upsert(data)
        assert item_id is not None

        item = download_db.get(item_id)
        assert item.filename == "1.mp3"
        assert item.status == DownloadStatus.PENDING

        # Update via upsert
        update_data = {
            "id": item_id,
            "status": DownloadStatus.COMPLETED,
            "downloaded_bytes": 5000,
            "total_bytes": 5000,
        }
        download_db.upsert(update_data)
        updated = download_db.get(item_id)
        assert updated.status == DownloadStatus.COMPLETED
        assert updated.downloaded_bytes == 5000

    def test_upsert_many(self, download_db):
        items = [
            {
                "url": f"https://example.com/{i}.mp3",
                "filename": f"{i}.mp3",
                "folder_path": "/downloads",
                "status": DownloadStatus.PENDING,
                "reciter_id": 1,
                "surah_number": i,
            }
            for i in range(1, 4)
        ]
        ids = download_db.upsert_many(items)
        assert len(ids) == 3

        all_items = download_db.all()
        assert len(all_items) == 3

    def test_update_status(self, download_db):
        item_id = download_db.upsert({
            "url": "https://example.com/test.mp3",
            "filename": "test.mp3",
            "folder_path": "/downloads",
            "status": DownloadStatus.PENDING,
            "reciter_id": 1,
            "surah_number": 2,
        })
        download_db.update_status(item_id, DownloadStatus.DOWNLOADING)
        assert download_db.get(item_id).status == DownloadStatus.DOWNLOADING

    def test_update_by_status(self, download_db):
        download_db.upsert({
            "url": "https://example.com/1.mp3",
            "filename": "1.mp3",
            "folder_path": "/downloads",
            "status": DownloadStatus.DOWNLOADING,
            "reciter_id": 1,
            "surah_number": 1,
        })
        download_db.upsert({
            "url": "https://example.com/2.mp3",
            "filename": "2.mp3",
            "folder_path": "/downloads",
            "status": DownloadStatus.DOWNLOADING,
            "reciter_id": 1,
            "surah_number": 2,
        })
        download_db.upsert({
            "url": "https://example.com/3.mp3",
            "filename": "3.mp3",
            "folder_path": "/downloads",
            "status": DownloadStatus.COMPLETED,
            "reciter_id": 1,
            "surah_number": 3,
        })

        # Update all DOWNLOADING -> PAUSED
        download_db.update_by_status(DownloadStatus.DOWNLOADING, DownloadStatus.PAUSED)
        all_items = download_db.all()
        paused_items = [i for i in all_items if i.status == DownloadStatus.PAUSED]
        assert len(paused_items) == 2

    def test_find_one(self, download_db):
        download_db.upsert({
            "url": "https://example.com/find.mp3",
            "filename": "find.mp3",
            "folder_path": "/downloads",
            "status": DownloadStatus.PENDING,
            "reciter_id": 99,
            "surah_number": 114,
        })
        found = download_db.find_one(reciter_id=99, surah_number=114)
        assert found is not None
        assert found.filename == "find.mp3"

        not_found = download_db.find_one(reciter_id=999)
        assert not_found is None

    def test_delete_and_delete_all(self, download_db):
        id1 = download_db.upsert({
            "url": "https://example.com/1.mp3",
            "filename": "1.mp3",
            "folder_path": "/downloads",
            "status": DownloadStatus.PENDING,
            "reciter_id": 1,
            "surah_number": 1,
        })
        id2 = download_db.upsert({
            "url": "https://example.com/2.mp3",
            "filename": "2.mp3",
            "folder_path": "/downloads",
            "status": DownloadStatus.PENDING,
            "reciter_id": 1,
            "surah_number": 2,
        })
        assert len(download_db.all()) == 2

        download_db.delete(id1)
        assert len(download_db.all()) == 1
        assert download_db.get(id1) is None

        download_db.delete_all()
        assert len(download_db.all()) == 0

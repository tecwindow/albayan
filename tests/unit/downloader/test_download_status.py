import time
import pytest
from core_functions.downloader.status import DownloadStatus, DownloadProgress


class TestDownloadStatus:
    def test_status_enum_values(self):
        assert DownloadStatus.PENDING.value == "pending"
        assert DownloadStatus.DOWNLOADING.value == "downloading"
        assert DownloadStatus.PAUSED.value == "paused"
        assert DownloadStatus.CANCELLED.value == "cancelled"
        assert DownloadStatus.COMPLETED.value == "completed"
        assert DownloadStatus.ERROR.value == "error"

    def test_arabic_labels(self):
        assert DownloadStatus.PENDING.label == "قيد الانتظار"
        assert DownloadStatus.DOWNLOADING.label == "يجري التنزيل"
        assert DownloadStatus.PAUSED.label == "متوقف مؤقتًا"
        assert DownloadStatus.CANCELLED.label == "تم الإلغاء"
        assert DownloadStatus.COMPLETED.label == "مكتمل"
        assert DownloadStatus.ERROR.label == "خطأ"


class TestDownloadProgress:
    def test_percentage_calculation(self):
        # Normal 50%
        p = DownloadProgress(download_id=1, downloaded_bytes=500, total_bytes=1000)
        assert p.percentage == 50

        # Complete 100%
        p = DownloadProgress(download_id=1, downloaded_bytes=1000, total_bytes=1000)
        assert p.percentage == 100

        # Zero total bytes avoids ZeroDivisionError
        p_zero = DownloadProgress(download_id=1, downloaded_bytes=0, total_bytes=0)
        assert p_zero.percentage == 0

    def test_megabyte_conversions(self):
        one_mb = 1024 * 1024
        p = DownloadProgress(download_id=1, downloaded_bytes=one_mb * 2, total_bytes=one_mb * 5)
        assert p.downloaded_mb == 2.0
        assert p.total_mb == 5.0

    def test_size_strings_kb_and_mb(self):
        # Below 1 MB displays in KB
        p_kb = DownloadProgress(download_id=1, downloaded_bytes=512 * 1024, total_bytes=800 * 1024)
        assert p_kb.downloaded_str == "512.00 KB"
        assert p_kb.total_str == "800.00 KB"

        # Above or equal 1 MB displays in MB
        p_mb = DownloadProgress(download_id=1, downloaded_bytes=1024 * 1024, total_bytes=2 * 1024 * 1024)
        assert p_mb.downloaded_str == "1.00 MB"
        assert p_mb.total_str == "2.00 MB"

    def test_speed_and_speed_str(self, monkeypatch):
        start = 1000.0
        p = DownloadProgress(download_id=1, downloaded_bytes=1024 * 100, total_bytes=1024 * 500, start_time=start)

        # Elapsed = 2 seconds -> downloaded 100 KB in 2s = 50 KB/s
        monkeypatch.setattr(time, "time", lambda: start + 2.0)
        assert p.elapsed_seconds == 2.0
        assert pytest.approx(p.speed_kbps, 0.01) == 50.0
        assert p.speed_str == "50.00 KB/s"

        # Elapsed = 1 second for 2 MB -> speed >= 1024 KB/s displays MB/s
        p_fast = DownloadProgress(download_id=1, downloaded_bytes=2 * 1024 * 1024, total_bytes=5 * 1024 * 1024, start_time=start)
        monkeypatch.setattr(time, "time", lambda: start + 1.0)
        assert p_fast.speed_kbps == 2048.0
        assert p_fast.speed_str == "2.00 MB/s"

    def test_remaining_time(self, monkeypatch):
        start = 1000.0
        # 1000 bytes out of 2000 in 1 second -> remaining 1000 bytes at 1000 B/s = 1s
        p = DownloadProgress(download_id=1, downloaded_bytes=1000, total_bytes=2000, start_time=start)
        monkeypatch.setattr(time, "time", lambda: start + 1.0)
        assert p.remaining_seconds == 1
        assert p.remaining_time_str == "00:00:01"

        # Zero speed / no progress -> unknown
        p_zero_speed = DownloadProgress(download_id=1, downloaded_bytes=0, total_bytes=1000, start_time=start)
        monkeypatch.setattr(time, "time", lambda: start + 1.0)
        assert p_zero_speed.remaining_seconds == -1
        assert p_zero_speed.remaining_time_str == "--:--:--"

    def test_is_complete(self):
        # 0 total bytes
        p1 = DownloadProgress(download_id=1, downloaded_bytes=0, total_bytes=0)
        assert p1.is_complete is False

        # In progress
        p2 = DownloadProgress(download_id=1, downloaded_bytes=50, total_bytes=100)
        assert p2.is_complete is False

        # Exactly complete
        p3 = DownloadProgress(download_id=1, downloaded_bytes=100, total_bytes=100)
        assert p3.is_complete is True

        # Overshot (e.g. metadata rounding)
        p4 = DownloadProgress(download_id=1, downloaded_bytes=110, total_bytes=100)
        assert p4.is_complete is True

    def test_update_and_reset_start_time(self, monkeypatch):
        start = 1000.0
        p = DownloadProgress(download_id=1, downloaded_bytes=10, total_bytes=100, start_time=start)

        p.update(downloaded_bytes=50)
        assert p.downloaded_bytes == 50
        assert p.total_bytes == 100

        p.update(total_bytes=200)
        assert p.downloaded_bytes == 50
        assert p.total_bytes == 200

        monkeypatch.setattr(time, "time", lambda: 2000.0)
        p.reset_start_time()
        assert p.start_time == 2000.0

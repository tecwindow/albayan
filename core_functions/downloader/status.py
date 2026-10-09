import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional


class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ERROR = "error"

    @property
    def _labels_ar(self) -> Dict[str, str]:
        return {
            self.PENDING: "قيد الانتظار",
            self.DOWNLOADING: "يجري التنزيل",
            self.PAUSED: "متوقف مؤقتًا",
            self.CANCELLED: "تم الإلغاء",
            self.COMPLETED: "مكتمل",
            self.ERROR: "خطأ",
        }

    @property
    def label(self) -> str:
        return self._labels_ar.get(self, self.name)


@dataclass
class DownloadProgress:
    """
    Represents the progress details of a single download operation.
    """
    download_id: int
    downloaded_bytes: int
    total_bytes: int
    start_time: float = field(default_factory=time.time)

    def update(self, downloaded_bytes: Optional[int] = None, total_bytes: Optional[int] = None) -> None:
        """
        Updates the progress information.

        Args:
            downloaded_bytes (Optional[int]): Updated value for downloaded bytes.
            total_bytes (Optional[int]): Updated value for total bytes.
        """
        if downloaded_bytes is not None:
            self.downloaded_bytes = downloaded_bytes
        if total_bytes is not None:
            self.total_bytes = total_bytes

    def reset_start_time(self) -> None:
        """
        Resets the start time to the current time.
        """
        self.start_time = time.time()

    @property
    def percentage(self) -> int:
        """
        Returns:
            int: Percentage of the download completed.
        """
        if self.total_bytes <= 0:
            return 0
        return max(0, min(100, int((self.downloaded_bytes / self.total_bytes) * 100)))

    @property
    def downloaded_mb(self) -> float:
        """
        Returns:
            float: Downloaded size in megabytes.
        """
        return self.downloaded_bytes / (1024 * 1024)

    @property
    def total_mb(self) -> float:
        """
        Returns:
            float: Total size in megabytes.
        """
        return self.total_bytes / (1024 * 1024)

    @property
    def downloaded_str(self) -> str:
        """
        Returns:
            str: Human-readable downloaded size (MB or KB).
        """
        mb = self.downloaded_mb
        if mb >= 1:
            return f"{mb:.2f} MB"
        return f"{self.downloaded_bytes / 1024:.2f} KB"

    @property
    def total_str(self) -> str:
        """
        Returns:
            str: Human-readable total size (MB or KB).
        """
        mb = self.total_mb
        if mb >= 1:
            return f"{mb:.2f} MB"
        return f"{self.total_bytes / 1024:.2f} KB"

    @property
    def elapsed_seconds(self) -> float:
        """
        Returns:
            float: Total elapsed time in seconds.
        """
        return time.time() - self.start_time

    @property
    def elapsed_time_str(self) -> str:
        """
        Returns:
            str: Elapsed time formatted as HH:MM:SS.
        """
        return time.strftime('%H:%M:%S', time.gmtime(self.elapsed_seconds))

    @property
    def speed_kbps(self) -> float:
        """
        Returns:
            float: Average download speed in kilobytes per second.
        """
        seconds = self.elapsed_seconds
        return (self.downloaded_bytes / 1024) / seconds if seconds > 0 else 0.0
    
    @property
    def speed_str(self) -> str:
        """
        Returns the download speed as a human-readable string (KB/s or MB/s).
        """
        speed_kbps = self.speed_kbps
        if speed_kbps >= 1024:
            return f"{speed_kbps / 1024:.2f} MB/s"
        return f"{speed_kbps:.2f} KB/s"

    @property
    def remaining_seconds(self) -> int:
        """
        Returns:
            int: Estimated remaining time in seconds, or -1 if unknown.
        """
        if self.total_bytes <= 0 or self.downloaded_bytes >= self.total_bytes:
            return 0
        remaining_bytes = self.total_bytes - self.downloaded_bytes
        speed_bps = self.downloaded_bytes / self.elapsed_seconds if self.elapsed_seconds > 0 else 0
        return max(0, int(remaining_bytes / speed_bps)) if speed_bps > 0 else -1

    @property
    def remaining_time_str(self) -> str:
        """
        Returns:
            str: Estimated remaining time as HH:MM:SS, or '--:--:--' if unknown.
        """
        secs = self.remaining_seconds
        return time.strftime('%H:%M:%S', time.gmtime(secs)) if secs >= 0 else "--:--:--"

    @property
    def is_complete(self) -> bool:
        """
        Returns:
            bool: True if download has completed.
        """
        return self.total_bytes > 0 and self.downloaded_bytes >= self.total_bytes
from typing import List, Union, Set
from PySide6.QtWidgets import QProgressBar
from core_functions.downloader.status import DownloadStatus
from core_functions.downloader.manager import DownloadManager


class SessionProgressBar(QProgressBar):
    """
    A QProgressBar that tracks overall download progress across one or more DownloadManager instances.
    Shows percentage from 0 to 100.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._managers: Set[DownloadManager] = set()
        self._total_files: int = 0
        self._completed_files: int = 0

        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.setFormat("%p%")

    def set_managers(
        self, managers: Union[DownloadManager, List[DownloadManager]]
    ) -> None:
        """Assign one or multiple managers to track."""
        if not isinstance(managers, list):
            managers = [managers]

        self._managers = set(managers)
        self.recalculate_totals()

        for mgr in self._managers:
            mgr.download_finished.connect(self._on_file_finished)
            mgr.status_changed.connect(self._on_status_changed)

    def recalculate_totals(self) -> None:
        """Recompute total downloads that belong to the session."""
        self._total_files = 0

        for mgr in self._managers:
            downloads = mgr.get_downloads(
                [
                    DownloadStatus.PENDING,
                    DownloadStatus.DOWNLOADING,
                    DownloadStatus.PAUSED,
                ]
            )
            self._total_files += len(downloads)

        self._update_progress()

    def _update_progress(self) -> None:
        """Calculate percentage and update the bar."""
        if self._total_files == 0:
            self.setValue(0)
            return

        percentage = int((self._completed_files / self._total_files) * 100)
        percentage = max(0, min(100, percentage))

        self.setValue(percentage)

    def increment(self, count: int = 1) -> None:
        """Increase completed counter."""
        self._completed_files += count
        self._update_progress()

    def decrement(self, count: int = 1) -> None:
        """Decrease completed counter (pause/cancel/error)."""
        self._completed_files = max(0, self._completed_files - count)
        self._update_progress()

    def finish_session(self) -> None:
        """Reset progress bar."""
        self._completed_files = 0
        self._total_files = 0

    def _on_file_finished(self, download_id: int) -> None:
        """Triggered when a download finishes."""
        self.increment()
        if self._completed_files >= self._total_files:
            self.finish_session()

    def _on_status_changed(self, download_id: int, status: DownloadStatus) -> None:
        """Triggered when a download changes state."""
        if status in (
            DownloadStatus.PAUSED,
            DownloadStatus.CANCELLED,
            DownloadStatus.ERROR,
        ):
            self.decrement()

from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QObject

from core_functions.downloader.status import DownloadStatus, DownloadProgress
from core_functions.downloader.manager import DownloadManager
from core_functions.Reciters import RecitersManager
from core_functions.quran.types import Surah

from typing import List, Dict, Any, Optional
from utils.audio_player import status
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class DownloadListModel(QAbstractListModel):
    """
    Model that wraps DownloadManager data for a QListView.
    Ensures efficiency with large lists and provides accessibility support.
    """

    ItemRole = Qt.ItemDataRole.UserRole
    ProgressRole = Qt.ItemDataRole.UserRole + 1
    StatusRole = Qt.ItemDataRole.UserRole + 2
    percentageRole = Qt.ItemDataRole.UserRole + 3
    speedRole = Qt.ItemDataRole.UserRole + 4
    downloadedSizeRole = Qt.ItemDataRole.UserRole + 5
    remainingTimeRole = Qt.ItemDataRole.UserRole + 6
    elapsedTimeRole = Qt.ItemDataRole.UserRole + 7

    def __init__(
        self,
        parent: QObject,
        manager: DownloadManager,
        reciter_manager: RecitersManager,
        surahs: List[Surah],
    ):
        super().__init__(parent)
        self.manager = manager
        self.reciter_manager = reciter_manager
        self.surahs = surahs
        self._download_ids: List[int] = []
        self._initialize_from_manager()

        # Connect signals
        self.manager.downloads_added.connect(self.on_downloads_added)
        self.manager.download_progress.connect(self.on_download_progress)
        self.manager.status_changed.connect(self.on_status_changed)
        self.manager.download_finished.connect(self.on_download_finished)
        self.manager.error.connect(self.on_download_error)
        self.manager.cancelled_all.connect(self.on_cancelled_all)
        self.manager.download_deleted.connect(self.on_download_deleted)
        self.manager.downloads_cleared.connect(self.on_downloads_cleared)

        # Cache for transient progress data (speed, eta, etc.) which isn't in main storage
        self._progress_cache: Dict[int, DownloadProgress] = {}

    def _initialize_from_manager(self):
        all_downloads = self.manager.get_downloads()
        self._download_ids = [d["id"] for d in all_downloads]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._download_ids)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        row = index.row()
        if row < 0 or row >= len(self._download_ids):
            return None

        download_id = self._download_ids[row]
        item_data = self.manager.get_download(download_id)
        reciter_data = self.reciter_manager.get_reciter(item_data["reciter_id"])

        if not item_data:
            return None

        file_name = item_data.get("filename", "ملف غير معروف")
        status = item_data.get("status", DownloadStatus.ERROR)
        size_text = item_data.get("size_text", "الحجم غير معروف")
        reciter_display_text = reciter_data.get("display_text", "قارئ غير معروف")
        surah = self.surahs[item_data["surah_number"] - 1]
        ayah_number = item_data.get("ayah_number")
        progress: DownloadProgress = self._progress_cache.get(download_id)

        if role == Qt.ItemDataRole.DisplayRole:
            return self._build_display_text(item_data, reciter_data, surah)

        elif role == Qt.ItemDataRole.ToolTipRole:
            return self._build_progress_text(progress, status, item_data)

        if role == Qt.ItemDataRole.AccessibleDescriptionRole:
            return self._build_progress_text(progress, status, item_data)

        elif role == self.ItemRole:
            return item_data

        elif role == self.StatusRole:
            return item_data["status"]

        elif role == self.ProgressRole:
            return progress

        elif role == self.percentageRole:
            return self.get_item_percentage(download_id)

        elif role == self.speedRole:
            return self.get_item_speed(download_id)

        elif role == self.downloadedSizeRole:
            return self.get_item_downloaded_size(download_id)

        elif role == self.remainingTimeRole:
            return self.get_item_remaining_time(download_id)

        elif role == self.elapsedTimeRole:
            return self.get_item_elapsed_time(download_id)

        return None

    def on_downloads_added(self, new_items: List[Dict]):
        if not new_items:
            return

        first_row = len(self._download_ids)
        last_row = first_row + len(new_items) - 1

        self.beginInsertRows(QModelIndex(), first_row, last_row)
        for item in new_items:
            self._download_ids.append(item["id"])
        self.endInsertRows()

    def on_download_progress(self, progress: DownloadProgress):
        # Update cache
        self._progress_cache[progress.download_id] = progress

        try:
            row = self._download_ids.index(progress.download_id)
            index = self.index(row, 0)
            roles = [
                self.ProgressRole,
                Qt.ItemDataRole.ToolTipRole,
                Qt.ItemDataRole.AccessibleDescriptionRole,
            ]
            self.dataChanged.emit(index, index, roles)
        except ValueError:
            pass

    def on_status_changed(self, download_id: int, new_status: DownloadStatus):
        try:
            row = self._download_ids.index(download_id)
            index = self.index(row, 0)
            self.dataChanged.emit(index, index, [self.StatusRole])
        except ValueError:
            pass

    def on_download_finished(self, download_id: int, file_path: str):
        self._progress_cache.pop(
            download_id, None
        )  # Clear progress cache on completion
        try:
            row = self._download_ids.index(download_id)
            index = self.index(row, 0)
            self.dataChanged.emit(
                index,
                index,
                [
                    self.StatusRole,
                    self.ProgressRole,
                    Qt.ItemDataRole.AccessibleDescriptionRole,
                ],
            )
        except ValueError:
            pass

    def on_download_error(self, download_id: int, error_msg: str):
        try:
            row = self._download_ids.index(download_id)
            index = self.index(row, 0)
            self.dataChanged.emit(
                index,
                index,
                [
                    self.StatusRole,
                    Qt.ItemDataRole.ToolTipRole,
                    Qt.ItemDataRole.AccessibleDescriptionRole,
                ],
            )
        except ValueError:
            pass

    def on_cancelled_all(self):
        self.beginResetModel()
        self._progress_cache.clear()
        self.endResetModel()

    def on_download_deleted(self, download_id: int):
        try:
            row = self._download_ids.index(download_id)
            self.beginRemoveRows(QModelIndex(), row, row)
            self._download_ids.pop(row)
            if download_id in self._progress_cache:
                del self._progress_cache[download_id]
            self.endRemoveRows()
        except ValueError:
            pass

    def on_downloads_cleared(self):
        self.beginResetModel()
        self._progress_cache.clear()
        self._download_ids.clear()
        self.endResetModel()

    def _build_display_text(
        self, item_data: dict, reciter_data: dict, surah: Surah
    ) -> str:
        file_name = item_data.get("filename", "ملف غير معروف")
        status = item_data.get("status", DownloadStatus.ERROR)
        reciter_text = reciter_data.get("display_text", "قارئ غير معروف")
        ayah_number = item_data.get("ayah_number")

        if ayah_number is None:
            surah_info = f"سورة {surah.name}"
        elif ayah_number == 0:
            surah_info = f"بسملة من سورة {surah.name}"
        else:
            surah_info = f"آية {ayah_number} من سورة {surah.name}"

        return f"{file_name}, {surah_info}, {reciter_text}, {status.label}"

    def _build_progress_text(
        self, progress: DownloadProgress, status: DownloadStatus, item_data: dict
    ) -> str:

        if progress and (
            progress.is_complete
            or status
            in (
                DownloadStatus.CANCELLED,
                DownloadStatus.COMPLETED,
                DownloadStatus.ERROR,
                DownloadStatus.PAUSED,
            )
        ):
            return f"{progress.percentage}%"

        if not progress:
            # fallback if no progress data to use item data
            if status in (DownloadStatus.PAUSED, DownloadStatus.ERROR):
                percentage = (
                    item_data.get("downloaded_bytes", 0)
                    / item_data.get("total_bytes", 1)
                    * 100
                    if item_data.get("total_bytes", 1) > 0
                    else 0
                )
                return f"{percentage:.2f}%"
            else:
                return ""

        return (
            f"{progress.percentage}%, "
            f"تم تنزيل {progress.downloaded_str} من {progress.total_str}, "
            f"السرعة: {progress.speed_str}, "
            f"الوقت المتبقي: {progress.remaining_time_str}"
            f", الوقت المنقضي: {progress.elapsed_time_str}"
        )

    def get_download_progress(self, download_id: int) -> Optional[DownloadProgress]:
        return self._progress_cache.get(download_id)

    def get_item_percentage(self, download_id: int) -> str:
        """Get current download percentage for a given download ID."""
        progress = self.get_download_progress(download_id)
        if not progress:
            download_data = self.manager.get_download(download_id)
            percentage = (
                download_data.get("downloaded_bytes", 0)
                / download_data.get("total_bytes", 1)
                * 100
                if download_data.get("total_bytes", 1) > 0
                else 0
            )
        else:
            percentage = progress.percentage

        return f"{percentage:.0f}%"

    def get_item_status(self, download_id: int) -> DownloadStatus:
        """Get current download status for a given download ID."""
        download_data = self.manager.get_download(download_id)
        return download_data.get("status", DownloadStatus.ERROR)

    def get_item_remaining_time(self, download_id: int) -> str:
        """Get current download remaining time for a given download ID."""
        progress = self.get_download_progress(download_id)
        if progress:
            return progress.remaining_time_str
        return "غير معروف"

    def get_item_elapsed_time(self, download_id: int) -> str:
        """Get current download elapsed time for a given download ID."""
        progress = self.get_download_progress(download_id)
        if progress:
            return progress.elapsed_time_str
        return "غير معروف"

    def get_item_speed(self, download_id: int) -> str:
        """Get current download speed for a given download ID."""
        progress = self.get_download_progress(download_id)
        if progress:
            return progress.speed_str
        return "غير معروف"

    def get_item_downloaded_size(self, download_id: int) -> str:
        """Get current download downloaded size for a given download ID."""
        progress = self.get_download_progress(download_id)
        if progress:
            return f"تم تنزيل {progress.downloaded_str} من {progress.total_str}"
        return "غير معروف"

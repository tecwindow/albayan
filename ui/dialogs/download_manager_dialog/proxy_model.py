from utils.settings import Config
from PySide6.QtCore import QSortFilterProxyModel, Qt, QModelIndex
from core_functions.downloader.status import DownloadStatus
from .download_model import DownloadListModel


class DownloadProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_status = None
        self.filter_string = ""
        self.setDynamicSortFilter(self.dynamicSortFilter())

    def set_status_filter(self, status: DownloadStatus):
        self.filter_status = status
        self.invalidateFilter()

    def set_text_filter(self, text: str):
        self.filter_string = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # Check source model
        source_model = self.sourceModel()
        if not source_model:
            return True

        index = source_model.index(source_row, 0, source_parent)

        # 1. Check Status
        if self.filter_status is not None:
            item_status = index.data(DownloadListModel.StatusRole)
            if item_status != self.filter_status:
                return False

        # 2. Check Text (Filename)
        if self.filter_string:
            filename = index.data(Qt.ItemDataRole.DisplayRole)
            if not filename or self.filter_string not in filename.lower():
                return False

        return True

    def dynamicSortFilter(self) -> bool:
        return Config.downloading.auto_refresh_downloads_lists

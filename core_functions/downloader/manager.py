import os
from typing import List, Dict, Optional, Union
from pathlib import Path
from PySide6.QtCore import QObject, QThreadPool, Signal

from core_functions import info

from .worker import DownloadWorker
from .status import DownloadStatus, DownloadProgress
from .db import DownloadDB
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class DownloadManager(QObject):
    download_progress = Signal(DownloadProgress)
    download_finished = Signal(int, str)  # id, file_path
    error = Signal(int, str)  # id, error message
    status_changed = Signal(int, DownloadStatus)  # id, new status
    cancelled_all = Signal()
    downloads_added = Signal(list)  # list of new download items
    download_deleted = Signal(int)
    downloads_cleared = Signal()

    def __init__(
        self,
        max_workers: int = 3,
        load_history: bool = False,
        save_history: bool = False,
        download_db: Optional[DownloadDB] = None,
    ):
        super().__init__()
        logger.debug("Initializing DownloaderManager")
        self.save_history = save_history
        self.pool = QThreadPool.globalInstance()
        self.pool.setMaxThreadCount(max_workers)
        self._downloads: Dict[int, Dict] = {}
        self._pause_all = False
        self._cancel_all = False
        self.is_shutdown = False
        self.db = download_db

        if not self.db and (save_history or load_history):
            raise ValueError(
                "DownloadDB instance is required for saving or loading history."
            )

        if load_history and self.db:
            self._load_history()

        logger.debug(
            "DownloaderManager initialized with max_workers=%d, load_history=%s, save_history=%s",
            max_workers,
            load_history,
            save_history,
        )

    def _load_history(self):
        """Load download history from the database."""
        logger.debug("Loading download history from database")

        if not self.db:
            logger.warning("No database instance available to load history.")
            return

        for item in self.db.all():
            self._downloads[item.id] = {
                "id": item.id,
                "url": item.url,
                "filename": item.filename,
                "folder_path": item.folder_path,
                "status": item.status,
                "downloaded_bytes": item.downloaded_bytes,
                "total_bytes": item.total_bytes,
                # "file_hash": item.file_hash,
            }
            self.set_size_text(item.id, item.total_bytes)

            # Include any additional fields that might exist in the DB model
            other_keys = set(item.__dict__.keys()) - set(
                self.db.download_table.__table__.c
            )
            for key in other_keys:
                self._downloads[item.id][key] = getattr(item, key)

        logger.info("Loaded %d download items from history", len(self._downloads))

    def add_new_downloads(self, download_items: List[Dict], download_folder: str):
        """Add multiple download items."""
        logger.debug("Adding new download items, count=%d", len(download_items))

        if not isinstance(download_items, list):
            raise ValueError("download_items must be a list of dictionaries.")

        # Prepare items for insertion
        items_to_process = []
        for entry in download_items:
            filename = os.path.basename(entry["url"])
            item_data = {
                "filename": filename,
                "folder_path": download_folder,
                "status": DownloadStatus.PENDING,
                "downloaded_bytes": 0,
                "total_bytes": 0,
                **entry,
            }
            items_to_process.append(item_data)

        # Bulk insert/upsert to DB if applicable
        generated_ids = []
        if self.db and self.save_history:
            generated_ids = self.db.upsert_many(items_to_process)

        # Populate memory cache
        new_items = []
        for index, item_data in enumerate(items_to_process):
            if generated_ids and index < len(generated_ids):
                download_id = generated_ids[index]
            else:
                # Fallback or non-DB mode
                download_id = len(self._downloads) + 1 + index

            item_data["id"] = download_id
            item_data["size_text"] = None
            self._downloads[download_id] = item_data
            new_items.append(item_data)

        if new_items:
            self.downloads_added.emit(new_items)

        logger.info("Added %d new download items", len(download_items))

    def add_download(self, url: str, download_folder: str, **extra_data):
        """
        Add a single download item.
        Optionally accepts extra_data like metadata to be stored with the download.
        """
        logger.debug("Adding single download item: %s", url)
        item = {"url": url}
        item.update(extra_data)
        self.add_new_downloads([item], download_folder)
        logger.info("Added download item: %s", url)

    def start(self):
        """Start processing the download queue (PENDING items only)."""
        logger.info("Starting downloading process")

        for download_id, info in self._downloads.items():
            # Only start PENDING items.
            # Ignore PAUSED, ERROR, COMPLETED, CANCELLED unless explicitly reset to PENDING.
            if info["status"] != DownloadStatus.PENDING:
                continue

            # Check if worker is already running (shouldn't be for PENDING, but safety check)
            if info.get("worker") and info["worker"].is_running():
                continue

            self._start_download(download_id)

    def _on_progress(self, progress: DownloadProgress):
        self.download_progress.emit(progress)

    def _on_status(self, download_id: int, new_status: DownloadStatus):
        logger.debug(
            "Download ID %d status changed to %s", download_id, new_status.name
        )

        if download_id not in self._downloads:
            logger.warning(
                "Received status update for unknown download ID: %d", download_id
            )
            return

        self._downloads[download_id]["status"] = new_status
        self.status_changed.emit(download_id, new_status)

        if self.db and self.save_history:
            self.db.update_status(download_id, new_status)

    def set_size_text(self, download_id: int, total_bytes: int) -> None:
        if download_id in self._downloads:
            self._downloads[download_id]["total_bytes"] = total_bytes
            size_text = (
                f"{total_bytes / (1024 * 1024):.2f} MB"
                if total_bytes > 1024 * 1024
                else f"{total_bytes / 1024:.2f} KB"
            )
            self._downloads[download_id]["size_text"] = size_text
            # logger.debug("Set size text for download ID %d: %s", download_id, size_text)
        # else:
        # logger.warning("Attempted to set size text for unknown download ID: %d", download_id)

    def _on_error(self, download_id: int, message: str):
        logger.error("Download error (ID: %d): %s", download_id, message)
        self.error.emit(download_id, message)

    def _on_finished(self, download_id: int, filename: str):
        logger.debug("Download finished (ID: %d): %s", download_id, filename)
        self.download_finished.emit(download_id, filename)

    def pause(self, download_id: int):
        logger.debug("Pausing download ID: %d", download_id)
        if worker := self._downloads.get(download_id, {}).get("worker"):
            worker.pause()

    def resume(self, download_id: int):
        logger.debug("Resuming download ID: %d", download_id)
        if worker := self._downloads.get(download_id, {}).get("worker"):
            worker.resume()
        else:
            # No existing worker, so start a new one
            self._start_download(download_id)

    def cancel(self, download_id: int):
        logger.debug("Cancelling download ID: %d", download_id)
        if worker := self._downloads.get(download_id, {}).get("worker"):
            worker.cancel()

    def shutdown(self, download_id: int):
        logger.debug("Shutting down download ID: %d", download_id)
        if worker := self._downloads.get(download_id, {}).get("worker"):
            worker.shutdown()

    def _start_download(self, download_id: int):
        """Internal method to start a download worker for a given download ID."""
        logger.debug("Starting download worker for ID: %d", download_id)
        if download_id not in self._downloads:
            logger.warning(
                "Attempted to start download for unknown ID: %d", download_id
            )
            return

        worker = DownloadWorker(
            self._downloads[download_id],
            callbacks={
                "progress": self._on_progress,
                "finished": self._on_finished,
                "status": self._on_status,
                "error": self._on_error,
            },
            manager=self,
        )
        self._downloads[download_id]["worker"] = worker
        self.pool.start(worker)
        logger.info("Download worker started for ID: %d", download_id)

    def restart(self, download_id: int):
        logger.debug("Restarting download ID: %d", download_id)

        info = self._downloads.get(download_id)
        if not info:
            return

        info["status"] = DownloadStatus.PENDING
        info["downloaded_bytes"] = 0

        if self.db and self.save_history:
            self.db.update_status(download_id, DownloadStatus.PENDING)

        self._start_download(download_id)

    def pause_all(self):
        logger.info("Pausing all downloads")
        self._pause_all = True

        if self.save_history and self.db:
            self.db.update_by_status(
                old_status=[DownloadStatus.DOWNLOADING, DownloadStatus.PENDING],
                new_status=DownloadStatus.PAUSED,
            )

        for download_item in self.get_downloads(DownloadStatus.DOWNLOADING):
            self.pause(download_item["id"])

        for download_item in self.get_downloads(
            [DownloadStatus.DOWNLOADING, DownloadStatus.PENDING]
        ):
            download_item["status"] = DownloadStatus.PAUSED

    def resume_all(self):
        logger.info("Resuming all downloads")
        self._pause_all = False
        for download_item in self.get_downloads(DownloadStatus.PAUSED):
            self.resume(download_item["id"])
            download_item["status"] = DownloadStatus.PENDING

        if self.save_history and self.db:
            self.db.update_by_status(
                old_status=DownloadStatus.PAUSED, new_status=DownloadStatus.PENDING
            )

    def cancel_all(self, update_memory_status: bool = True, is_shutdown: bool = False):
        logger.info("Cancelling all downloads")
        self.pool.clear()
        self.is_shutdown = is_shutdown

        for download_item in self.get_downloads(DownloadStatus.DOWNLOADING):
            self.cancel(download_item["id"])

        if self.save_history and self.db:
            self.db.update_by_status(
                old_status=[DownloadStatus.DOWNLOADING, DownloadStatus.PENDING],
                new_status=DownloadStatus.CANCELLED,
            )

        # If shutting down, ensure PAUSED downloads are also properly handled
        if is_shutdown:
            for download_item in self.get_downloads(DownloadStatus.PAUSED):
                self.shutdown(download_item["id"])

        # Update in-memory statuses as well
        if update_memory_status:
            for download_item in self.get_downloads(
                [DownloadStatus.DOWNLOADING, DownloadStatus.PENDING]
            ):
                self._downloads[download_item["id"]][
                    "status"
                ] = DownloadStatus.CANCELLED

        self.cancelled_all.emit()

    def restart_all(self):
        logger.info("Restarting all downloads")

        if self.save_history and self.db:
            self.db.update_by_status(
                old_status=[DownloadStatus.CANCELLED, DownloadStatus.ERROR],
                new_status=DownloadStatus.PENDING,
            )

        for download in self.get_downloads(
            [DownloadStatus.CANCELLED, DownloadStatus.ERROR]
        ):
            self._downloads[download["id"]]["status"] = DownloadStatus.PENDING
            self._start_download(download["id"])

    def delete(self, download_id: int, delete_file: bool = True):
        logger.debug("Deleting download ID: %d", download_id)
        if download_id in self._downloads:
            if worker := self._downloads[download_id].get("worker"):
                worker.cancel()
            if self.db and self.save_history:
                self.db.delete(download_id)
            if delete_file:
                file_path = (
                    Path(self._downloads[download_id]["folder_path"])
                    / self._downloads[download_id]["filename"]
                )
                file_path.unlink(missing_ok=True)
                logger.info("Deleted file: %s", file_path)
            del self._downloads[download_id]
            logger.info("Deleted download ID: %d", download_id)
            self.download_deleted.emit(download_id)
        else:
            logger.warning(
                "Attempted to delete non-existent download ID: %d", download_id
            )

    def delete_by_status(self, status: Union[DownloadStatus, List[DownloadStatus]]):
        logger.info("Deleting downloads with status: %s", status)
        for download_item in self.get_downloads(status):
            self.delete(download_item["id"])
        logger.info("Deleted downloads with status: %s", status)

    def delete_all(self, delete_files: bool = True):
        logger.debug("Deleting all downloads")
        if self.db:
            self.db.delete_all()
        if delete_files:
            for info in self._downloads.values():
                file_path = Path(info["folder_path"]) / info["filename"]
                file_path.unlink(missing_ok=True)
                logger.info("Deleted file: %s", file_path)
        self._downloads.clear()
        logger.info("All downloads deleted")
        self.downloads_cleared.emit()

    def get_download(self, download_id: int) -> Optional[Dict]:
        """Return the download item by ID, or None if not found."""
        return self._downloads.get(download_id)

    def get_downloads(
        self, status: Optional[Union[DownloadStatus, List[DownloadStatus]]] = None
    ) -> List[Dict]:
        """
        Return a list of downloads filtered by status.
        - If `status` is None → return all downloads.
        - If `status` is a single DownloadStatus → return matching downloads.
        - If `status` is a list → return downloads matching any of the statuses.
        """
        if status is None:
            logger.debug("Fetching all downloads (no status filter applied)")
            return list(self._downloads.values())

        if not isinstance(status, list):
            status = [status]

        logger.debug("Fetching downloads with statuses: %s", [s.name for s in status])
        return [info for info in self._downloads.values() if info["status"] in status]

    def has_active_downloads(self) -> bool:
        """Check if there are any active downloads (DOWNLOADING or PENDING)."""
        active_statuses = [DownloadStatus.DOWNLOADING, DownloadStatus.PENDING]
        return bool(self.get_downloads(active_statuses))

    def resume_interrupted_downloads(self):
        """
        Resume downloads that were interrupted (status DOWNLOADING or PENDING).
        Should be called on application startup.
        """
        logger.info("Checking for interrupted downloads to resume...")

        # 1. Downloads stuck in DOWNLOADING state (e.g. app crashed or closed)
        # We need to reset them to PENDING so they can be picked up by start()
        # but WITHOUT resetting downloaded_bytes (so they resume).
        interrupted = self.get_downloads(
            [DownloadStatus.DOWNLOADING, DownloadStatus.PENDING]
        )
        for download in interrupted:
            logger.debug(f"resuming interrupted download ID: {download['id']}")
            self._downloads[download["id"]]["status"] = DownloadStatus.PENDING
            if self.db and self.save_history:
                self.db.update_status(download["id"], DownloadStatus.PENDING)

        # 2. PENDING items are already PENDING, so start() will pick them up naturally.

        # 3. Trigger start to process the queue
        self.start()

        count = len(interrupted) + len(self.get_downloads(DownloadStatus.PENDING))
        logger.info(f"Resumed {count} interrupted/pending downloads.")

import os
import requests
from typing import Callable, Dict
from PySide6.QtCore import QRunnable, Slot, QThread, QMutex, QWaitCondition
from .status import DownloadStatus, DownloadProgress
from .db import DownloadDB
from utils.func import calculate_sha256
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class DownloadWorker(QRunnable):
    def __init__(self, item_data: dict, callbacks: Dict[str, Callable], manager):
        super().__init__()
        self.item = item_data
        self.callbacks = callbacks
        self.manager = manager
        self.db: DownloadDB = self.manager.db

        self.filename = item_data["filename"]
        self.folder_path = item_data["folder_path"]
        self.final_path = os.path.join(self.folder_path, self.filename)
        self.temp_path = self.final_path + ".part"
        self.url = item_data["url"]
        self.download_id = item_data["id"]

        self._running = False
        self._paused = False
        self._resume_requested = False
        self._cancelled = False

        # Synchronization primitives
        self._pause_mutex = QMutex()
        self._pause_condition = QWaitCondition()

        logger.debug(f"[Worker Init] ID={self.download_id}, URL={self.url}")

    @Slot()
    def run(self) -> None:
        logger.debug(f"[Download Start] ID={self.download_id}")
        try:
            self._running = True
            self._download_file()
        except Exception as e:
            logger.exception(f"[Download Error] ID={self.download_id}")
            self.callbacks["status"](self.download_id, DownloadStatus.ERROR)
            self.callbacks["error"](self.download_id, str(e))
        finally:
            self._running = False

    def _download_file(self) -> None:
        os.makedirs(self.folder_path, exist_ok=True)

        resume_header = {}
        downloaded_bytes = (
            os.path.getsize(self.temp_path) if os.path.exists(self.temp_path) else 0
        )
        file_mode = "ab" if downloaded_bytes > 0 else "wb"

        if downloaded_bytes > 0:
            resume_header["Range"] = f"bytes={downloaded_bytes}-"

        with requests.get(
            self.url, stream=True, headers=resume_header, timeout=10
        ) as r:
            r.raise_for_status()
            content_length = int(r.headers.get("content-length", 0))
            total_bytes = downloaded_bytes + content_length
            self.manager.set_size_text(self.download_id, total_bytes)

            progress = DownloadProgress(
                download_id=self.download_id,
                downloaded_bytes=downloaded_bytes,
                total_bytes=total_bytes,
            )
            last_percentage = progress.percentage

            if self.can_report_download:
                self.callbacks["status"](self.download_id, DownloadStatus.DOWNLOADING)

            with open(self.temp_path, file_mode) as f:
                for chunk in r.iter_content(chunk_size=256 * 1024):

                    if self._cancelled or self.manager._cancel_all:
                        logger.info(f"[Cancelled] ID={self.download_id}")
                        self.callbacks["status"](
                            self.download_id, DownloadStatus.CANCELLED
                        )
                        return

                    self._pause_mutex.lock()
                    try:
                        while self._paused or self.manager._pause_all:
                            if (
                                self.manager.is_shutdown
                                or self._cancelled
                                or self.manager._cancel_all
                            ):
                                return

                            self.callbacks["status"](
                                self.download_id, DownloadStatus.PAUSED
                            )
                            self._pause_condition.wait(self._pause_mutex)

                        if self._resume_requested:
                            progress.reset_start_time()  # Reset timer when resumed
                            if self.can_report_download():
                                self.callbacks["status"](
                                    self.download_id, DownloadStatus.DOWNLOADING
                                )
                            self._resume_requested = False

                    finally:
                        self._pause_mutex.unlock()

                    if chunk:
                        f.write(chunk)
                        downloaded_bytes += len(chunk)
                        last_percentage = progress.percentage
                        progress.update(downloaded_bytes)

                        if (
                            progress.percentage - last_percentage >= 1
                            or downloaded_bytes == total_bytes
                        ):
                            self.callbacks["progress"](progress)

                            if self.db:
                                self.db.upsert(
                                    {
                                        **self.item,
                                        "downloaded_bytes": downloaded_bytes,
                                        "total_bytes": total_bytes,
                                        "status": DownloadStatus.DOWNLOADING,
                                    }
                                )

        if not self._cancelled and not self.manager._cancel_all:
            os.replace(self.temp_path, self.final_path)
            logger.info(f"[Download Completed] ID={self.download_id}")
            self.callbacks["status"](self.download_id, DownloadStatus.COMPLETED)
            self.callbacks["finished"](self.download_id, self.final_path)

            if self.db:
                # file_hash = calculate_sha256(self.final_path)
                self.db.upsert(
                    {
                        **self.item,
                        "downloaded_bytes": downloaded_bytes,
                        "total_bytes": total_bytes,
                        # "file_hash": file_hash,
                        "status": DownloadStatus.COMPLETED,
                    }
                )

    def is_running(self) -> bool:
        return self._running

    def can_report_download(self) -> bool:
        return (
            not self._paused
            and not self._cancelled
            and not self.manager._pause_all
            and not self.manager._cancel_all
            and not self.manager.is_shutdown
        )

    def pause(self) -> None:
        logger.debug(f"[Paused] ID={self.download_id}")
        self._pause_mutex.lock()
        self._paused = True
        self._pause_mutex.unlock()
        self.callbacks["status"](self.download_id, DownloadStatus.PAUSED)

    def resume(self) -> None:
        logger.debug(f"[Resumed] ID={self.download_id}")
        if self.is_running():
            self._pause_mutex.lock()
            self._paused = False
            self._resume_requested = True
            self._pause_condition.wakeAll()
            self._pause_mutex.unlock()
            self.callbacks["status"](self.download_id, DownloadStatus.DOWNLOADING)

    def cancel(self) -> None:
        logger.debug(f"[Cancel Requested] ID={self.download_id}")
        self._pause_mutex.lock()
        self._cancelled = True
        self._pause_condition.wakeAll()
        self._pause_mutex.unlock()
        self.delete_temp_file()
        self.callbacks["status"](self.download_id, DownloadStatus.CANCELLED)

    def shutdown(self) -> None:
        logger.debug(f"[Shutdown Requested] ID={self.download_id}")
        if self.is_running():
            self._pause_mutex.lock()
            self._cancelled = True
            self._pause_condition.wakeAll()
            self._pause_mutex.unlock()

    def delete_temp_file(self) -> None:
        if os.path.exists(self.temp_path):
            while True:
                try:
                    os.unlink(self.temp_path)
                    break
                except PermissionError:
                    QThread.msleep(100)
            logger.debug(f"[Temp File Deleted] ID={self.download_id}")

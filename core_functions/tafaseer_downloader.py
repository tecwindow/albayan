import os
import time
import zipfile
import sqlite3
import requests
from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import QThread, Signal
from utils.logger import LoggerManager
from utils.paths import paths
from core_functions.tafaseer import Category

logger = LoggerManager.get_logger(__name__)


def format_bytes(bytes_count: int) -> str:
    """Formats bytes into human readable string (KB, MB, GB)."""
    if bytes_count < 1024:
        return f"{bytes_count} بايت"
    elif bytes_count < 1024 * 1024:
        return f"{bytes_count / 1024:.1f} ك.ب"
    elif bytes_count < 1024 * 1024 * 1024:
        return f"{bytes_count / (1024 * 1024):.2f} م.ب"
    else:
        return f"{bytes_count / (1024 * 1024 * 1024):.2f} ج.ب"


class TafaseerDownloadThread(QThread):
    """
    Background worker thread to download a Tafsir archive (.zip)
    with automatic failover across multiple mirrors, pause/cancel support,
    and automatic database extraction and validation.
    """

    # Signals
    download_progress = Signal(str, int, int, float, str)  # (tafsir_id, downloaded_bytes, total_bytes, percent, speed_text)
    status_changed = Signal(str, str)                      # (tafsir_id, message)
    mirror_switched = Signal(str, str, int)                # (tafsir_id, mirror_url, mirror_index)
    download_finished = Signal(str, str)                   # (tafsir_id, final_db_path)
    download_error = Signal(str, str)                      # (tafsir_id, error_message)
    download_cancelled = Signal(str)                       # (tafsir_id)

    def __init__(
        self,
        tafsir_id: str,
        mirrors: List[str],
        dest_dir: Optional[Path] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.tafsir_id = tafsir_id
        self.mirrors = list(mirrors)
        self.dest_dir = dest_dir or paths.tafaseer_folder
        self.dest_dir.mkdir(parents=True, exist_ok=True)

        info = Category.get_tafsir_info(tafsir_id)
        self.zip_filename = info.get("zip_filename", f"{tafsir_id}.zip") if info else f"{tafsir_id}.zip"
        self.db_filename = info.get("db_filename", f"{tafsir_id}.db") if info else f"{tafsir_id}.db"

        self.temp_zip_path = self.dest_dir / f"{self.zip_filename}.part"
        self.final_zip_path = self.dest_dir / self.zip_filename
        self.final_db_path = self.dest_dir / self.db_filename

        self._cancelled = False
        self._session: Optional[requests.Session] = None

    def cancel(self):
        """Requests cancellation of active download."""
        logger.info(f"Cancellation requested for tafsir download: {self.tafsir_id}")
        self._cancelled = True
        if self._session:
            try:
                self._session.close()
            except Exception:
                pass

    def run(self):
        logger.info(f"Starting download for tafsir: {self.tafsir_id} with {len(self.mirrors)} mirrors.")
        self.status_changed.emit(self.tafsir_id, "جارٍ بدء الاتصال بالخادم...")

        success = False
        last_error = "لا توجد روابط متاحة للتنزيل."

        for index, mirror_url in enumerate(self.mirrors, start=1):
            if self._cancelled:
                break

            logger.info(f"Attempting mirror #{index}: {mirror_url}")
            self.mirror_switched.emit(self.tafsir_id, mirror_url, index)
            self.status_changed.emit(
                self.tafsir_id,
                f"جارٍ الاتصال (الرابط {index} من {len(self.mirrors)})..."
            )

            try:
                self._download_from_url(mirror_url)
                if self._cancelled:
                    break

                # If download completed, extract and verify
                self.status_changed.emit(self.tafsir_id, "جارٍ فك الضغط وتثبيت قاعدة البيانات...")
                self._extract_and_verify()
                success = True
                break

            except requests.RequestException as e:
                logger.warning(f"Mirror #{index} failed for {self.tafsir_id}: {e}")
                last_error = f"تعذر التحميل من الرابط {index}: {str(e)}"
                # Clean up partial file on switch if needed
                if self.temp_zip_path.exists():
                    try:
                        self.temp_zip_path.unlink()
                    except Exception:
                        pass
                continue
            except Exception as e:
                logger.error(f"Unexpected error on mirror #{index} for {self.tafsir_id}: {e}", exc_info=True)
                last_error = f"خطأ أثناء المعالجة: {str(e)}"
                if self.temp_zip_path.exists():
                    try:
                        self.temp_zip_path.unlink()
                    except Exception:
                        pass
                continue

        if self._cancelled:
            logger.info(f"Download cancelled for tafsir: {self.tafsir_id}")
            self._cleanup_temp_files()
            self.download_cancelled.emit(self.tafsir_id)
        elif success:
            logger.info(f"Tafsir {self.tafsir_id} downloaded and verified successfully at {self.final_db_path}.")
            self.download_finished.emit(self.tafsir_id, str(self.final_db_path))
        else:
            logger.error(f"All mirrors failed for tafsir: {self.tafsir_id}. Last error: {last_error}")
            self._cleanup_temp_files()
            self.download_error.emit(
                self.tafsir_id,
                f"فشل تنزيل التفسير من جميع الروابط المتاحة.\n{last_error}"
            )

    def _download_from_url(self, url: str):
        self._session = requests.Session()
        headers = {
            "User-Agent": "Albayan-Quran-App/6.2.1",
        }

        downloaded_bytes = 0
        if self.temp_zip_path.exists():
            downloaded_bytes = self.temp_zip_path.stat().st_size
            if downloaded_bytes > 0:
                headers["Range"] = f"bytes={downloaded_bytes}-"

        response = self._session.get(url, stream=True, headers=headers, timeout=20)

        # Handle 416 Range Not Satisfiable (retry fresh)
        if response.status_code == 416:
            logger.warning("HTTP 416: Range invalid, restarting fresh download.")
            response.close()
            if self.temp_zip_path.exists():
                self.temp_zip_path.unlink()
            downloaded_bytes = 0
            headers.pop("Range", None)
            response = self._session.get(url, stream=True, headers=headers, timeout=20)

        response.raise_for_status()

        if response.status_code == 206:
            file_mode = "ab"
            content_length = int(response.headers.get("Content-Length", 0))
            total_bytes = downloaded_bytes + content_length
        else:
            file_mode = "wb"
            downloaded_bytes = 0
            total_bytes = int(response.headers.get("Content-Length", 0))

        chunk_size = 64 * 1024  # 64 KB
        start_time = time.time()
        last_emit_time = start_time
        bytes_since_last_emit = 0

        with open(self.temp_zip_path, file_mode) as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if self._cancelled:
                    response.close()
                    break

                if chunk:
                    f.write(chunk)
                    chunk_len = len(chunk)
                    downloaded_bytes += chunk_len
                    bytes_since_last_emit += chunk_len

                    now = time.time()
                    time_diff = now - last_emit_time
                    if time_diff >= 0.25 or downloaded_bytes == total_bytes:
                        speed = bytes_since_last_emit / time_diff if time_diff > 0 else 0
                        speed_text = f"{format_bytes(int(speed))}/ث"
                        percent = (downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0.0

                        self.download_progress.emit(
                            self.tafsir_id,
                            downloaded_bytes,
                            total_bytes,
                            percent,
                            speed_text
                        )
                        last_emit_time = now
                        bytes_since_last_emit = 0

        response.close()

        if not self._cancelled:
            # Rename .part to final zip
            if self.final_zip_path.exists():
                self.final_zip_path.unlink()
            self.temp_zip_path.rename(self.final_zip_path)

    def _extract_and_verify(self):
        """Extracts the sqlite db from the zip file and verifies its schema."""
        if not self.final_zip_path.exists():
            raise FileNotFoundError(f"ملف الأرشيف غير موجود: {self.final_zip_path}")

        extracted_file = None
        with zipfile.ZipFile(self.final_zip_path, "r") as zf:
            for member in zf.namelist():
                if member.lower().endswith(".db"):
                    # Extract directly to destination
                    target_extracted = self.dest_dir / self.db_filename
                    with zf.open(member) as source, open(target_extracted, "wb") as target:
                        chunk = source.read(1024 * 1024)
                        while chunk:
                            target.write(chunk)
                            chunk = source.read(1024 * 1024)
                    extracted_file = target_extracted
                    break

        if not extracted_file or not extracted_file.exists():
            raise ValueError("الأرشيف لا يحتوي على قاعدة بيانات صالحة بصيغة SQLite (.db).")

        # Verify SQLite integrity
        conn = sqlite3.connect(str(extracted_file))
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
            count = cursor.fetchone()[0]
            if count == 0:
                raise ValueError("قاعدة البيانات المستخرجة فارغة ولا تحتوي على جداول.")
            # Check tafsir_1 exists
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='tafsir_1';")
            if cursor.fetchone()[0] == 0:
                raise ValueError("بنية قاعدة البيانات غير متوافقة مع جداول التفسير.")
        finally:
            conn.close()

        # Remove the downloaded .zip file to save user disk space
        try:
            self.final_zip_path.unlink()
            logger.debug(f"Removed temporary archive: {self.final_zip_path}")
        except Exception as e:
            logger.warning(f"Could not remove temp zip: {e}")

    def _cleanup_temp_files(self):
        for p in [self.temp_zip_path, self.final_zip_path]:
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass

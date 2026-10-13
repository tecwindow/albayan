import os
import qtawesome as qta
from typing import Optional, Dict
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QTextEdit,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from utils.universal_speech import UniversalSpeech
from utils.const import Globals
from utils.logger import LoggerManager
from core_functions.tafaseer import Category, TAFASEER_CATALOG, DEFAULT_BUNDLED_TAFSIR_ID
from core_functions.tafaseer_downloader import TafaseerDownloadThread, format_bytes

logger = LoggerManager.get_logger(__name__)


def _play_sound(effect_name: str):
    if hasattr(Globals, "effects_manager") and Globals.effects_manager:
        try:
            Globals.effects_manager.play(effect_name)
        except Exception:
            pass


class TafaseerManagerDialog(QDialog):
    """
    Dialog to manage installed and available online Tafaseer:
    - Download missing tafaseer with automatic mirror fallback
    - Delete installed tafaseer (except the bundled default)
    - View book info, authors, and download progress
    - Fully accessible for screen readers (NVDA/JAWS) using accessibleName only
    """

    tafaseer_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("Initializing TafaseerManagerDialog...")
        self.parent = parent
        self.setWindowTitle("إدارة وتنزيل التفاسير")
        self.resize(650, 480)

        self._active_worker: Optional[TafaseerDownloadThread] = None
        self._current_downloading_id: Optional[str] = None

        self._setup_ui()
        self._setup_shortcuts()
        self.refresh_list()

        _play_sound("open")
        logger.info("TafaseerManagerDialog opened successfully.")

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # 1. Header / List Label
        self.list_label = QLabel("قائمة التفاسير المتاحة:")
        self.list_label.setAccessibleName("قائمة التفاسير المتاحة")
        main_layout.addWidget(self.list_label)

        # 2. Tafaseer List Widget
        self.tafaseer_list = QListWidget()
        self.tafaseer_list.setAccessibleName("قائمة التفاسير")
        self.tafaseer_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.tafaseer_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        main_layout.addWidget(self.tafaseer_list)

        # 3. Tafsir Information Label
        self.info_label = QLabel("معلومات التفسير:")
        self.info_label.setAccessibleName("معلومات التفسير المحدد")
        main_layout.addWidget(self.info_label)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(85)
        self.info_text.setAccessibleName("تفاصيل التفسير")
        main_layout.addWidget(self.info_text)

        # 4. Progress Section (Hidden by default)
        self.progress_layout = QVBoxLayout()
        self.status_label = QLabel("")
        self.status_label.setAccessibleName("حالة التنزيل")
        self.status_label.setVisible(False)
        self.progress_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setAccessibleName("شريط تقدم التنزيل")
        self.progress_bar.setVisible(False)
        self.progress_layout.addWidget(self.progress_bar)

        main_layout.addLayout(self.progress_layout)

        # 5. Buttons
        button_layout = QHBoxLayout()

        self.btn_download = QPushButton("تنزيل التفسير")
        self.btn_download.setIcon(qta.icon("fa5s.download"))
        self.btn_download.setAccessibleName("تنزيل التفسير المحدد")
        self.btn_download.clicked.connect(self.start_download_selected)
        button_layout.addWidget(self.btn_download)

        self.btn_cancel = QPushButton("إلغاء التنزيل")
        self.btn_cancel.setIcon(qta.icon("fa5s.stop"))
        self.btn_cancel.setAccessibleName("إلغاء تنزيل التفسير الحالي")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_download)
        button_layout.addWidget(self.btn_cancel)

        self.btn_delete = QPushButton("حذف التفسير")
        self.btn_delete.setIcon(qta.icon("fa5s.trash-alt"))
        self.btn_delete.setAccessibleName("حذف التفسير المحدد")
        self.btn_delete.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.btn_delete)

        self.btn_close = QPushButton("إغلاق")
        self.btn_close.setIcon(qta.icon("fa5s.times"))
        self.btn_close.setAccessibleName("إغلاق نافذة إدارة التفاسير")
        self.btn_close.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_close)

        main_layout.addLayout(button_layout)

        QTimer.singleShot(100, self.tafaseer_list.setFocus)

    def _setup_shortcuts(self):
        close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_shortcut.activated.connect(self.reject)

        close_shortcut_f4 = QShortcut(QKeySequence("Ctrl+F4"), self)
        close_shortcut_f4.activated.connect(self.reject)

        del_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self.tafaseer_list)
        del_shortcut.activated.connect(self.delete_selected)

        ret_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self.tafaseer_list)
        ret_shortcut.activated.connect(self.start_download_selected)

    def refresh_list(self, select_category_id: Optional[str] = None):
        """Populates the list of tafaseer with current status and sizes."""
        current_id = select_category_id or self.get_selected_category_id()
        logger.debug(f"Refreshing tafaseer list. Target selection: '{current_id}'")
        self.tafaseer_list.clear()

        selected_row = 0
        row_index = 0

        for cat_id, info in TAFASEER_CATALOG.items():
            name = info["arabic_name"]
            full_name = info["full_name"]
            is_installed = Category.is_installed(cat_id)
            is_bundled = (cat_id == DEFAULT_BUNDLED_TAFSIR_ID)

            if self._current_downloading_id == cat_id:
                status_str = "جارٍ التنزيل..."
                size_str = f"حجم التحميل: {info['download_size_mb']} م.ب"
            elif is_bundled:
                status_str = "مضمن مع البرنامج - أساسي"
                size_str = f"{info['approx_size_mb']} م.ب"
            elif is_installed:
                status_str = "تم التنزيل - جاهز للقراءة"
                size_str = f"{info['approx_size_mb']} م.ب"
            else:
                status_str = "غير مُنزَّل"
                size_str = f"حجم التحميل: {info['download_size_mb']} م.ب"

            display_text = f"{full_name} [{status_str}] - ({size_str})"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, cat_id)

            if is_bundled:
                item.setIcon(qta.icon("fa5s.check-double", color="#2e7d32"))
            elif is_installed:
                item.setIcon(qta.icon("fa5s.check", color="#1976d2"))
            else:
                item.setIcon(qta.icon("fa5s.arrow-alt-circle-down", color="#616161"))

            self.tafaseer_list.addItem(item)

            if current_id == cat_id:
                selected_row = row_index

            row_index += 1

        if self.tafaseer_list.count() > 0:
            self.tafaseer_list.setCurrentRow(selected_row)
            self._update_buttons_and_info()
        logger.debug(f"Tafaseer list refreshed. Total items: {self.tafaseer_list.count()}")

    def get_selected_category_id(self) -> Optional[str]:
        item = self.tafaseer_list.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def _on_selection_changed(self):
        cat_id = self.get_selected_category_id()
        logger.debug(f"Tafaseer selection changed to: {cat_id}")
        self._update_buttons_and_info()

    def _on_item_double_clicked(self, item: QListWidgetItem):
        cat_id = item.data(Qt.ItemDataRole.UserRole)
        logger.debug(f"Tafaseer item double-clicked: {cat_id}")
        if not Category.is_installed(cat_id) and self._current_downloading_id != cat_id:
            self.start_download_selected()

    def _update_buttons_and_info(self):
        cat_id = self.get_selected_category_id()
        if not cat_id:
            self.btn_download.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.info_text.clear()
            return

        info = Category.get_tafsir_info(cat_id)
        if not info:
            return

        is_installed = Category.is_installed(cat_id)
        is_bundled = (cat_id == DEFAULT_BUNDLED_TAFSIR_ID)
        is_downloading = (self._current_downloading_id == cat_id)
        is_any_downloading = (self._active_worker is not None and self._active_worker.isRunning())

        # Update Info text
        details = (
            f"الكتاب: {info['full_name']}\n"
            f"المؤلف: {info['author']}\n"
            f"الوصف: {info['description']}\n"
            f"الحجم عند التثبيت: {info['approx_size_mb']} م.ب | حجم التنزيل: {info['download_size_mb']} م.ب"
        )
        self.info_text.setPlainText(details)

        # Update Buttons
        self.btn_download.setEnabled(not is_installed and not is_any_downloading)
        self.btn_delete.setEnabled(is_installed and not is_bundled and not is_downloading)
        self.btn_cancel.setEnabled(is_downloading)

    def start_download_selected(self):
        cat_id = self.get_selected_category_id()
        if not cat_id:
            return

        if Category.is_installed(cat_id):
            logger.debug(f"Download requested for already installed tafsir: {cat_id}")
            UniversalSpeech.say("هذا التفسير مثبت بالفعل وجاهز للاستخدام.")
            return

        if self._active_worker and self._active_worker.isRunning():
            logger.warning(f"Download attempted for {cat_id} while worker is already busy with {self._current_downloading_id}")
            UniversalSpeech.say("هناك عملية تنزيل جارية بالفعل، يرجى الانتظار حتى تكتمل.")
            QMessageBox.information(
                self,
                "تنبيه",
                "هناك عملية تنزيل جارية حالياً، يرجى الانتظار حتى اكتمالها.",
            )
            return

        info = Category.get_tafsir_info(cat_id)
        if not info:
            logger.error(f"No catalog information found for category: {cat_id}")
            return

        logger.info(f"User started download for tafsir: {cat_id} ({info['full_name']})")
        self._current_downloading_id = cat_id
        mirrors = info.get("mirrors", [])
        logger.debug(f"Configured mirrors for {cat_id}: {mirrors}")

        # Start thread
        self._active_worker = TafaseerDownloadThread(cat_id, mirrors, parent=self)
        self._active_worker.download_progress.connect(self._on_download_progress)
        self._active_worker.status_changed.connect(self._on_status_changed)
        self._active_worker.mirror_switched.connect(self._on_mirror_switched)
        self._active_worker.download_finished.connect(self._on_download_finished)
        self._active_worker.download_error.connect(self._on_download_error)
        self._active_worker.download_cancelled.connect(self._on_download_cancelled)

        self.status_label.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"بدأ تنزيل {info['full_name']}...")

        UniversalSpeech.say(f"بدأ تنزيل {info['full_name']}.")
        _play_sound("change")

        self.btn_download.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_delete.setEnabled(False)

        self.refresh_list(cat_id)
        self._active_worker.start()
        logger.info(f"Worker thread launched for tafsir: {cat_id}")

    def cancel_download(self):
        if self._active_worker and self._active_worker.isRunning():
            logger.info(f"User requested cancellation of download for tafsir: {self._current_downloading_id}")
            self.status_label.setText("جارٍ إلغاء التنزيل...")
            UniversalSpeech.say("جارٍ إلغاء التنزيل...")
            self._active_worker.cancel()
            self.btn_cancel.setEnabled(False)

    def _on_download_progress(
        self, tafsir_id: str, downloaded_bytes: int, total_bytes: int, percent: float, speed_str: str
    ):
        self.progress_bar.setValue(int(percent))
        info = Category.get_tafsir_info(tafsir_id)
        name = info["arabic_name"] if info else tafsir_id
        progress_text = (
            f"تنزيل {name}: {percent:.1f}% ({format_bytes(downloaded_bytes)} من {format_bytes(total_bytes)}) - السرعة: {speed_str}"
        )
        self.status_label.setText(progress_text)

    def _on_status_changed(self, tafsir_id: str, message: str):
        logger.debug(f"Download status for {tafsir_id}: {message}")
        self.status_label.setText(message)

    def _on_mirror_switched(self, tafsir_id: str, mirror_url: str, mirror_index: int):
        logger.info(f"Mirror switched for {tafsir_id}: mirror #{mirror_index} ({mirror_url})")
        if mirror_index > 1:
            UniversalSpeech.say(f"جارٍ المحاولة من الرابط البديل رقم {mirror_index}...")

    def _on_download_finished(self, tafsir_id: str, final_db_path: str):
        info = Category.get_tafsir_info(tafsir_id)
        full_name = info["full_name"] if info else tafsir_id
        logger.info(f"Tafsir download completed successfully: {tafsir_id} ({full_name}) at {final_db_path}")

        self._active_worker = None
        self._current_downloading_id = None
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)

        _play_sound("open")
        UniversalSpeech.say(f"اكتمل تنزيل {full_name} بنجاح، وأصبح جاهزاً للاستخدام.")

        self.refresh_list(tafsir_id)
        self.tafaseer_changed.emit()

        QMessageBox.information(
            self,
            "اكتمل التنزيل",
            f"تم تنزيل وتثبيت ({full_name}) بنجاح، يمكنك الآن مطالعته من قائمة التفسير.",
        )

    def _on_download_error(self, tafsir_id: str, error_message: str):
        info = Category.get_tafsir_info(tafsir_id)
        name = info["arabic_name"] if info else tafsir_id
        logger.error(f"Tafsir download failed for {tafsir_id}: {error_message}")

        self._active_worker = None
        self._current_downloading_id = None
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)

        UniversalSpeech.say(f"فشل تنزيل {name}.")
        self.refresh_list(tafsir_id)

        QMessageBox.critical(
            self,
            "خطأ في التنزيل",
            f"حدث خطأ أثناء تنزيل {name}:\n{error_message}",
        )

    def _on_download_cancelled(self, tafsir_id: str):
        info = Category.get_tafsir_info(tafsir_id)
        name = info["arabic_name"] if info else tafsir_id
        logger.info(f"Tafsir download cancelled notification received for: {tafsir_id}")

        self._active_worker = None
        self._current_downloading_id = None
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)

        UniversalSpeech.say(f"تم إلغاء تنزيل {name}.")
        self.refresh_list(tafsir_id)

    def delete_selected(self):
        cat_id = self.get_selected_category_id()
        if not cat_id:
            return

        logger.debug(f"User requested delete for tafsir: {cat_id}")
        if cat_id == DEFAULT_BUNDLED_TAFSIR_ID:
            logger.warning(f"Delete requested for bundled default tafsir '{cat_id}' (rejected)")
            UniversalSpeech.say("لا يمكن حذف التفسير الأساسي المضمن مع البرنامج.")
            QMessageBox.warning(
                self,
                "تنبيه",
                "التفسير الميسر هو التفسير الأساسي المضمن مع البرنامج ولا يمكن حذفه لضمان عمل البرنامج دائماً دون إنترنت.",
            )
            return

        if not Category.is_installed(cat_id):
            logger.warning(f"Delete requested for uninstalled tafsir: '{cat_id}'")
            UniversalSpeech.say("هذا التفسير غير مثبت أصلاً.")
            return

        info = Category.get_tafsir_info(cat_id)
        name = info["full_name"] if info else cat_id

        confirm = QMessageBox.question(
            self,
            "تأكيد الحذف",
            f"هل أنت متأكد من حذف ({name}) من جهازك؟\nيمكنك إعادة تنزيله في أي وقت لاحقاً.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            logger.info(f"User confirmed deletion of tafsir: {cat_id} ({name})")
            try:
                Category.delete_tafsir(cat_id)
                _play_sound("change")
                UniversalSpeech.say(f"تم حذف {name} بنجاح.")
                self.refresh_list(cat_id)
                self.tafaseer_changed.emit()
            except Exception as e:
                logger.error(f"Error deleting tafsir {cat_id}: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "خطأ",
                    f"تعذر حذف ملف التفسير:\n{str(e)}",
                )

    def reject(self):
        logger.debug("User requested to close TafaseerManagerDialog.")
        if self._active_worker and self._active_worker.isRunning():
            logger.info("Active download detected while attempting to close dialog, asking confirmation.")
            confirm = QMessageBox.question(
                self,
                "إلغاء التنزيل",
                "هناك عملية تنزيل جارية، هل تريد إلغاء التنزيل وإغلاق النافذة؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if confirm != QMessageBox.StandardButton.Yes:
                logger.debug("Close dialog aborted by user to keep active download running.")
                return
            self.cancel_download()

        _play_sound("clos")
        logger.debug("TafaseerManagerDialog closed.")
        super().reject()

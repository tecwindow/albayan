from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PySide6.QtCore import Qt, QSize, QRect, QEvent
from PySide6.QtGui import QPainter, QColor
from core_functions.downloader.status import DownloadStatus, DownloadProgress
from .download_model import DownloadListModel


class DownloadDelegate(QStyledItemDelegate):
    """
    Custom delegate to render download items with a progress bar and status text.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.padding = 10
        self.bar_height = 8

    def sizeHint(self, option: QStyleOptionViewItem, index) -> QSize:
        # Provide enough height for filename, status, and progress bar
        return QSize(option.rect.width(), 65)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        if not index.isValid():
            return

        painter.save()

        # Data retrieval
        item_data = index.data(DownloadListModel.ItemRole)
        progress_data: DownloadProgress = index.data(DownloadListModel.ProgressRole)

        # Fallback if data isn't ready
        if not item_data:
            painter.restore()
            return

        filename = item_data.get("filename", "Unknown")
        status = item_data.get("status", DownloadStatus.PENDING)

        percentage = 0
        downloaded_str = "0 B"
        total_str = "0 B"

        if progress_data:
            percentage = progress_data.percentage
            downloaded = progress_data.downloaded_bytes
            total = progress_data.total_bytes

            # Simple formatter (can use util function if available)
            def fmt(b):
                return (
                    f"{b / (1024*1024):.2f} MB"
                    if b > 1024 * 1024
                    else f"{b / 1024:.2f} KB"
                )

            downloaded_str = fmt(downloaded)
            total_str = fmt(total)

        # Draw Background
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            text_color = option.palette.highlightedText().color()
            subtext_color = QColor(220, 220, 220)  # Lighter for subtext on selection
        else:
            painter.fillRect(option.rect, option.palette.base())
            text_color = option.palette.text().color()
            subtext_color = option.palette.text().color()
            subtext_color.setAlpha(150)  # Dimmed text

        # Setup layout rects
        rect = option.rect
        content_rect = rect.adjusted(
            self.padding, self.padding, -self.padding, -self.padding
        )

        # 1. Filename (Top Left)
        painter.setPen(text_color)
        title_font = option.font
        title_font.setBold(True)
        title_font.setPointSize(10)
        painter.setFont(title_font)

        # Calculate text rects
        fm = painter.fontMetrics()
        title_height = fm.height()
        title_rect = QRect(
            content_rect.left(), content_rect.top(), content_rect.width(), title_height
        )

        painter.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            filename,
        )

        # 2. Status & Size Info (Middle Right / Left)
        status_font = option.font
        status_font.setBold(False)
        status_font.setPointSize(9)
        painter.setFont(status_font)
        painter.setPen(subtext_color)

        # Status Text (Right aligned)
        status_text = status.label if hasattr(status, "label") else str(status)
        status_rect = QRect(
            content_rect.left(), content_rect.top(), content_rect.width(), title_height
        )
        painter.drawText(
            status_rect,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            status_text,
        )

        # Size info (Below Filename)
        size_text = f"{downloaded_str} / {total_str}"
        size_rect = QRect(
            content_rect.left(),
            title_rect.bottom() + 5,
            content_rect.width(),
            title_height,
        )
        painter.drawText(
            size_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            size_text,
        )

        # 3. Progress Bar (Bottom)
        bar_rect = QRect(
            content_rect.left(),
            content_rect.bottom() - self.bar_height,
            content_rect.width(),
            self.bar_height,
        )

        # Background bar
        bg_bar_color = QColor(220, 220, 220)
        if option.state & QStyle.StateFlag.State_Selected:
            bg_bar_color = QColor(
                255, 255, 255, 100
            )  # Semi-transparent white on selection

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_bar_color)
        painter.drawRoundedRect(bar_rect, 4, 4)

        # Foreground bar
        if percentage > 0 or status == DownloadStatus.DOWNLOADING:
            progress_width = int(bar_rect.width() * (percentage / 100))
            # Ensure at least a sliver is visible if determining
            if progress_width == 0 and status == DownloadStatus.DOWNLOADING:
                progress_width = int(bar_rect.width() * 0.05)

            progress_rect = QRect(
                bar_rect.left(), bar_rect.top(), progress_width, bar_rect.height()
            )

            # Color based on status
            color = QColor(0, 120, 215)  # Default Blue
            if status == DownloadStatus.COMPLETED:
                color = QColor(0, 180, 0)  # Green
            elif status == DownloadStatus.ERROR:
                color = QColor(200, 0, 0)  # Red
            elif status == DownloadStatus.PAUSED:
                color = QColor(255, 165, 0)  # Orange

            # If selected, maybe brighten/white? Keep color for clarity for now.
            painter.setBrush(color)
            painter.drawRoundedRect(progress_rect, 4, 4)

        painter.restore()

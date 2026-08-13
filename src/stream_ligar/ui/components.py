"""Shared widgets, matching Streamer Sidekick's neon-panel language."""

from typing import Optional

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget

from stream_ligar.ui.theme import (
    ACID_LIME,
    ELECTRIC_CYAN,
    NEON_MAGENTA,
    PANEL_BORDER,
    SOFT_WHITE,
)


def _cut_corner_path(rect: QRectF, radius: float, cut: float) -> QPainterPath:
    path = QPainterPath()
    path.moveTo(rect.left() + radius, rect.top())
    path.lineTo(rect.right() - cut, rect.top())
    path.lineTo(rect.right(), rect.top() + cut)
    path.lineTo(rect.right(), rect.bottom() - radius)
    path.quadTo(rect.right(), rect.bottom(), rect.right() - radius, rect.bottom())
    path.lineTo(rect.left() + cut, rect.bottom())
    path.lineTo(rect.left(), rect.bottom() - cut)
    path.lineTo(rect.left(), rect.top() + radius)
    path.quadTo(rect.left(), rect.top(), rect.left() + radius, rect.top())
    return path


class NeonPanel(QFrame):
    """The cut-corner card with a cyan→magenta gradient border and underglow."""

    def __init__(self, parent: Optional[QWidget] = None, accent: str = ELECTRIC_CYAN) -> None:
        super().__init__(parent)
        self.accent = QColor(accent)
        self.setObjectName("NeonPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0.8, 0.8, self.width() - 1.6, self.height() - 1.6)
        path = _cut_corner_path(rect, 14, 12)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(13, 18, 27, 236))
        painter.drawPath(path)

        border = QLinearGradient(rect.topLeft(), rect.bottomRight())
        border.setColorAt(0.0, QColor(ELECTRIC_CYAN))
        border.setColorAt(0.46, QColor(PANEL_BORDER))
        border.setColorAt(0.74, QColor(NEON_MAGENTA))
        border.setColorAt(1.0, QColor(PANEL_BORDER))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QBrush(border), 1.1))
        painter.drawPath(path)

        glow = QLinearGradient(rect.left(), rect.bottom(), rect.right(), rect.bottom())
        glow.setColorAt(0.05, QColor(0, 0, 0, 0))
        glow.setColorAt(0.35, QColor(ELECTRIC_CYAN))
        glow.setColorAt(0.58, QColor(NEON_MAGENTA))
        glow.setColorAt(0.95, QColor(0, 0, 0, 0))
        painter.setPen(QPen(QBrush(glow), 1.8))
        y = rect.bottom() - 1.5
        painter.drawLine(QPointF(rect.left() + 18, y), QPointF(rect.right() - 18, y))

        super().paintEvent(event)


class SectionHeader(QWidget):
    """Numbered kicker + magenta divider + title, like Sidekick's section rows."""

    def __init__(self, number: str, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        number_label = QLabel(number)
        number_label.setObjectName("Kicker")
        divider = QLabel("|")
        divider.setObjectName("AccentDivider")
        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")

        layout.addWidget(number_label)
        layout.addWidget(divider)
        layout.addWidget(title_label)
        layout.addStretch(1)


class StatusDot(QWidget):
    """A small filled circle used as a per-item state light."""

    def __init__(self, color: str = PANEL_BORDER, size: int = 14, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedSize(size, size)

    def set_color(self, color: str) -> None:
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(1.5, 1.5, self.width() - 3, self.height() - 3)
        glow = QColor(self._color)
        glow.setAlpha(70)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(QRectF(0, 0, self.width(), self.height()))
        painter.setBrush(self._color)
        painter.drawEllipse(rect)


class Wordmark(QWidget):
    """Draws the power bolt + "StreamOn" in the Sidekick colour treatment."""

    def __init__(self, compact: bool = False, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.compact = compact
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(46 if compact else 74)

    def sizeHint(self) -> QSize:
        return QSize(210 if self.compact else 460, 48 if self.compact else 80)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        height = self.height()

        icon_size = min(height - 6, 40 if self.compact else 66)
        icon_rect = QRectF(2, (height - icon_size) / 2, icon_size, icon_size)
        _draw_power_icon(painter, icon_rect)

        text_x = icon_rect.right() + (10 if self.compact else 16)
        segments = [(ELECTRIC_CYAN, "Stream"), (NEON_MAGENTA, "On")]
        size = 22 if self.compact else 40
        font = QFont("Bahnschrift", size, QFont.Weight.Bold)
        metrics = QFontMetrics(font)
        baseline = int((height + metrics.ascent() - metrics.descent()) / 2)
        painter.setFont(font)
        cursor = int(text_x)
        for color, text in segments:
            painter.setPen(QColor(color))
            painter.drawText(cursor, baseline, text)
            cursor += metrics.horizontalAdvance(text)


def _gradient_pen(rect: QRectF, width: float) -> QPen:
    gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
    gradient.setColorAt(0.0, QColor(ELECTRIC_CYAN))
    gradient.setColorAt(0.55, QColor(ELECTRIC_CYAN))
    gradient.setColorAt(0.8, QColor(NEON_MAGENTA))
    gradient.setColorAt(1.0, QColor(NEON_MAGENTA))
    pen = QPen(QBrush(gradient), width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def _draw_power_icon(painter: QPainter, rect: QRectF) -> None:
    """A power symbol (ring + top stroke) — the 'ligar' motif."""
    painter.save()
    pen = _gradient_pen(rect, max(3.0, rect.width() * 0.11))
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    inset = rect.width() * 0.2
    ring = QRectF(
        rect.left() + inset,
        rect.top() + inset * 1.15,
        rect.width() - inset * 2,
        rect.height() - inset * 2,
    )
    # Arc leaving a gap at the top for the vertical stroke.
    painter.drawArc(ring, 70 * 16, 320 * 16)
    cx = rect.center().x()
    painter.drawLine(QPointF(cx, rect.top() + rect.height() * 0.12), QPointF(cx, rect.center().y()))
    painter.restore()

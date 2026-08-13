"""Generate app_icon.ico / .png with the Stream Ligar neon power mark.

Run: python scripts/make_icon.py
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import (  # noqa: E402
    QBrush,
    QColor,
    QGuiApplication,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)

CYAN = "#37F2FF"
MAGENTA = "#FF4FD8"
VOID = "#0A0B12"
BORDER = "#273140"

OUT_DIR = Path(__file__).resolve().parents[1] / "src" / "stream_ligar" / "assets" / "brand"


def render(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # rounded square backdrop
    margin = size * 0.06
    rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    radius = size * 0.22
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(VOID))
    p.drawPath(path)
    border_pen = QPen(QColor(BORDER), size * 0.02)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(border_pen)
    p.drawPath(path)

    # neon power symbol
    grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
    grad.setColorAt(0.0, QColor(CYAN))
    grad.setColorAt(0.6, QColor(CYAN))
    grad.setColorAt(1.0, QColor(MAGENTA))
    pen = QPen(QBrush(grad), size * 0.09)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)

    inset = size * 0.30
    ring = QRectF(inset, inset * 1.08, size - 2 * inset, size - 2 * inset)
    p.drawArc(ring, 70 * 16, 320 * 16)
    cx = rect.center().x()
    p.drawLine(QPointF(cx, size * 0.24), QPointF(cx, size * 0.5))
    p.end()
    return pm


def main() -> int:
    QGuiApplication(sys.argv)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sizes = [16, 24, 32, 48, 64, 128, 256]
    pixmaps = [render(s) for s in sizes]
    pixmaps[-1].save(str(OUT_DIR / "app_icon.png"), "PNG")

    # Build a multi-resolution .ico
    try:
        from PIL import Image  # type: ignore

        png = OUT_DIR / "_tmp_256.png"
        pixmaps[-1].save(str(png), "PNG")
        img = Image.open(png)
        img.save(str(OUT_DIR / "app_icon.ico"), sizes=[(s, s) for s in sizes])
        png.unlink(missing_ok=True)
    except Exception:
        # Fallback: Qt can write a single-size .ico
        pixmaps[-1].save(str(OUT_DIR / "app_icon.ico"), "ICO")
    print("icon written to", OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

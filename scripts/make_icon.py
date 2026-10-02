"""Gera o icone do StreamOn: pixel-art 12x12 do Sidekick OS, fundo transparente.

Segue o PLUGIN_STANDARD §5 e o DESIGN.md do Streamer Sidekick (Iconography,
icon-brand): grade 12x12 de celulas solidas, sem antisserrilhado e sem degrade,
com uma cor de papel, um acento e a tinta clara. O desenho e o mesmo que o hub
usa para o StreamOn (``streamer_sidekick.ui.icons.BRAND["power"]``); mudou
la, mude aqui.

Cada tamanho usa um numero inteiro de pixels por celula, centralizado, para o
icone ficar nitido em qualquer escala.

    python scripts/make_icon.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRect, Qt  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter  # noqa: E402

# Tokens do Sidekick OS (DESIGN.md, Colors).
CORES = {"primary": "#37F2FF", "brand": "#FF4FD8", "success": "#B9FF43", "ink": "#F4F0FF"}

# '#' cor principal, '+' acento, '*' tinta clara (ink), '.' transparente
PRINCIPAL, ACENTO = "primary", "brand"
GRADE = [
    "............",
    ".....++.....",
    "..#..++..#..",
    ".#...++...#.",
    "#....++....#",
    "#....++....#",
    "#..........#",
    "#..........#",
    ".#........#.",
    "..#......#..",
    "...######...",
    "............",
]

DESTINO = Path(__file__).resolve().parent.parent / "src/stream_ligar/assets/brand/app_icon.png"


def render(tamanho: int) -> QImage:
    imagem = QImage(tamanho, tamanho, QImage.Format.Format_ARGB32)
    imagem.fill(Qt.GlobalColor.transparent)
    celula = max(1, tamanho // 12)
    margem = (tamanho - celula * 12) // 2
    tintas = {"#": QColor(CORES[PRINCIPAL]), "+": QColor(CORES[ACENTO]), "*": QColor(CORES["ink"])}
    p = QPainter(imagem)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    for linha, texto in enumerate(GRADE):
        for coluna, ch in enumerate(texto):
            if ch in tintas:
                p.fillRect(QRect(margem + coluna * celula, margem + linha * celula, celula, celula), tintas[ch])
    p.end()
    return imagem


def main() -> int:
    QGuiApplication(sys.argv)
    assert len(GRADE) == 12 and all(len(linha) == 12 for linha in GRADE), "a grade tem de ser 12x12"
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    imagem = render(256)
    imagem.save(str(DESTINO), "PNG")
    print(f"icone salvo em {DESTINO} ({imagem.width()}x{imagem.height()})")
    # .ico multi-resolucao para o executavel e a janela (o build usa este arquivo).
    ico = DESTINO.with_suffix(".ico")
    tamanhos = [16, 24, 32, 48, 64, 128, 256]
    try:
        from PIL import Image  # type: ignore

        temporario = DESTINO.with_name("_tmp_256.png")
        imagem.save(str(temporario), "PNG")
        Image.open(temporario).save(str(ico), sizes=[(t, t) for t in tamanhos])
        temporario.unlink(missing_ok=True)
    except Exception:
        imagem.save(str(ico), "ICO")  # sem Pillow: .ico de um tamanho so
    print(f"icone salvo em {ico}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

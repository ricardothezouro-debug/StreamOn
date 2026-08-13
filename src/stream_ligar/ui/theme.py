"""Visual theme shared by both windows.

The palette, fonts and QSS are aligned with Streamer Sidekick (Void black base,
electric cyan / neon magenta / acid lime accents, Bahnschrift titles) so the two
apps read as one product — and so a future dock into Sidekick needs no restyle.
"""

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

# ---- palette (identical to Streamer Sidekick) ----
VOID_BLACK = "#0A0B12"
GRAPHITE = "#141826"
SOFT_WHITE = "#F3F6FF"
ELECTRIC_CYAN = "#37F2FF"
NEON_MAGENTA = "#FF4FD8"
ACID_LIME = "#B9FF43"
PANEL_BORDER = "#273140"
MUTED = "#A8B0BC"

TITLE_FONT = "Bahnschrift"
BODY_FONT = "Segoe UI"
MONO_FONT = "Consolas"


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setFont(QFont(BODY_FONT, 10))
    _load_optional_fonts()
    app.setStyleSheet(_STYLESHEET)


_STYLESHEET = f"""
QWidget {{
    background: {VOID_BLACK};
    color: {SOFT_WHITE};
    font-family: "{BODY_FONT}";
    font-size: 14px;
}}

QLabel {{ background: transparent; }}

QMainWindow, QDialog, QStackedWidget {{ background: {VOID_BLACK}; }}

QWidget#ContentSurface {{ background: {VOID_BLACK}; }}

QScrollArea#PageScroll {{ background: transparent; border: 0; }}
QScrollArea#PageScroll > QWidget > QWidget {{ background: transparent; }}

QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {PANEL_BORDER}; border-radius: 5px; min-height: 36px; }}
QScrollBar::handle:vertical:hover {{ background: {ELECTRIC_CYAN}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; border: 0; background: transparent; }}

QLabel#PageTitle {{ font-family: "{TITLE_FONT}"; font-size: 38px; font-weight: 700; color: {SOFT_WHITE}; }}
QLabel#SectionTitle {{ font-size: 18px; font-weight: 700; color: {SOFT_WHITE}; }}
QLabel#CardTitle {{ font-family: "{TITLE_FONT}"; font-size: 24px; font-weight: 700; color: {SOFT_WHITE}; }}
QLabel#Muted {{ color: {MUTED}; }}
QLabel#Kicker {{ font-family: "{MONO_FONT}"; color: {ELECTRIC_CYAN}; font-size: 18px; font-weight: 700; }}
QLabel#AccentDivider {{ color: {NEON_MAGENTA}; font-size: 18px; font-weight: 700; }}

QLabel#StatusPill {{
    background: {VOID_BLACK}; border: 1px solid {PANEL_BORDER};
    border-radius: 8px; padding: 7px 10px; color: #C7D0DD; font-weight: 600;
}}

QPushButton {{
    background: #111722; border: 1px solid {PANEL_BORDER}; border-radius: 8px;
    padding: 10px 14px; color: {SOFT_WHITE}; font-weight: 600;
}}
QPushButton:hover {{ background: #151E2C; border-color: {ELECTRIC_CYAN}; color: #FFFFFF; }}
QPushButton:pressed {{ background: #0D121B; border-color: {NEON_MAGENTA}; }}
QPushButton:disabled {{ color: #687180; border-color: #1B2430; }}

QPushButton#PrimaryButton {{ background: #14383F; border-color: {ELECTRIC_CYAN}; color: #FFFFFF; }}
QPushButton#PrimaryButton:hover {{ background: #174A52; border-color: {NEON_MAGENTA}; }}
QPushButton#PrimaryButton:disabled {{ background: #0F1A20; border-color: #1B2430; color: #5B6472; }}

QPushButton#DangerButton {{ background: #33121E; border-color: {NEON_MAGENTA}; color: #FFE3F6; }}
QPushButton#DangerButton:hover {{ background: #46182A; }}

QPushButton#GhostButton {{ background: transparent; border: 1px solid {PANEL_BORDER}; color: {MUTED}; }}
QPushButton#GhostButton:hover {{ background: #101722; color: {SOFT_WHITE}; border-color: {ELECTRIC_CYAN}; }}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit, QTextEdit {{
    background: #0B111A; border: 1px solid {PANEL_BORDER}; border-radius: 8px;
    padding: 9px 10px; color: {SOFT_WHITE}; min-height: 20px;
    selection-background-color: {ELECTRIC_CYAN}; selection-color: {VOID_BLACK};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus {{
    border-color: {ELECTRIC_CYAN}; background: #0D1621;
}}
QComboBox::drop-down {{ border: 0; width: 22px; }}
QComboBox QAbstractItemView {{
    background: #080B12; border: 1px solid {PANEL_BORDER};
    selection-background-color: #14383F; color: {SOFT_WHITE}; outline: 0;
}}

QListWidget {{
    background: #0B111A; border: 1px solid {PANEL_BORDER}; border-radius: 8px;
    padding: 6px; color: {SOFT_WHITE};
}}
QListWidget::item {{ border-radius: 6px; padding: 4px; }}
QListWidget::item:hover {{ background: #111B28; }}
QListWidget::item:selected {{ background: #142632; border: 1px solid {ELECTRIC_CYAN}; }}

QCheckBox {{ spacing: 8px; color: #D9E4EF; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border-radius: 5px; border: 1px solid #596373; background: #0B111A;
}}
QCheckBox::indicator:checked {{ background: #14383F; border-color: {ELECTRIC_CYAN}; }}

QMenu {{ background: #080B12; border: 1px solid {PANEL_BORDER}; color: {SOFT_WHITE}; padding: 6px; }}
QMenu::item {{ background: transparent; border-radius: 6px; padding: 8px 28px 8px 12px; }}
QMenu::item:selected {{ background: #14383F; color: #FFFFFF; }}

QToolTip {{ background: #080B12; color: {SOFT_WHITE}; border: 1px solid {ELECTRIC_CYAN}; padding: 6px; }}
"""


def _load_optional_fonts() -> None:
    try:
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        fonts = root / "assets" / "fonts"
        if not fonts.exists():
            return
        for file in fonts.glob("*.*"):
            if file.suffix.lower() in {".ttf", ".otf"}:
                QFontDatabase.addApplicationFont(str(file))
    except Exception:
        pass

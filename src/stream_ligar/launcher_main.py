"""Entry point for the launcher executable (Stream Ligar.exe)."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from stream_ligar.core.paths import brand_icon_path
from stream_ligar.ui.launcher_window import LauncherWindow
from stream_ligar.ui.theme import apply_theme


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Stream Ligar")
    app.setOrganizationName("Gamox")
    apply_theme(app)

    icon_path = brand_icon_path()
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = LauncherWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())

"""Entry point for the configuration executable (Config.exe)."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from stream_ligar.core.paths import brand_icon_path
from stream_ligar.ui.config_window import ConfigWindow
from stream_ligar.ui.theme import apply_theme


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Stream Ligar Config")
    app.setOrganizationName("Gamox")
    apply_theme(app)

    icon_path = brand_icon_path()
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = ConfigWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())

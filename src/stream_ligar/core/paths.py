import os
import sys
from pathlib import Path


APP_NAME = "StreamLigar"


def asset_dir() -> Path:
    """Locate the bundled assets folder in both source and frozen (PyInstaller) runs."""
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        candidate = base / "stream_ligar" / "assets"
        if candidate.exists():
            return candidate
        return base / "assets"
    return Path(__file__).resolve().parents[1] / "assets"


def brand_icon_path() -> Path:
    return asset_dir() / "brand" / "app_icon.ico"


def app_data_dir() -> Path:
    """Return a writable per-user data directory, mirroring Streamer Sidekick."""
    candidates: list[Path] = []
    if os.getenv("APPDATA"):
        candidates.append(Path(os.getenv("APPDATA", "")) / APP_NAME)
    if os.getenv("LOCALAPPDATA"):
        candidates.append(Path(os.getenv("LOCALAPPDATA", "")) / APP_NAME)
    candidates.append(Path.cwd() / ".stream_ligar")

    for path in candidates:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except OSError:
            continue

    fallback = Path.cwd() / ".stream_ligar"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def user_config_path() -> Path:
    return app_data_dir() / "config.json"

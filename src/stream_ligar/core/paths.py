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
    """Melhor arquivo de ícone para a plataforma atual.

    O Qt só renderiza ``.ico`` com consistência no Windows; nas demais
    plataformas (e sempre que o ``.ico`` não existir) usamos o PNG.
    """
    brand = asset_dir() / "brand"
    ico = brand / "app_icon.ico"
    png = brand / "app_icon.png"
    if sys.platform == "win32" and ico.exists():
        return ico
    if png.exists():
        return png
    return ico


def _platform_candidates() -> list[Path]:
    """Diretórios de dados preferenciais por sistema operacional.

    Espelha o Streamer Sidekick. Sem isto, fora do Windows a config caía em
    ``./.stream_ligar`` — ou seja, na pasta de onde o app foi aberto, mudando de
    lugar a cada execução.
    """
    home = Path.home()
    if sys.platform == "win32":
        candidates: list[Path] = []
        if os.getenv("APPDATA"):
            candidates.append(Path(os.getenv("APPDATA", "")) / APP_NAME)
        if os.getenv("LOCALAPPDATA"):
            candidates.append(Path(os.getenv("LOCALAPPDATA", "")) / APP_NAME)
        return candidates
    if sys.platform == "darwin":
        return [home / "Library" / "Application Support" / APP_NAME]
    # Linux e outros: segue o XDG Base Directory.
    xdg = os.getenv("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else home / ".config"
    return [base / APP_NAME]


def app_data_dir() -> Path:
    """Return a writable per-user data directory, mirroring Streamer Sidekick."""
    candidates = _platform_candidates()
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

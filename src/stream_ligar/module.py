"""Docking adapter for Streamer Sidekick.

Streamer Sidekick loads tools as *modules*, each described by a
``ModuleInfo(module_id, title, subtitle, status, accent)`` and shown as a card
on the hub with its own page in the sidebar.

When we eventually merge Stream Ligar into Sidekick, this file is the seam:
``module_info()`` returns the card description, and ``build_page()`` returns the
QWidget to drop into the hub's QStackedWidget. It works standalone (using our own
ModuleInfo copy) and light-touch upgrades to Sidekick's real class when present.
"""

from dataclasses import dataclass

# The accent used across Stream Ligar's UI (Sidekick's "electric cyan").
ACCENT = "#37F2FF"
MODULE_ID = "launcher"


@dataclass(frozen=True)
class ModuleInfo:
    module_id: str
    title: str
    subtitle: str
    status: str
    accent: str


def module_info() -> "ModuleInfo":
    """Return a ModuleInfo. If Sidekick is importable, use ITS class so the object
    is drop-in compatible with ``ModuleRegistry.register``."""
    data = dict(
        module_id=MODULE_ID,
        title="Ligar Live",
        subtitle="Abre NVIDIA Broadcast, OBS, Sidekick e os painéis de live em um clique.",
        status="Pronto para transmitir",
        accent=ACCENT,
    )
    try:  # pragma: no cover - only when running inside Sidekick
        from streamer_sidekick.core.modules import ModuleInfo as SidekickModuleInfo

        return SidekickModuleInfo(**data)  # type: ignore[return-value]
    except Exception:
        return ModuleInfo(**data)


def build_page(config=None):
    """Return the launcher page widget for embedding inside the Sidekick hub.

    Standalone we build our own ConfigStore; inside Sidekick a shared store can be
    passed in later. The page reuses Sidekick's theme automatically because the
    QApplication stylesheet is global.
    """
    from stream_ligar.core.config import ConfigStore
    from stream_ligar.ui.launcher_window import LauncherPage

    return LauncherPage(config or ConfigStore())

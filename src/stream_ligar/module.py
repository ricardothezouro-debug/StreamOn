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
        title="StreamOn",
        subtitle="Abre seus apps e painéis de live (OBS, dashboards e o que você configurar) em um clique.",
        status="Pronto para transmitir",
        accent=ACCENT,
    )
    try:  # pragma: no cover - only when running inside Sidekick
        from streamer_sidekick.core.modules import ModuleInfo as SidekickModuleInfo

        return SidekickModuleInfo(**data)  # type: ignore[return-value]
    except Exception:
        return ModuleInfo(**data)


def help_text() -> str:
    """Texto de ajuda exibido na tela 'Ajuda' do Streamer Sidekick."""
    return (
        "O StreamOn abre seus programas e painéis de live na ordem certa, com um "
        "clique — como OBS, software de câmera/áudio e os dashboards do YouTube/"
        "Twitch no Chrome.\n\n"
        "Como usar:\n"
        "• Clique em \"Configurar\" para montar sua sequência (ela começa vazia).\n"
        "• Adicione itens: Programa (.exe), Chrome (perfil + abas) ou Link.\n"
        "• Defina um delay (segundos) após cada item, para dar tempo de carregar.\n"
        "• Reordene, duplique, desative ou remova itens como quiser.\n"
        "• De volta na tela principal, clique em \"LIGAR LIVE\" para disparar tudo.\n\n"
        "Dica: o delay evita que o próximo programa abra antes do anterior estar pronto."
    )


def build_page(config=None):
    """Return the launcher page widget for embedding inside the Sidekick hub.

    Standalone we build our own ConfigStore; inside Sidekick a shared store can be
    passed in later. The page reuses Sidekick's theme automatically because the
    QApplication stylesheet is global.
    """
    from stream_ligar.core.config import ConfigStore
    from stream_ligar.ui.launcher_window import LauncherPage

    return LauncherPage(config or ConfigStore())

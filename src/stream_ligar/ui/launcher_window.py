"""The launcher: a hero panel with the big LIGAR LIVE button and a live checklist."""

from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QFrame,
)

from stream_ligar.core.config import KIND_APP, KIND_CHROME, KIND_URL, ConfigStore, Target
from stream_ligar.core.launcher import LaunchWorker
from stream_ligar.core.paths import brand_icon_path
from stream_ligar.ui.components import NeonPanel, SectionHeader, StatusDot, Wordmark
from stream_ligar.ui.theme import ACID_LIME, ELECTRIC_CYAN, MUTED, NEON_MAGENTA, PANEL_BORDER

ASSET_ICON = brand_icon_path()

_KIND_LABEL = {KIND_APP: "Programa", KIND_CHROME: "Chrome", KIND_URL: "Link"}


class _TargetRow(QWidget):
    def __init__(self, target: Target, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(12)

        self.dot = StatusDot(PANEL_BORDER, 14)

        name = QLabel(target.name)
        name.setObjectName("SectionTitle")
        kind = QLabel(_KIND_LABEL.get(target.kind, target.kind))
        kind.setObjectName("Muted")

        name_box = QVBoxLayout()
        name_box.setSpacing(1)
        name_box.addWidget(name)
        name_box.addWidget(kind)

        self.status = QLabel("Aguardando" if target.enabled else "Desativado")
        self.status.setObjectName("Muted")
        self.status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.dot, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(name_box, 1)
        layout.addWidget(self.status, 0)

        if not target.enabled:
            self.setEnabled(False)

    def set_state(self, color: str, text: str) -> None:
        self.dot.set_color(color)
        self.status.setText(text)


class LauncherPage(QWidget):
    """Embeddable launcher widget (also reused when docking into Sidekick)."""

    def __init__(self, config: ConfigStore, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config = config
        self.worker: Optional[LaunchWorker] = None
        self._targets: list[Target] = []
        self._rows: dict[int, _TargetRow] = {}
        self.on_open_config = None  # optional callback set by the window
        self._config_window = None  # editor aberto pela propria pagina (modo embutido)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setObjectName("PageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        content = QWidget()
        content.setObjectName("ContentSurface")
        self.layout_root = QVBoxLayout(content)
        self.layout_root.setContentsMargins(28, 24, 28, 24)
        self.layout_root.setSpacing(22)
        scroll.setWidget(content)

        self.layout_root.addWidget(self._build_hero())
        self.layout_root.addWidget(SectionHeader("01", "Sequência de abertura"))
        self.checklist = NeonPanel(accent=ELECTRIC_CYAN)
        self.checklist_layout = QVBoxLayout(self.checklist)
        self.checklist_layout.setContentsMargins(18, 14, 18, 16)
        self.checklist_layout.setSpacing(2)
        self.layout_root.addWidget(self.checklist)

        self.footer = QLabel("")
        self.footer.setObjectName("Muted")
        self.layout_root.addWidget(self.footer)
        self.layout_root.addStretch(1)

        self.reload_targets()

    # ---- build ---------------------------------------------------------
    def _build_hero(self) -> QWidget:
        hero = NeonPanel(accent=ELECTRIC_CYAN)
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(28, 24, 28, 26)
        layout.setSpacing(14)

        layout.addWidget(Wordmark())
        subtitle = QLabel("Abre seus programas e painéis de live na ordem certa, com um clique.")
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        self.start_button = QPushButton("LIGAR LIVE")
        self.start_button.setObjectName("PrimaryButton")
        self.start_button.setMinimumHeight(56)
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.clicked.connect(self.start_sequence)

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("DangerButton")
        self.cancel_button.setMinimumHeight(56)
        self.cancel_button.setVisible(False)
        self.cancel_button.clicked.connect(self.cancel_sequence)

        self.config_button = QPushButton("Configurar")
        self.config_button.setObjectName("GhostButton")
        self.config_button.setMinimumHeight(56)
        self.config_button.clicked.connect(self._open_config)

        buttons.addWidget(self.start_button, 2)
        buttons.addWidget(self.cancel_button, 1)
        buttons.addWidget(self.config_button, 1)
        layout.addLayout(buttons)
        return hero

    # ---- data ----------------------------------------------------------
    def reload_targets(self) -> None:
        self.config.reload()
        self._targets = self.config.targets()
        self._rows.clear()
        while self.checklist_layout.count():
            item = self.checklist_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not self._targets:
            empty = QLabel("Nenhum item configurado. Clique em \"Configurar\" para adicionar.")
            empty.setObjectName("Muted")
            self.checklist_layout.addWidget(empty)
            return

        for index, target in enumerate(self._targets):
            row = _TargetRow(target)
            self._rows[index] = row
            self.checklist_layout.addWidget(row)
            if index < len(self._targets) - 1:
                sep = QFrame()
                sep.setFixedHeight(1)
                sep.setStyleSheet(f"background: {PANEL_BORDER};")
                self.checklist_layout.addWidget(sep)

    # ---- run -----------------------------------------------------------
    def start_sequence(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            return
        enabled = [t for t in self._targets if t.enabled]
        if not enabled:
            self.footer.setText("Nada para abrir — todos os itens estão desativados.")
            return

        for index, target in enumerate(self._targets):
            if target.enabled:
                self._rows[index].set_state(PANEL_BORDER, "Na fila")

        self.start_button.setEnabled(False)
        self.start_button.setText("Abrindo…")
        self.cancel_button.setVisible(True)
        self.config_button.setEnabled(False)
        self.footer.setText("")

        self.worker = LaunchWorker(self._targets)
        self.worker.item_started.connect(self._on_item_started)
        self.worker.item_finished.connect(self._on_item_finished)
        self.worker.countdown.connect(self._on_countdown)
        self.worker.sequence_finished.connect(self._on_sequence_finished)
        self.worker.start()

    def cancel_sequence(self) -> None:
        if self.worker is not None:
            self.worker.cancel()
        self.footer.setText("Cancelando…")

    def _on_item_started(self, index: int) -> None:
        row = self._rows.get(index)
        if row:
            row.set_state(ELECTRIC_CYAN, "Abrindo…")

    def _on_item_finished(self, index: int, ok: bool, message: str) -> None:
        row = self._rows.get(index)
        if row:
            row.set_state(ACID_LIME if ok else NEON_MAGENTA, ("✓ " if ok else "✗ ") + message)

    def _on_countdown(self, index: int, remaining: float, total: float) -> None:
        if remaining > 0:
            self.footer.setText(f"Próximo item em {remaining:0.1f}s…")
        else:
            self.footer.setText("")

    def _on_sequence_finished(self, launched_ok: int, total: int) -> None:
        self.start_button.setEnabled(True)
        self.start_button.setText("LIGAR LIVE")
        self.cancel_button.setVisible(False)
        self.config_button.setEnabled(True)
        self.footer.setText(f"Concluído: {launched_ok}/{total} itens abertos.")
        if launched_ok == total and total > 0 and bool(self.config.get("close_after_launch", False)):
            QTimer.singleShot(1200, self._quit_app)

    def _quit_app(self) -> None:
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _open_config(self) -> None:
        # Modo standalone: a janela injeta um callback proprio.
        if callable(self.on_open_config):
            self.on_open_config()
            return
        # Modo embutido (plugin do Sidekick): a propria pagina abre o editor.
        from stream_ligar.ui.config_window import ConfigWindow

        if self._config_window is None:
            self._config_window = ConfigWindow(self.config)
            self._config_window.saved.connect(self.reload_targets)
        self._config_window.show()
        self._config_window.raise_()
        self._config_window.activateWindow()


class LauncherWindow(QMainWindow):
    def __init__(self, config: Optional[ConfigStore] = None) -> None:
        super().__init__()
        self.config = config or ConfigStore()
        self.setWindowTitle("StreamOn")
        if ASSET_ICON.exists():
            self.setWindowIcon(QIcon(str(ASSET_ICON)))
        self.resize(760, 720)
        self.setMinimumSize(620, 560)

        self.page = LauncherPage(self.config)
        self.page.on_open_config = self.open_config
        self.setCentralWidget(self.page)
        self._config_window = None

    def open_config(self) -> None:
        # Imported lazily to avoid a cycle; opens the editor in-process.
        from stream_ligar.ui.config_window import ConfigWindow

        if self._config_window is None:
            self._config_window = ConfigWindow(self.config)
            self._config_window.saved.connect(self.page.reload_targets)
        self._config_window.show()
        self._config_window.raise_()
        self._config_window.activateWindow()

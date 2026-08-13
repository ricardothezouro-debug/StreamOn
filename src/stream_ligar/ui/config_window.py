"""The Config editor: manage which apps/links open, their order and delays."""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)

from stream_ligar.core.browsers import list_chrome_profiles
from stream_ligar.core.config import (
    KIND_APP,
    KIND_CHROME,
    KIND_URL,
    ConfigStore,
    Target,
)
from stream_ligar.core.paths import brand_icon_path
from stream_ligar.ui.components import NeonPanel, SectionHeader, Wordmark
from stream_ligar.ui.theme import MUTED, PANEL_BORDER

ASSET_ICON = brand_icon_path()

_KIND_ITEMS = [
    ("Programa (.exe)", KIND_APP),
    ("Chrome (perfil + abas)", KIND_CHROME),
    ("Link (navegador padrão)", KIND_URL),
]
_KIND_TAG = {KIND_APP: "Programa", KIND_CHROME: "Chrome", KIND_URL: "Link"}


class ConfigWindow(QMainWindow):
    saved = Signal()

    def __init__(self, config: Optional[ConfigStore] = None) -> None:
        super().__init__()
        self.config = config or ConfigStore()
        self._targets: list[Target] = self.config.targets()
        self._current: Optional[int] = None
        self._loading = False

        self.setWindowTitle("StreamOn — Configuração")
        if ASSET_ICON.exists():
            self.setWindowIcon(QIcon(str(ASSET_ICON)))
        self.resize(1040, 720)
        self.setMinimumSize(900, 600)

        central = QWidget()
        central.setObjectName("ContentSurface")
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(18)
        self.setCentralWidget(central)

        header = QHBoxLayout()
        header.addWidget(Wordmark(compact=True), 1)
        self.close_after = QCheckBox("Fechar o StreamOn após abrir tudo")
        self.close_after.setChecked(bool(self.config.get("close_after_launch", False)))
        header.addWidget(self.close_after, 0, Qt.AlignmentFlag.AlignRight)
        root.addLayout(header)

        columns = QHBoxLayout()
        columns.setSpacing(18)
        columns.addWidget(self._build_list_panel(), 1)
        columns.addWidget(self._build_editor_panel(), 2)
        root.addLayout(columns, 1)

        footer = QHBoxLayout()
        reset = QPushButton("Restaurar padrão")
        reset.setObjectName("GhostButton")
        reset.clicked.connect(self._reset_defaults)
        footer.addWidget(reset)
        footer.addStretch(1)
        save = QPushButton("Salvar")
        save.setObjectName("PrimaryButton")
        save.setMinimumWidth(160)
        save.clicked.connect(self._save)
        footer.addWidget(save)
        root.addLayout(footer)

        self._reload_list(select=0 if self._targets else None)

    # ---- list panel ----------------------------------------------------
    def _build_list_panel(self) -> QWidget:
        panel = NeonPanel(accent="#37F2FF")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("01", "Itens"))
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._on_row_changed)
        layout.addWidget(self.list, 1)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        add = QPushButton("Adicionar")
        add.clicked.connect(self._add_target)
        dup = QPushButton("Duplicar")
        dup.clicked.connect(self._duplicate_target)
        remove = QPushButton("Remover")
        remove.setObjectName("DangerButton")
        remove.clicked.connect(self._remove_target)
        actions.addWidget(add)
        actions.addWidget(dup)
        actions.addWidget(remove)
        layout.addLayout(actions)

        move = QHBoxLayout()
        move.setSpacing(8)
        up = QPushButton("↑ Subir")
        up.clicked.connect(lambda: self._move(-1))
        down = QPushButton("↓ Descer")
        down.clicked.connect(lambda: self._move(1))
        move.addWidget(up)
        move.addWidget(down)
        layout.addLayout(move)
        return panel

    # ---- editor panel --------------------------------------------------
    def _build_editor_panel(self) -> QWidget:
        panel = NeonPanel(accent="#FF4FD8")
        wrapper = QVBoxLayout(panel)
        wrapper.setContentsMargins(4, 4, 4, 4)

        scroll = QScrollArea()
        scroll.setObjectName("PageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        wrapper.addWidget(scroll)

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)
        scroll.setWidget(body)

        layout.addWidget(SectionHeader("02", "Detalhes do item"))

        self.enabled = QCheckBox("Item ativo (será aberto ao ligar a live)")
        self.enabled.stateChanged.connect(self._on_field_changed)
        layout.addWidget(self.enabled)

        layout.addWidget(self._field_label("Nome"))
        self.name = QLineEdit()
        self.name.textChanged.connect(self._on_field_changed)
        layout.addWidget(self.name)

        layout.addWidget(self._field_label("Tipo"))
        self.kind = QComboBox()
        for label, value in _KIND_ITEMS:
            self.kind.addItem(label, value)
        self.kind.currentIndexChanged.connect(self._on_kind_changed)
        layout.addWidget(self.kind)

        # --- app fields ---
        self.app_group = QWidget()
        app_layout = QVBoxLayout(self.app_group)
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout.setSpacing(8)
        app_layout.addWidget(self._field_label("Caminho do programa (.exe)"))
        app_layout.addLayout(self._path_row("path"))
        app_layout.addWidget(self._field_label("Argumentos (opcional)"))
        self.args = QLineEdit()
        self.args.setPlaceholderText("ex.: --start-minimized")
        self.args.textChanged.connect(self._on_field_changed)
        app_layout.addWidget(self.args)
        app_layout.addWidget(self._field_label("Pasta de trabalho (opcional — vazio usa a pasta do exe)"))
        app_layout.addLayout(self._path_row("workdir", pick_dir=True))
        layout.addWidget(self.app_group)

        # --- url fields ---
        self.url_group = QWidget()
        url_layout = QVBoxLayout(self.url_group)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(8)
        url_layout.addWidget(self._field_label("Endereço (URL)"))
        self.url = QLineEdit()
        self.url.setPlaceholderText("https://…")
        self.url.textChanged.connect(self._on_field_changed)
        url_layout.addWidget(self.url)
        layout.addWidget(self.url_group)

        # --- chrome fields ---
        self.chrome_group = QWidget()
        chrome_layout = QVBoxLayout(self.chrome_group)
        chrome_layout.setContentsMargins(0, 0, 0, 0)
        chrome_layout.setSpacing(8)
        chrome_layout.addWidget(self._field_label("Perfil do Chrome"))
        self.profile = QComboBox()
        self._populate_profiles()
        self.profile.currentIndexChanged.connect(self._on_field_changed)
        chrome_layout.addWidget(self.profile)
        chrome_layout.addWidget(self._field_label("Abas a abrir (uma URL por linha)"))
        self.urls = QPlainTextEdit()
        self.urls.setPlaceholderText("https://studio.youtube.com/…\nhttps://dashboard.twitch.tv/…")
        self.urls.setMinimumHeight(90)
        self.urls.textChanged.connect(self._on_field_changed)
        chrome_layout.addWidget(self.urls)
        layout.addWidget(self.chrome_group)

        # --- delay ---
        layout.addWidget(self._field_label("Delay após abrir este item (segundos)"))
        self.delay = QDoubleSpinBox()
        self.delay.setRange(0.0, 120.0)
        self.delay.setSingleStep(0.5)
        self.delay.setDecimals(1)
        self.delay.setSuffix(" s")
        self.delay.valueChanged.connect(self._on_field_changed)
        layout.addWidget(self.delay)

        hint = QLabel("Dica: o delay dá tempo do programa anterior carregar antes do próximo abrir.")
        hint.setObjectName("Muted")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)
        return panel

    def _field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("Muted")
        return label

    def _path_row(self, attr: str, pick_dir: bool = False) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        edit = QLineEdit()
        edit.textChanged.connect(self._on_field_changed)
        setattr(self, attr, edit)
        browse = QPushButton("Procurar…")
        browse.clicked.connect(lambda: self._browse(edit, pick_dir))
        row.addWidget(edit, 1)
        row.addWidget(browse, 0)
        return row

    def _populate_profiles(self) -> None:
        self.profile.clear()
        profiles = list_chrome_profiles()
        if not profiles:
            self.profile.addItem("Default", "Default")
            return
        for directory, name in profiles:
            self.profile.addItem(f"{name}  ({directory})", directory)

    # ---- list <-> model ------------------------------------------------
    def _reload_list(self, select: Optional[int]) -> None:
        self.list.blockSignals(True)
        self.list.clear()
        for target in self._targets:
            self.list.addItem(self._list_text(target))
        self.list.blockSignals(False)
        if select is not None and 0 <= select < len(self._targets):
            self.list.setCurrentRow(select)
        else:
            self._current = None
            self._load_into_form(None)

    def _list_text(self, target: Target) -> str:
        tag = _KIND_TAG.get(target.kind, target.kind)
        mark = "" if target.enabled else "  ·  (desativado)"
        return f"{target.name}   —   {tag} · {target.delay_after:g}s{mark}"

    def _refresh_current_list_text(self) -> None:
        if self._current is None:
            return
        item = self.list.item(self._current)
        if item is not None:
            item.setText(self._list_text(self._targets[self._current]))

    def _on_row_changed(self, row: int) -> None:
        if row < 0 or row >= len(self._targets):
            self._current = None
            self._load_into_form(None)
            return
        self._current = row
        self._load_into_form(self._targets[row])

    def _load_into_form(self, target: Optional[Target]) -> None:
        self._loading = True
        enable = target is not None
        for widget in (self.name, self.kind, self.enabled, self.delay, self.args,
                       self.path, self.workdir, self.url, self.profile, self.urls):
            widget.setEnabled(enable)
        if target is None:
            self.name.setText("")
            self._loading = False
            self._update_kind_visibility(KIND_APP)
            return

        self.name.setText(target.name)
        self.enabled.setChecked(target.enabled)
        self.delay.setValue(float(target.delay_after))
        self.kind.setCurrentIndex(max(0, self.kind.findData(target.kind)))
        self.args.setText(target.args)
        self.path.setText(target.path)
        self.workdir.setText(target.workdir)
        self.url.setText(target.url)
        self._select_profile(target.chrome_profile)
        self.urls.setPlainText("\n".join(target.urls))
        self._update_kind_visibility(target.kind)
        self._loading = False

    def _select_profile(self, directory: str) -> None:
        if not directory:
            return
        index = self.profile.findData(directory)
        if index < 0:
            self.profile.addItem(f"{directory}  (não encontrado)", directory)
            index = self.profile.findData(directory)
        self.profile.setCurrentIndex(index)

    def _update_kind_visibility(self, kind: str) -> None:
        self.app_group.setVisible(kind == KIND_APP)
        self.url_group.setVisible(kind == KIND_URL)
        self.chrome_group.setVisible(kind == KIND_CHROME)

    # ---- edits write back to the model ---------------------------------
    def _on_kind_changed(self, _index: int) -> None:
        kind = self.kind.currentData()
        self._update_kind_visibility(kind)
        self._on_field_changed()

    def _on_field_changed(self, *_args) -> None:
        if self._loading or self._current is None:
            return
        target = self._targets[self._current]
        target.name = self.name.text().strip() or "Sem nome"
        target.kind = self.kind.currentData()
        target.enabled = self.enabled.isChecked()
        target.delay_after = float(self.delay.value())
        target.args = self.args.text()
        target.path = self.path.text()
        target.workdir = self.workdir.text()
        target.url = self.url.text()
        target.chrome_profile = self.profile.currentData() or ""
        target.urls = [line.strip() for line in self.urls.toPlainText().splitlines() if line.strip()]
        self._refresh_current_list_text()

    def _browse(self, edit: QLineEdit, pick_dir: bool) -> None:
        if pick_dir:
            chosen = QFileDialog.getExistingDirectory(self, "Escolher pasta", edit.text() or "")
        else:
            chosen, _ = QFileDialog.getOpenFileName(
                self, "Escolher programa", edit.text() or "", "Programas (*.exe);;Todos (*.*)"
            )
        if chosen:
            edit.setText(chosen)

    # ---- list operations ----------------------------------------------
    def _add_target(self) -> None:
        self._targets.append(Target(name="Novo item", delay_after=3.0))
        self._reload_list(select=len(self._targets) - 1)

    def _duplicate_target(self) -> None:
        if self._current is None:
            return
        import copy

        clone = copy.deepcopy(self._targets[self._current])
        clone.id = Target().id
        clone.name = f"{clone.name} (cópia)"
        self._targets.insert(self._current + 1, clone)
        self._reload_list(select=self._current + 1)

    def _remove_target(self) -> None:
        if self._current is None:
            return
        target = self._targets[self._current]
        confirm = QMessageBox.question(
            self, "Remover item", f"Remover \"{target.name}\" da lista?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        removed = self._current
        self._targets.pop(removed)
        self._reload_list(select=min(removed, len(self._targets) - 1) if self._targets else None)

    def _move(self, direction: int) -> None:
        if self._current is None:
            return
        new_index = self._current + direction
        if new_index < 0 or new_index >= len(self._targets):
            return
        self._targets[self._current], self._targets[new_index] = (
            self._targets[new_index],
            self._targets[self._current],
        )
        self._reload_list(select=new_index)

    # ---- persistence ---------------------------------------------------
    def _save(self) -> None:
        self.config.set_targets(self._targets)
        self.config.set("close_after_launch", self.close_after.isChecked())
        self.saved.emit()
        QMessageBox.information(self, "Configuração", "Configuração salva com sucesso.")

    def _reset_defaults(self) -> None:
        confirm = QMessageBox.question(
            self, "Restaurar padrão",
            "Isto substitui todos os itens pela configuração padrão do Ricardo. Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.config.reset_to_defaults()
        self._targets = self.config.targets()
        self.close_after.setChecked(bool(self.config.get("close_after_launch", False)))
        self._reload_list(select=0 if self._targets else None)
        self.saved.emit()

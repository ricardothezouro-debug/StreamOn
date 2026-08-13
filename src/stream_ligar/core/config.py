"""Configuration model for Stream Ligar.

A config holds an ordered list of *targets*. Each target is one thing to launch:
an application, a plain URL (default browser), or a Chrome window opened on a
specific profile with one or more tabs. Every target carries its own
``delay_after`` (seconds to wait before starting the next one).
"""

import json
import uuid
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from stream_ligar.core.paths import user_config_path

# Target kinds
KIND_APP = "app"
KIND_URL = "url"
KIND_CHROME = "chrome"


@dataclass
class Target:
    name: str = "Novo item"
    kind: str = KIND_APP
    path: str = ""                      # app: exe path
    args: str = ""                      # app: extra command-line arguments
    workdir: str = ""                   # app: working directory ("" = folder of exe)
    url: str = ""                       # url: single address
    chrome_profile: str = ""            # chrome: profile directory ("Profile 2")
    urls: list[str] = field(default_factory=list)  # chrome: tabs to open
    delay_after: float = 3.0            # seconds to wait after launching this item
    enabled: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Target":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        clean = {k: v for k, v in data.items() if k in known}
        target = cls(**clean)
        if not target.id:
            target.id = uuid.uuid4().hex
        return target

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_targets() -> list[Target]:
    """Configuração inicial vazia.

    O StreamOn começa zerado: cada usuário adiciona seus próprios itens (apps,
    links e janelas do Chrome) pela tela de configuração. Assim a sequência de
    inicialização faz sentido para qualquer pessoa, não só para um setup
    específico.
    """
    return []


DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "close_after_launch": False,
    "targets": [t.to_dict() for t in default_targets()],
}


class ConfigStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or user_config_path()
        self._data = self._load()

    # ---- targets -------------------------------------------------------
    def targets(self) -> list[Target]:
        return [Target.from_dict(item) for item in self._data.get("targets", [])]

    def set_targets(self, targets: list[Target]) -> None:
        self._data["targets"] = [t.to_dict() for t in targets]
        self.save()

    # ---- scalar options ------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    # ---- persistence ---------------------------------------------------
    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(self._data, file, indent=2, ensure_ascii=False)

    def reload(self) -> None:
        self._data = self._load()

    def reset_to_defaults(self) -> None:
        self._data = deepcopy(DEFAULT_CONFIG)
        self.save()

    def _load(self) -> dict[str, Any]:
        data = deepcopy(DEFAULT_CONFIG)
        if not self.path.exists():
            return data
        try:
            with self.path.open("r", encoding="utf-8") as file:
                existing = json.load(file)
        except (OSError, json.JSONDecodeError):
            return data
        if not isinstance(existing, dict):
            return data
        data.update({k: v for k, v in existing.items() if k != "targets"})
        if isinstance(existing.get("targets"), list):
            data["targets"] = existing["targets"]
        return data

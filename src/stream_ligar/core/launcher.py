"""Launching logic: turn a Target into a running process, and drive the whole
sequence on a background thread so the UI stays responsive."""

import os
import shlex
import subprocess
import time
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from stream_ligar.core.browsers import find_chrome
from stream_ligar.core.config import KIND_APP, KIND_CHROME, KIND_URL, Target

# Windows process-creation flags: run detached so the children outlive the launcher.
_DETACHED_PROCESS = 0x00000008
_CREATE_NEW_PROCESS_GROUP = 0x00000200
_CREATION_FLAGS = _DETACHED_PROCESS | _CREATE_NEW_PROCESS_GROUP


def _split_args(raw: str) -> list[str]:
    raw = (raw or "").strip()
    if not raw:
        return []
    try:
        return shlex.split(raw, posix=False)
    except ValueError:
        return raw.split()


def launch_target(target: Target) -> tuple[bool, str]:
    """Start a single target. Returns (ok, human-readable message)."""
    try:
        if target.kind == KIND_APP:
            return _launch_app(target)
        if target.kind == KIND_CHROME:
            return _launch_chrome(target)
        if target.kind == KIND_URL:
            return _launch_url(target)
        return False, f"Tipo desconhecido: {target.kind}"
    except FileNotFoundError as exc:
        return False, f"Não encontrado: {exc}"
    except OSError as exc:
        return False, f"Erro ao abrir: {exc}"


def _launch_app(target: Target) -> tuple[bool, str]:
    path = target.path.strip()
    if not path:
        return False, "Caminho do programa não definido."
    exe = Path(path)
    if not exe.exists():
        return False, f"Arquivo não existe: {path}"
    workdir = target.workdir.strip() or str(exe.parent)
    cmd = [str(exe), *_split_args(target.args)]
    subprocess.Popen(
        cmd,
        cwd=workdir,
        creationflags=_CREATION_FLAGS,
        close_fds=True,
    )
    return True, "Programa iniciado."


def _launch_chrome(target: Target) -> tuple[bool, str]:
    chrome = find_chrome()
    if not chrome:
        return False, "chrome.exe não encontrado."
    urls = [u for u in target.urls if u.strip()]
    cmd = [chrome]
    if target.chrome_profile.strip():
        cmd.append(f"--profile-directory={target.chrome_profile.strip()}")
    cmd.extend(urls)
    subprocess.Popen(cmd, creationflags=_CREATION_FLAGS, close_fds=True)
    tabs = f"{len(urls)} aba(s)" if urls else "sem abas"
    return True, f"Chrome aberto ({tabs})."


def _launch_url(target: Target) -> tuple[bool, str]:
    url = target.url.strip()
    if not url:
        return False, "URL não definida."
    os.startfile(url)  # noqa: S606 - opens default browser on Windows
    return True, "Link aberto no navegador padrão."


class LaunchWorker(QThread):
    """Runs the enabled targets in order, honoring each target's delay_after."""

    item_started = Signal(int)                     # index
    item_finished = Signal(int, bool, str)         # index, ok, message
    countdown = Signal(int, float, float)          # index, remaining, total
    sequence_finished = Signal(int, int)           # launched_ok, total

    def __init__(self, targets: list[Target]) -> None:
        super().__init__()
        self._targets = targets
        self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    def run(self) -> None:
        enabled = [(i, t) for i, t in enumerate(self._targets) if t.enabled]
        launched_ok = 0
        for position, (index, target) in enumerate(enabled):
            if self._cancel:
                break
            self.item_started.emit(index)
            ok, message = launch_target(target)
            if ok:
                launched_ok += 1
            self.item_finished.emit(index, ok, message)

            is_last = position == len(enabled) - 1
            delay = max(0.0, float(target.delay_after))
            if not is_last and delay > 0 and not self._cancel:
                self._sleep_with_countdown(index, delay)

        self.sequence_finished.emit(launched_ok, len(enabled))

    def _sleep_with_countdown(self, index: int, total: float) -> None:
        step = 0.1
        remaining = total
        while remaining > 0 and not self._cancel:
            self.countdown.emit(index, remaining, total)
            time.sleep(min(step, remaining))
            remaining -= step
        self.countdown.emit(index, 0.0, total)

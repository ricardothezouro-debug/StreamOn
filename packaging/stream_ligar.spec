# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: builds two windowed executables that share one dist folder.

    dist/StreamLigar/
        Stream Ligar.exe   -> the launcher
        Config.exe         -> the editor
        _internal/...      -> shared PySide6 runtime + assets

Build from the project root:
    pyinstaller packaging/stream_ligar.spec --noconfirm
"""

import os

ROOT = os.path.dirname(os.path.abspath(SPECPATH))
SRC = os.path.join(ROOT, "src")
ICON = os.path.join(SRC, "stream_ligar", "assets", "brand", "app_icon.ico")
ASSETS = (os.path.join(SRC, "stream_ligar", "assets"), os.path.join("stream_ligar", "assets"))

launcher_a = Analysis(
    [os.path.join(SRC, "stream_ligar", "launcher_main.py")],
    pathex=[SRC],
    binaries=[],
    datas=[ASSETS],
    hiddenimports=["stream_ligar.ui.config_window"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

config_a = Analysis(
    [os.path.join(SRC, "stream_ligar", "config_main.py")],
    pathex=[SRC],
    binaries=[],
    datas=[ASSETS],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

# Share common dependencies between the two executables (dedup the PySide6 payload).
MERGE(
    (launcher_a, "launcher_main", "Stream Ligar"),
    (config_a, "config_main", "Config"),
)

launcher_pyz = PYZ(launcher_a.pure)
launcher_exe = EXE(
    launcher_pyz,
    launcher_a.scripts,
    [],
    exclude_binaries=True,
    name="Stream Ligar",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=ICON,
)

config_pyz = PYZ(config_a.pure)
config_exe = EXE(
    config_pyz,
    config_a.scripts,
    [],
    exclude_binaries=True,
    name="Config",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=ICON,
)

coll = COLLECT(
    launcher_exe,
    launcher_a.binaries,
    launcher_a.datas,
    config_exe,
    config_a.binaries,
    config_a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="StreamLigar",
)

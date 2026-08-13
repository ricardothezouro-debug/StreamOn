"""Chrome discovery helpers: locate the executable and read user profiles."""

import json
import os
from pathlib import Path


def find_chrome() -> str:
    """Return the path to chrome.exe, or an empty string if not found."""
    candidates = [
        Path(os.getenv("PROGRAMFILES", r"C:\Program Files")) / "Google/Chrome/Application/chrome.exe",
        Path(os.getenv("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "Google/Chrome/Application/chrome.exe",
        Path(os.getenv("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return ""


def chrome_user_data_dir() -> Path:
    return Path(os.getenv("LOCALAPPDATA", "")) / "Google/Chrome/User Data"


def list_chrome_profiles() -> list[tuple[str, str]]:
    """Return [(directory, display_name)] for every Chrome profile found.

    ``directory`` is what Chrome expects in ``--profile-directory`` (e.g. "Default",
    "Profile 2"); ``display_name`` is the friendly label the user sees ("Ricardo").
    """
    local_state = chrome_user_data_dir() / "Local State"
    profiles: list[tuple[str, str]] = []
    try:
        data = json.loads(local_state.read_text(encoding="utf-8"))
        info_cache = data.get("profile", {}).get("info_cache", {})
        for directory, meta in info_cache.items():
            name = str(meta.get("name") or directory)
            profiles.append((directory, name))
    except (OSError, json.JSONDecodeError, AttributeError):
        return profiles
    # Keep "Default" first, then Profile 1, Profile 2, ... in a stable order.
    profiles.sort(key=lambda item: (item[0] != "Default", item[0]))
    return profiles


def profile_display_name(directory: str) -> str:
    for candidate_dir, name in list_chrome_profiles():
        if candidate_dir == directory:
            return name
    return directory

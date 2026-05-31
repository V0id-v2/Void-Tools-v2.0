"""Void-Tools — settings.json load/save."""
import json
import os
from . import constants as C

DEFAULTS = {
    "language": "en",
    "theme": "red",
    "username": "Operator",
    "skip_boot": False,
    "setup_complete": False,
    "last_seen_config_rev": "0",
    "last_remote_sync": 0,
}


class Settings:
    def __init__(self):
        self.data = dict(DEFAULTS)
        self.load()

    def load(self):
        os.makedirs(C.CONFIG_DIR, exist_ok=True)
        if os.path.isfile(C.SETTINGS_PATH):
            try:
                with open(C.SETTINGS_PATH, encoding="utf-8") as f:
                    merged = {**DEFAULTS, **json.load(f)}
                merged.pop("compact_mode", None)
                self.data = merged
            except Exception:
                pass
        C.apply_theme(C._THEME_ALIASES.get(self.data.get("theme", "red"), self.data.get("theme", "red")))

    def save(self):
        os.makedirs(C.CONFIG_DIR, exist_ok=True)
        with open(C.SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self.data.get(key, default if default is not None else DEFAULTS.get(key))

    def set(self, key, value):
        self.data[key] = value
        if key == "theme":
            C.apply_theme(C._THEME_ALIASES.get(value, value))

    @property
    def lang(self):
        return self.data.get("language", "en")

    @property
    def username(self):
        return self.data.get("username", "Operator")


_settings = None


def get_settings():
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def nuker_status():
    """Return (token_ok, server_ok) for dashboard monitor."""
    if not os.path.isfile(C.NUKER_CFG_PATH):
        return False, False
    try:
        with open(C.NUKER_CFG_PATH, encoding="utf-8") as f:
            d = json.load(f)
        return bool(d.get("token")), bool(d.get("server_id"))
    except Exception:
        return False, False

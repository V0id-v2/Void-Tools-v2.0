"""Void-Tools — constants, paths, theme palette."""
import colorsys
import os

REMOTE_MANIFEST_URL = (
    "https://raw.githubusercontent.com/V0id-v2/Void-Tools-v2.0/main/Void/config/remote-manifest.json"
)

VERSION = "2.0.0"
GITHUB = "https://github.com/V0id-v2/Void-Tools-v2.0"
STAR_GIF_URL = (
    "https://raw.githubusercontent.com/V0id-v2/Void-Tools-v2.0/main/Void/screenshots/star.PNG"
)
NUKER_GITHUB = "https://github.com/void4real/Void-Nuke"
DISCORD = "https://discord.gg/v0id"
SHOP = "https://void-tools.mysellauth.com/"
AUTHOR = "1s0e"

VOID_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(VOID_DIR)
CONFIG_DIR = os.path.join(VOID_DIR, "config")
DATA_DIR = os.path.join(VOID_DIR, "data")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")
NUKER_CFG_PATH = os.path.join(CONFIG_DIR, "discord-nuker.json")
CUSTOM_TOOLS_DIR = os.path.join(VOID_DIR, "tools", "custom")

CHANGELOG = """VOID-TOOLS v2.0.0
- Dashboard modulaire · 150+ tools · 13 thèmes + rainbow
- Remote sync Discord / shop / alertes MAJ · auto-update ZIP
- Setup wizard FR/EN · premium → shop + Discord"""

THEMES = {
    "red": {
        "blood": "#8B0000", "dark": "#AA0000", "mid": "#CC0000",
        "red": "#EE0000", "neon": "#FF2020", "bright": "#FF4444",
    },
    "green": {
        "blood": "#0a3d0a", "dark": "#0d5c0d", "mid": "#118811",
        "red": "#22aa22", "neon": "#00FF88", "bright": "#88FFAA",
    },
    "blue": {
        "blood": "#0a1a4a", "dark": "#1a2a6a", "mid": "#2244aa",
        "red": "#3366cc", "neon": "#4488FF", "bright": "#88BBFF",
    },
    "yellow": {
        "blood": "#5c4a00", "dark": "#7a6200", "mid": "#997a00",
        "red": "#cc9900", "neon": "#FFD700", "bright": "#FFEE88",
    },
    "purple": {
        "blood": "#2a0a4a", "dark": "#3a126a", "mid": "#551a99",
        "red": "#7733cc", "neon": "#AA44FF", "bright": "#CC88FF",
    },
    "cyan": {
        "blood": "#003344", "dark": "#004455", "mid": "#006677",
        "red": "#008899", "neon": "#00DDFF", "bright": "#88EEFF",
    },
    "orange": {
        "blood": "#4a1a00", "dark": "#6a2800", "mid": "#994400",
        "red": "#cc6600", "neon": "#FF8800", "bright": "#FFBB66",
    },
    "pink": {
        "blood": "#4a0028", "dark": "#6a0038", "mid": "#990055",
        "red": "#cc2288", "neon": "#FF44AA", "bright": "#FF88CC",
    },
    "lime": {
        "blood": "#1a3d00", "dark": "#285c00", "mid": "#3d8800",
        "red": "#66cc00", "neon": "#AAFF00", "bright": "#CCFF66",
    },
    "white": {
        "blood": "#333333", "dark": "#555555", "mid": "#777777",
        "red": "#aaaaaa", "neon": "#FFFFFF", "bright": "#EEEEEE",
    },
    "rose": {
        "blood": "#4a1020", "dark": "#6a1830", "mid": "#992848",
        "red": "#cc4466", "neon": "#FF6688", "bright": "#FF99AA",
    },
    "gold": {
        "blood": "#3d2e00", "dark": "#5c4500", "mid": "#886600",
        "red": "#bb9900", "neon": "#FFCC00", "bright": "#FFE566",
    },
}

THEME_LABELS = {
    "red": ("Rouge", "Red"),
    "green": ("Vert", "Green"),
    "blue": ("Bleu", "Blue"),
    "yellow": ("Jaune", "Yellow"),
    "purple": ("Violet", "Purple"),
    "cyan": ("Cyan", "Cyan"),
    "orange": ("Orange", "Orange"),
    "pink": ("Rose", "Pink"),
    "lime": ("Lime", "Lime"),
    "white": ("Blanc", "White"),
    "rose": ("Rose vif", "Rose"),
    "gold": ("Or", "Gold"),
    "rainbow": ("Arc-en-ciel", "Rainbow"),
}

THEME_ORDER = list(THEMES.keys()) + ["rainbow"]

_THEME_ALIASES = {
    "crimson": "red", "discord": "blue", "roblox": "red",
    "midnight": "purple", "white": "white",
}

_ACTIVE_THEME = "red"

C_WHITE = "#FFFFFF"
C_SILVER = "#CCCCCC"
C_DIM = "#444444"
C_GOLD = "#FFD700"
C_GOLD2 = "#FFA500"

# Active theme (updated by apply_theme)
C_BLOOD = THEMES["red"]["blood"]
C_DARK = THEMES["red"]["dark"]
C_MID = THEMES["red"]["mid"]
C_RED = THEMES["red"]["red"]
C_NEON = THEMES["red"]["neon"]
C_BRIGHT = THEMES["red"]["bright"]


def _hsv_hex(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def rainbow_hex(phase=0.0, sat=1.0, val=1.0):
    return _hsv_hex(phase, sat, val)


def is_rainbow():
    return _ACTIVE_THEME == "rainbow"


def active_theme():
    return _ACTIVE_THEME


def _rainbow_palette(phase=0.0):
    h = phase % 1.0
    return {
        "blood": _hsv_hex(h, 0.85, 0.35),
        "dark": _hsv_hex(h + 0.02, 0.9, 0.45),
        "mid": _hsv_hex(h + 0.04, 0.95, 0.55),
        "red": _hsv_hex(h + 0.06, 1.0, 0.7),
        "neon": _hsv_hex(h + 0.08, 1.0, 1.0),
        "bright": _hsv_hex(h + 0.12, 0.85, 1.0),
    }


def palette(phase=0.0):
    """Couleurs actives — animées si thème rainbow."""
    if _ACTIVE_THEME == "rainbow":
        return _rainbow_palette(phase)
    return {
        "blood": C_BLOOD, "dark": C_DARK, "mid": C_MID,
        "red": C_RED, "neon": C_NEON, "bright": C_BRIGHT,
    }


def sp(folder, name):
    return os.path.join(VOID_DIR, "tools", folder, name)


def sp_discord(name):
    return os.path.join(VOID_DIR, "tools", "discord", name)


def sp_roblox(name):
    return os.path.join(VOID_DIR, "tools", "roblox", name)


def sp_social(name):
    return os.path.join(VOID_DIR, "tools", "social", name)


def sp_nuker():
    return os.path.join(VOID_DIR, "tools", "void-nuke", "main.py")


def apply_theme(name: str):
    global C_BLOOD, C_DARK, C_MID, C_RED, C_NEON, C_BRIGHT, _ACTIVE_THEME
    name = _THEME_ALIASES.get(name, name)
    if name != "rainbow" and name not in THEMES:
        name = "red"
    _ACTIVE_THEME = name
    if name == "rainbow":
        p = _rainbow_palette(0.0)
    else:
        p = THEMES[name]
    C_BLOOD, C_DARK, C_MID = p["blood"], p["dark"], p["mid"]
    C_RED, C_NEON, C_BRIGHT = p["red"], p["neon"], p["bright"]

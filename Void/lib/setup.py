"""First-run setup wizard — light, no lag."""
import time

from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from . import constants as C
from .config import get_settings
from .void_common import ansi_hex, cls, console, read_console_key


def _t(key, fr):
    L = {
        "sub": ("Configure ton profil", "Configure your profile"),
        "lang": ("Langue", "Language"),
        "color": ("Couleur", "Color"),
        "name": ("Pseudo", "Username"),
        "display": ("Démarrage", "Startup"),
        "skip": ("Skip boot anim", "Skip boot animation"),
        "yes": ("OUI", "YES"),
        "no": ("NON", "NO"),
        "hint1": ("↑ ↓ choisir · Entrée continuer", "↑ ↓ select · Enter continue"),
        "hint2": ("↑ ↓ couleur · Entrée continuer", "↑ ↓ color · Enter continue"),
        "hint3": ("Tape ton pseudo · Entrée continuer", "Type username · Enter continue"),
        "hint4": ("↑ ↓ OUI/NON · Entrée finir", "↑ ↓ YES/NO · Enter finish"),
        "save": ("Enregistrement...", "Saving..."),
        "ready": ("SYSTÈME PRÊT", "SYSTEM READY"),
        "welcome": ("Bienvenue", "Welcome"),
        "enter": ("Entrée pour le dashboard", "Enter for dashboard"),
        "fr": ("Français", "Français"),
        "en": ("English", "English"),
    }
    return L.get(key, (key, key))[0 if fr else 1]


COLOR_OPTIONS = []
for _key in C.THEME_ORDER:
    if _key == "rainbow":
        COLOR_OPTIONS.append((
            "rainbow", "RAINBOW", "#FF00FF",
            C.THEME_LABELS["rainbow"][0], C.THEME_LABELS["rainbow"][1],
        ))
    else:
        _theme = C.THEMES[_key]
        _lbl = C.THEME_LABELS.get(_key, (_key, _key))
        COLOR_OPTIONS.append((
            _key, _key.upper(), _theme["neon"], _lbl[0], _lbl[1],
        ))


def _skip_block(fr, skip_yes):
    yes_m = "[bold #88FFAA]►[/] " if skip_yes else "   "
    no_m = "[bold #88FFAA]►[/] " if not skip_yes else "   "
    return (
        f"[bold {C.C_WHITE}]{_t('skip', fr)}[/]\n\n"
        f"{yes_m}{_t('yes', fr)}\n"
        f"{no_m}{_t('no', fr)}"
    )


def _color_preview(key):
    if key == "rainbow":
        bars = " ".join(f"[{C.rainbow_hex(i / 7.0)}]██[/]" for i in range(8))
        return Panel(
            Align.center(Text.from_markup(
                f"{bars}\n[bold {C.rainbow_hex(0.33)}]RAINBOW[/]"
            )),
            border_style=C.rainbow_hex(0.15),
            box=box.ROUNDED,
            padding=(1, 2),
        )
    t = C.THEMES.get(key, C.THEMES["red"])
    return Panel(
        Align.center(Text.from_markup(
            f"[{t['neon']}]████████[/]\n"
            f"[{t['blood']}]████████[/]\n"
            f"[bold {t['bright']}]{key.upper()}[/]"
        )),
        border_style=t["neon"],
        box=box.ROUNDED,
        padding=(1, 2),
    )


def _draw(step, fr, sel_lang, sel_color, name_buf, sel_skip):
    bar = "█" * step + "░" * (4 - step)
    head = Panel(
        Align.center(Text.from_markup(
            f"[bold {C.C_GOLD}]VOID CONFIG[/]  [{C.C_DIM}]·[/]  [{C.C_SILVER}]{_t('sub', fr)}[/]\n"
            f"[{C.C_NEON}]{bar}[/]  [{C.C_DIM}]{step}/4[/]"
        )),
        border_style=C.C_BLOOD, box=box.HEAVY_EDGE,
    )

    grid = Table.grid(padding=(1, 2))
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)

    if step == 1:
        grid.add_row(
            Panel(
                Align.center(Text.from_markup(
                    f"[bold {C.C_WHITE}]{_t('lang', fr)}[/]\n\n"
                    f"{'[bold #88FFAA]►[/] ' if sel_lang == 0 else '   '}{_t('fr', fr)}\n"
                    f"{'[bold #88FFAA]►[/] ' if sel_lang == 1 else '   '}{_t('en', fr)}"
                )),
                title="[gold1]01[/]", border_style=C.C_BLOOD, box=box.DOUBLE,
            ),
            Panel(
                Align.center(Text.from_markup(f"[{C.C_DIM}]{_t('hint1', fr)}[/]")),
                border_style=C.C_DIM, box=box.ROUNDED,
            ),
        )
        hint = _t("hint1", fr)
    elif step == 2:
        lines = []
        for i, (key, label, hex_c, dfr, den) in enumerate(COLOR_OPTIONS):
            desc = dfr if fr else den
            mark = "[bold #88FFAA]►[/] " if i == sel_color else "   "
            lines.append(f"{mark}[{hex_c} bold]{label:8}[/]  [{C.C_DIM}]{desc}[/]")
        key = COLOR_OPTIONS[sel_color][0]
        grid.add_row(
            Panel(Text.from_markup("\n".join(lines)), title=f"[gold1]02 · {_t('color', fr)}[/]",
                  border_style=C.C_BLOOD, box=box.DOUBLE),
            _color_preview(key),
        )
        hint = _t("hint2", fr)
    elif step == 3:
        grid.add_row(
            Panel(
                Align.center(Text.from_markup(
                    f"[bold {C.C_WHITE}]{_t('name', fr)}[/]\n\n"
                    f"[bold {C.C_NEON}]{name_buf or 'Operator'}▌[/]"
                )),
                title="[gold1]03[/]", border_style=C.C_BLOOD, box=box.DOUBLE,
            ),
            Panel(Align.center(Text.from_markup(f"[{C.C_DIM}]{_t('hint3', fr)}[/]")),
                 border_style=C.C_DIM, box=box.ROUNDED),
        )
        hint = _t("hint3", fr)
    else:
        grid.add_row(
            Panel(
                Align.center(Text.from_markup(_skip_block(fr, sel_skip))),
                title=f"[gold1]04 · {_t('display', fr)}[/]", border_style=C.C_BLOOD, box=box.DOUBLE,
            ),
            Panel(Align.center(Text.from_markup(f"[{C.C_DIM}]{_t('hint4', fr)}[/]")),
                 border_style=C.C_DIM, box=box.ROUNDED),
        )
        hint = _t("hint4", fr)

    foot = Panel(Align.center(Text.from_markup(f"[{C.C_DIM}]{hint}[/]")), border_style=C.C_DIM)
    cls()
    console.print(head)
    console.print(grid)
    console.print(foot)


def _save(fr, s):
    cls()
    console.print(Panel(Align.center(Text.from_markup(f"[bold {C.C_GOLD}]{_t('save', fr)}[/]")),
                        border_style=C.C_BLOOD))
    s.set("setup_complete", True)
    s.save()


def _outro(fr, s):
    cls()
    console.print(Panel(
        Align.center(Text.from_markup(
            f"[bold {C.C_NEON}]{_t('ready', fr)}[/]\n\n"
            f"{_t('welcome', fr)}, [bold {C.C_NEON}]{s.username}[/]\n"
            f"[{C.C_DIM}]{s.lang} · {s.get('theme')}[/]"
        )),
        title=f"[bold {C.C_GOLD}]VOID-TOOLS[/]",
        border_style=C.C_GOLD, box=box.DOUBLE, padding=(1, 3),
    ))
    input(f"  {ansi_hex(C.C_MID)}► {_t('enter', fr)}… \033[0m")


def run_setup_wizard(force=False):
    s = get_settings()
    if s.get("setup_complete") and not force:
        C.apply_theme(C._THEME_ALIASES.get(s.get("theme", "red"), s.get("theme", "red")))
        return

    cls()
    console.print(Panel(Align.center(Text.from_markup(
        f"[bold {C.C_GOLD}]VOID CONFIG[/]\n[{C.C_DIM}]Initialisation…[/]"
    )), border_style=C.C_BLOOD))
    time.sleep(0.35)

    sel_lang = 0 if s.lang != "en" else 1
    fr = sel_lang == 0
    theme_key = C._THEME_ALIASES.get(s.get("theme", "red"), s.get("theme", "red"))
    sel_color = next((i for i, (k, *_) in enumerate(COLOR_OPTIONS) if k == theme_key), 0)
    sel_skip = bool(s.get("skip_boot"))
    name_buf = "" if s.username in ("Operator", "") else s.username
    step = 1
    C.apply_theme(COLOR_OPTIONS[sel_color][0])

    while step <= 4:
        _draw(step, fr, sel_lang, sel_color, name_buf, sel_skip)
        key = read_console_key()

        if key in (b"H", b"P"):
            if step == 1:
                sel_lang, fr = (0, True) if key == b"H" else (1, False)
            elif step == 2:
                sel_color = (sel_color + (-1 if key == b"H" else 1)) % len(COLOR_OPTIONS)
                C.apply_theme(COLOR_OPTIONS[sel_color][0])
            elif step == 4:
                sel_skip = key == b"H"
            continue

        if key == b"\r":
            if step >= 4:
                break
            step += 1
            continue

        if step == 1 and key in (b"f", b"1"):
            sel_lang, fr = 0, True
        elif step == 1 and key in (b"e", b"2"):
            sel_lang, fr = 1, False
        elif step == 2 and key in (b"1", b"2", b"3", b"4", b"5", b"6", b"7", b"8", b"9"):
            sel_color = int(key) - 1
            if sel_color < len(COLOR_OPTIONS):
                C.apply_theme(COLOR_OPTIONS[sel_color][0])
        elif step == 3 and key == b"\x08":
            name_buf = name_buf[:-1]
        elif step == 3 and len(key) == 1 and key >= b" " and key <= b"~" and len(name_buf) < 24:
            name_buf += key.decode("utf-8", errors="ignore")
        elif step == 4 and key in (b"y", b"Y", b"o", b"O", b"M"):
            sel_skip = True
        elif step == 4 and key in (b"n", b"N", b"K"):
            sel_skip = False
        elif step == 4 and key == b" ":
            sel_skip = not sel_skip

    s.set("language", "fr" if sel_lang == 0 else "en")
    s.set("theme", COLOR_OPTIONS[sel_color][0])
    s.set("username", (name_buf or "Operator")[:24])
    s.set("skip_boot", sel_skip)
    C.apply_theme(COLOR_OPTIONS[sel_color][0])

    _save(fr, s)
    _outro(fr, s)
    cls()

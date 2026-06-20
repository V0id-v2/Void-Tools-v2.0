"""Void-Tools — shared UI helpers."""
import os
import re
import shutil
import subprocess
import sys
import time

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from . import constants as C
from .config import get_settings
from .i18n import t

console = Console(highlight=False)


def open_community_links():
    """Ouvre Telegram + Discord (liens remote sync)."""
    import webbrowser
    for url in (getattr(C, "TELEGRAM", ""), getattr(C, "DISCORD", "")):
        if not url:
            continue
        try:
            webbrowser.open(url)
        except Exception:
            pass


def open_first_launch_links():
    """Premier lancement : Telegram → voidv2 → dawa → GitHub + image star."""
    import webbrowser

    steps = (
        getattr(C, "TELEGRAM", "https://t.me/v0idtool"),
        getattr(C, "DISCORD", "https://discord.gg/voidv2"),
        getattr(C, "DISCORD_DAWA", "https://discord.gg/dawa"),
    )
    for url in steps:
        if not url:
            continue
        try:
            webbrowser.open(url)
        except Exception:
            pass
        time.sleep(0.5)

    try:
        github = getattr(C, "GITHUB", "")
        if github:
            webbrowser.open(github)
        time.sleep(0.4)
        star = star_image_path()
        if os.path.exists(star):
            if os.name == "nt":
                os.startfile(star)
            else:
                webbrowser.open(star)
    except Exception:
        pass


def mark_first_launch_done():
    flag_dir = os.path.join(C.DATA_DIR)
    os.makedirs(flag_dir, exist_ok=True)
    flag = os.path.join(flag_dir, ".launched")
    if not os.path.isfile(flag):
        with open(flag, "w", encoding="utf-8") as f:
            f.write("1")


def open_premium_links():
    """Ouvre Discord (shop premium) + Telegram."""
    import webbrowser
    webbrowser.open(C.DISCORD)
    open_community_links()


def star_image_path():
    shots = os.path.join(C.VOID_DIR, "screenshots")
    for name in ("star.PNG", "Star.png", "star.png", "Star.PNG"):
        path = os.path.join(shots, name)
        if os.path.exists(path):
            return path
    return os.path.join(shots, "star.PNG")


def star_unlock_label() -> str:
    return t("Star pour débloquer [STAR]", "Star for unlock [STAR]")


def localize_item_label(label: str, action) -> str:
    """Traduit les libellés figés au build (ex. star unlock slots)."""
    if action is open_star_unlock:
        return star_unlock_label()
    return label


def open_star_unlock():
    """Star funnel — Discord, GitHub repo, star screenshot."""
    import webbrowser

    panel(
        t("STAR POUR DÉBLOQUER", "STAR FOR UNLOCK"),
        t(
            "Star le repo GitHub pour soutenir Void-Tools et débloquer le premium.",
            "Star the GitHub repo to support Void-Tools and unlock premium.",
        ),
    )
    try:
        open_community_links()
        time.sleep(0.4)
        webbrowser.open(C.GITHUB)
        time.sleep(0.4)
        star = star_image_path()
        if os.path.exists(star):
            if os.name == "nt":
                os.startfile(star)
            else:
                webbrowser.open(star)
    except Exception:
        pass
    pause()


def append_star_unlock_items(items):
    """Ajoute 4 slots Star for unlock en bas de catégorie."""
    if not items:
        return items
    label = star_unlock_label()
    base = len(items)
    extra = []
    for i in range(4):
        code = f"{base + i + 1:02d}"
        extra.append((code, label, open_star_unlock))
    return list(items) + extra


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def tw():
    return shutil.get_terminal_size((100, 30)).columns


def th():
    return shutil.get_terminal_size((100, 30)).lines


def ansi_hex(h):
    hx = h.lstrip("#")
    r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"


def poll_console_key():
    """Read one key; arrows normalized to H/P/K/M. None if idle."""
    import msvcrt
    if not msvcrt.kbhit():
        return None
    k = msvcrt.getch()
    if k in (b"\x00", b"\xe0"):
        k2 = msvcrt.getch()
        while msvcrt.kbhit():
            msvcrt.getch()
        return k2
    return k


def read_console_key():
    """Block until key pressed."""
    while True:
        k = poll_console_key()
        if k is not None:
            return k
        time.sleep(0.01)


def is_arrow(k):
    return k in (b"H", b"P", b"K", b"M")


def pause(msg=None):
    console.print()
    if msg is None:
        msg = t(
            "\033[38;2;120;0;0m  ► Entrée pour continuer…\033[0m",
            "\033[38;2;120;0;0m  ► Press Enter to continue…\033[0m",
        )
    input(msg)


def fmt_label(label: str, max_len: int = 24) -> str:
    clean = re.sub(r"\s*\[(PREMIUM|STAR)\]", "", label, flags=re.I).strip()
    if len(clean) > max_len:
        clean = clean[: max_len - 1] + "…"
    return clean


def is_star_unlock(label: str) -> bool:
    return "[STAR]" in str(label).upper()


def is_premium(label: str) -> bool:
    return "[PREMIUM]" in str(label).upper() or is_star_unlock(label)


def sort_free_first(items):
    if not items:
        return items
    head, normal, tail = [], [], []
    for item in items:
        code = str(item[0]).upper()
        if code == "00":
            head.append(item)
        elif code in ("X", "Q", "41"):
            tail.append(item)
        else:
            normal.append(item)
    ordered = [x for x in normal if not is_premium(x[1])] + [x for x in normal if is_premium(x[1])]
    out, n = [], 1
    for _, label, action in ordered:
        out.append((f"{n:02d}", label, action))
        n += 1
    tail_codes = {str(t[0]).upper() for t in tail}
    tail_sorted = [i for i in items if str(i[0]).upper() in tail_codes]
    return head + out + tail_sorted


def count_free_premium(items):
    free = prem = 0
    for _, label, _ in items:
        if is_premium(label):
            prem += 1
        else:
            free += 1
    return free, prem


def panel(title, desc):
    console.print()
    console.print(Panel(
        Align.center(Text.from_markup(
            f"[{C.C_GOLD} bold]◆ {title}[/]\n[{C.C_DIM}]{desc}[/]"
        )),
        border_style=C.C_BLOOD, box=box.DOUBLE_EDGE, padding=(1, 3),
        width=min(64, tw() - 2),
    ))
    console.print()


def error_box(title: str, message: str, detail: str = None):
    body = Text.from_markup(f"[{C.C_NEON} bold]{message}[/]")
    if detail:
        body.append("\n")
        body.append(Text.from_markup(f"[{C.C_DIM}]{detail}[/]"))
    console.print(Panel(body, title=f"[bold white]✖ {title}[/]", border_style=C.C_NEON, box=box.HEAVY, padding=(1, 2)))


def success_box(title: str, message: str):
    console.print(Panel(
        Text.from_markup(f"[#88FFAA bold]{message}[/]"),
        title=f"[bold white]✔ {title}[/]", border_style="#88FFAA", box=box.ROUNDED, padding=(0, 2),
    ))


def safe_action(fn, tool_name: str = "Module"):
    try:
        fn()
    except KeyboardInterrupt:
        console.print(f"\n[{C.C_DIM}]  ○ {tool_name} — {t('annulé', 'cancelled')}[/]")
        time.sleep(0.6)
    except FileNotFoundError as e:
        error_box(
            t("Fichier introuvable", "File not found"),
            str(e),
            t("Vérifie l'installation de Void-Tools.", "Check your Void-Tools installation."),
        )
        time.sleep(2)
    except subprocess.CalledProcessError as e:
        error_box(
            t("Exécution échouée", "Execution failed"),
            tool_name,
            f"{t('code sortie', 'exit code')}: {e.returncode}",
        )
        time.sleep(2)
    except Exception as e:
        error_box(t("Erreur", "Error"), tool_name, f"{type(e).__name__}: {e}")
        time.sleep(2)

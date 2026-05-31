"""Dashboard UI — Rich panels, theme colors, no blink."""
import time

from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from rich import box

from . import constants as C
from .void_common import count_free_premium, fmt_label, is_premium


def _phase():
    return (time.time() * 0.15) % 1.0 if C.is_rainbow() else 0.0


def make_title_text(text="VOID-TOOLS", phase=None):
    phase = _phase() if phase is None else phase
    txt = Text()
    if C.is_rainbow():
        for i, char in enumerate(text):
            txt.append(char, style=C.rainbow_hex(phase + i * 0.045))
        return txt
    p = C.palette(phase)
    for i, char in enumerate(text):
        c = p["neon"] if i % 2 == 0 else p["bright"]
        txt.append(char, style=c)
    return txt


def make_card_cell(key, label, is_selected, phase=None):
    if not key or not str(key).strip() or key == "  ":
        return Text("")

    phase = _phase() if phase is None else phase
    p = C.palette(phase)
    prem = is_premium(label)
    color = p["neon"] if is_selected else (C.C_GOLD if prem else p["blood"])
    border = C.C_WHITE if is_selected else (C.C_GOLD if prem else C.C_DIM)
    style = p["neon"] if is_selected else (C.C_GOLD2 if prem else C.C_WHITE)
    text = fmt_label(label, max_len=26)
    inner = Text.from_markup(
        f"[{style} bold] {text} [/]" if is_selected else f"   [{style}]{text}[/]   "
    )
    return Panel(
        Align.center(inner),
        title=f"[{color} bold]{key}[/]",
        title_align="left",
        border_style=border,
        box=box.HEAVY if is_selected else box.ROUNDED,
        padding=(1, 1),
    )


def monitor_block(cat_label, n_tools, items, username, nuker=(False, False), remote_badge="", phase=None):
    phase = _phase() if phase is None else phase
    p = C.palette(phase)
    free, prem = count_free_premium(items)
    tok = "OK" if nuker[0] else "--"
    srv = "OK" if nuker[1] else "--"
    user = (username or "Op")[:14]
    cat = (cat_label or "?")[:12]
    badge = f"│ [{C.C_GOLD} bold]! {remote_badge}[/]\n" if remote_badge else ""
    return Text.from_markup(
        f"\n\n[{p['blood']}]┌─ MONITOR\n"
        f"{badge}"
        f"│ [bold {p['neon']}]{user}[/]\n"
        f"│ [{C.C_GOLD}]{free}[/] free · [{C.C_GOLD2}]{prem}[/] vip\n"
        f"│ NUKER {tok}/{srv}\n"
        f"│ [{C.C_SILVER}]{cat}[/] · [{C.C_GOLD}]{n_tools}[/] tools\n"
        f"└─ [{p['neon']}]READY[/]"
    )

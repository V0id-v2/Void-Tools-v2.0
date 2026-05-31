"""Fuzzy global search with free/premium/category filters."""
from difflib import SequenceMatcher

from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from . import constants as C
from .void_common import ansi_hex, console, error_box, fmt_label, is_premium, pause


def _score(query: str, label: str, cat: str, code: str) -> float:
    blob = f"{label} {cat} {code}".lower()
    q = query.lower()
    if q in blob:
        return 1.0 + SequenceMatcher(None, q, label.lower()).ratio()
    tokens = q.split()
    if all(t in blob for t in tokens):
        return 0.85 + 0.1 * sum(1 for t in tokens if t in label.lower()) / max(len(tokens), 1)
    return SequenceMatcher(None, q, label.lower()).ratio() * 0.7


def parse_filters(raw: str):
    """Syntax: free: discord token  |  prem: nuke  |  cat:roblox item"""
    parts = raw.strip().split()
    tier, cat = None, None
    terms = []
    for p in parts:
        pl = p.lower()
        if pl in ("free:", "free"):
            tier = "free"
        elif pl in ("prem:", "premium:", "prem", "premium"):
            tier = "premium"
        elif pl.startswith("cat:"):
            cat = pl[4:]
        else:
            terms.append(p)
    return tier, cat, " ".join(terms) if terms else raw.strip()


def search_tools(categories, pages_data, raw_query: str, limit=40):
    tier_f, cat_f, q = parse_filters(raw_query)
    if not q and not tier_f and not cat_f:
        return []

    matches = []
    for cat_key, cat_label in categories:
        if cat_f and cat_f not in cat_key.lower() and cat_f not in cat_label.lower():
            continue
        for code, label, action in pages_data.get(cat_key, []):
            prem = is_premium(label)
            if tier_f == "free" and prem:
                continue
            if tier_f == "premium" and not prem:
                continue
            if q:
                sc = _score(q, label, cat_label, str(code))
                if sc < 0.35:
                    continue
            else:
                sc = 1.0
            matches.append((sc, cat_label, code, label, action))

    matches.sort(key=lambda x: -x[0])
    return matches[:limit]


def run_search_ui(router, live):
    from .void_common import cls

    live.stop()
    cls()
    s = router.settings
    hint = (
        "free: · prem: · cat:discord · fuzzy"
        if s.lang == "fr"
        else "free: · prem: · cat:discord · fuzzy"
    )
    console.print(Panel(
        Align.center(Text.from_markup(
            f"[{C.C_GOLD} bold]{'RECHERCHE' if s.lang == 'fr' else 'SEARCH'}[/]\n[{C.C_DIM}]{hint}[/]"
        )),
        border_style=C.C_BLOOD, box=box.DOUBLE_EDGE, padding=(0, 2),
    ))
    q = input(f"\n{ansi_hex(C.C_MID)}  >> \033[0m").strip()
    if not q:
        cls()
        live.start()
        return

    matches = search_tools(router.categories, router.pages_data, q)
    if not matches:
        error_box("Aucun résultat" if s.lang == "fr" else "No results", q, "free: token · cat:social")
        pause()
        cls()
        live.start()
        return

    console.print()
    tbl = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style=f"bold {C.C_GOLD}")
    tbl.add_column("#", style=C.C_GOLD, width=4)
    tbl.add_column("Cat", style=C.C_DIM, max_width=12)
    tbl.add_column("Code", width=5)
    tbl.add_column("Tool")
    tbl.add_column("Type", width=8)
    for i, (_, cat, code, label, _) in enumerate(matches[:30], 1):
        typ = "PREM" if is_premium(label) else "FREE"
        tbl.add_row(f"{i:02d}", cat[:12], str(code), fmt_label(label), typ)
    console.print(Padding(tbl, (0, 2)))
    console.print(Text.from_markup(f"  [{C.C_DIM}]{len(matches)} result(s)[/]"))
    pick = input(f"\n{ansi_hex(C.C_MID)}  # (Entrée = retour) >> \033[0m").strip()
    if pick.isdigit() and 1 <= int(pick) <= min(30, len(matches)):
        _, _, _, lbl, act = matches[int(pick) - 1]
        router._run_tool(live, act, lbl)
        return
    pause()
    cls()
    live.start()

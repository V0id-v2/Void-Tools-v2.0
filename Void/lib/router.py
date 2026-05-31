"""Main dashboard — Rich layout, live clock, sidebar scroll."""
import shutil
import time

import msvcrt
from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from . import constants as C
from . import remote as R
from .config import get_settings, nuker_status
from .pages import build_pages_data
from .plugins import discover_plugins
from .search import run_search_ui
from .ui import make_card_cell, make_title_text, monitor_block
from .void_common import cls, is_arrow, poll_console_key, safe_action, sort_free_first


class MasterRouter:
    MAX_ROWS = 4
    MAX_CAT_VISIBLE = 9

    def __init__(self):
        self.settings = get_settings()
        plugins = discover_plugins()
        cats = [
            ("home", "HOME"), ("osint", "OSINT"), ("attack", "ATTACK"),
            ("nuker", "NUKER"), ("discord", "DISCORD"), ("social", "SOCIAL"),
            ("roblox", "ROBLOX"), ("ip-web", "IP / WEB"), ("generator", "GEN"),
            ("crypto-utils", "UTILS"), ("darkweb", "DARKWEB"), ("about", "ABOUT"),
        ]
        if plugins:
            cats.insert(-1, ("plugins", "PLUGINS"))
        self.categories = cats
        self.cat_idx = 0
        self.cat_scroll = 0
        self.grid_idx = 0
        self.scroll_row = 0
        self.focus = "sidebar"
        self.running = True
        self._nuker = (False, False)
        self._nuker_at = 0.0
        self._next_remote = time.time() + 300
        self.pages_data = build_pages_data(plugins)
        skip = {"nuker", "home", "about", "darkweb", "generator", "crypto-utils", "plugins"}
        for key, items in self.pages_data.items():
            if key not in skip:
                self.pages_data[key] = sort_free_first(items)

    def _cat_key(self):
        return self.categories[self.cat_idx][0]

    def _tools(self):
        return self.pages_data.get(self._cat_key(), [])

    def _nuker_state(self):
        now = time.time()
        if now - self._nuker_at > 5.0:
            self._nuker = nuker_status()
            self._nuker_at = now
        return self._nuker

    def _sync_cat_scroll(self):
        n = len(self.categories)
        max_scroll = max(0, n - self.MAX_CAT_VISIBLE)
        if self.cat_idx < self.cat_scroll:
            self.cat_scroll = self.cat_idx
        elif self.cat_idx >= self.cat_scroll + self.MAX_CAT_VISIBLE:
            self.cat_scroll = self.cat_idx - self.MAX_CAT_VISIBLE + 1
        self.cat_scroll = max(0, min(self.cat_scroll, max_scroll))

    def _sync_scroll(self):
        tools = self._tools()
        n = len(tools)
        if not n:
            self.scroll_row = 0
            return
        total_rows = (n + 1) // 2
        active_row = self.grid_idx // 2
        max_scroll = max(0, total_rows - self.MAX_ROWS)
        if active_row < self.scroll_row:
            self.scroll_row = active_row
        elif active_row >= self.scroll_row + self.MAX_ROWS:
            self.scroll_row = active_row - self.MAX_ROWS + 1
        self.scroll_row = max(0, min(self.scroll_row, max_scroll))

    def build_ui(self):
        s = self.settings
        tools = self._tools()
        phase = (time.time() * 0.15) % 1.0 if C.is_rainbow() else 0.0
        pal = C.palette(phase)
        n = len(tools)
        if n:
            self.grid_idx = max(0, min(n - 1, self.grid_idx))
        else:
            self.grid_idx = 0
        self._sync_cat_scroll()
        self._sync_scroll()

        layout = Layout()
        layout.split_column(Layout(name="header", size=4), Layout(name="main"))
        layout["main"].split_row(Layout(name="sidebar", size=30), Layout(name="body"))

        head = Table.grid(expand=True)
        head.add_column(ratio=1, justify="left")
        head.add_column(ratio=2, justify="center")
        head.add_column(ratio=1, justify="right")
        head.add_row(
            Text.from_markup(f"[{pal['neon']} bold]● ONLINE[/]"),
            make_title_text("VOID-TOOLS", phase),
            Text.from_markup(f"[bold {pal['neon']}]{s.username[:16]}[/]"),
        )
        badge = R.status_badge()
        sub = f"[ {time.strftime('%H:%M:%S')} ]"
        if badge:
            sub += f"  [{C.C_GOLD} bold]! {badge}[/]"
        layout["header"].update(Panel(
            head, border_style=pal["blood"], box=box.HEAVY_EDGE,
            subtitle=sub,
        ))

        sidebar = Table.grid(expand=True)
        n_cat = len(self.categories)
        cat_up = f"[{pal['neon']}]▲[/]" if self.cat_scroll > 0 else " "
        cat_dn = f"[{pal['neon']}]▼[/]" if self.cat_scroll + self.MAX_CAT_VISIBLE < n_cat else " "
        sidebar.add_row(Text.from_markup(f"[{C.C_DIM}]{cat_up} {cat_dn}[/]"))

        end_cat = min(n_cat, self.cat_scroll + self.MAX_CAT_VISIBLE)
        for i in range(self.cat_scroll, end_cat):
            _, label = self.categories[i]
            act = i == self.cat_idx
            foc = act and self.focus == "sidebar"
            if foc:
                sidebar.add_row(Text.from_markup(f"[black on {pal['neon']} bold] » {label:<22} [/]"))
            elif act:
                sidebar.add_row(Text.from_markup(f"[{pal['neon']} bold] █ {label:<22} [/]"))
            else:
                sidebar.add_row(Text.from_markup(f"[{C.C_DIM}] │ {label:<22} [/]"))

        cat_label = self.categories[self.cat_idx][1]
        layout["sidebar"].update(Panel(
            Group(sidebar, monitor_block(cat_label, n, tools, s.username, self._nuker_state(), R.status_badge(), phase)),
            title="[bold white]CATEGORIES",
            border_style=pal["mid"],
            box=box.SQUARE,
            padding=(1, 2),
        ))

        start = self.scroll_row * 2
        end = min(n, start + self.MAX_ROWS * 2)
        visible = tools[start:end]
        grid = Table.grid(expand=True, padding=(1, 1))
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)
        for i in range(0, len(visible), 2):
            L = visible[i]
            right = visible[i + 1] if i + 1 < len(visible) else None
            abs_l, abs_r = start + i, start + i + 1
            sel = self.focus == "grid"
            grid.add_row(
                make_card_cell(L[0], L[1], sel and self.grid_idx == abs_l, phase),
                make_card_cell(right[0], right[1], sel and self.grid_idx == abs_r, phase) if right else Text(""),
            )

        total_rows = max(1, (n + 1) // 2)
        up = f"[{pal['neon']}] ▲ MORE UP [/]" if self.scroll_row > 0 else "                  "
        dn = f"[{pal['neon']}] ▼ MORE DOWN [/]" if self.scroll_row + self.MAX_ROWS < total_rows else "                  "
        footer = Text.assemble(
            Text.from_markup(up), Text("   "), Text.from_markup(dn),
            Text("   "), Text.from_markup(f"[{C.C_DIM}]←→ · ↑↓ · Enter · F[/]"),
        )
        layout["body"].update(Panel(
            grid,
            title=f"[bold white]{cat_label}",
            subtitle=footer,
            border_style=pal["blood"],
            box=box.DOUBLE,
            padding=(1, 2),
        ))
        return layout

    def _on_arrow(self, k):
        tools = self._tools()
        n = len(tools)

        if k == b"H":
            if self.focus == "sidebar":
                self.cat_idx = (self.cat_idx - 1) % len(self.categories)
                self.grid_idx = 0
                self.scroll_row = 0
                self._sync_cat_scroll()
            else:
                self.grid_idx = max(0, self.grid_idx - 2)
                self._sync_scroll()
        elif k == b"P":
            if self.focus == "sidebar":
                self.cat_idx = (self.cat_idx + 1) % len(self.categories)
                self.grid_idx = 0
                self.scroll_row = 0
                self._sync_cat_scroll()
            else:
                if n:
                    if self.grid_idx + 2 < n:
                        self.grid_idx += 2
                    elif self.grid_idx + 1 < n:
                        self.grid_idx += 1
                self._sync_scroll()
        elif k == b"K":
            if self.focus == "grid":
                if self.grid_idx % 2 == 0:
                    self.focus = "sidebar"
                else:
                    self.grid_idx -= 1
        elif k == b"M":
            if self.focus == "sidebar":
                self.focus = "grid"
                self.grid_idx = 0
            elif self.grid_idx % 2 == 0 and n:
                self.grid_idx = min(n - 1, self.grid_idx + 1)

    def _on_key(self, k):
        if is_arrow(k):
            self._on_arrow(k)
            return "redraw"

        if k == b"\r":
            while msvcrt.kbhit():
                msvcrt.getch()
            if self.focus == "grid":
                tools = self._tools()
                if tools and self.grid_idx < len(tools):
                    return ("run", tools[self.grid_idx][2], tools[self.grid_idx][1])
            else:
                self.focus = "grid"
                self.grid_idx = 0
            return "redraw"

        if k in (b"f", b"F"):
            while msvcrt.kbhit():
                msvcrt.getch()
            return "search"

        if k == b"\x03":
            return "exit"

        return None

    def _run_tool(self, live, action, label="Module"):
        live.stop()
        cls()
        safe_action(action, label)
        cls()
        live.start()

    def start(self):
        cols, rows = shutil.get_terminal_size((100, 30))
        if cols < 90 or rows < 28:
            cls()
            print(f"\n  [!] Terminal trop petit ({cols}x{rows}). Min ~100x30.\n")
            input("  Enter...")
        cls()
        with Live(self.build_ui(), auto_refresh=False, screen=True, transient=False) as live:
            next_clock = time.time()
            while self.running:
                now = time.time()
                if now >= next_clock:
                    live.update(self.build_ui(), refresh=True)
                    next_clock = now + 1.0
                    if now >= self._next_remote:
                        R.sync()
                        self._next_remote = now + 300

                if msvcrt.kbhit():
                    k = poll_console_key()
                    if k is None:
                        continue
                    res = self._on_key(k)
                    if res == "exit":
                        break
                    if isinstance(res, tuple):
                        self._run_tool(live, res[1], res[2])
                    elif res == "search":
                        run_search_ui(self, live)
                    if res:
                        live.update(self.build_ui(), refresh=True)
                        next_clock = time.time() + 1.0
                else:
                    time.sleep(0.03)

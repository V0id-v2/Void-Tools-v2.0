import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, asyncio, aiohttp

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich import box

console = Console()

C_RED     = "#CC0000"
C_NEON    = "#FF2020"
C_WHITE   = "#FFFFFF"
C_DIM     = "#444444"

ASCII = r"""
   ██╗   ██╗███████╗███████╗██████╗ ███╗   ██╗ █████╗ ███╗   ███╗███████╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
   ██║   ██║██╔════╝██╔════╝██╔══██╗████╗  ██║██╔══██╗████╗ ████║██╔════╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
   ██║   ██║███████╗█████╗  ██████╔╝██╔██╗ ██║███████║██╔████╔██║█████╗      ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
   ██║   ██║╚════██║██╔══╝  ██╔══██╗██║╚██╗██║██╔══██║██║╚██╔╝██║██╔══╝      ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
   ╚██████╔╝███████║███████╗██║  ██║██║ ╚████║██║  ██║██║ ╚═╝ ██║███████╗    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
    ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
"""

SITES = [
    ("GitHub", "https://github.com/{}", "GitHub"),
    ("Twitter", "https://twitter.com/{}", "Twitter/X"),
    ("Instagram", "https://instagram.com/{}", "Instagram"),
    ("TikTok", "https://tiktok.com/@{}", "TikTok"),
    ("Reddit", "https://reddit.com/u/{}", "Reddit"),
    ("Twitch", "https://twitch.tv/{}", "Twitch"),
    ("YouTube", "https://youtube.com/@{}", "YouTube"),
    ("Steam", "https://steamcommunity.com/id/{}", "Steam"),
    ("Pinterest", "https://pinterest.com/{}", "Pinterest"),
    ("Telegram", "https://t.me/{}", "Telegram"),
    ("DailyMotion", "https://www.dailymotion.com/{}", "DailyMotion"),
    ("SoundCloud", "https://soundcloud.com/{}", "SoundCloud"),
    ("Roblox", "https://www.roblox.com/user.aspx?username={}", "Roblox")
]

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID USERNAME HUNTER // OSINT CORE")
    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.write("\033[?25l")
    lines = ASCII.strip("\n").split("\n")
    t0 = time.time()
    try:
        while time.time() - t0 < 1.4:
            t = time.time() - t0
            sys.stdout.write("\033[H\n")
            for line in lines:
                sys.stdout.write("  ")
                for c, ch in enumerate(line):
                    if ch == " ":
                        sys.stdout.write(" ")
                    else:
                        v = max(40, min(255, int(100 + 155 * math.sin(t * 10 - c * 0.2))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

async def check_site(session, url, name):
    try:
        async with session.get(url, timeout=5) as r:
            return name, r.status == 200
    except:
        return name, False

async def run_hunt(user, update_fn):
    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        tasks = []
        for name, url_tmpl, _ in SITES:
            tasks.append(check_site(session, url_tmpl.format(user), name))
        
        results = []
        for i, task in enumerate(asyncio.as_completed(tasks)):
            res = await task
            results.append(res)
            update_fn(res, i+1, len(SITES))
        return results

def main():
    boot()
    console.print(Align.center(Panel(Text.from_markup(f"[bold red]VOID-TOOLS[/] [dim]||[/] [white]USERNAME HUNTER V2[/]"), border_style="red", padding=(0, 5))))
    console.print()
    
    user = console.input(" [bold red]└─▶[/] [white]Username to hunt >> ").strip()
    if not user: return

    layout = Layout()
    layout.split_column(Layout(name="header", size=4), Layout(name="body", ratio=1), Layout(name="footer", size=3))
    
    results = []
    current_status = "Initializing..."
    progress = 0

    def update(res, count, total):
        nonlocal results, current_status, progress
        results.append(res)
        current_status = f"Scanning {res[0]}..."
        progress = int((count / total) * 100)

    import threading
    def start_loop(): asyncio.run(run_hunt(user, update))
    threading.Thread(target=start_loop, daemon=True).start()

    with Live(layout, screen=True, refresh_per_second=10):
        while len(results) < len(SITES):
            layout["header"].update(Panel(Align.center(Text.from_markup(f"[bold red]HUNTING : [white]{user}[/] [dim]||[/] [red]{progress}%")), border_style="red"))
            
            table = Table(box=box.SIMPLE, expand=True, header_style="bold red")
            table.add_column("PLATFORM", ratio=1)
            table.add_column("STATUS", ratio=1, justify="center")
            
            for name, found in sorted(results):
                status = "[bold green][✓] FOUND[/]" if found else "[dim red][x] MISSING[/]"
                table.add_row(name.upper(), status)
            
            layout["body"].update(Panel(table, title="[bold white]LIVE SCAN", border_style="red"))
            layout["footer"].update(Panel(Align.center(Text.from_markup(f"[dim]VOID OSINT ENGINE - SCANNING {current_status}[/]")), border_style="red"))
            time.sleep(0.1)

    os.system("cls")
    console.print(Align.center(Panel(Text.from_markup(f"[bold green]REPORT COMPLETED FOR : {user}"), border_style="green", padding=(1, 5))))
    
    final_table = Table(box=box.ROUNDED, border_style="red", expand=True)
    final_table.add_column("Platform", style="white")
    final_table.add_column("Result", justify="center")
    final_table.add_column("Direct Link", style="blue underline")
    
    for name, found in sorted(results):
        if found:
            url = [s[1] for s in SITES if s[0] == name][0].format(user)
            final_table.add_row(name, "[bold green]OPERATIONAL[/]", url)
    
    console.print(final_table)
    console.input(f"\n [dim]Press [bold red]ENTER[/] to exit...[/]")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit()

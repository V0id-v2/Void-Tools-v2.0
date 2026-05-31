import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, asyncio, threading, random, re
import subprocess

try:
    import holehe
    from holehe.core import import_submodules, get_functions
except ImportError:
    # Auto-install holehe but show a cool UI
    pass

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

console = Console()

# -- COLORS --
C_RED     = "#CC0000"
C_NEON    = "#FF2020"
C_WHITE   = "#FFFFFF"
C_SILVER  = "#CCCCCC"
C_DIM     = "#444444"
C_OK      = "#00FF00"
C_NO      = "#440000"

ASCII = r"""
   ██╗   ██╗ ██████╗ ██╗██████╗     ███████╗███╗   ███╗ █████╗ ██╗██╗     
   ██║   ██║██╔═══██╗██║██╔══██╗    ██╔════╝████╗ ████║██╔══██╗██║██║     
   ██║   ██║██║   ██║██║██║  ██║    █████╗  ██╔████╔██║███████║██║██║     
   ╚██╗ ██╔╝██║   ██║██║██║  ██║    ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║     
    ╚████╔╝ ╚██████╔╝██║██████╔╝    ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗
     ╚═══╝   ╚═════╝ ╚═╝╚═════╝     ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
"""

SUBTITLE = " E L I T E   E M A I L   O S I N T   I N T E L L I G E N C E "

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID EMAIL INTEL // OSINT CORE")
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
            sys.stdout.write(f"\n  \033[38;2;80;0;0m{SUBTITLE}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

def check_holehe():
    try:
        import holehe
        return True
    except ImportError:
        console.print("\n [bold yellow][!][/] Installation des dépendances OSINT manquantes...")
        subprocess.run([sys.executable, "-m", "pip", "install", "holehe", "aiohttp"], capture_output=True)
        return True

async def run_scan(email, update_fn):
    import holehe.modules
    from holehe.core import import_submodules, get_functions
    
    modules = import_submodules(holehe.modules)
    all_websites = get_functions(modules)
    
    found = []
    not_found = []
    total = len(all_websites)
    
    async def probe(website, name):
        try:
            # Simple wrapper to handle the library's internal async calls
            res = await website(email)
            if res:
                if res['exists']: found.append(name)
                else: not_found.append(name)
            update_fn(name, len(found) + len(not_found), total)
        except:
            not_found.append(name)
            update_fn(name, len(found) + len(not_found), total)

    # limit concurrency
    sem = asyncio.Semaphore(20)
    async def sem_probe(w, n):
        async with sem: await probe(w, n)

    tasks = [sem_probe(site, name) for name, site in all_websites.items()]
    await asyncio.gather(*tasks)
    return found

def make_layout():
    l = Layout()
    l.split_column(
        Layout(name="header", size=4),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3)
    )
    l["body"].split_row(
        Layout(name="results", ratio=2),
        Layout(name="stats", ratio=1)
    )
    return l

def main():
    boot()
    check_holehe()
    
    console.print(Align.center(Panel(
        Text.from_markup(f"[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]EMAIL CORE[/]  [dim]//[/]  [red]OSINT ANALYZER[/]"),
        border_style="red", padding=(0, 6)
    )))
    console.print()
    
    email = console.input(" [bold red]└─▶[/] [bold white]E-mail cible >> ").strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        console.print("\n [bold red][x][/] Format d'e-mail invalide.")
        time.sleep(2)
        return

    layout = make_layout()
    found_list = []
    current_site = "Initialisation..."
    progress_val = 0
    total_sites = 120
    start_time = time.time()

    def update_view(site, count, total):
        nonlocal current_site, progress_val, total_sites
        current_site = site
        progress_val = count
        total_sites = total

    async def scan_thread():
        nonlocal found_list
        found_list = await run_scan(email, update_view)

    loop_thread = threading.Thread(target=lambda: asyncio.run(scan_thread()), daemon=True)
    loop_thread.start()

    with Live(layout, refresh_per_second=10, screen=True) as live:
        while loop_thread.is_alive():
            layout["header"].update(Panel(Align.center(Text.from_markup(f"[bold red]VOID-EMAIL ENGINE[/] [dim]||[/] [white]SCAN EN COURS...[/]")), border_style="red"))
            
            # Results Table
            res_table = Table(box=box.SIMPLE, expand=True, show_header=True, header_style="bold red")
            res_table.add_column("PLATEFORME", ratio=2)
            res_table.add_column("STATUT", ratio=1, justify="center")
            
            # Show only found ones to keep it clean
            for f in sorted(found_list)[-15:]: # Show last 15 found
                res_table.add_row(f.upper(), f"[bold {C_OK}][✓] TROUVÉ[/]")
            
            layout["results"].update(Panel(res_table, title="[bold white]BASE DE DONNÉES", border_style="red"))
            
            # Stats Panel
            elapsed = time.time() - start_time
            stats_grp = Group(
                Text.from_markup(f"\n[red]CIBLE   :[/] [white]{email}"),
                Text.from_markup(f"[red]TROUVÉS :[/] [bold green]{len(found_list)}[/] sites"),
                Text.from_markup(f"[red]SCANNÉS :[/] [white]{progress_val}/{total_sites}"),
                Text.from_markup(f"[red]TEMPS   :[/] [white]{int(elapsed)}s"),
                Text.from_markup(f"\n[dim]CURRENT :[/]\n[bold silver]{current_site}"),
                Text.from_markup(f"\n[red][bold]PROGRESS :[/] [white]{int((progress_val/total_sites)*100)}%"),
            )
            layout["stats"].update(Panel(stats_grp, title="[bold white]OSINT STATS", border_style="red"))
            
            layout["footer"].update(Panel(Align.center(Text.from_markup(f"[dim]VOID ELITE OSINT SYSTEM - LICENSE VERIFIED[/]")), border_style="red"))
            time.sleep(0.1)

    # FINAL VIEW
    os.system("cls")
    console.print(Align.center(Panel(
        Text.from_markup(f"[bold green]RAPPORT DE SCAN TERMINÉ POUR {email}"),
        border_style="green", box=box.HEAVY, padding=(1, 5)
    )))
    
    if found_list:
        table = Table(title="[bold white]COMPTES IDENTIFIÉS", box=box.ROUNDED, border_style="green", expand=True)
        table.add_column("Service", style="white")
        table.add_column("Lien / Statut", style="green", justify="center")
        for f in sorted(found_list):
            table.add_row(f.capitalize(), "[ ✓ ] REGISTERED")
        console.print(table)
    else:
        console.print("\n [bold red][!][/] Aucun compte public identifié.")

    console.input(f"\n [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit()

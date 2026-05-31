import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, asyncio, aiohttp, json

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
C_RED     = "#8B0000"
C_NEON    = "#FF2020"
C_WHITE   = "#FFFFFF"
C_SILVER  = "#CCCCCC"
C_DIM     = "#444444"
C_OK      = "#00FF00"
C_NO      = "#FF4444"

ASCII = r"""
   ██████╗ ██████╗ ███████╗ █████╗  ██████╗██╗  ██╗    ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗ 
   ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║    ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗
   ██████╔╝██████╔╝█████╗  ███████║██║     ███████║    █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝
   ██╔══██╗██╔══██╗██╔══╝  ██╔══██║██║     ██╔══██║    ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
   ██████╔╝██║  ██║███████╗██║  ██║╚██████╗██║  ██║    ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║
   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝
"""

SUBTITLE = " P R E M I U M   L E A K   D A T A B A S E   S E A R C H E R   V 2 "

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID BREACH-FINDER // LEAK INTEL")
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

async def get_leaks(target):
    # Switching to LeakCheck Public API (STABLE & NO KEY REQUIRED)
    try:
        async with aiohttp.ClientSession() as session:
            # We add a fake User-Agent to avoid early blocks
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Void-Tools-Prime"}
            async with session.get(f"https://leakcheck.io/api/v2/public/{target}", headers=headers) as r:
                if r.status == 200:
                    data = await r.json()
                    if data.get("success"):
                        # Normalize format to be consistent
                        return [{"Name": b, "BreachDate": "N/A", "DataClasses": ["Check Deep for more..."]} for b in data.get("sources", [])]
                    return []
                elif r.status == 404: return []
                else: return None
    except: return None

def main():
    boot()
    
    console.print(Align.center(Panel(
        Text.from_markup(f"[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]BREACH DATABASE[/]  [dim]//[/]  [red]LEAK FINDER[/]"),
        border_style="red", padding=(0, 6)
    )))
    console.print()
    
    target = console.input(" [bold red]└─▶[/] [bold white]E-mail ou Pseudo >> ").strip()
    if not target: return

    # Dashboard Layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3)
    )
    
    leaks = []
    scanning = True
    
    async def fetch():
        nonlocal leaks, scanning
        leaks = await get_leaks(target)
        scanning = False

    loop = asyncio.new_event_loop()
    import threading
    t = threading.Thread(target=loop.run_until_complete, args=(fetch(),), daemon=True)
    t.start()
    
    with Live(layout, screen=True, refresh_per_second=10):
        start_t = time.time()
        while scanning:
            layout["header"].update(Panel(Align.center(Text.from_markup(f"[bold red]VOID-DATABASE ENGINE[/] [dim]||[/] [white]INTERROGATION DES ARCHIVES...[/]")), border_style="red"))
            
            pnl_body = Table.grid(expand=True)
            pnl_body.add_row(Align.center(Group(
                Text.from_markup(f"\n[bold white]CIBLE : [red]{target}"),
                Text.from_markup(f"[dim]Connexion aux serveurs de Leaks sécurisée...[/]\n"),
                Progress(SpinnerColumn(spinner_name="earth", style="red"), TextColumn("[bold red]SCANNING GLOBAL SOURCES..."), console=console)
            )))
            layout["body"].update(Panel(pnl_body, border_style="red", title="[bold white]OSINT PROCESSING"))
            
            layout["footer"].update(Panel(Align.center(Text.from_markup(f"[dim]TEMPS ÉCOULÉ: {int(time.time()-start_t)}s - VOID PRIME DATABASE[/]")), border_style="red"))
            time.sleep(0.1)

    # FINAL REPORT (Inside Terminal)
    os.system("cls")
    console.print(Align.center(Panel(
        Text.from_markup(f"[bold green]RAPPORT DE FUITE TERMINÉ POUR [white]{target}"),
        border_style="green", box=box.HEAVY, padding=(1, 5)
    )))
    
    if leaks is None:
        console.print(Align.center(Panel("[bold red]ERREUR DE CONNEXION: ACCÈS REFUSÉ PAR LE SERVEUR D'ARCHYVES", border_style="red")))
    elif not leaks:
        console.print(Align.center(Panel(f"[bold white]AUCUNE FUITE DÉTÉCTÉE POUR [green]{target}[/]\n[dim]Cette cible semble avoir une bonne hygiène numérique.", border_style="green")))
    else:
        table = Table(title=f"BASE DE DONNÉES DES COMPTES COMPROMIS ({len(leaks)})", box=box.ROUNDED, border_style="red", expand=True)
        table.add_column("PLATEFORME", style="bold red", ratio=1)
        table.add_column("DATE", style="white", ratio=1)
        table.add_column("DONNÉES COMPROMISES", style="silver", ratio=2)
        
        for leak in leaks:
            name = leak.get("Name", leak.get("Title", "Unknown"))
            date = leak.get("BreachDate", "Unknown")
            data = ", ".join(leak.get("DataClasses", ["Mots de passe", "E-mails"]))
            table.add_row(name.upper(), date, f"[bold]{data}[/]")
            
        console.print(table)
        console.print(f"\n [bold red][!][/] ALERTE: {len(leaks)} instances de compromission trouvées.")

    console.input(f"\n [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit()

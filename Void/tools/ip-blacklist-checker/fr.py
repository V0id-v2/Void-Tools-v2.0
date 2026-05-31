import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, socket, threading, concurrent.futures
import requests
from urllib.parse import urlparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
import urllib3
urllib3.disable_warnings()

console = Console()
TIMEOUT = 5

ASCII = r"""
  ██╗   ██╗ ██████╗ ██╗██████╗       ██╗██████╗ 
  ██║   ██║██╔═══██╗██║██╔══██╗      ██║██╔══██╗
  ██║   ██║██║   ██║██║██║  ██║█████╗██║██████╔╝
  ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║██╔═══╝ 
   ╚████╔╝ ╚██████╔╝██║██████╔╝      ██║██║     
    ╚═══╝   ╚═════╝ ╚═╝╚═════╝       ╚═╝╚═╝     
"""
SUBTITLE = " I P   B L A C K L I S T   &   R E P U T A T I O N "

def boot():
    if sys.platform.startswith("win"): os.system("title VOID IP // BLACKLIST CHECKER")
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
                    if ch == " ": sys.stdout.write(" ")
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


DNSBLs = ["zen.spamhaus.org", "b.barracudacentral.org", "dnsbl.sorbs.net", "spam.dnsbl.sorbs.net", "bl.spamcop.net"]

def check_bl(ip, bl):
    rev_ip = ".".join(reversed(ip.split(".")))
    query = f"{rev_ip}.{bl}"
    try:
        if socket.gethostbyname(query):
            return bl, True
    except: pass
    return bl, False

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]VOID IP[/]  [dim]//[/]  [red]BLACKLIST CHECKER[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()
        console.print(" [bold red]┌─[[/][bold white] Adresse IP Cible [/][bold red]][/]")
        target = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not target: sys.exit(0)
        
        console.print()
        results = []
        with Progress(SpinnerColumn(spinner_name="point", style="red"), TextColumn("[dim white]{task.description}"), console=console, transient=True) as p:
            p.add_task("Vérification sur les bases de données mondiales...", total=None)
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
                futs = [ex.submit(check_bl, target, bl) for bl in DNSBLs]
                for f in concurrent.futures.as_completed(futs):
                    results.append(f.result())
        
        tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False, expand=True)
        tbl.add_column("DB", style="white")
        tbl.add_column("STATUS", justify="right")
        for bl, is_listed in results:
            stat = "[bold red]SIGNALÉ[/]" if is_listed else "[dim green]CLEAN[/]"
            tbl.add_row(bl, stat)
            
        console.print(Align.center(Panel(tbl, title="[bold red]* DNSBL RÉSULTATS *", border_style="red")))
        console.print()
        console.input(" [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")
    except (KeyboardInterrupt, EOFError): pass


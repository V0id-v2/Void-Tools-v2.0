import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, re, requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()
IP_REGEX = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

ASCII = r"""
  ██╗██████╗      ██╗      ██████╗  ██████╗ ██╗  ██╗██╗   ██╗██████╗ 
  ██║██╔══██╗     ██║     ██╔═══██╗██╔═══██╗██║ ██╔╝██║   ██║██╔══██╗
  ██║██████╔╝     ██║     ██║   ██║██║   ██║█████═╝ ██║   ██║██████╔╝
  ██║██╔═══╝      ██║     ██║   ██║██║   ██║██╔═██╗ ██║   ██║██╔═══╝ 
  ██║██║          ███████╗╚██████╔╝╚██████╔╝██║  ██╗╚██████╔╝██║     
  ╚═╝╚═╝          ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     
"""
SUBTITLE = "D E E P   I P   I N T E L L I G E N C E   L O O K U P"

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // IP LOOKUP")
    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.write("\033[?25l")
    lines = ASCII.strip("\n").split("\n")
    t0 = time.time()
    try:
        while time.time() - t0 < 1.4:
            t = time.time() - t0
            sys.stdout.write("\033[H\n")
            for line in lines:
                sys.stdout.write(" ")
                for c, ch in enumerate(line):
                    if ch == " ":
                        sys.stdout.write(" ")
                    else:
                        v = max(40, min(255, int(100 + 155 * math.sin(t * 10 - c * 0.15))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;80;0;0m{SUBTITLE}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

def lookup_ip(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=8)
        return r.json()
    except: return {}

def afficher(ip, data):
    tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False, padding=(0, 2))
    tbl.add_column("K", style="dim red", width=18); tbl.add_column("V", style="white")

    tbl.add_row("ADRESSE IP", f"[bold white]{ip}[/]")
    tbl.add_row("PAYS", data.get("country", "—"))
    tbl.add_row("RÉGION", data.get("regionName", "—"))
    tbl.add_row("VILLE", data.get("city", "—"))
    tbl.add_row("CODE POSTAL", data.get("zip", "—"))
    tbl.add_row("COORDONNÉES", f"{data.get('lat','—')} / {data.get('lon','—')}")
    tbl.add_row("FUSEAU", data.get("timezone", "—"))
    tbl.add_row("FAI", f"[cyan]{data.get('isp','—')}[/]")
    tbl.add_row("ORGANISATION", data.get("org", "—"))
    tbl.add_row("ASN", data.get("as", "—"))
    tbl.add_row("PROXY / VPN", "[red]OUI[/]" if data.get("proxy") else "Non")
    tbl.add_row("HÉBERGEMENT", "Oui" if data.get("hosting") else "Non")

    console.print(Align.center(Panel(tbl, title=f"[bold red] INTEL [/] [dim]─[/] [white]{ip}[/]", border_style="red")))
    console.print()

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]IP LOOKUP[/]  [dim]//[/]  [red]OSINT[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Adresse IP [/][bold red]][/]")
        ip = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not ip: sys.exit(0)

        if not IP_REGEX.match(ip):
            console.print(f"\n [bold red][!] Format IP invalide:[/] {ip}")
            time.sleep(2); sys.exit(0)

        with Progress(SpinnerColumn(style="red"), TextColumn("[dim]{task.description}"), console=console, transient=True) as p:
            p.add_task("Interrogation de la base de données...", total=None)
            data = lookup_ip(ip)

        os.system("cls" if os.name == "nt" else "clear")
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]IP LOOKUP[/]  [dim]//[/]  [red]RAPPORT[/]"),
            border_style="red", padding=(0, 6)
        )))
        afficher(ip, data)
        console.input(" [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")

    except (KeyboardInterrupt, EOFError):
        pass

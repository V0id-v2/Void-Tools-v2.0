import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, re, time, math
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()
TIMEOUT = 8

IP_REGEX = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

ASCII = r"""
  ██╗   ██╗ ██████╗ ██╗██████╗       ██╗██████╗ 
  ██║   ██║██╔═══██╗██║██╔══██╗      ██║██╔══██╗
  ██║   ██║██║   ██║██║██║  ██║█████╗██║██████╔╝
  ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║██╔═══╝ 
   ╚████╔╝ ╚██████╔╝██║██████╔╝      ██║██║     
    ╚═══╝   ╚═════╝ ╚═╝╚═════╝       ╚═╝╚═╝     
"""

SUBTITLE = " D É T E C T E U R   D E   V P N   &   P R O X I E S "

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // IP VPN DETECTOR")
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


def detect_vpn(ip):
    url = f"https://proxycheck.io/v2/{ip}?vpn=1&asn=1"
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def afficher(data, ip):
    if data.get("status") != "ok":
        console.print(Panel(f"[red]  Erreur API : {data.get('message', 'Inconnue')}[/]", border_style="red"))
        return

    res = data.get(ip, {})
    is_proxy = res.get("proxy", "no") == "yes"

    tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False,
                padding=(0, 2), expand=False)
    tbl.add_column("KEY", style="dim red", width=18, no_wrap=True)
    tbl.add_column("VAL", style="white")

    proxy_tag = "[bold red]  OUI  ─ VPN/PROXY DÉTECTÉ[/]" if is_proxy else "[dim green]Non[/]"

    tbl.add_row("IP RÉSOLUE",     f"[bold bright_white]{ip}[/]")
    tbl.add_row("PROXY / VPN",    proxy_tag)
    tbl.add_row("TYPE",           res.get("type", "N/A"))
    tbl.add_row("FOURNISSEUR",    f"[cyan]{res.get('provider', 'N/A')}[/]")
    tbl.add_row("ASN",            res.get("asn", "N/A"))
    tbl.add_row("PAYS",           f"[bold white]{res.get('country','N/A')}[/] [dim]({res.get('isocode','??')})[/]")

    console.print()
    console.print(Align.center(Panel(
        tbl,
        title=f"[bold red]  RÉSULTATS DE DÉTECTION[/]  [dim white]─[/]  [white]{ip}[/]",
        border_style="red",
        padding=(1, 3),
    )))
    console.print()


if __name__ == "__main__":
    try:
        boot()

        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]VOID IP[/]  [dim]//[/]  [red]VPN DETECTOR[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Adresse IP Cible [/][bold red]][/]")
        ip = console.input(" [bold red]└─▶[/] [bold white]").strip()

        if not ip:
            console.print("\n[red] [!] Aucune adresse saisie.[/]")
            sys.exit(0)

        if not IP_REGEX.match(ip):
            console.print(f"\n[red] [!] Format IPv4 invalide :[/] [white]{ip}[/]")
            sys.exit(0)

        console.print()
        with Progress(
            SpinnerColumn(spinner_name="point", style="red"),
            TextColumn("[dim white]{task.description}"),
            console=console, transient=True,
        ) as p:
            p.add_task("Vérification Proxy / VPN en cours...", total=None)
            data = detect_vpn(ip)

        afficher(data, ip)
        console.input(" [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")

    except requests.RequestException as e:
        console.print(f"\n[red] [!] Erreur réseau :[/] {e}")
    except (KeyboardInterrupt, EOFError):
        console.print("\n[red] [!] Interrompu.[/]")

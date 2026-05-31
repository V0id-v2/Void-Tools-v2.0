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
SUBTITLE = "I S P   &   O R G A N I Z A T I O N   I N T E L L I G E N C E"

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // IP OPERATOR")
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


def get_operator(ip):
    r = requests.get(
        f"http://ip-api.com/json/{ip}?fields=status,message,isp,org,as,asname,query,country,countryCode,regionName,city",
        timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.json()


def display(ip, data):
    if data.get("status") == "fail":
        console.print(Panel(f"[red]  API Error: {data.get('message')}[/]", border_style="red"))
        return

    tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False,
                padding=(0, 2), expand=False)
    tbl.add_column("K", style="dim red", width=18, no_wrap=True)
    tbl.add_column("V", style="white")

    tbl.add_row("IP",           f"[bold bright_white]{data.get('query', ip)}[/]")
    tbl.add_row("COUNTRY",      f"{data.get('country','N/A')} [dim]({data.get('countryCode','?')})[/]")
    tbl.add_row("REGION",       data.get("regionName", "N/A"))
    tbl.add_row("CITY",         data.get("city", "N/A"))
    tbl.add_row("ISP",          f"[cyan]{data.get('isp', 'N/A')}[/]")
    tbl.add_row("ORGANIZATION", f"[cyan]{data.get('org', 'N/A')}[/]")
    tbl.add_row("ASN",          f"[dim]{data.get('as', 'N/A')}[/]")
    tbl.add_row("AS NAME",      f"[dim]{data.get('asname', 'N/A')}[/]")

    console.print()
    console.print(Align.center(Panel(
        tbl,
        title=f"[bold red]  NETWORK OPERATOR[/]  [dim]─[/]  [white]{data.get('query', ip)}[/]",
        border_style="red",
        padding=(1, 4),
    )))
    console.print()


if __name__ == "__main__":
    try:
        boot()

        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]IP OPERATOR[/]  [dim]//[/]  [red]ISP INTELLIGENCE[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Target IP Address [/][bold red]][/]")
        ip = console.input(" [bold red]└─▶[/] [bold white]").strip()

        if not ip:
            console.print("\n[red] [!] No address entered.[/]")
            sys.exit(0)
        if not IP_REGEX.match(ip):
            console.print(f"\n[red] [!] Invalid IPv4 format:[/] [white]{ip}[/]")
            sys.exit(0)

        console.print()
        with Progress(
            SpinnerColumn(spinner_name="point", style="red"),
            TextColumn("[dim white]{task.description}"),
            console=console, transient=True,
        ) as p:
            p.add_task("Fetching operator intelligence...", total=None)
            data = get_operator(ip)

        display(ip, data)
        console.input(" [dim]Press [bold red]ENTER[/] to quit...[/]")

    except requests.RequestException as e:
        console.print(f"\n[red] [!] Network error:[/] {e}")
    except (KeyboardInterrupt, EOFError):
        console.print("\n[red] [!] Interrupted.[/]")

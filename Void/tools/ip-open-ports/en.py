import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, re, time, math, socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich import box

console = Console()
IP_REGEX = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

PORTS = {
    21:"FTP", 22:"SSH", 23:"Telnet", 25:"SMTP", 53:"DNS",
    80:"HTTP", 110:"POP3", 135:"RPC", 139:"NetBIOS", 143:"IMAP",
    161:"SNMP", 389:"LDAP", 443:"HTTPS", 445:"SMB", 465:"SMTPS",
    587:"SMTP-Alt", 993:"IMAPS", 995:"POP3S", 1080:"SOCKS",
    1433:"MSSQL", 1521:"Oracle", 2082:"cPanel", 2083:"cPanel-SSL",
    3306:"MySQL", 3389:"RDP", 5432:"PostgreSQL", 5900:"VNC",
    6379:"Redis", 8080:"HTTP-Alt", 8443:"HTTPS-Alt", 8888:"Alt",
    9200:"Elasticsearch", 27017:"MongoDB",
}

ASCII = r"""
  ██╗   ██╗ ██████╗ ██╗██████╗       ██╗██████╗ 
  ██║   ██║██╔═══██╗██║██╔══██╗      ██║██╔══██╗
  ██║   ██║██║   ██║██║██║  ██║█████╗██║██████╔╝
  ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║██╔═══╝ 
   ╚████╔╝ ╚██████╔╝██║██████╔╝      ██║██║     
    ╚═══╝   ╚═════╝ ╚═╝╚═════╝       ╚═╝╚═╝     
"""
SUBTITLE = "T C P   C O N N E C T   V U L N E R A B I L I T Y   S C A N N E R"

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // OPEN PORTS SCANNER")
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
                        v = max(40, min(255, int(80 + 175 * abs(math.sin(t * 8 - c * 0.12)))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;80;0;0m{SUBTITLE}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")


def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.8)
            return port, s.connect_ex((ip, port)) == 0
    except Exception:
        return port, False


def display(ip, results):
    open_ports   = [(p, PORTS.get(p, "?")) for p, o in sorted(results.items()) if o]
    closed_ports = [(p, PORTS.get(p, "?")) for p, o in sorted(results.items()) if not o]

    tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red",
                header_style="dim red", show_lines=False, expand=False, padding=(0, 2))
    tbl.add_column("PORT", style="white", width=7, justify="right")
    tbl.add_column("SERVICE", style="dim white", width=14)
    tbl.add_column("STATUS", width=12, justify="center")

    for p, svc in open_ports:
        tbl.add_row(str(p), svc, "[bold bright_green]●  OPEN[/]")
    for p, svc in closed_ports:
        tbl.add_row(f"[dim]{p}[/]", f"[dim]{svc}[/]", "[dim red]○  CLOSED[/]")

    console.print()
    console.print(Align.center(Panel(
        tbl,
        title=f"[bold red]  PORT SCAN[/]  [dim]─[/]  [white]{ip}[/]  [dim]─[/]  [red]{len(open_ports)} OPEN[/] [dim]/ {len(closed_ports)} CLOSED[/]",
        border_style="red", padding=(1, 2)
    )))
    console.print()

    if open_ports:
        svc_list = "  ".join(f"[red]{p}[/][dim]/{svc}[/]" for p, svc in open_ports)
        console.print(Align.center(f"[dim]Exposed services:[/]  {svc_list}"))
        console.print()


if __name__ == "__main__":
    try:
        boot()

        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]OPEN PORTS[/]  [dim]//[/]  [red]TCP VULNERABILITY SCAN[/]"),
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
        results = {}
        with Progress(
            SpinnerColumn(spinner_name="point", style="red"),
            TextColumn("[dim white]Running TCP scan...[/]"),
            BarColumn(bar_width=35, style="dark_red", complete_style="red"),
            TextColumn("[red]{task.completed}[dim]/{task.total}[/]"),
            TimeElapsedColumn(),
            console=console, transient=True,
        ) as prog:
            task = prog.add_task("Scan", total=len(PORTS))
            with ThreadPoolExecutor(max_workers=60) as ex:
                futs = {ex.submit(scan_port, ip, p): p for p in PORTS}
                for fut in as_completed(futs):
                    port, open_ = fut.result()
                    results[port] = open_
                    prog.advance(task)

        display(ip, results)
        console.input(" [dim]Press [bold red]ENTER[/] to quit...[/]")

    except (KeyboardInterrupt, EOFError):
        console.print("\n[red] [!] Scan interrupted.[/]")

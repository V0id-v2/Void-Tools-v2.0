import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, re, time, math, socket, subprocess, platform
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()
IP_REGEX = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
PING_COUNT = 8

ASCII = r"""
  ██╗   ██╗ ██████╗ ██╗██████╗       ██╗██████╗ 
  ██║   ██║██╔═══██╗██║██╔══██╗      ██║██╔══██╗
  ██║   ██║██║   ██║██║██║  ██║█████╗██║██████╔╝
  ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║██╔═══╝ 
   ╚████╔╝ ╚██████╔╝██║██████╔╝      ██║██║     
    ╚═══╝   ╚═════╝ ╚═╝╚═════╝       ╚═╝╚═╝     
"""
SUBTITLE = "I C M P   L A T E N C Y   &   R E A C H A B I L I T Y   T E S T"

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // IP PINGER")
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


def ping_once(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        t0 = time.time()
        result = subprocess.run(
            ["ping", param, "1", "-w", "1000", host] if platform.system().lower() == "windows"
            else ["ping", param, "1", "-W", "1", host],
            capture_output=True, timeout=3
        )
        elapsed = (time.time() - t0) * 1000
        if result.returncode == 0:
            return round(elapsed, 2)
        return None
    except Exception:
        return None


def tcp_check(host, port=80):
    try:
        t0 = time.time()
        with socket.create_connection((host, port), timeout=3):
            return round((time.time() - t0) * 1000, 2)
    except Exception:
        return None


def display(host, ip, latencies, tcp_ms):
    valid = [l for l in latencies if l is not None]
    lost  = len(latencies) - len(valid)

    if valid:
        avg_ms   = round(sum(valid) / len(valid), 2)
        min_ms   = round(min(valid), 2)
        max_ms   = round(max(valid), 2)
        jitter   = round(max_ms - min_ms, 2)
        loss_pct = round((lost / len(latencies)) * 100)
    else:
        avg_ms = min_ms = max_ms = jitter = 0
        loss_pct = 100

    def latency_color(ms):
        if ms is None: return "dim red"
        if ms < 50:  return "bright_green"
        if ms < 120: return "yellow"
        if ms < 250: return "orange3"
        return "red"

    def loss_color(pct):
        if pct == 0: return "bright_green"
        if pct < 30: return "yellow"
        return "red"

    bar = ""
    for l in latencies:
        if l is None:
            bar += "[red]✗[/]"
        elif l < 50:
            bar += "[bright_green]▇[/]"
        elif l < 120:
            bar += "[yellow]▄[/]"
        else:
            bar += "[red]▁[/]"
        bar += " "

    tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False,
                padding=(0, 2), expand=False)
    tbl.add_column("K", style="dim red", width=20, no_wrap=True)
    tbl.add_column("V", style="white")

    tbl.add_row("TARGET",        f"[bold bright_white]{host}[/]")
    tbl.add_row("RESOLVED IP",   f"[bold white]{ip}[/]" if ip else "[dim red]Resolution failed[/]")
    tbl.add_row("PACKETS",       f"{len(latencies)} sent")
    tbl.add_row("PACKET LOSS",   f"[{loss_color(loss_pct)}]{lost} lost ({loss_pct}%)[/]")
    tbl.add_row("MIN LATENCY",   f"[bright_green]{min_ms} ms[/]" if valid else "[dim]—[/]")
    tbl.add_row("AVG LATENCY",   f"[{latency_color(avg_ms)}]{avg_ms} ms[/]" if valid else "[dim]—[/]")
    tbl.add_row("MAX LATENCY",   f"[{latency_color(max_ms)}]{max_ms} ms[/]" if valid else "[dim]—[/]")
    tbl.add_row("JITTER",        f"[{latency_color(jitter)}]{jitter} ms[/]" if valid else "[dim]—[/]")
    if tcp_ms:
        tbl.add_row("TCP :80",   f"[cyan]{tcp_ms} ms[/]")
    tbl.add_row("ACTIVITY",      bar)

    console.print()
    reachable = "[bold bright_green]  REACHABLE[/]" if valid else "[bold red]  UNREACHABLE[/]"
    console.print(Align.center(Panel(
        tbl,
        title=f"[bold red]  PING REPORT[/]  [dim]─[/]  [white]{host}[/]  [dim]─[/]  {reachable}",
        border_style="red" if valid else "dim red",
        padding=(1, 3),
    )))
    console.print()


if __name__ == "__main__":
    try:
        boot()

        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]IP PINGER[/]  [dim]//[/]  [red]LATENCY ANALYSIS[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Target IP or Hostname [/][bold red]][/]")
        host = console.input(" [bold red]└─▶[/] [bold white]").strip()

        if not host:
            console.print("\n[red] [!] No target entered.[/]")
            sys.exit(0)

        console.print()
        ip = None
        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            pass

        latencies = []
        with Progress(
            SpinnerColumn(spinner_name="point", style="red"),
            TextColumn("[dim white]Sending ICMP packets...[/]"),
            console=console, transient=True,
        ) as p:
            p.add_task("ping", total=None)
            with ThreadPoolExecutor(max_workers=PING_COUNT) as ex:
                futs = [ex.submit(ping_once, host) for _ in range(PING_COUNT)]
                latencies = [f.result() for f in futs]

        tcp_ms = tcp_check(host)
        display(host, ip, latencies, tcp_ms)
        console.input(" [dim]Press [bold red]ENTER[/] to quit...[/]")

    except (KeyboardInterrupt, EOFError):
        console.print("\n[red] [!] Ping test interrupted.[/]")

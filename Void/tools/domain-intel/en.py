import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, socket, ssl, json, asyncio, aiohttp

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

C_RED     = "#CC0000"
C_NEON    = "#FF2020"
C_WHITE   = "#FFFFFF"
C_GOLD    = "#FFD700"
C_DIM     = "#444444"

ASCII = r"""
   ██████╗  ██████╗ ███╗   ███╗ █████╗ ██╗███╗   ██╗    ██╗███╗   ██╗████████╗███████╗██╗     
   ██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██║████╗  ██║    ██║████╗  ██║╚══██╔══╝██╔════╝██║     
   ██║  ██║██║   ██║██╔████╔██║███████║██║██╔██╗ ██║    ██║██╔██╗ ██║   ██║   █████╗  ██║     
   ██║  ██║██║   ██║██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ██║██║╚██╗██║   ██║   ██╔══╝  ██║     
   ██████╔╝╚██████╔╝██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ██║██║ ╚████║   ██║   ███████╗███████╗
   ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝
"""

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID DOMAIN INTEL // OSINT CORE")
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

def get_dns_info(domain):
    data = {}
    try:
        data["IP Access (A)"] = socket.gethostbyname(domain)
    except: data["IP Access (A)"] = "Not Found"
    return data

async def get_headers(domain):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{domain}", timeout=5) as r:
                return dict(r.headers)
    except: return None

def main():
    boot()
    console.print(Align.center(Panel(Text.from_markup(f"[bold red]VOID-TOOLS[/] [dim]||[/] [white]DOMAIN INTELLIGENCE V2[/]"), border_style="red", padding=(0, 5))))
    console.print()
    
    domain = console.input(" [bold red]└─▶[/] [white]Domain (ex: domain.com) >> ").strip().lower().replace("https://","").replace("http://","").split("/")[0]
    if not domain: return

    os.system("cls")
    with Progress(SpinnerColumn(style="red"), TextColumn("[bold red]INTERROGATING DNS SERVERS..."), console=console, transient=True) as p:
        p.add_task("", total=None)
        dns = get_dns_info(domain)
        time.sleep(0.8)
        p.columns[1].text = "[bold red]CAPTURING HTTP HEADERS..."
        headers = asyncio.run(get_headers(domain))
        time.sleep(0.8)

    layout = Layout()
    layout.split_column(Layout(name="header", size=4), Layout(name="body", ratio=1))
    layout["body"].split_row(Layout(name="left"), Layout(name="right"))

    layout["header"].update(Panel(Align.center(Text.from_markup(f"[bold red]INTELLIGENCE REPORT : [white]{domain}")), border_style="red"))
    
    dns_table = Table(title="[bold white]DNS & NETWORK RECORDS", box=box.SIMPLE, expand=True)
    dns_table.add_column("DNS TAG", style="red")
    dns_table.add_column("INTEL VALUE", style="white")
    for k, v in dns.items(): dns_table.add_row(k, v)
    layout["left"].update(Panel(dns_table, border_style="red"))

    head_table = Table(title="[bold white]CORE HTTP HEADERS", box=box.SIMPLE, expand=True)
    head_table.add_column("RESPONSE TAG", style="red")
    head_table.add_column("VALUE DETECTED", style="white", overflow="fold")
    if headers:
        for k in ["Server", "Content-Type", "Strict-Transport-Security", "X-Frame-Options", "X-Powered-By"]:
            if k in headers: head_table.add_row(k, headers[k])
    else:
        head_table.add_row("Status", "Remote Host Unreachable")
    
    layout["right"].update(Panel(head_table, border_style="red"))

    console.print(layout)
    console.print(f"\n [bold red][!][/] Intelligence collection finished. Check OSINT Framework for deep WHOIS.")
    console.input(f"\n [dim]Press [bold red]ENTER[/] to exit...[/]")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit()

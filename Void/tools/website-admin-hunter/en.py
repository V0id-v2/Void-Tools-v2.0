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
   ██╗   ██╗ ██████╗ ██╗██████╗      ██╗    ██╗███████╗██████╗ 
   ██║   ██║██╔═══██╗██║██╔══██╗     ██║    ██║██╔════╝██╔══██╗
   ██║   ██║██║   ██║██║██║  ██║█████╗██║ █╗ ██║█████╗  ██████╔╝
   ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║███╗██║██╔══╝  ██╔══██╗
    ╚████╔╝ ╚██████╔╝██║██████╔╝      ╚███╔███╔╝███████╗██████╔╝
     ╚═══╝   ╚═════╝ ╚═╝╚═════╝        ╚══╝╚══╝ ╚══════╝╚═════╝ 
"""
SUBTITLE = " A D M I N   P A N E L   &   L O G I N   H U N T E R "

def boot():
    if sys.platform.startswith("win"): os.system("title VOID WEB // ADMIN HUNTER")
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


PANELS = ["admin", "administrator", "wp-admin", "wp-login.php", "cpanel", "login", "admin/login", "dashboard", "manage", "manager", "admin.php", "admin.html", "user", "users", "panel", "webadmin"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"

def check_admin(base, p):
    url = f"{base}/{p}"
    try:
        r = requests.get(url, headers={"User-Agent": UA}, verify=False, timeout=4)
        if r.status_code in [200, 301, 302, 401, 403]:
            return url, r.status_code
    except: pass
    return None

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]VOID WEB[/]  [dim]//[/]  [red]ADMIN HUNTER[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()
        console.print(" [bold red]┌─[[/][bold white] Target URL (ex: https://site.com) [/][bold red]][/]")
        target = console.input(" [bold red]└─▶[/] [bold white]").strip().rstrip("/")
        if not target: sys.exit(0)
        if not target.startswith("http"): target = "https://" + target
        
        console.print()
        found = []
        with Progress(SpinnerColumn(spinner_name="point", style="red"), TextColumn("[dim white]{task.description}"), console=console, transient=True) as p:
            p.add_task(f"Hunting on {target}...", total=None)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
                futs = [ex.submit(check_admin, target, d) for d in PANELS]
                for f in concurrent.futures.as_completed(futs):
                    res = f.result()
                    if res:
                        found.append(res)
                        col = "green" if res[1] == 200 else "yellow"
                        console.print(f" [bold {col}][{res[1]}][/] [white]{res[0]}[/]")
        
        console.print()
        console.print(f" [bold green][✓] Done. Found {len(found)} panels.[/]")
        console.input(" [dim]Press [bold red]ENTER[/] to exit...[/]")
    except (KeyboardInterrupt, EOFError): pass


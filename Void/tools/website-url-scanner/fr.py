import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, re, concurrent.futures, threading
from urllib.parse import urlparse, urljoin
import requests, urllib3
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich import box

console = Console()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ASCII = r"""
   ██╗   ██╗ ██████╗ ██╗██████╗      ██╗    ██╗███████╗██████╗ 
   ██║   ██║██╔═══██╗██║██╔══██╗     ██║    ██║██╔════╝██╔══██╗
   ██║   ██║██║   ██║██║██║  ██║█████╗██║ █╗ ██║█████╗  ██████╔╝
   ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║███╗██║██╔══╝  ██╔══██╗
    ╚████╔╝ ╚██████╔╝██║██████╔╝      ╚███╔███╔╝███████╗██████╔╝
     ╚═══╝   ╚═════╝ ╚═╝╚═════╝        ╚══╝╚══╝ ╚══════╝╚═════╝ 
"""
SUBTITLE = " D É C O U V E R T E   R É C U R S I V E   D ' L I E N S   W E B "

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID WEB // SCANNER D'URLS")
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
                        v = max(40, min(255, int(100 + 155 * math.sin(t * 10 - c * 0.08))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;80;0;0m{SUBTITLE}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
HEADERS = {"User-Agent": UA}
discovered = set()
visited = set()
lock = threading.Lock()

def crawl(url, domain):
    with lock:
        if url in visited: return
        visited.add(url)
    try:
        r = requests.get(url, headers=HEADERS, timeout=5, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        links = set()
        for a in soup.find_all("a", href=True):
            full = urljoin(url, a["href"]).split("#")[0].rstrip("/")
            if domain in full and full not in discovered:
                links.add(full)
                with lock:
                    discovered.add(full)
                    console.print(f" [bold red][[/][white]{len(discovered)}[/][bold red]][/] [white]{full}[/]")
        return links
    except: return set()

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]VOID WEB[/]  [dim]//[/]  [red]SCANNER D'URLS[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] URL ou Domaine Cible [/][bold red]][/]")
        target = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not target: sys.exit(0)
        if not target.startswith("http"): target = "https://" + target
        domain = urlparse(target).netloc
        discovered.add(target)

        console.print(f"\n [dim]Lancement de la découverte récursive sur [red]{target}[/]...\n")

        queue = {target}
        for _ in range(2): # Shallow crawl for demo
            next_q = set()
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
                futs = [pool.submit(crawl, u, domain) for u in queue]
                for f in concurrent.futures.as_completed(futs):
                    next_q.update(f.result())
            queue = next_q - visited
            if not queue: break

        console.print(Rule(style="dim red"))
        console.print(f" [bold green][✓] Découverte terminée. {len(discovered)} endpoints trouvés.")
        console.input("\n [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")
    except (KeyboardInterrupt, EOFError): pass

import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math
import requests
from urllib.parse import urlparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
TIMEOUT = 10

ASCII = r"""
   ██╗   ██╗ ██████╗ ██╗██████╗      ██╗    ██╗███████╗██████╗ 
   ██║   ██║██╔═══██╗██║██╔══██╗     ██║    ██║██╔════╝██╔══██╗
   ██║   ██║██║   ██║██║██║  ██║█████╗██║ █╗ ██║█████╗  ██████╔╝
   ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║███╗██║██╔══╝  ██╔══██╗
    ╚████╔╝ ╚██████╔╝██║██████╔╝      ╚███╔███╔╝███████╗██████╔╝
     ╚═══╝   ╚═════╝ ╚═╝╚═════╝        ╚══╝╚══╝ ╚══════╝╚═════╝ 
"""

SUBTITLE = " W E B P A G E   S O U R C E   C L O N E R "

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID WEB // WEB CLONER")
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

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

if __name__ == "__main__":
    try:
        boot()

        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]VOID WEB[/]  [dim]//[/]  [red]WEB CLONER[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Target URL (e.g., https://site.com) [/][bold red]][/]")
        target = console.input(" [bold red]└─▶[/] [bold white]").strip()

        if not target:
            sys.exit(0)
        if not target.startswith("http"):
            target = "https://" + target

        domain = urlparse(target).netloc or "unknown_site"
        domain = domain.replace("www.", "")

        out_dir = os.path.join(os.getcwd(), "Void - Output")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        out_file = os.path.join(out_dir, f"{domain}_clone.html")

        console.print()
        with Progress(
            SpinnerColumn(spinner_name="point", style="red"),
            TextColumn("[dim white]{task.description}"),
            console=console, transient=True,
        ) as p:
            p.add_task("Cloning webpage in progress...", total=None)
            
            try:
                r = requests.get(target, headers={"User-Agent": UA}, timeout=TIMEOUT)
                r.raise_for_status()
                html = r.text
                
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(html)
                success = True
            except Exception as e:
                success = False
                error_msg = str(e)

        if success:
            console.print(f" [bold green][✓][/] Source code successfully cloned.")
            console.print(f" [dim]File saved to :[/] [white]{out_file}[/]")
            
            css_count = html.count("stylesheet")
            js_count = html.count("<script")
            console.print(f"\n [dim]Statistics : {len(html)} characters, {css_count} CSS links, {js_count} script tags.[/]")
        else:
            console.print(f" [bold red][x] Cloning failed :[/] {error_msg}")

        console.print()
        console.input(" [dim]Press [bold red]ENTER[/] to exit...[/]")

    except (KeyboardInterrupt, EOFError):
        pass

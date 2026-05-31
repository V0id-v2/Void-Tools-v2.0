import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()
BASE_DIR = os.path.join(os.getcwd(), 'Void - Input', 'DATA-BASE')

ASCII = r"""
  ███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗    ██████╗ ██████╗ 
  ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║    ██╔══██╗██╔══██╗
  ███████╗█████╗  ███████║██████╔╝██║     ███████║    ██║  ██║██████╔╝
  ╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║    ██║  ██║██╔══██╗
  ███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║    ██████╔╝██████╔╝
  ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═════╝ ╚═════╝ 
"""
SUBTITLE = "L O C A L   B R E A C   D A T A B A S E   Q U E R Y"

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // DATABASE SEARCH")
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
                        v = max(40, min(255, int(100 + 155 * math.sin(t * 10 - c * 0.1))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;80;0;0m{SUBTITLE}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

def perform_search(term):
    res = []
    f_count = 0
    if not os.path.exists(BASE_DIR): return [], 0, "DATA-BASE folder not found."
    
    for root, _, files in os.walk(BASE_DIR):
        for f in files:
            f_count += 1
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    for i, line in enumerate(fh, 1):
                        if term.lower() in line.lower():
                            res.append({"f": f, "l": i, "c": line.strip()})
            except: continue
    return res, f_count, None

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]DATABASE SEARCH[/]  [dim]//[/]  [red]OSINT[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Search term [/][bold red]][/]")
        term = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not term: sys.exit(0)

        with Progress(SpinnerColumn(style="red"), TextColumn("[dim]{task.description}"), console=console, transient=True) as p:
            p.add_task(f"Scanning archives for '{term}'...", total=None)
            results, count, error = perform_search(term)

        if error:
            console.print(f"\n [bold red][!] {error}")
            time.sleep(2); sys.exit(0)

        os.system("cls" if os.name == "nt" else "clear")
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]SEARCH RESULTS[/]  [dim]//[/]  [red]CORE[/]"),
            border_style="red", padding=(0, 4)
        )))

        if not results:
            console.print(Align.center(f"\n [bold red][!] No results found for '{term}' in {count} files.[/]"))
        else:
            tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", header_style="bold red")
            tbl.add_column("FILE", style="dim white")
            tbl.add_column("LINE", justify="right", style="cyan")
            tbl.add_column("CONTENT", style="white")

            for r in results[:100]:
                match_text = r['c'].replace(term, f"[bold yellow]{term}[/]")
                tbl.add_row(r['f'], str(r['l']), match_text)
            
            console.print(Align.center(tbl))
            console.print(Align.center(f"\n [bold bright_green][✓] {len(results)} matches found [/][dim]({count} files analyzed)[/]"))

        console.input("\n [dim]Press [bold red]ENTER[/] to exit...[/]")

    except (KeyboardInterrupt, EOFError):
        pass

import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, threading, zipfile, random
from concurrent.futures import ThreadPoolExecutor

_VOID = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _VOID not in sys.path:
    sys.path.insert(0, _VOID)

from lib import constants as C
from lib.void_common import open_premium_links

try:
    import pyzipper
except ImportError:
    pyzipper = None

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import box

try:
    from tkinter import Tk, filedialog
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False

console = Console()

# -- COLORS --
C_BLOOD   = "#8B0000"
C_RED     = "#CC0000"
C_NEON    = "#FF2020"
C_WHITE   = "#FFFFFF"
C_SILVER  = "#CCCCCC"
C_DIM     = "#444444"
C_GOLD    = "#FFD700"

ASCII = r"""
   ███████╗██╗██████╗      ██████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
   ╚══███╔╝██║██╔══██╗    ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
     ███╔╝ ██║██████╔╝    ██║     ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
    ███╔╝  ██║██╔═══╝     ██║     ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
   ███████╗██║██║         ╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
   ╚══════╝╚═╝╚═╝          ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""

SUBTITLE = " V O I D   Z I P   -   B R U T E F O R C E   S Y S T E M   V 2 "

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID ZIP // BRUTEFORCE ENGINE")
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

def ask_file():
    if TK_AVAILABLE and os.name == 'nt':
        try:
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            f = filedialog.askopenfilename(
                title="VOID-TOOLS - Select ZIP file",
                filetypes=[("ZIP Archives", "*.zip"), ("All files", "*.*")]
            )
            root.destroy()
            return f
        except Exception:
            pass
    console.print("\n [bold red]┌─[[/][bold white] Chemin du fichier cible (.zip) [/][bold red]][/]")
    return console.input(" [bold red]└─▶[/] [bold white]").strip().strip('"')

password_found = None
stop_search = threading.Event()
stats = {"tested": 0, "speed": 0, "start_time": 0, "current_pwd": "..."}

def crack_worker(filepath, ext, passwords_chunk, progress, task):
    global password_found
    if stop_search.is_set(): return
    
    batch = 0
    try:
        _zf_class = pyzipper.AESZipFile if pyzipper else zipfile.ZipFile
        with _zf_class(filepath, 'r') as zf:
            filename = zf.namelist()[0]
            for pwd in passwords_chunk:
                if stop_search.is_set(): break
                try:
                    stats["current_pwd"] = pwd
                    with zf.open(filename, 'r', pwd=pwd.encode('utf-8', errors='ignore')) as f:
                        f.read(16)
                    password_found = pwd
                    stop_search.set()
                    progress.update(task, advance=batch+1, current=pwd[:15])
                    return
                except Exception:
                    batch += 1
                    stats["tested"] += 1
                    if batch >= 50:
                        progress.update(task, advance=batch, current=pwd[:15])
                        batch = 0
                        # Speed calculation
                        elapsed = time.time() - stats["start_time"]
                        if elapsed > 0:
                            stats["speed"] = stats["tested"] / elapsed
    except: pass
    if batch > 0 and not stop_search.is_set():
        progress.update(task, advance=batch, current="...")

def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["body"].split_row(
        Layout(name="main_crack", ratio=3),
        Layout(name="sidebar", ratio=1)
    )
    return layout

def premium_screen():
    os.system("cls")
    with Progress(
        SpinnerColumn(spinner_name="dots2", style="gold1"),
        TextColumn("[bold gold1]VÉRIFICATION DE LA LICENCE..."),
        console=console, transient=True
    ) as p:
        p.add_task("", total=None)
        time.sleep(2)
        
    console.print("\n" * 2)
    pnl = Panel(
        Align.center(Group(
            Text.from_markup(f"\n[bold #FFD700]DÉSOLÉ ! ACCÈS RÉSERVÉ[/]"),
            Text.from_markup(f"\n[white]L'option [bold #FFD700]RAR CRACKER[/] est un module avancé\nnécessitant une licence [bold #FFD700]VOID PREMIUM[/]."),
            Text.from_markup(f"\n[dim]Shop · Discord[/]"),
            Text.from_markup(f"\n[bold #5865F2]{C.SHOP}[/]"),
            Text.from_markup(f"\n[dim #5865F2]{C.DISCORD}[/]"),
            Text.from_markup(f"\n[dim white]Ouverture shop + Discord...[/]")
        )),
        border_style="#FFD700", box=box.DOUBLE_EDGE, padding=(1, 5), title="[bold #FFD700]LICENSE_MISSING_ERROR"
    )
    console.print(Align.center(pnl))
    open_premium_links()
    console.print("\n")
    console.input(Align.center(" [dim]Appuyez sur [bold red]ENTRÉE[/] pour revenir au menu...[/]"))

def main():
    boot()
    
    console.print(Align.center(Panel(
        Text.from_markup(f"[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]BRUTEFORCE ENGINE[/]  [dim]//[/]  [red]ZIP CRACKER[/]"),
        border_style="red", padding=(0, 6)
    )))
    console.print()
    
    filepath = ask_file()
    if not filepath or not os.path.exists(filepath):
        console.print(f"\n [bold red][x][/] Aucun fichier sélectionné.")
        time.sleep(2)
        return
        
    console.print(f"\n [dim]Cible :[/] [bold white]{os.path.basename(filepath)}[/]")
    console.print(Panel(
        Group(
            Text.from_markup(f" [bold red]01  » [/][bold white]Attaque par Dictionnaire (Combolist)"),
            Text.from_markup(f" [bold red]02  » [/][bold white]Bruteforce Aléatoire"),
            Text.from_markup(f" [bold #FFD700]07  » [/][bold #FFD700]RAR Cracker [PREMIUM]")
        ),
        title="[bold red]MODULES D'ATTAQUE", border_style="red", box=box.ROUNDED, padding=(1, 2)
    ))
    
    choice = console.input("\n [bold red]└─▶[/] [bold white]choix >> ").strip()
    
    if choice == "7":
        premium_screen()
        return

    if choice == "1":
        script_dir = os.path.dirname(os.path.abspath(__file__))
        combolist_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", "Void - Input", "Combolist"))
        
        if not os.path.exists(combolist_dir):
            console.print(f"\n [bold red][x][/] Dossier Combolist introuvable.")
            return
            
        passwords = set()
        for f_name in os.listdir(combolist_dir):
            file_path = os.path.join(combolist_dir, f_name)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if line.strip(): passwords.add(line.strip())
                except: pass
        passwords = list(passwords)
            
        if not passwords:
            console.print(f"\n [bold red][x][/] Aucune combolist chargée.")
            return
            
        console.print(f"\n [bold green][✓][/] {len(passwords)} mots de passe chargés.")
        
        default_threads = min(32, (os.cpu_count() or 4) + 4)
        console.print(f" [bold red]┌─[[/][bold white] Threads (1-100) [/][bold red]][/] [dim](Défaut: {default_threads})[/]")
        t_input = console.input(" [bold red]└─▶[/] [bold white]").strip()
        try:
            workers = int(t_input)
            workers = max(1, min(100, workers))
        except ValueError:
            workers = default_threads

        chunk_size = 2000
        chunks = [passwords[i:i + chunk_size] for i in range(0, len(passwords), chunk_size)]
        
        global password_found
        password_found = None
        stop_search.clear()
        stats["tested"] = 0
        stats["start_time"] = time.time()

        layout = make_layout()
        
        with Progress(
            SpinnerColumn(spinner_name="point", style="red"),
            TextColumn(f"[bold white]Cracking...[/] [bold red]{{task.percentage:>3.0f}}%"),
            BarColumn(complete_style="red", bar_width=None),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("crack", total=len(passwords), current="...")
            
            with Live(layout, refresh_per_second=10, screen=True) as live:
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    futures = []
                    for chunk in chunks:
                        if stop_search.is_set(): break
                        futures.append(executor.submit(crack_worker, filepath, ".zip", chunk, progress, task))
                    
                    while any(not f.done() for f in futures) and not stop_search.is_set():
                        t_u = time.time()
                        layout["header"].update(Panel(Align.center(Text.from_markup(f"[bold red]VOID-ZIP ENGINE[/] [dim]||[/] [white]DICTIONARY ATTACK[/]")), border_style="red"))
                        
                        main_body = Table.grid(expand=True)
                        main_body.add_row(progress)
                        layout["main_crack"].update(Panel(main_body, title="[bold white]PROCESSOR", border_style="red", padding=(2, 2)))
                        
                        side_table = Table.grid(expand=True)
                        side_table.add_row(Text.from_markup(f"[red]THREADS:[/] [white]{workers}"))
                        side_table.add_row(Text.from_markup(f"[red]TESTED :[/] [white]{stats['tested']}"))
                        side_table.add_row(Text.from_markup(f"[red]SPEED  :[/] [white]{int(stats['speed'])} p/s"))
                        side_table.add_row(Text.from_markup(f"\n[dim]CURRENT:[/]\n[bold silver]{stats['current_pwd'][:15]}..."))
                        layout["sidebar"].update(Panel(side_table, title="[bold white]STATS", border_style="red", padding=(1, 1)))
                        
                        layout["footer"].update(Panel(Align.center(Text.from_markup(f"[dim]SYSTEM RUNNING - VOID PRIME V2[/]")), border_style="red"))
                        time.sleep(0.1)

                    for f in futures:
                        if stop_search.is_set(): f.cancel()
    
    elif choice == "2":
        console.print(f"\n [bold red][!][/] Option en cours de développement.")
        time.sleep(2)
        return
    else: return
        
    console.print()
    if password_found:
        console.print(Panel(
            Align.center(Text.from_markup(f"[bold green]SUCCESS: PASSWORD CAPTURED[white]\n\n[bold #00FF00]{password_found}")),
            border_style="green", box=box.HEAVY, padding=(1,4)
        ))
    else:
        console.print(f" [bold red][x][/] Failure: Decryption failed.")

    console.input("\n [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_search.set()
        console.print(f"\n [bold red][!][/] System Aborted.")

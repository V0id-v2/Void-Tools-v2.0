import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, requests, webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import box

console = Console()

SITES = {
    "Twitter": "https://twitter.com/{}", "Facebook": "https://www.facebook.com/{}",
    "Instagram": "https://www.instagram.com/{}", "GitHub": "https://github.com/{}",
    "Reddit": "https://www.reddit.com/user/{}", "LinkedIn": "https://www.linkedin.com/in/{}",
    "Pinterest": "https://www.pinterest.com/{}", "YouTube": "https://www.youtube.com/{}",
    "TikTok": "https://www.tiktok.com/@{}", "Twitch": "https://www.twitch.tv/{}",
    "SoundCloud": "https://soundcloud.com/{}", "Medium": "https://medium.com/@{}",
    "DeviantArt": "https://www.deviantart.com/{}", "Behance": "https://www.behance.net/{}",
    "Patreon": "https://www.patreon.com/{}", "GitLab": "https://gitlab.com/{}",
    "Snapchat": "https://www.snapchat.com/add/{}", "Telegram": "https://t.me/{}"
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

ASCII = r"""
  ███╗   ██╗ █████╗ ███╗   ███╗███████╗    ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
  ████╗  ██║██╔══██╗████╗ ████║██╔════╝    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
  ██╔██╗ ██║███████║██╔████╔██║█████╗         ██║   ██████╔╝███████║██║     █████═╝ █████╗  ██████╔╝
  ██║╚██╗██║██╔══██║██║╚██╔╝██║██╔══╝         ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
  ██║ ╚████║██║  ██║██║ ╚═╝ ██║███████╗       ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
  ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""
SUBTITLE = "M U L T I - P L A T F O R M   U S E R N A M E   R E C O N"

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // NAME TRACKER")
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

def check_user(site, template, user):
    url = template.format(user)
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if r.status_code == 200:
            if "not found" not in r.text.lower() and "doesn't exist" not in r.text.lower():
                return (site, True, url)
    except: pass
    return (site, False, None)

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]NAME TRACKER[/]  [dim]//[/]  [red]OSINT[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Pseudo à rechercher [/][bold red]][/]")
        user = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not user: sys.exit(0)

        results = []
        with Progress(
            SpinnerColumn(style="red"),
            TextColumn("[dim]{task.description}"),
            BarColumn(bar_width=30, style="dark_red", complete_style="red"),
            console=console, transient=True
        ) as prog:
            task = prog.add_task(f"Traçage de '{user}'...", total=len(SITES))
            with ThreadPoolExecutor(max_workers=20) as ex:
                futs = {ex.submit(check_user, site, url, user): site for site, url in SITES.items()}
                for f in as_completed(futs):
                    results.append(f.result())
                    prog.advance(task)

        trouves = [r for r in results if r[1]]
        
        tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", header_style="bold red")
        tbl.add_column("PLATEFORME", style="white")
        tbl.add_column("STATUT", justify="center")
        tbl.add_column("LIEN", style="cyan")

        for site, found, url in sorted(results, key=lambda x: x[0]):
            if found:
                tbl.add_row(site, "[bold bright_green]TROUVÉ[/]", url)
            else:
                tbl.add_row(f"[dim]{site}[/]", "[dim red]ABSENT[/]", "[dim]—[/]")

        os.system("cls" if os.name == "nt" else "clear")
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]NAME TRACKER[/]  [dim]//[/]  [red]RESULTATS[/]"),
            border_style="red", padding=(0, 4)
        )))
        console.print(Align.center(tbl))
        console.print(Align.center(f"\n [bold bright_green]Trouvés: {len(trouves)}[/] [dim]/ {len(SITES)} sites testés[/]"))

        if trouves:
            console.print("\n [bold red]┌─[[/][bold white] Ouvrir les liens ? (oui/non) [/][bold red]][/]")
            ask = console.input(" [bold red]└─▶[/] [bold white]").strip().lower()
            if ask in ("oui", "o", "yes", "y"):
                for _, _, url in trouves: webbrowser.open(url)

        console.input("\n [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")

    except (KeyboardInterrupt, EOFError):
        pass

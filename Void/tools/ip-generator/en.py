import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, random, ipaddress
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import box

console = Console()
TIMEOUT = 8

ASCII = r"""
  ██╗   ██╗ ██████╗ ██╗██████╗       ██╗██████╗ 
  ██║   ██║██╔═══██╗██║██╔══██╗      ██║██╔══██╗
  ██║   ██║██║   ██║██║██║  ██║█████╗██║██████╔╝
  ╚██╗ ██╔╝██║   ██║██║██║  ██║╚════╝██║██╔═══╝ 
   ╚████╔╝ ╚██████╔╝██║██████╔╝      ██║██║     
    ╚═══╝   ╚═════╝ ╚═╝╚═════╝       ╚═╝╚═╝     
"""
SUBTITLE = "R A N D O M I Z E D   I P v 4   S P O O F I N G   S U B N E T"

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // IP GENERATOR")
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
                        v = max(40, min(255, int(100 + 155 * math.sin(t * 10 - c * 0.15))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;80;0;0m{SUBTITLE}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

def is_public(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved)
    except:
        return False

def generate_ips(n):
    generate_list = []
    while len(generate_list) < n:
        ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        if is_public(ip):
            generate_list.append(ip)
    return generate_list

def send_webhook(url, ips):
    try:
        content = "\n".join(f"`{ip}`" for ip in ips[:10])
        if len(ips) > 10: content += f"\n... (+{len(ips)-10} more)"
        payload = {"content": f"**[VOID-TOOLS]** IPs Generated:\n{content}"}
        requests.post(url, json=payload, timeout=TIMEOUT)
        return True
    except:
        return False

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]IP GENERATOR[/]  [dim]//[/]  [red]RANDOMIZER[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Multiple IPs to generate [/][bold red]][/]")
        count_input = console.input(" [bold red]└─▶[/] [bold white]").strip()
        
        if not count_input: sys.exit(0)
        n = int(count_input) if count_input.isdigit() else 10

        console.print(" [bold red]┌─[[/][bold white] Discord Webhook (Optional) [/][bold red]][/]")
        webhook = console.input(" [bold red]└─▶[/] [bold white]").strip()

        ips = []
        with Progress(
            SpinnerColumn(style="red"),
            TextColumn("[dim]{task.description}"),
            BarColumn(bar_width=30, style="dark_red", complete_style="red"),
            console=console, transient=True
        ) as prog:
            task = prog.add_task("Generating public IPs...", total=n)
            ips = generate_ips(n)
            prog.update(task, completed=n)

        tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", header_style="bold red")
        tbl.add_column("#", justify="right", style="dim white")
        tbl.add_column("IP ADDRESS", style="cyan")

        for i, ip in enumerate(ips, 1):
            tbl.add_row(str(i), ip)

        console.print(Align.center(Panel(tbl, title=f"[bold red] {n} IPs GENERATED [/]", border_style="red")))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Save result? (yes/no) [/][bold red]][/]")
        save = console.input(" [bold red]└─▶[/] [bold white]").strip().lower()
        if save in ("yes", "y", "o", "oui"):
            with open("ips_generated.txt", "w") as f:
                f.write("\n".join(ips))
            console.print(" [bold green][✓] Saved to ips_generated.txt[/]")

        if webhook:
            if send_webhook(webhook, ips):
                console.print(" [bold green][✓] Webhook sent successfully.[/]")
            else:
                console.print(" [bold red][!] Webhook failed to send.[/]")

        console.input("\n [dim]Press [bold red]ENTER[/] to exit...[/]")

    except (KeyboardInterrupt, EOFError):
        pass
    except Exception as e:
        console.print(f"\n [bold red][!] Error: {e}[/]")

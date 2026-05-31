import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, phonenumbers
from phonenumbers import geocoder, carrier, timezone as ph_tz
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()

ASCII = r"""
  ██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗███████╗    ██╗███╗   ██╗███████╗ ██████╗ 
  ██╔══██╗██║  ██║██╔═══██╗████╗  ██║██╔════╝    ██║████╗  ██║██╔════╝██╔═══██╗
  ██████╔╝███████║██║   ██║██╔██╗ ██║█████╗      ██║██╔██╗ ██║█████╗  ██║   ██║
  ██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║██╔══╝      ██║██║╚██╗██║██╔══╝  ██║   ██║
  ██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗    ██║██║ ╚████║██║     ╚██████╔╝
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝    ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ 
"""
SUBTITLE = "G L O B A L   T E L E P H O N Y   I N T E L L I G E N C E"

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID // NUMBER INFO")
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

def analyze_num(num_str):
    try:
        parsed = phonenumbers.parse(num_str, None)
        if not phonenumbers.is_valid_number(parsed): return None
        
        return {
            "National": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            "International": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "E164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
            "Pays": geocoder.country_name_for_number(parsed, "fr"),
            "Region": geocoder.description_for_number(parsed, "fr"),
            "Operateur": carrier.name_for_number(parsed, "fr") or "Inconnu",
            "Fuseau": ", ".join(ph_tz.time_zones_for_number(parsed)),
            "Type": str(phonenumbers.number_type(parsed)).split(".")[-1]
        }
    except: return None

if __name__ == "__main__":
    try:
        boot()
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]NUMBER INFO[/]  [dim]//[/]  [red]OSINT[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print()

        console.print(" [bold red]┌─[[/][bold white] Numéro de téléphone [/][bold red]][/]")
        num = console.input(" [bold red]└─▶[/] [bold white]").strip()
        if not num: sys.exit(0)

        data = analyze_num(num)
        if not data:
            console.print("\n [bold red][!] Numéro invalide ou format non reconnu (ex: +33...).")
            time.sleep(2); sys.exit(0)

        tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style="red", show_header=False, padding=(0, 2))
        tbl.add_column("K", style="dim red", width=18); tbl.add_column("V", style="white")

        for k, v in data.items():
            tbl.add_row(k.upper(), str(v))

        os.system("cls" if os.name == "nt" else "clear")
        console.print(Align.center(Panel(
            Text.from_markup("[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]NUMBER INFO[/]  [dim]//[/]  [red]REPORT[/]"),
            border_style="red", padding=(0, 6)
        )))
        console.print(Align.center(tbl))
        console.input("\n [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")

    except (KeyboardInterrupt, EOFError):
        pass

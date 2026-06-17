#!/usr/bin/env python3
"""Void-Tools — Webhook tools (Void theme)."""
import sys, os, re, shutil, time, json, base64, threading, random
import concurrent.futures
from datetime import datetime, timezone
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.padding import Padding
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich import box

from lib import constants as C
from lib.config import get_settings

get_settings()

console = Console(highlight=False)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
C_OK = "#88FFAA"
C_ERR = C.C_NEON
C_HOOK = "#57F287"
L = {}


def set_language(s):
    global L
    L = s


def t(k):
    return L.get(k, k)


def _community_tags():
    parts = []
    for tag in (getattr(C, "TELEGRAM_TAG", ""), getattr(C, "DISCORD_TAG", "")):
        if tag and tag not in parts:
            parts.append(tag)
    return parts


def _community_pub_short():
    tags = _community_tags()
    head = " · ".join(tags) if tags else "Void-Tools"
    return f"{head} · Void-Tools v{C.VERSION}"


def _pub_tag():
    s = t("pub_tag")
    tags = _community_tags()
    return s if s != "pub_tag" else (" · ".join(tags) if tags else "Void-Tools")


def _pub_short():
    s = t("pub_short")
    return s if s != "pub_short" else _community_pub_short()


def _pub_line():
    s = t("pub_line")
    tags = _community_tags()
    joined = " · ".join(tags) if tags else "Void-Tools"
    return s if s != "pub_line" else f"**Void-Tools** → {joined}"


def _pub_user():
    s = t("pub_user")
    return s if s != "pub_user" else "Void-Tools"


def _has_pub(text):
    if not text:
        return False
    low = str(text).lower()
    for tag in _community_tags():
        if tag.lower() in low:
            return True
    return "t.me/" in low or "discord.gg/" in low or "telegram" in low


def _with_pub(content):
    if not content:
        return _pub_line()[:2000]
    if _has_pub(content):
        return content[:2000]
    return f"{content}\n{_pub_short()}"[:2000]


def _brand_embed(embed):
    e = dict(embed)
    foot = e.get("footer") if isinstance(e.get("footer"), dict) else {}
    txt = (foot.get("text") or "").strip()
    if not _has_pub(txt):
        e["footer"] = {"text": (f"{txt} · {_pub_short()}" if txt else _pub_short())[:2048]}
    desc = e.get("description") or ""
    if desc and not _has_pub(desc):
        e["description"] = _with_pub(desc)[:4096]
    elif not desc and (e.get("title") or e.get("image")):
        e["description"] = _pub_short()[:4096]
    title = e.get("title") or ""
    if title and not _has_pub(title) and title.strip().lower() in ("void-tools", "webhook", "embed"):
        e["title"] = f"{title} · {_pub_tag()}"[:256]
    return e


def _brand_payload(payload):
    if not isinstance(payload, dict):
        return payload
    p = dict(payload)
    p["username"] = (p.get("username") or _pub_user())[:80]
    embeds = p.get("embeds")
    if embeds:
        p["embeds"] = [_brand_embed(e) for e in embeds if isinstance(e, dict)]
    if p.get("content") is not None and str(p.get("content")).strip():
        p["content"] = _with_pub(p["content"])
    elif not p.get("content") and not embeds:
        p["content"] = _pub_line()[:2000]
    return p


def _pal():
    return C.palette()


def _tw():
    return max(54, min(72, shutil.get_terminal_size((90, 30)).columns - 4))


def _ask(p):
    return input(f"\033[38;2;136;0;0m  ◆ {p} \033[38;2;180;180;200m▸\033[0m ").strip()


def _pause():
    console.print()
    input(f"\033[38;2;120;0;0m  ► {t('pause')} \033[0m")


def _panel(title, desc):
    p = _pal()
    console.print()
    head = Text.from_markup(
        f"[{C.C_GOLD} bold]◆ {title}[/]\n"
        f"[{C.C_DIM}]{desc}[/]\n"
        f"[{C_HOOK} dim]▸ WEBHOOK · {_pub_tag()}[/]"
    )
    console.print(Panel(
        Align.center(head),
        border_style=p["blood"], box=box.DOUBLE_EDGE, padding=(1, 2), width=_tw(),
    ))


def _fail(msg, detail=None):
    body = Text.from_markup(f"[{C_ERR} bold]{msg}[/]")
    if detail:
        body.append("\n")
        body.append(Text.from_markup(f"[{C.C_DIM}]{detail}[/]"))
    console.print(Panel(
        body, title=f"[bold white]✖ {t('error_title')}[/]",
        border_style=C_ERR, box=box.HEAVY, padding=(1, 2), width=_tw(),
    ))


def _ok(title, msg):
    console.print(Panel(
        Align.center(Text.from_markup(f"[{C_OK} bold]{msg}[/]")),
        title=f"[bold white]✔ {title}[/]",
        border_style=C_OK, box=box.ROUNDED, padding=(1, 2), width=_tw(),
    ))


def _hint(text):
    console.print(Padding(Text.from_markup(f"[{C.C_DIM}]{text}[/]"), (0, 1)))


def _show_table(title, rows, columns=None):
    p = _pal()
    if columns:
        tbl = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=p["blood"], show_header=True, padding=(0, 1))
        for col in columns:
            tbl.add_column(col, style=C.C_GOLD if col == columns[0] else "white")
        for row in rows:
            tbl.add_row(*[str(x) for x in row])
    else:
        tbl = Table(box=box.SIMPLE, border_style=p["blood"], show_header=False, padding=(0, 1))
        tbl.add_column("", style=C.C_SILVER, width=16, no_wrap=True)
        tbl.add_column("", overflow="fold")
        for k, v in rows:
            tbl.add_row(k, str(v))
    console.print(Padding(Panel(
        tbl, title=f"[{C.C_GOLD} bold]{title}[/]",
        border_style=p["blood"], box=box.ROUNDED, padding=(0, 1), width=_tw(),
    ), (1, 0)))


def _stats_bar(items):
    p = _pal()
    parts = "   ".join(
        f"[{C.C_SILVER}]{k}[/] [{C.C_GOLD} bold]{v}[/]" for k, v in items
    )
    console.print(Panel(
        Align.center(Text.from_markup(parts)),
        border_style=p["dark"], box=box.SIMPLE, padding=(0, 1), width=_tw(),
    ))


def _as_dict(d):
    return d if isinstance(d, dict) else {}


def _confirm(msg):
    return _ask(msg).lower() in ("yes", "y", "oui", "o")


def _parse_webhook(raw):
    m = re.search(r"webhooks/(\d+)/([A-Za-z0-9_-]+)", raw)
    return (m.group(1), m.group(2)) if m else (None, None)


def _valid_webhook_url(url):
    return bool(url) and "webhooks/" in url and ("discord.com" in url or "discordapp.com" in url)


def _api_url(wid, wtoken):
    return f"https://discord.com/api/v9/webhooks/{wid}/{wtoken}"


def _msg_url(wid, wtoken, msg_id):
    return f"{_api_url(wid, wtoken)}/messages/{msg_id}"


def _normalize_post_url(raw):
    raw = raw.strip()
    if not _valid_webhook_url(raw):
        return None
    wid, wtoken = _parse_webhook(raw)
    if not wid:
        return None
    return _api_url(wid, wtoken)


def _snowflake_ts(snow_id):
    try:
        sid = int(snow_id)
        ts_ms = (sid >> 22) + 1420070400000
        created = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        return created.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return "?"


def _headers(json_body=False):
    h = {"User-Agent": UA, "Accept": "application/json"}
    if json_body:
        h["Content-Type"] = "application/json"
    return h


def _request(method, url, json_body=None, files=None, timeout=12):
    try:
        r = requests.request(
            method, url, headers=_headers(json_body is not None and files is None),
            json=json_body, files=files, timeout=timeout,
        )
        data = {}
        if r.text:
            try:
                data = r.json()
            except ValueError:
                data = {"raw": r.text[:300]}
        return r.status_code, data
    except requests.RequestException as ex:
        return 0, {"error": str(ex)}


def _get_webhook(wid, wtoken):
    return _request("GET", _api_url(wid, wtoken))


def _post_webhook(url, payload, files=None, wait=False, brand=True):
    if brand and isinstance(payload, dict):
        payload = _brand_payload(payload)
    if wait and "?" not in url:
        url = f"{url}?wait=true"
    return _request("POST", url, json_body=payload if not files else None, files=files)


def _patch_webhook(wid, wtoken, body):
    return _request("PATCH", _api_url(wid, wtoken), json_body=body)


def _delete_webhook(wid, wtoken):
    return _request("DELETE", _api_url(wid, wtoken))


def _delete_message(wid, wtoken, msg_id):
    return _request("DELETE", _msg_url(wid, wtoken, msg_id))


def _mode_menu(options):
    p = _pal()
    tbl = Table(box=box.SIMPLE_HEAVY, border_style=p["mid"], show_header=False, padding=(0, 1))
    tbl.add_column("", style=C.C_GOLD, width=5, no_wrap=True)
    tbl.add_column("", style="white")
    for key, label in options.items():
        tbl.add_row(f"[{key}]", label)
    console.print(Padding(Panel(
        tbl, title=f"[{C.C_GOLD} bold]{t('pick_mode')}[/]",
        border_style=p["blood"], box=box.ROUNDED, width=_tw() - 2,
    ), (0, 0, 1, 0)))


def _webhooks_lib_path():
    return os.path.join(C.CONFIG_DIR, "webhooks.json")


def _load_webhook_lib():
    path = _webhooks_lib_path()
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            pass
    return {}


def _save_webhook_lib(data):
    os.makedirs(C.CONFIG_DIR, exist_ok=True)
    with open(_webhooks_lib_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _patch_message(wid, wtoken, msg_id, body):
    return _request("PATCH", _msg_url(wid, wtoken, msg_id), json_body=body)


def _clone_payload_from(wid, wtoken):
    code, info = _get_webhook(wid, wtoken)
    if code != 200:
        return code, None
    info = _as_dict(info)
    body = {"name": info.get("name", "Webhook")[:80]}
    if info.get("avatar"):
        try:
            url = f"https://cdn.discordapp.com/avatars/{wid}/{info['avatar']}.png?size=256"
            body["avatar"] = _avatar_data_uri(url)
        except Exception:
            pass
    return 200, body


def _avatar_from_source(src):
    if src.startswith("http"):
        return _avatar_data_uri(src)
    if os.path.isfile(src):
        with open(src, "rb") as f:
            raw = f.read()
        ext = os.path.splitext(src)[1].lower()
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
        b64 = base64.b64encode(raw).decode()
        return f"data:{mime};base64,{b64}"
    raise FileNotFoundError(src)


def _post_raw(url, payload):
    try:
        r = requests.post(url, json=payload, headers=_headers(True), timeout=12)
        data = {}
        if r.text:
            try:
                data = r.json()
            except ValueError:
                data = {}
        return r.status_code, r.headers, data
    except requests.RequestException as ex:
        return 0, {}, {"error": str(ex)}


def _ask_webhook():
    raw = _ask(t("wh_prompt"))
    if not raw:
        return None, None, None
    if not _valid_webhook_url(raw):
        _fail(t("wh_invalid"))
        return None, None, None
    wid, wtoken = _parse_webhook(raw)
    if not wid:
        _fail(t("wh_invalid"))
        return None, None, None
    return raw.strip(), wid, wtoken


def _load_lines(prompt, file_prompt):
    raw = _ask(prompt)
    if not raw:
        return []
    if raw.lower() == "file":
        fp = _ask(file_prompt).strip().strip('"')
        if not fp or not os.path.isfile(fp):
            _fail(t("file_not_found"))
            return []
        with open(fp, encoding="utf-8", errors="ignore") as f:
            return [l.strip() for l in f if l.strip()]
    if "," in raw:
        return [x.strip() for x in raw.split(",") if x.strip()]
    lines = [raw]
    _hint(t("lines_hint"))
    while True:
        line = input(f"\033[38;2;80;80;100m    ▸ \033[0m").strip()
        if not line:
            break
        lines.append(line)
    return lines


def _avatar_data_uri(url):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=12)
    r.raise_for_status()
    mime = (r.headers.get("content-type") or "image/png").split(";")[0]
    if not mime.startswith("image/"):
        mime = "image/png"
    b64 = base64.b64encode(r.content).decode()
    return f"data:{mime};base64,{b64}"


def _extract_msg_id(data):
    d = _as_dict(data)
    return str(d.get("id", "")) if d.get("id") else ""


def webhook_info():
    _panel(t("wh_title"), t("wh_desc"))
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    with Progress(SpinnerColumn(style=C.C_GOLD), TextColumn("{task.description}"), transient=True, console=console) as prog:
        prog.add_task(t("wh_fetch"), total=None)
        code, d = _get_webhook(wid, wtoken)
    if code != 200:
        _fail(f"{t('wh_fail')} (HTTP {code})")
        return
    d = _as_dict(d)
    avatar = "—"
    if d.get("avatar"):
        avatar = f"https://cdn.discordapp.com/avatars/{wid}/{d['avatar']}.png?size=256"
    _show_table(d.get("name", "Webhook"), [
        ("ID", d.get("id", "?")),
        (t("name"), d.get("name", "?")),
        ("Channel", d.get("channel_id", "?")),
        ("Guild", d.get("guild_id", "?")),
        (t("type"), d.get("type", "?")),
        ("App ID", d.get("application_id") or "—"),
        (t("created"), _snowflake_ts(d.get("id", wid))),
        ("Avatar", avatar),
        ("Token", f"[dim]{wtoken[:12]}…[/]"),
        ("API URL", _api_url(wid, wtoken)),
        ("Void-Tools", _pub_short()),
    ])


def webhook_send():
    _panel(t("wsg_title"), t("wsg_desc"))
    _mode_menu({
        "1": t("wsg_test"), "2": t("wsg_custom"), "3": t("wsg_tts"),
        "4": t("wsg_silent"), "5": t("wsg_fake"), "6": t("wsg_mention"), "7": t("wsg_thread"),
    })
    mode = _ask(t("pick_mode")) or "1"
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    api = _api_url(wid, wtoken)
    payload = {"username": _pub_user()}
    wait = mode in ("1", "2")
    if mode == "1":
        payload["content"] = t("wt_ping")
    elif mode == "2":
        msg = _ask(t("ws_msg"))
        if not msg:
            return
        payload["content"] = msg
        un = _ask(t("ws_name"))
        if un:
            payload["username"] = un[:80]
    elif mode == "3":
        msg = _ask(t("ws_msg")) or _pub_line()
        payload.update({"content": msg, "tts": True})
    elif mode == "4":
        payload.update({"content": _ask(t("ws_msg")) or t("wt_ping"), "flags": 4096})
    elif mode == "5":
        payload["content"] = _ask(t("ws_msg")) or t("wt_ping")
        payload["username"] = (_ask(t("ws_name")) or _pub_user())[:80]
        av = _ask(t("wim_avatar"))
        if av.startswith("http"):
            payload["avatar_url"] = av
    elif mode == "6":
        _mode_menu({"1": "@everyone", "2": "@here", "3": t("wmc_block")})
        m = _ask(t("pick_mode")) or "1"
        base = _ask(t("ws_msg")) or _pub_line()
        if m == "1":
            payload.update({"content": f"@everyone {base}", "allowed_mentions": {"parse": ["everyone"]}})
        elif m == "2":
            payload.update({"content": f"@here {base}", "allowed_mentions": {"parse": ["here"]}})
        else:
            payload.update({"content": f"@everyone {base}", "allowed_mentions": {"parse": []}})
    else:
        tid = _ask(t("wt2_thread"))
        tname = _ask(t("wfo_name"))
        payload["content"] = _ask(t("ws_msg")) or t("wt_ping")
        if tid and tid.isdigit():
            api = f"{api}?thread_id={tid}"
        if tname:
            payload["thread_name"] = tname[:100]
    with Progress(SpinnerColumn(style=C.C_GOLD), TextColumn("{task.description}"), transient=True, console=console) as prog:
        prog.add_task(t("wt_sending"), total=None)
        code, data = _post_webhook(api, payload, wait=wait)
    if code in (200, 204):
        mid = _extract_msg_id(data) if wait else ""
        msg = t("wt_ok") + (f" · ID {mid}" if mid else "")
        _ok(t("wsg_title"), msg)
    else:
        _fail(f"{t('wt_fail')} (HTTP {code})")


def webhook_spam():
    _panel(t("ws_title"), t("ws_desc"))
    _mode_menu({
        "1": t("ws_mode_normal"), "2": t("ws_mode_mass"), "3": t("ws_mode_multi"),
        "4": t("ws_mode_random"), "5": t("ws_mode_embed"),
    })
    mode = _ask(t("pick_mode")) or "1"
    if mode == "3":
        urls = _load_lines(t("wb_prompt"), t("wb_file"))
        urls = [u for u in dict.fromkeys(urls) if _valid_webhook_url(u)]
        if not urls:
            _fail(t("wh_invalid"))
            return
        msg = _ask(t("ws_msg")) or _pub_line()
        try:
            count = max(1, min(20, int(_ask(t("ws_count")) or "3")))
        except ValueError:
            count = 3
        total_sent, total_fail = 0, 0
        for url in urls:
            w, tk = _parse_webhook(url)
            for _ in range(count):
                c, _ = _post_webhook(_api_url(w, tk), {"content": msg, "username": _pub_user()})
                if c in (200, 204):
                    total_sent += 1
                else:
                    total_fail += 1
                time.sleep(0.35)
        _stats_bar([(t("ws_sent"), total_sent), (t("ws_failed"), total_fail)])
        return
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    url = _api_url(wid, wtoken)
    if mode == "2":
        msg = _ask(t("ws_msg")) or _pub_line()
        try:
            threads = max(1, min(8, int(_ask(t("wms_threads")) or "4")))
        except ValueError:
            threads = 4
        try:
            per = max(1, min(25, int(_ask(t("wms_per")) or "5")))
        except ValueError:
            per = 5
        stats = {"sent": 0, "failed": 0}
        lock = threading.Lock()

        def worker():
            for _ in range(per):
                c, _ = _post_webhook(url, {"content": msg, "username": _pub_user()})
                with lock:
                    if c in (200, 204):
                        stats["sent"] += 1
                    else:
                        stats["failed"] += 1
                time.sleep(0.15)

        with Progress(SpinnerColumn(style=C.C_GOLD), TextColumn("{task.description}"), transient=True, console=console) as prog:
            prog.add_task(t("wms_running"), total=None)
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as pool:
                concurrent.futures.wait([pool.submit(worker) for _ in range(threads)])
        _stats_bar([(t("ws_sent"), stats["sent"]), (t("ws_failed"), stats["failed"])])
        return
    if mode == "4":
        slug = (_community_tags() or ["void"])[0].rsplit("/", 1)[-1]
        words = _load_lines(t("wrs_words"), t("wb_file")) or [_pub_tag(), "Void-Tools", _pub_short(), f"join {slug}"]
        try:
            count = max(1, min(50, int(_ask(t("ws_count")) or "10")))
        except ValueError:
            count = 10
        try:
            delay = max(0.2, float(_ask(t("ws_delay")) or "0.4"))
        except ValueError:
            delay = 0.4
        sent = 0
        for i in range(count):
            if _post_webhook(url, {"content": f"{random.choice(words)} [{i+1}]", "username": _pub_user()})[0] in (200, 204):
                sent += 1
            time.sleep(delay)
        _stats_bar([(t("ws_sent"), f"{sent}/{count}")])
        return
    if mode == "5":
        title = _ask(t("we_embed_title")) or f"Void-Tools · {_pub_tag()}"
        desc = _ask(t("we_embed_desc")) or t("we_default_desc")
        try:
            count = max(1, min(50, int(_ask(t("ws_count")) or "5")))
        except ValueError:
            count = 5
        try:
            delay = max(0.2, float(_ask(t("ws_delay")) or "0.5"))
        except ValueError:
            delay = 0.5
        sent, failed = 0, 0
        p = _pal()
        with Progress(SpinnerColumn(style=C.C_GOLD), BarColumn(bar_width=30, complete_style=p["neon"]),
                      TextColumn("{task.completed}/{task.total}"), TimeElapsedColumn(), console=console) as prog:
            task = prog.add_task(t("wse_running"), total=count)
            for i in range(count):
                emb = {"title": f"{title} #{i+1}", "description": desc[:4096], "color": 0x880000 + (i * 1000) % 0xFFFFFF}
                c, _ = _post_webhook(url, {"username": _pub_user(), "embeds": [emb]})
                if c in (200, 204):
                    sent += 1
                else:
                    failed += 1
                prog.advance(task)
                time.sleep(delay)
        _stats_bar([(t("ws_sent"), sent), (t("ws_failed"), failed)])
        return
    msg = _ask(t("ws_msg")) or _pub_line()
    try:
        count = max(1, min(100, int(_ask(t("ws_count")) or "10")))
    except ValueError:
        count = 10
    try:
        delay = max(0.1, float(_ask(t("ws_delay")) or "0.3"))
    except ValueError:
        delay = 0.3
    username = _ask(t("ws_name")) or _pub_user()
    mention = _ask(t("ws_mention")).lower() in ("yes", "y", "oui", "o")
    if mention:
        msg = f"@everyone {msg}"
    url = _api_url(wid, wtoken)
    sent, failed = 0, 0
    p = _pal()
    with Progress(
        SpinnerColumn(style=C.C_GOLD),
        BarColumn(bar_width=30, complete_style=p["neon"], finished_style=C_OK),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as prog:
        task = prog.add_task(t("ws_running"), total=count)
        for i in range(count):
            payload = {"content": f"{msg} [{i + 1}/{count}]", "username": username[:80]}
            code, _ = _post_webhook(url, payload)
            if code in (200, 204):
                sent += 1
            else:
                failed += 1
            prog.advance(task)
            time.sleep(delay)
    _stats_bar([
        (t("ws_sent"), sent),
        (t("ws_failed"), failed),
        ("Total", count),
    ])


_DEFAULT_GIFS = [
    "https://media.giphy.com/media/ICOgHjp646ZUs/giphy.gif",
    "https://media.giphy.com/media/13CoXDiaIcGyw/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "https://media.giphy.com/media/3o7aCTPPm4OHfRLSH6/giphy.gif",
    "https://media.giphy.com/media/26BRuo6zEo4BgKjzW/giphy.gif",
    "https://media.tenor.com/WiDMEGnToeMAAAAd/mind-blown-exploding-head.gif",
    "https://media.tenor.com/847x846G2UAAAAd/cat-cat-meme.gif",
    "https://media.tenor.com/x8v1oNUOmg4AAAAd/cat-meme.gif",
]

_DEFAULT_BAD_WORDS = [
    "merde", "putain", "connard", "fdp", "ntm", "salope", "enculé", "batard",
    "fuck", "shit", "bitch", "asshole", "damn", "bastard", "dick", "cunt",
    "trash", "noob", "loser", "ez", "ratio", "skill issue", "cry", "mad",
]


def _default_bad_words():
    tags = _community_tags()
    extra = []
    for tag in tags:
        extra.append(tag)
        slug = tag.rsplit("/", 1)[-1]
        if slug and slug != tag:
            extra.append(f"join {slug}")
    return list(_DEFAULT_BAD_WORDS) + extra + ["Void-Tools"]


def _default_gifs():
    return list(_DEFAULT_GIFS)


def _gif_spam_payload(gifs, bads, mode):
    gif = random.choice(gifs)
    word = random.choice(bads) if bads else "spam"
    payload = {"username": _pub_user()}
    if mode == "1":
        payload["embeds"] = [{"image": {"url": gif}, "color": 0x880000}]
    elif mode == "2":
        payload["content"] = word[:500]
        payload["embeds"] = [{"image": {"url": gif}, "color": 0xFF0000}]
    elif mode == "3":
        payload["content"] = f"{word} [{random.randint(1, 9999)}]"
    else:
        payload["content"] = word[:500]
        payload["embeds"] = [{
            "title": f"{word} · {_pub_tag()}"[:256],
            "image": {"url": gif},
            "color": 0x880000 + random.randint(0, 0x777777),
        }]
    return payload


def webhook_gif_spam():
    _panel(t("wgf_title"), t("wgf_desc"))
    _mode_menu({
        "1": t("wgf_mode_gif"),
        "2": t("wgf_mode_fast"),
        "3": t("wgf_mode_bad"),
        "4": t("wgf_mode_mix"),
    })
    mode = _ask(t("pick_mode")) or "1"
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    gifs = _load_lines(t("wgf_gifs"), t("wb_file")) or _default_gifs()
    gifs = [u for u in gifs if u.startswith("http")]
    if not gifs:
        gifs = _default_gifs()
    bads = _load_lines(t("wgf_badwords"), t("wb_file")) or _default_bad_words()
    try:
        count = max(1, min(100, int(_ask(t("ws_count")) or "15")))
    except ValueError:
        count = 15
    default_delay = "0.08" if mode == "2" else "0.35"
    try:
        delay = max(0.05, float(_ask(t("ws_delay")) or default_delay))
    except ValueError:
        delay = float(default_delay)
    url = _api_url(wid, wtoken)
    sent, failed = 0, 0
    p = _pal()
    with Progress(
        SpinnerColumn(style=C.C_GOLD),
        BarColumn(bar_width=30, complete_style=p["neon"], finished_style=C_OK),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as prog:
        task = prog.add_task(t("wgf_running"), total=count)
        for _ in range(count):
            payload = _gif_spam_payload(gifs, bads, mode)
            code, _ = _post_webhook(url, payload)
            if code in (200, 204):
                sent += 1
            else:
                failed += 1
            prog.advance(task)
            time.sleep(delay)
    _stats_bar([(t("ws_sent"), sent), (t("ws_failed"), failed), ("Total", count)])


def webhook_embed():
    _panel(t("we_title"), t("we_desc"))
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    title = _ask(t("we_embed_title")) or f"Void-Tools · {_pub_tag()}"
    desc = _ask(t("we_embed_desc")) or t("we_default_desc")
    color_raw = _ask(t("we_color")) or "880000"
    try:
        color = int(color_raw.lstrip("#"), 16)
    except ValueError:
        color = 0x880000
    footer = _ask(t("we_footer")) or _pub_short()
    thumb = _ask(t("we_thumb"))
    embed = {
        "title": title[:256],
        "description": desc[:4096],
        "color": color,
        "footer": {"text": footer[:2048]},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if thumb.startswith("http"):
        embed["thumbnail"] = {"url": thumb}
    _hint(t("wef_fields_hint"))
    fields = []
    for i in range(1, 4):
        fname = _ask(f"{t('wef_fname')} {i} (Enter=skip)")
        if not fname:
            break
        fields.append({"name": fname[:256], "value": (_ask(f"{t('wef_fval')} {i}") or "—")[:1024], "inline": True})
    if fields:
        embed["fields"] = fields
    payload = {"username": _pub_user(), "embeds": [embed]}
    with Progress(SpinnerColumn(style=C.C_GOLD), TextColumn("{task.description}"), transient=True, console=console) as prog:
        prog.add_task(t("we_sending"), total=None)
        code, data = _post_webhook(_api_url(wid, wtoken), payload)
    if code in (200, 204):
        mid = _extract_msg_id(data)
        _ok(t("we_title"), f"{t('we_ok')}" + (f" · ID {mid}" if mid else ""))
    else:
        _fail(f"{t('we_fail')} (HTTP {code})")


def webhook_json():
    _panel(t("wj_title"), t("wj_desc"))
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    _hint(t("wj_hint"))
    sample = json.dumps({"content": _pub_line(), "username": _pub_user()}, indent=2)
    console.print(Padding(Text.from_markup(f"[{C.C_DIM}]{sample}[/]"), (0, 1)))
    body = _ask(t("wj_body"))
    if not body:
        body = sample
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as ex:
        _fail(t("wj_invalid"), str(ex))
        return
    if not isinstance(payload, dict):
        _fail(t("wj_invalid"))
        return
    with Progress(SpinnerColumn(style=C.C_GOLD), TextColumn("{task.description}"), transient=True, console=console) as prog:
        prog.add_task(t("wj_sending"), total=None)
        code, data = _post_webhook(_api_url(wid, wtoken), payload)
    if code in (200, 204):
        _ok(t("wj_title"), t("wj_ok"))
    else:
        detail = _as_dict(data).get("message", str(data)[:120])
        _fail(f"{t('wj_fail')} (HTTP {code})", detail)


def webhook_ghost():
    _panel(t("wg_title"), t("wg_desc"))
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    msg = _ask(t("wg_msg")) or f"@everyone {_pub_line()}"
    try:
        delay = max(0.3, float(_ask(t("wg_delay")) or "1.5"))
    except ValueError:
        delay = 1.5
    payload = {"content": msg, "username": _pub_user()}
    code, data = _post_webhook(_api_url(wid, wtoken), payload, wait=True)
    if code not in (200, 204):
        _fail(f"{t('wg_fail_send')} (HTTP {code})")
        return
    mid = _extract_msg_id(data)
    if not mid:
        _fail(t("wg_no_id"))
        return
    _hint(f"{t('wg_wait')} {delay}s…")
    time.sleep(delay)
    dcode, _ = _delete_message(wid, wtoken, mid)
    if dcode in (200, 204):
        _ok(t("wg_title"), t("wg_ok"))
    else:
        _fail(f"{t('wg_fail_del')} (HTTP {dcode})", f"Message ID: {mid}")


def webhook_edit():
    _panel(t("wx_title"), t("wx_desc"))
    _mode_menu({"1": t("wx_mode_name"), "2": t("wx_mode_avatar"), "3": t("wx_mode_clear")})
    mode = _ask(t("pick_mode")) or "1"
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    if mode == "3":
        if not _confirm(t("wca_confirm")):
            _hint(t("cancelled"))
            return
        code, _ = _patch_webhook(wid, wtoken, {"avatar": None})
        if code == 200:
            _ok(t("wx_title"), t("wca_ok"))
        else:
            _fail(f"{t('wca_fail')} (HTTP {code})")
        return
    body = {}
    if mode == "1":
        name = _ask(t("wx_name"))
        if not name:
            _hint(t("wx_nothing"))
            return
        body["name"] = name[:80]
    else:
        src = _ask(t("wav_source"))
        if not src:
            return
        try:
            body["avatar"] = _avatar_from_source(src)
        except Exception as ex:
            _fail(t("wx_avatar_fail"), str(ex))
            return
    with Progress(SpinnerColumn(style=C.C_GOLD), TextColumn("{task.description}"), transient=True, console=console) as prog:
        prog.add_task(t("wx_patch"), total=None)
        pcode, nd = _patch_webhook(wid, wtoken, body)
    if pcode == 200:
        _ok(t("wx_title"), f"{t('wx_ok')} → {_as_dict(nd).get('name', '?')}")
    else:
        _fail(f"{t('wx_fail')} (HTTP {pcode})")


def webhook_bulk():
    _panel(t("wb_title"), t("wb_desc"))
    urls = _load_lines(t("wb_prompt"), t("wb_file"))
    urls = list(dict.fromkeys(urls))
    if not urls:
        return
    rows = []
    valid = 0
    p = _pal()
    with Progress(
        SpinnerColumn(style=C.C_GOLD),
        BarColumn(bar_width=30, complete_style=p["neon"], finished_style=C_OK),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as prog:
        task = prog.add_task(t("wb_running"), total=len(urls))
        for i, url in enumerate(urls, 1):
            if not _valid_webhook_url(url):
                rows.append((str(i), f"[{C_ERR}]INVALID[/]", "—", "—"))
            else:
                wid, wtoken = _parse_webhook(url)
                code, d = _get_webhook(wid, wtoken)
                if code == 200:
                    valid += 1
                    d = _as_dict(d)
                    rows.append((str(i), f"[{C_OK}]OK[/]", d.get("name", "?"), d.get("guild_id", "?")))
                else:
                    rows.append((str(i), f"[{C_ERR}]HTTP {code}[/]", "—", "—"))
            prog.advance(task)
            time.sleep(0.2)
    _show_table(t("wb_result"), rows, columns=["#", "Status", t("name"), "Guild"])
    _stats_bar([(t("wb_valid"), f"{valid}/{len(urls)}")])


def webhook_file():
    _panel(t("wf_title"), t("wf_desc"))
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    src = _ask(t("wf_source"))
    if not src:
        return
    caption = _with_pub(_ask(t("wf_caption")) or _pub_line())
    url = _api_url(wid, wtoken)
    form = {"content": caption[:2000], "username": _pub_user()}
    try:
        if src.startswith("http"):
            with Progress(SpinnerColumn(style=C.C_GOLD), TextColumn("{task.description}"), transient=True, console=console) as prog:
                prog.add_task(t("wf_download"), total=None)
                r = requests.get(src, headers={"User-Agent": UA}, timeout=20)
                r.raise_for_status()
            name = src.rstrip("/").split("/")[-1].split("?")[0] or "file.bin"
            resp = requests.post(
                url, data=form,
                files={"file": (name[:80], r.content)},
                headers={"User-Agent": UA}, timeout=20,
            )
            code = resp.status_code
        elif os.path.isfile(src):
            fname = os.path.basename(src)
            with open(src, "rb") as f:
                resp = requests.post(
                    url, data=form,
                    files={"file": (fname[:80], f.read())},
                    headers={"User-Agent": UA}, timeout=20,
                )
            code = resp.status_code
        else:
            _fail(t("file_not_found"))
            return
    except requests.RequestException as ex:
        _fail(t("network"), str(ex))
        return
    if code in (200, 204):
        _ok(t("wf_title"), t("wf_ok"))
    else:
        _fail(f"{t('wf_fail')} (HTTP {code})")


def webhook_delete_msg():
    _panel(t("wm_title"), t("wm_desc"))
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    msg_id = _ask(t("wm_id"))
    if not msg_id or not msg_id.isdigit():
        _fail(t("wm_id_invalid"))
        return
    if not _confirm(t("wm_confirm")):
        _hint(t("cancelled"))
        return
    code, _ = _delete_message(wid, wtoken, msg_id)
    if code in (200, 204):
        _ok(t("wm_title"), t("wm_ok"))
    else:
        _fail(f"{t('wm_fail')} (HTTP {code})")


def webhook_destroyer():
    _panel(t("wd_title"), t("wd_desc"))
    _mode_menu({"1": t("wd_single"), "2": t("wd_bulk")})
    mode = _ask(t("pick_mode")) or "1"
    if mode == "2":
        urls = _load_lines(t("wb_prompt"), t("wb_file"))
        urls = [u for u in dict.fromkeys(urls) if _valid_webhook_url(u)]
        if not urls:
            _fail(t("wh_invalid"))
            return
        if not _confirm(t("wbd_confirm")):
            _hint(t("cancelled"))
            return
        ok_n, fail_n = 0, 0
        for url in urls:
            w, tk = _parse_webhook(url)
            c, _ = _delete_webhook(w, tk)
            if c in (200, 204):
                ok_n += 1
            else:
                fail_n += 1
            time.sleep(0.3)
        _stats_bar([(t("wd_ok"), ok_n), (t("wd_fail"), fail_n)])
        return
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    code, info = _get_webhook(wid, wtoken)
    if code == 200:
        info = _as_dict(info)
        _show_table(t("wh_title"), [
            (t("name"), info.get("name", "?")),
            ("ID", info.get("id", "?")),
            ("Channel", info.get("channel_id", "?")),
        ])
    if not _confirm(t("wd_confirm")):
        _hint(t("cancelled"))
        return
    dcode, _ = _delete_webhook(wid, wtoken)
    if dcode in (200, 204):
        _ok(t("wd_title"), t("wd_ok"))
    else:
        _fail(f"{t('wd_fail')} (HTTP {dcode})")


def webhook_clone():
    _panel(t("wc_title"), t("wc_desc"))
    src = _ask(t("wc_source"))
    dest = _ask(t("wc_target"))
    if not _valid_webhook_url(src) or not _valid_webhook_url(dest):
        _fail(t("wh_invalid"))
        return
    sw, st = _parse_webhook(src)
    dw, dt = _parse_webhook(dest)
    with Progress(SpinnerColumn(style=C.C_GOLD), TextColumn("{task.description}"), transient=True, console=console) as prog:
        prog.add_task(t("wc_running"), total=None)
        code, body = _clone_payload_from(sw, st)
    if code != 200 or not body:
        _fail(t("wc_fail_src"), f"HTTP {code}")
        return
    pcode, nd = _patch_webhook(dw, dt, body)
    if pcode == 200:
        nd = _as_dict(nd)
        _ok(t("wc_title"), f"{t('wc_ok')} → {nd.get('name', '?')}")
    else:
        _fail(f"{t('wc_fail')} (HTTP {pcode})")


def webhook_library():
    _panel(t("wl_title"), t("wl_desc"))
    _mode_menu({"1": t("wl_save"), "2": t("wl_list"), "3": t("wl_remove")})
    mode = _ask(t("pick_mode")) or "2"
    lib = _load_webhook_lib()
    if mode == "1":
        label = _ask(t("wl_label"))
        raw, wid, wtoken = _ask_webhook()
        if not wid or not label:
            return
        code, info = _get_webhook(wid, wtoken)
        if code != 200:
            _fail(f"{t('wh_fail')} (HTTP {code})")
            return
        lib[label] = raw.strip()
        _save_webhook_lib(lib)
        _ok(t("wl_title"), f"{t('wl_saved')} [{label}]")
    elif mode == "3":
        label = _ask(t("wl_label"))
        if label in lib:
            del lib[label]
            _save_webhook_lib(lib)
            _ok(t("wl_title"), t("wl_removed"))
        else:
            _fail(t("wl_not_found"))
    else:
        if not lib:
            _hint(t("wl_empty"))
            return
        rows = [(k, v[:55] + "…" if len(v) > 55 else v) for k, v in lib.items()]
        _show_table(t("wl_list"), rows, columns=[t("wl_label"), "URL"])


def webhook_edit_msg():
    _panel(t("wem_title"), t("wem_desc"))
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    msg_id = _ask(t("wm_id"))
    if not msg_id or not msg_id.isdigit():
        _fail(t("wm_id_invalid"))
        return
    new_content = _ask(t("wem_content"))
    if not new_content:
        return
    code, _ = _patch_message(wid, wtoken, msg_id, {"content": new_content[:2000]})
    if code == 200:
        _ok(t("wem_title"), t("wem_ok"))
    else:
        _fail(f"{t('wem_fail')} (HTTP {code})")


def webhook_curl():
    _panel(t("wcu_title"), t("wcu_desc"))
    raw, wid, wtoken = _ask_webhook()
    if not wid:
        return
    api = _api_url(wid, wtoken)
    msg = _ask(t("ws_msg")) or _pub_line()
    safe = msg.replace("\\", "\\\\").replace('"', '\\"').replace("'", "'\\''")
    curls = [
        ("GET info", f'curl -s "{api}"'),
        ("POST msg", f'curl -X POST "{api}" -H "Content-Type: application/json" -d \'{{"content":"{safe}","username":"{_pub_user()}"}}\''),
        ("DELETE hook", f'curl -X DELETE "{api}"'),
    ]
    rows = [(k, f"[dim]{v}[/]") for k, v in curls]
    _show_table(t("wcu_title"), rows)
    _hint(f"{t('wcu_hint')} · {_pub_short()}")


def webhook_extract():
    _panel(t("wex_title"), t("wex_desc"))
    raw = _ask(t("wh_prompt"))
    if not raw or not _valid_webhook_url(raw):
        _fail(t("wh_invalid"))
        return
    wid, wtoken = _parse_webhook(raw)
    _show_table(t("wex_title"), [
        ("ID", f"[bold]{wid}[/]"),
        ("Token", f"[dim]{wtoken}[/]"),
        (t("created"), _snowflake_ts(wid)),
        ("POST URL", _api_url(wid, wtoken)),
        ("discord.com", f"https://discord.com/api/webhooks/{wid}/{wtoken}"),
        ("discordapp.com", f"https://discordapp.com/api/webhooks/{wid}/{wtoken}"),
        ("Void-Tools", _pub_short()),
    ])


def webhook_create():
    _panel(t("wcr_title"), t("wcr_desc"))
    token = _ask(t("wcr_token"))
    if not token:
        _fail(t("wcr_no_token"))
        return
    if not token.lower().startswith("bot "):
        token = f"Bot {token}"
    channel = _ask(t("wcr_channel"))
    if not channel or not channel.isdigit():
        _fail(t("wcr_channel_invalid"))
        return
    name = _ask(t("wcr_name")) or f"Void-Tools · {_pub_tag()}"
    try:
        r = requests.post(
            f"https://discord.com/api/v9/channels/{channel}/webhooks",
            headers={"User-Agent": UA, "Authorization": token, "Content-Type": "application/json"},
            json={"name": name[:80]},
            timeout=12,
        )
        data = r.json() if r.text else {}
        if r.status_code not in (200, 201):
            _fail(f"{t('wcr_fail')} (HTTP {r.status_code})", str(data.get("message", data))[:120])
            return
        wh_url = data.get("url") or f"https://discord.com/api/webhooks/{data.get('id')}/{data.get('token')}"
        _show_table(t("wcr_title"), [
            ("ID", data.get("id", "?")),
            (t("name"), data.get("name", "?")),
            ("Channel", data.get("channel_id", channel)),
            ("URL", wh_url),
        ])
        _ok(t("wcr_title"), t("wcr_ok"))
    except requests.RequestException as ex:
        _fail(t("network"), str(ex))


TOOLS = {
    "webhook-info": webhook_info,
    "webhook-send": webhook_send,
    "webhook-spam": webhook_spam,
    "webhook-gif-spam": webhook_gif_spam,
    "webhook-embed": webhook_embed,
    "webhook-json": webhook_json,
    "webhook-file": webhook_file,
    "webhook-ghost": webhook_ghost,
    "webhook-edit-msg": webhook_edit_msg,
    "webhook-delete-msg": webhook_delete_msg,
    "webhook-edit": webhook_edit,
    "webhook-clone": webhook_clone,
    "webhook-extract": webhook_extract,
    "webhook-bulk": webhook_bulk,
    "webhook-library": webhook_library,
    "webhook-curl": webhook_curl,
    "webhook-create": webhook_create,
    "webhook-destroyer": webhook_destroyer,
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
        console.print(f"\n  [{C.C_DIM}]○ {t('cancelled')}[/]")
    except requests.RequestException as ex:
        _fail(t("network"), str(ex))
    except Exception as ex:
        _fail(type(ex).__name__, str(ex))
    _pause()

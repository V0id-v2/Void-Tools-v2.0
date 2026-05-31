#!/usr/bin/env python3
"""Void-Tools — Roblox free tools (core)."""
import sys, json, os, webbrowser, shutil
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
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

C_ROBLOX = "#E2231A"
C_OK = "#00FF88"
C_ERR = "#FF4444"
C_GOLD = "#FFD700"
C_DIM = "#888888"

L = {}


def set_language(strings: dict):
    global L
    L = strings


def t(key: str) -> str:
    return L.get(key, key)


def _tw():
    return max(52, min(70, shutil.get_terminal_size((80, 24)).columns - 4))


def _ask(prompt: str) -> str:
    return input(f"\033[38;2;226;35;26m  {prompt} \033[38;2;180;180;200m>>\033[0m ").strip()


def _pause():
    console.print()
    input(f"\033[38;2;100;100;120m  {t('pause')} \033[0m")


def _panel(title: str, desc: str):
    console.print()
    console.print(Panel(
        Align.center(Text.from_markup(f"[bold {C_GOLD}]{title}[/]\n[{C_DIM}]{desc}[/]")),
        border_style=C_ROBLOX, box=box.ROUNDED, padding=(1, 2), width=_tw(),
    ))


def _norm_cookie(raw: str) -> str:
    raw = raw.strip()
    if raw.lower().startswith(".roblosecurity="):
        raw = raw.split("=", 1)[1].strip()
    return raw


def _parse_json(raw: bytes):
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _as_dict(data):
    return data if isinstance(data, dict) else {}


def _rbx(method: str, url: str, cookie: str = None, body: dict = None, timeout: int = 12):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if cookie:
        headers["Cookie"] = f".ROBLOSECURITY={_norm_cookie(cookie)}"
    data = json.dumps(body).encode() if body is not None else None
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, _parse_json(r.read())
    except urllib.error.HTTPError as e:
        return e.code, _parse_json(e.read())
    except Exception as ex:
        return 0, {"error": str(ex)}


def _robux_val(code, data):
    if code != 200:
        return "?"
    d = _as_dict(data)
    return d.get("robux", "?")


def _count_val(code, data):
    if code != 200:
        return "?"
    d = _as_dict(data)
    return d.get("count", "?")


def _premium_val(code, data):
    if code != 200:
        return False
    if isinstance(data, bool):
        return data
    return bool(_as_dict(data).get("isPremium", False))


def _resolve_user(query: str):
    query = query.strip()
    if query.isdigit():
        code, data = _rbx("GET", f"https://users.roblox.com/v1/users/{query}")
        if code == 200:
            return _as_dict(data) or None
        return None
    code, data = _rbx("POST", "https://users.roblox.com/v1/usernames/users",
                      body={"usernames": [query], "excludeBannedUsers": False})
    data = _as_dict(data)
    if code == 200 and data.get("data"):
        u = data["data"][0]
        if u.get("id"):
            code2, full = _rbx("GET", f"https://users.roblox.com/v1/users/{u['id']}")
            full = _as_dict(full)
            if code2 == 200:
                full["displayName"] = u.get("displayName", full.get("name"))
                full["hasVerifiedBadge"] = u.get("hasVerifiedBadge", False)
                return full
    return None


def _auth_user(cookie: str):
    code, data = _rbx("GET", "https://users.roblox.com/v1/users/authenticated", cookie=cookie)
    data = _as_dict(data)
    if code == 200 and data.get("id"):
        return data
    return None


def _show_table(title: str, rows: list):
    tbl = Table(box=box.SIMPLE, border_style=C_ROBLOX, show_header=False, padding=(0, 1))
    tbl.add_column("K", style="dim", width=16, no_wrap=True)
    tbl.add_column("V", style="white", overflow="fold")
    for k, v in rows:
        tbl.add_row(k, str(v))
    console.print(Padding(Panel(
        tbl, title=f"[bold {C_GOLD}]{title}[/]", border_style=C_ROBLOX,
        box=box.ROUNDED, padding=(0, 1), width=_tw(),
    ), (1, 0)))


def _yn() -> bool:
    return input(f"\033[38;2;100;0;0m  {t('open_yn')} \033[0m").strip().lower() in ("y", "yes", "o", "oui")


def cookie_checker():
    _panel(t("cookie_title"), t("cookie_desc"))
    raw = _ask(t("cookie_prompt"))
    if not raw:
        return
    user = _auth_user(raw)
    if not user:
        console.print(f"\n  [bold {C_ERR}]{t('invalid_cookie')}[/]")
        return
    uid = user["id"]
    c_rbx, robux = _rbx("GET", f"https://economy.roblox.com/v1/users/{uid}/currency", cookie=raw)
    _show_table(t("cookie_ok"), [
        ("Status", f"[bold {C_OK}]VALID[/]"),
        ("User ID", uid),
        (t("username"), user.get("name", "?")),
        (t("display"), user.get("displayName", "?")),
        ("Robux", _robux_val(c_rbx, robux)),
    ])


def username_lookup():
    _panel(t("user_title"), t("user_desc"))
    q = _ask(t("user_prompt"))
    if not q:
        return
    u = _resolve_user(q)
    if not u:
        console.print(f"\n  [bold {C_ERR}]{t('user_not_found')}[/]")
        return
    uid = u["id"]
    c_fr, friends = _rbx("GET", f"https://friends.roblox.com/v1/users/{uid}/friends/count")
    _, presence = _rbx("POST", "https://presence.roblox.com/v1/presence/users",
                       body={"userIds": [uid]})
    pres = _as_dict(presence).get("userPresences", [{}])[0]
    ptype = pres.get("userPresenceType", 0)
    status = t("status_off"), t("status_on"), t("status_game"), t("status_studio")
    st = status[ptype] if 0 <= ptype < len(status) else str(ptype)
    _show_table(f"@{u.get('name', q)}", [
        ("User ID", uid),
        (t("display"), u.get("displayName", u.get("name", "?"))),
        (t("created"), (u.get("created") or "?")[:10]),
        (t("banned"), t("yes") if u.get("isBanned") else t("no")),
        (t("verified"), t("yes") if u.get("hasVerifiedBadge") else t("no")),
        (t("friends"), _count_val(c_fr, friends)),
        (t("status"), st),
        ("Profile", f"https://www.roblox.com/users/{uid}/profile"),
    ])
    if _yn():
        webbrowser.open(f"https://www.roblox.com/users/{uid}/profile")


def game_lookup():
    _panel(t("game_title"), t("game_desc"))
    pid = _ask(t("place_prompt"))
    if not pid or not pid.isdigit():
        console.print(f"\n  [bold {C_ERR}]{t('place_invalid')}[/]")
        return
    code, uni = _rbx("GET", f"https://apis.roblox.com/universes/v1/places/{pid}/universe")
    uni = _as_dict(uni)
    if code != 200 or not uni.get("universeId"):
        console.print(f"\n  [bold {C_ERR}]{t('game_not_found')}[/]")
        return
    uid = uni["universeId"]
    code, games = _rbx("GET", f"https://games.roblox.com/v1/games?universeIds={uid}")
    games = _as_dict(games)
    if code != 200 or not games.get("data"):
        console.print(f"\n  [bold {C_ERR}]{t('game_details_fail')}[/]")
        return
    g = games["data"][0]
    _show_table(g.get("name", "Game"), [
        ("Place ID", pid),
        ("Universe ID", uid),
        (t("playing"), g.get("playing", "?")),
        (t("visits"), g.get("visits", "?")),
        (t("max_players"), g.get("maxPlayers", "?")),
        (t("created"), (g.get("created") or "?")[:10]),
        ("Link", f"https://www.roblox.com/games/{pid}"),
    ])
    if _yn():
        webbrowser.open(f"https://www.roblox.com/games/{pid}")


def group_lookup():
    _panel(t("group_title"), t("group_desc"))
    gid = _ask(t("group_prompt"))
    if not gid or not gid.isdigit():
        console.print(f"\n  [bold {C_ERR}]{t('group_invalid')}[/]")
        return
    code, g = _rbx("GET", f"https://groups.roblox.com/v1/groups/{gid}")
    g = _as_dict(g)
    if code != 200:
        console.print(f"\n  [bold {C_ERR}]{t('group_not_found')}[/]")
        return
    _show_table(g.get("name", "Group"), [
        ("Group ID", gid),
        (t("owner_id"), g.get("owner", {}).get("userId", "?")),
        (t("members"), g.get("memberCount", "?")),
        (t("public"), t("yes") if g.get("publicEntryAllowed") else t("no")),
        (t("description"), (g.get("description") or "—")[:80]),
        ("Link", f"https://www.roblox.com/groups/{gid}"),
    ])
    if _yn():
        webbrowser.open(f"https://www.roblox.com/groups/{gid}")


def avatar_viewer():
    _panel(t("avatar_title"), t("avatar_desc"))
    q = _ask(t("user_prompt"))
    if not q:
        return
    u = _resolve_user(q)
    if not u:
        console.print(f"\n  [bold {C_ERR}]{t('user_not_found')}[/]")
        return
    uid = u["id"]
    code, av = _rbx("GET", f"https://avatar.roblox.com/v1/users/{uid}/avatar")
    code2, thumb = _rbx("GET",
        f"https://thumbnails.roblox.com/v1/users/avatar?userIds={uid}&size=420x420&format=Png")
    av = _as_dict(av)
    thumb = _as_dict(thumb)
    img = ""
    if code2 == 200 and thumb.get("data"):
        img = thumb["data"][0].get("imageUrl", "")
    assets = av.get("assets", []) if code == 200 else []
    _show_table(f"Avatar — {u.get('name', q)}", [
        ("User ID", uid),
        (t("assets"), len(assets)),
        ("Image URL", img or "—"),
    ])
    if assets:
        tbl = Table(box=box.SIMPLE, border_style="red", show_header=True)
        tbl.add_column("Asset ID", style="white")
        tbl.add_column(t("name"), style="dim")
        for a in assets[:20]:
            aid = a.get("id", "?")
            c3, det = _rbx("GET", f"https://economy.roblox.com/v2/assets/{aid}/details")
            det = _as_dict(det)
            name = det.get("Name", "?") if c3 == 200 else "?"
            tbl.add_row(str(aid), name)
        console.print(Padding(Panel(tbl, title=f"[bold]{t('equipped')}[/]", border_style="red"), (1, 0)))
    if img and _yn():
        webbrowser.open(img)


def robux_checker():
    _panel(t("robux_title"), t("robux_desc"))
    raw = _ask(t("cookie_prompt"))
    if not raw:
        return
    user = _auth_user(raw)
    if not user:
        console.print(f"\n  [bold {C_ERR}]{t('invalid_cookie')}[/]")
        return
    uid = user["id"]
    code, cur = _rbx("GET", f"https://economy.roblox.com/v1/users/{uid}/currency", cookie=raw)
    if code != 200:
        console.print(f"\n  [bold {C_ERR}]{t('robux_fail')} (HTTP {code})[/]")
        return
    _show_table("Robux", [
        (t("username"), user.get("name", "?")),
        ("User ID", uid),
        ("Robux", f"[bold {C_GOLD}]{_robux_val(code, cur)}[/]"),
    ])


def account_checker():
    _panel(t("account_title"), t("account_desc"))
    raw = _ask(t("cookie_prompt"))
    if not raw:
        return
    user = _auth_user(raw)
    if not user:
        console.print(f"\n  [bold {C_ERR}]{t('invalid_cookie')}[/]")
        return
    uid = user["id"]
    c_cur, cur = _rbx("GET", f"https://economy.roblox.com/v1/users/{uid}/currency", cookie=raw)
    c_prem, prem = _rbx("GET", f"https://premiumfeatures.roblox.com/v1/users/{uid}/validate-membership", cookie=raw)
    c_fr, friends = _rbx("GET", f"https://friends.roblox.com/v1/users/{uid}/friends/count", cookie=raw)
    c_prof, profile = _rbx("GET", f"https://users.roblox.com/v1/users/{uid}")
    profile = _as_dict(profile)
    _show_table(t("account_result"), [
        ("Status", f"[bold {C_OK}]VALID[/]"),
        (t("username"), user.get("name", "?")),
        (t("display"), user.get("displayName", "?")),
        ("User ID", uid),
        ("Robux", _robux_val(c_cur, cur)),
        ("Premium", t("yes") if _premium_val(c_prem, prem) else t("no")),
        (t("friends"), _count_val(c_fr, friends)),
        (t("created"), (profile.get("created") or "?")[:10]),
        (t("banned"), t("yes") if profile.get("isBanned") else t("no")),
    ])


def profile_viewer():
    _panel(t("profile_title"), t("profile_desc"))
    q = _ask(t("user_prompt"))
    if not q:
        return
    u = _resolve_user(q)
    if not u:
        console.print(f"\n  [bold {C_ERR}]{t('user_not_found')}[/]")
        return
    uid = u["id"]
    c_fr, friends = _rbx("GET", f"https://friends.roblox.com/v1/users/{uid}/friends/count")
    c_fo, followers = _rbx("GET", f"https://friends.roblox.com/v1/users/{uid}/followers/count")
    c_fi, following = _rbx("GET", f"https://friends.roblox.com/v1/users/{uid}/followings/count")
    _, presence = _rbx("POST", "https://presence.roblox.com/v1/presence/users",
                        body={"userIds": [uid]})
    pres = _as_dict(presence).get("userPresences", [{}])[0]
    ptype = pres.get("userPresenceType", 0)
    status = (t("status_off"), t("status_on"), t("status_game"), t("status_studio"))
    st = status[ptype] if 0 <= ptype < len(status) else "?"
    _show_table(f"Profile — {u.get('name')}", [
        ("User ID", uid),
        (t("display"), u.get("displayName", "?")),
        (t("description"), ((u.get("description") or "—")[:100])),
        (t("created"), (u.get("created") or "?")[:10]),
        (t("friends"), _count_val(c_fr, friends)),
        (t("followers"), _count_val(c_fo, followers)),
        (t("following"), _count_val(c_fi, following)),
        (t("status"), st),
        (t("in_game"), pres.get("lastLocation") or "—"),
        ("URL", f"https://www.roblox.com/users/{uid}/profile"),
    ])


def item_lookup():
    _panel(t("item_title"), t("item_desc"))
    aid = _ask(t("item_prompt"))
    if not aid or not aid.isdigit():
        console.print(f"\n  [bold {C_ERR}]{t('item_invalid')}[/]")
        return
    code, d = _rbx("GET", f"https://economy.roblox.com/v2/assets/{aid}/details")
    d = _as_dict(d)
    if code != 200:
        console.print(f"\n  [bold {C_ERR}]{t('item_not_found')} (HTTP {code})[/]")
        return
    _show_table(d.get("Name", "Item"), [
        ("Asset ID", aid),
        (t("creator"), d.get("Creator", {}).get("Name", "?")),
        (t("price"), d.get("PriceInRobux") or d.get("OriginalPrice") or t("off_sale")),
        ("Limited", t("yes") if d.get("IsLimited") or d.get("IsLimitedUnique") else t("no")),
        (t("sales"), d.get("Sales", "?")),
        (t("created"), (d.get("Created") or "?")[:10]),
        ("Link", f"https://www.roblox.com/catalog/{aid}"),
    ])


def badge_checker():
    _panel(t("badge_title"), t("badge_desc"))
    raw = _ask(t("cookie_prompt"))
    if not raw:
        return
    user = _auth_user(raw)
    if not user:
        console.print(f"\n  [bold {C_ERR}]{t('invalid_cookie')}[/]")
        return
    uid = _ask(t("uid_prompt").format(user["id"])) or str(user["id"])
    if not uid.isdigit():
        console.print(f"\n  [bold {C_ERR}]{t('uid_invalid')}[/]")
        return
    code, data = _rbx("GET", f"https://badges.roblox.com/v1/users/{uid}/badges?limit=50&sortOrder=Asc", cookie=raw)
    data = _as_dict(data)
    if code != 200:
        console.print(f"\n  [bold {C_ERR}]{t('badge_fail')} (HTTP {code})[/]")
        return
    badges = data.get("data", [])
    if not badges:
        console.print(f"\n  [{C_DIM}]{t('badge_empty')}[/]")
        return
    tbl = Table(box=box.SIMPLE, border_style="red")
    tbl.add_column("#", style="dim", width=4)
    tbl.add_column("Badge", style="white")
    tbl.add_column("Game", style="dim")
    for i, b in enumerate(badges[:30], 1):
        tbl.add_row(str(i), b.get("name", "?"), str(b.get("awarder", {}).get("name", "?")))
    console.print(Padding(Panel(tbl, title=f"[bold {C_GOLD}]{len(badges)} badge(s)[/]", border_style="red"), (1, 0)))


def inventory_view():
    _panel(t("inv_title"), t("inv_desc"))
    raw = _ask(t("cookie_prompt"))
    if not raw:
        return
    user = _auth_user(raw)
    if not user:
        console.print(f"\n  [bold {C_ERR}]{t('invalid_cookie')}[/]")
        return
    uid = _ask(t("uid_prompt").format(user["id"])) or str(user["id"])
    if not uid.isdigit():
        console.print(f"\n  [bold {C_ERR}]{t('uid_invalid')}[/]")
        return
    code, data = _rbx("GET",
        f"https://inventory.roblox.com/v1/users/{uid}/assets/collectibles?limit=50&sortOrder=Asc",
        cookie=raw)
    data = _as_dict(data)
    if code != 200:
        console.print(f"\n  [bold {C_ERR}]{t('inv_fail')} (HTTP {code})[/]")
        return
    items = data.get("data", [])
    if not items:
        console.print(f"\n  [{C_DIM}]{t('inv_empty')}[/]")
        return
    tbl = Table(box=box.SIMPLE, border_style="red")
    tbl.add_column(t("name"), style="white")
    tbl.add_column("Asset ID", style="dim")
    tbl.add_column("UAID", style="dim")
    for it in items[:40]:
        tbl.add_row(it.get("name", "?"), str(it.get("assetId", "?")), str(it.get("userAssetId", "?")))
    console.print(Padding(Panel(tbl, title=f"[bold {C_GOLD}]{len(items)} collectible(s)[/]", border_style="red"), (1, 0)))


def game_favorites():
    _panel(t("fav_title"), t("fav_desc"))
    pid = _ask(t("place_prompt"))
    if not pid or not pid.isdigit():
        console.print(f"\n  [bold {C_ERR}]{t('place_invalid')}[/]")
        return
    code, uni = _rbx("GET", f"https://apis.roblox.com/universes/v1/places/{pid}/universe")
    uni = _as_dict(uni)
    if code != 200 or not uni.get("universeId"):
        console.print(f"\n  [bold {C_ERR}]{t('game_not_found')}[/]")
        return
    uid = uni["universeId"]
    code, games = _rbx("GET", f"https://games.roblox.com/v1/games?universeIds={uid}")
    games = _as_dict(games)
    if code != 200 or not games.get("data"):
        return
    g = games["data"][0]
    _show_table(g.get("name", "Game"), [
        ("Place ID", pid),
        (t("favorites"), g.get("favoritedCount", "?")),
        (t("playing"), g.get("playing", "?")),
        (t("visits"), g.get("visits", "?")),
        ("Upvotes", g.get("upVotes", "?")),
        ("Downvotes", g.get("downVotes", "?")),
    ])


def group_roles():
    _panel(t("roles_title"), t("roles_desc"))
    gid = _ask(t("group_prompt"))
    if not gid or not gid.isdigit():
        console.print(f"\n  [bold {C_ERR}]{t('group_invalid')}[/]")
        return
    code, data = _rbx("GET", f"https://groups.roblox.com/v1/groups/{gid}/roles")
    data = _as_dict(data)
    if code != 200:
        console.print(f"\n  [bold {C_ERR}]{t('group_not_found')}[/]")
        return
    roles = data.get("roles", [])
    tbl = Table(box=box.SIMPLE, border_style="red")
    tbl.add_column("ID", style="dim")
    tbl.add_column(t("name"), style="white")
    tbl.add_column(t("members"), style="dim")
    for r in roles[:25]:
        tbl.add_row(str(r.get("id", "?")), r.get("name", "?"), str(r.get("memberCount", "?")))
    console.print(Padding(Panel(tbl, title=f"[bold {C_GOLD}]{len(roles)} role(s)[/]", border_style="red"), (1, 0)))


def limited_price():
    _panel(t("limited_title"), t("limited_desc"))
    aid = _ask(t("item_prompt"))
    if not aid or not aid.isdigit():
        console.print(f"\n  [bold {C_ERR}]{t('item_invalid')}[/]")
        return
    c1, det = _rbx("GET", f"https://economy.roblox.com/v2/assets/{aid}/details")
    det = _as_dict(det)
    c2, resale = _rbx("GET", f"https://economy.roblox.com/v1/assets/{aid}/resale-data")
    resale = _as_dict(resale)
    if c1 != 200:
        console.print(f"\n  [bold {C_ERR}]{t('item_not_found')}[/]")
        return
    _show_table(det.get("Name", "Limited"), [
        ("Asset ID", aid),
        ("Limited", t("yes") if det.get("IsLimited") or det.get("IsLimitedUnique") else t("no")),
        (t("price"), det.get("PriceInRobux") or det.get("OriginalPrice") or t("off_sale")),
        (t("rap"), resale.get("recentAveragePrice", "?") if c2 == 200 else "?"),
        (t("stock"), resale.get("numberRemaining", "?") if c2 == 200 else "?"),
        (t("sales"), resale.get("sales", det.get("Sales", "?"))),
    ])


def friends_list():
    _panel(t("friends_title"), t("friends_desc"))
    raw = _ask(t("cookie_prompt"))
    if not raw:
        return
    user = _auth_user(raw)
    if not user:
        console.print(f"\n  [bold {C_ERR}]{t('invalid_cookie')}[/]")
        return
    uid = str(user["id"])
    code, data = _rbx("GET", f"https://friends.roblox.com/v1/users/{uid}/friends?userSort=StatusFrequents", cookie=raw)
    data = _as_dict(data)
    friends = data.get("data", [])
    if not friends:
        console.print(f"\n  [{C_DIM}]{t('friends_empty')}[/]")
        return
    tbl = Table(box=box.SIMPLE, border_style=C_ROBLOX)
    tbl.add_column("#", width=4)
    tbl.add_column("User", style="white")
    tbl.add_column("ID", style="dim")
    for i, f in enumerate(friends[:40], 1):
        tbl.add_row(str(i), f.get("name", "?"), str(f.get("id", "?")))
    console.print(Padding(Panel(tbl, title=f"[bold {C_GOLD}]{len(friends)} friends[/]", border_style=C_ROBLOX, width=_tw()), (1, 0)))


def followers_count():
    _panel(t("follow_title"), t("follow_desc"))
    uid = _ask(t("uid_only"))
    if not uid or not uid.isdigit():
        console.print(f"\n  [bold {C_ERR}]{t('uid_invalid')}[/]")
        return
    c1, f = _rbx("GET", f"https://friends.roblox.com/v1/users/{uid}/followers/count")
    c2, g = _rbx("GET", f"https://friends.roblox.com/v1/users/{uid}/followings/count")
    _show_table(f"User {uid}", [
        (t("followers"), _count_val(c1, f)),
        (t("following"), _count_val(c2, g)),
    ])


def account_age():
    _panel(t("age_title"), t("age_desc"))
    uid = _ask(t("uid_only"))
    if not uid or not uid.isdigit():
        return
    code, u = _rbx("GET", f"https://users.roblox.com/v1/users/{uid}")
    u = _as_dict(u)
    if code != 200:
        console.print(f"\n  [bold {C_ERR}]{t('user_not_found')}[/]")
        return
    created = (u.get("created") or "?")[:10]
    _show_table(u.get("name", "User"), [
        ("ID", uid),
        (t("created"), created),
        (t("display"), u.get("displayName", "?")),
        ("Profile", f"https://roblox.com/users/{uid}/profile"),
    ])


def gamepass_lookup():
    _panel(t("gp_title"), t("gp_desc"))
    gpid = _ask(t("gamepass_id"))
    if not gpid or not gpid.isdigit():
        return
    code, d = _rbx("GET", f"https://apis.roblox.com/game-passes/v1/game-passes/{gpid}/product-info")
    d = _as_dict(d)
    if code != 200:
        console.print(f"\n  [bold {C_ERR}]{t('not_found')}[/]")
        return
    _show_table(d.get("Name", "GamePass"), [
        ("ID", gpid),
        (t("price"), d.get("PriceInRobux", "?")),
        ("Enabled", t("yes") if d.get("IsForSale") else t("no")),
    ])


def place_universe():
    _panel(t("place_title"), t("place_desc"))
    pid = _ask(t("place_id"))
    if not pid or not pid.isdigit():
        return
    code, d = _rbx("GET", f"https://apis.roblox.com/universes/v1/places/{pid}/universe")
    d = _as_dict(d)
    _show_table("Place → Universe", [
        ("Place ID", pid),
        ("Universe ID", d.get("universeId", "?")),
        ("HTTP", code),
    ])


def catalog_search():
    _panel(t("cat_title"), t("cat_desc"))
    q = _ask(t("search_q"))
    if not q:
        return
    import urllib.parse
    url = f"https://catalog.roblox.com/v1/search/items?category=All&keyword={urllib.parse.quote(q)}&limit=10"
    code, d = _rbx("GET", url)
    d = _as_dict(d)
    items = d.get("data", [])
    tbl = Table(box=box.SIMPLE, border_style=C_ROBLOX)
    tbl.add_column("Name")
    tbl.add_column("ID", style="dim")
    for it in items[:10]:
        tbl.add_row(it.get("name", "?"), str(it.get("id", "?")))
    console.print(Padding(Panel(tbl, title=q, border_style=C_ROBLOX, width=_tw()), (1, 0)))


def multi_cookie_check():
    _panel(t("multi_title"), t("multi_desc"))
    console.print(f"  [{C_DIM}]{t('multi_hint')}[/]")
    lines = []
    while True:
        line = input().strip()
        if not line:
            break
        lines.append(line)
    tbl = Table(box=box.SIMPLE, border_style=C_ROBLOX)
    tbl.add_column("#", width=4)
    tbl.add_column("Status")
    tbl.add_column("User")
    for i, ck in enumerate(lines, 1):
        u = _auth_user(ck)
        if u:
            tbl.add_row(str(i), f"[{C_OK}]OK[/]", u.get("name", "?"))
        else:
            tbl.add_row(str(i), f"[{C_ERR}]FAIL[/]", "—")
    console.print(Padding(Panel(tbl, border_style=C_ROBLOX, width=_tw()), (1, 0)))


def export_profile():
    _panel(t("export_title"), t("export_desc"))
    uid = _ask(t("uid_only"))
    if not uid or not uid.isdigit():
        return
    code, u = _rbx("GET", f"https://users.roblox.com/v1/users/{uid}")
    u = _as_dict(u)
    if code != 200:
        return
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "exports")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"roblox_{uid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(u, f, indent=2)
    console.print(f"\n  [{C_OK}]{path}[/]")


def avatar_batch():
    _panel(t("batch_title"), t("batch_desc"))
    raw = _ask(t("uids_csv"))
    uids = [x.strip() for x in raw.replace(",", " ").split() if x.strip().isdigit()]
    tbl = Table(box=box.SIMPLE, border_style=C_ROBLOX)
    tbl.add_column("ID")
    tbl.add_column("Avatar URL")
    for uid in uids[:20]:
        code, d = _rbx("GET", f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={uid}&size=150x150&format=Png")
        d = _as_dict(d)
        url = d.get("data", [{}])[0].get("imageUrl", "—") if code == 200 else "—"
        tbl.add_row(uid, url)
    console.print(Padding(Panel(tbl, border_style=C_ROBLOX, width=_tw()), (1, 0)))


def group_funds():
    _panel(t("gfunds_title"), t("gfunds_desc"))
    gid = _ask(t("group_id"))
    raw = _ask(t("cookie_prompt"))
    if not gid or not gid.isdigit() or not raw:
        return
    code, d = _rbx("GET", f"https://economy.roblox.com/v1/groups/{gid}/currency", cookie=raw)
    d = _as_dict(d)
    robux = d.get("robux", "?") if code == 200 else f"HTTP {code}"
    _show_table(f"Group {gid}", [(t("robux"), robux), ("Note", t("gfunds_note"))])


TOOLS = {
    "cookie-checker": cookie_checker,
    "username-lookup": username_lookup,
    "game-lookup": game_lookup,
    "group-lookup": group_lookup,
    "avatar-viewer": avatar_viewer,
    "robux-checker": robux_checker,
    "account-checker": account_checker,
    "profile-viewer": profile_viewer,
    "item-lookup": item_lookup,
    "badge-checker": badge_checker,
    "inventory-view": inventory_view,
    "game-favorites": game_favorites,
    "group-roles": group_roles,
    "limited-price": limited_price,
    "friends-list": friends_list,
    "followers-count": followers_count,
    "account-age": account_age,
    "gamepass-lookup": gamepass_lookup,
    "place-universe": place_universe,
    "catalog-search": catalog_search,
    "multi-cookie": multi_cookie_check,
    "export-profile": export_profile,
    "avatar-batch": avatar_batch,
    "group-funds": group_funds,
}


def _fail(title: str, message: str, detail: str = None):
    body = Text.from_markup(f"[bold {C_ERR}]{message}[/]")
    if detail:
        body.append("\n")
        body.append(Text.from_markup(f"[{C_DIM}]{detail}[/]"))
    console.print(Panel(
        body, title=f"[bold white]✖ {title}[/]",
        border_style=C_ERR, box=box.ROUNDED, padding=(1, 2), width=_tw(),
    ))


def run_tool(tool_key: str):
    os.system("cls" if os.name == "nt" else "clear")
    fn = TOOLS.get(tool_key)
    if not fn:
        _fail(t("unknown_tool"), tool_key)
        _pause()
        return
    try:
        fn()
    except KeyboardInterrupt:
        console.print(f"\n  [{C_DIM}]{t('cancelled')}[/]")
    except urllib.error.URLError as ex:
        _fail(t("error"), t("network"), str(ex.reason))
    except Exception as ex:
        _fail(t("error"), type(ex).__name__, str(ex))
    _pause()

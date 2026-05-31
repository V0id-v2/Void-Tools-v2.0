"""Built-in dashboard tools."""
import os, sys, time, json, random, string, webbrowser
import urllib.request, urllib.error

from . import constants as C
from .void_common import (
    ansi_hex as _ansi, console, error_box as _error_box, open_premium_links,
    panel as _panel, pause as _pause, success_box as _success_box,
)
from .runner import run, run_nuker
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.padding import Padding
from rich import box

sp = C.sp
_VOID_DIR = C.VOID_DIR
VERSION = C.VERSION
GITHUB = C.GITHUB
DISCORD = C.DISCORD
CHANGELOG = C.CHANGELOG
C_BLOOD = C.C_BLOOD
C_MID = C.C_MID
C_NEON = C.C_NEON
C_WHITE = C.C_WHITE
C_SILVER = C.C_SILVER
C_DIM = C.C_DIM
C_GOLD = C.C_GOLD
C_GOLD2 = C.C_GOLD2


def star():
    import time
    _panel("PREMIUM ONLY", "Fonction réservée aux membres VOID PREMIUM.")
    console.print(Panel(
        Text.from_markup(
            f"[{C_SILVER}]Shop · Discord\n"
            f"[{C_GOLD2}]{C.SHOP}[/]\n"
            f"[{C_GOLD2}]{C.DISCORD}[/]"
        ), border_style=C_GOLD, box=box.ROUNDED, padding=(1, 2)))
    open_premium_links()
    time.sleep(1.5)


def tool_vpn_detector():
    import urllib.request, json
    _panel("VPN DETECTOR", "Détecte VPN · Proxy · Tor sur une IP")
    ip = input(f"{_ansi(C_MID)}  IP address >> \033[0m").strip()
    if not ip: return
    console.print(Text.from_markup(f"[{C_NEON} bold] ┌── VPN Check : {ip}"))
    
    try:
        url = f"https://proxycheck.io/v2/{ip}?vpn=1&asn=1"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            if data.get("status") != "ok":
                console.print(f"[{C_NEON} bold]  [!] Error: {data.get('message', 'Unknown error')}")
                return
            
            res = data.get(ip, {})
            is_proxy = res.get("proxy", "no") == "yes"
            p_color = C_NEON if is_proxy else "#00FF00"
            
            table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C_BLOOD, show_header=False)
            table.add_row(f"[{C_SILVER}]IP Address", f"[{C_WHITE}]{ip}")
            table.add_row(f"[{C_SILVER}]Proxy/VPN", f"[{p_color} bold]{res.get('proxy', 'no').upper()}")
            table.add_row(f"[{C_SILVER}]Type", f"[{C_WHITE}]{res.get('type', 'N/A')}")
            table.add_row(f"[{C_SILVER}]Provider", f"[{C_WHITE}]{res.get('provider', 'N/A')}")
            table.add_row(f"[{C_SILVER}]ASN", f"[{C_WHITE}]{res.get('asn', 'N/A')}")
            table.add_row(f"[{C_SILVER}]Country", f"[{C_WHITE}]{res.get('country', 'N/A')} ({res.get('isocode', '??')})")
            
            console.print(Padding(Panel(table, title=f"[{C_GOLD} bold]Results[/]", border_style=C_BLOOD), (1, 2)))
            
    except Exception as e:
        console.print(f"[{C_NEON} bold]  [!] Network Error: {e}")
    
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def tool_rar_premium():
    _panel("RAR CRACKER [PREMIUM]", "Option réservée aux membres Premium.")
    console.print(f"\n[{C_GOLD} bold]  * ACCÈS VIP REQUIS\n[{C_WHITE}]  Shop · Discord\n[{C_GOLD2}]{C.SHOP}[/]\n[{C_GOLD2}]{C.DISCORD}[/]")
    open_premium_links()
    console.print(); input(f"\033[38;2;136;0;0m  press enter to return...\033[0m")

def tool_username_hunter():
    _panel("USERNAME HUNTER", "Cherche un pseudo sur 12 plateformes")
    u = input(f"{_ansi(C_MID)}  username >> \033[0m").strip()
    if not u: return
    console.print(Text.from_markup(f"[{C_NEON} bold] ┌── Results for : {u}"))
    _open_links([
        ("GitHub",    f"https://github.com/{u}"),
        ("Twitter/X", f"https://x.com/{u}"),
        ("Instagram", f"https://instagram.com/{u}"),
        ("TikTok",    f"https://tiktok.com/@{u}"),
        ("Reddit",    f"https://reddit.com/u/{u}"),
        ("Twitch",    f"https://twitch.tv/{u}"),
        ("YouTube",   f"https://youtube.com/@{u}"),
        ("Steam",     f"https://steamcommunity.com/id/{u}"),
        ("Snapchat",  f"https://snapchat.com/add/{u}"),
        ("Pinterest", f"https://pinterest.com/{u}"),
        ("Medium",    f"https://medium.com/@{u}"),
        ("Telegram",  f"https://t.me/{u}"),
    ])

def tool_domain_intel():
    _panel("DOMAIN INTEL", "WHOIS · DNS · SSL · Shodan · VirusTotal")
    d = input(f"{_ansi(C_MID)}  domain (ex: google.com) >> \033[0m").strip()
    if not d: return
    console.print(Text.from_markup(f"[{C_NEON} bold] ┌── Intel for : {d}"))
    _open_links([
        ("WHOIS",       f"https://who.is/whois/{d}"),
        ("DNS Lookup",  f"https://dnschecker.org/#A/{d}"),
        ("Subdomains",  f"https://subdomainfinder.c99.nl/?domain={d}"),
        ("SSL Cert",    f"https://crt.sh/?q={d}"),
        ("VirusTotal",  f"https://virustotal.com/gui/domain/{d}"),
        ("Shodan",      f"https://shodan.io/search?query=hostname%3A{d}"),
        ("URLScan",     f"https://urlscan.io/search/#domain%3A{d}"),
    ])

def tool_social_scraper():
    _panel("SOCIAL SCRAPER", "Outils de scraping de profils publics")
    console.print(Text.from_markup(f"[{C_NEON} bold] ┌── Social Scraper Tools"))
    _open_links([
        ("Instagram",    "https://imginn.com/"),
        ("TikTok",       "https://exolyt.com/"),
        ("Facebook ID",  "https://lookup-id.com/"),
        ("LinkedIn",     "https://osint.support/"),
        ("Social Search","https://socialsearcher.com/"),
        ("Sherlock",     "https://sherlock-project.github.io/"),
    ])

def tool_sms_bomber():
    _panel("SMS BOMBER", "Plateformes de flood SMS (web)")
    console.print(Text.from_markup(f"[{C_NEON} bold] ┌── SMS Services"))
    _open_links([
        ("SMS24",        "https://sms24.me/"),
        ("SMSPool",      "https://smspool.net/"),
        ("TextBelt",     "https://textbelt.com/"),
        ("Receive-SMS",  "https://receive-sms.com/"),
        ("SMS Receive",  "https://smsreceivefree.com/"),
    ])

def tool_token_checker():
    import urllib.request, json
    _panel("TOKEN CHECKER", "Vérifie la validité d'un token Discord")
    token = input(f"{_ansi(C_MID)}  Discord token >> \033[0m").strip()
    if not token: return
    try:
        req = urllib.request.Request(
            "https://discord.com/api/v9/users/@me",
            headers={"Authorization": token}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read())
        console.print(Panel(
            Text.from_markup(
                f"[{C_GOLD} bold]* TOKEN VALID *\n\n"
                f"[{C_SILVER}]User   : [{C_WHITE} bold]{d.get('username','?')}#{d.get('discriminator','0')}\n"
                f"[{C_SILVER}]ID     : [{C_WHITE}]{d.get('id','?')}\n"
                f"[{C_SILVER}]Email  : [{C_WHITE}]{d.get('email','hidden')}\n"
                f"[{C_SILVER}]Nitro  : [{C_WHITE}]{'Yes' if d.get('premium_type') else 'No'}\n"
                f"[{C_SILVER}]Phone  : [{C_WHITE}]{'Yes' if d.get('phone') else 'No'}"
            ),
            border_style=C_GOLD, box=box.DOUBLE_EDGE, padding=(0, 3)
        ))
    except Exception:
        console.print(f"\n[{C_NEON} bold]  [!] INVALID TOKEN or network error")
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def _check_discord_token(token):
    import urllib.request, urllib.error
    token = token.strip()
    if not token:
        return False, None
    try:
        req = urllib.request.Request(
            "https://discord.com/api/v9/users/@me",
            headers={"Authorization": token, "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            return True, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return False, {"status": e.code}
    except Exception as ex:
        return False, {"error": str(ex)}

def _discord_user_tag(d):
    user = d.get("username", "?")
    disc = d.get("discriminator", "0")
    if disc and disc != "0":
        return f"{user}#{disc}"
    return user

def tool_token_checker_pro():
    _panel("TOKEN CHECKER PRO", "Vérifie plusieurs tokens Discord en masse")
    console.print(Text.from_markup(
        f"[{C_SILVER}]Colle tes tokens (1 par ligne), puis une ligne vide.\n"
        f"Ou entre [bold]file[/] + chemin vers un .txt[/]"
    ))
    lines, raw = [], input(f"{_ansi(C_MID)}  >> \033[0m").strip()
    if raw.lower() == "file":
        fp = input(f"{_ansi(C_MID)}  fichier .txt >> \033[0m").strip().strip('"')
        if not fp or not os.path.isfile(fp):
            console.print(f"[{C_NEON} bold]  [!] fichier introuvable")
            time.sleep(2)
            return
        with open(fp, encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]
    else:
        if raw:
            lines.append(raw)
        while True:
            line = input().strip()
            if not line:
                break
            lines.append(line)
    tokens = list(dict.fromkeys(t for t in lines if t))
    if not tokens:
        console.print(f"[{C_NEON} bold]  [!] aucun token")
        time.sleep(2)
        return

    console.print(Text.from_markup(f"\n[{C_NEON} bold] ┌── {len(tokens)} token(s) en cours...\n"))
    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C_BLOOD, show_header=True)
    table.add_column("#", style=C_DIM, width=4)
    table.add_column("Status", width=10)
    table.add_column("User", style=C_WHITE)
    table.add_column("ID", style=C_SILVER)
    table.add_column("Nitro", width=6)
    table.add_column("Phone", width=6)
    table.add_column("Token", style=C_DIM, max_width=28)

    valid, invalid = [], []
    for i, tok in enumerate(tokens, 1):
        ok, data = _check_discord_token(tok)
        mask = tok[:18] + "..." if len(tok) > 21 else tok
        if ok and data:
            tag = _discord_user_tag(data)
            nitro = "Yes" if data.get("premium_type") else "No"
            phone = "Yes" if data.get("phone") else "No"
            table.add_row(str(i), f"[#00FF00 bold]VALID[/]", tag, str(data.get("id", "?")), nitro, phone, mask)
            valid.append({"token": tok, "user": tag, "id": data.get("id"), "data": data})
        else:
            err = data.get("status", "?") if isinstance(data, dict) else "err"
            table.add_row(str(i), f"[{C_NEON} bold]INVALID[/]", "-", "-", "-", "-", f"{mask} ({err})")
            invalid.append(tok)
        time.sleep(0.35)

    console.print(Padding(Panel(table, title=f"[{C_GOLD} bold]Results[/]", border_style=C_BLOOD), (1, 1)))
    console.print(Text.from_markup(
        f"\n[{C_SILVER}]valid   [{C_GOLD} bold]{len(valid)}[/]   "
        f"invalid [{C_NEON} bold]{len(invalid)}[/]   total {len(tokens)}"
    ))
    if valid:
        save = input(f"\n{_ansi(C_MID)}  sauvegarder les valides ? (yes/no) >> \033[0m").strip().lower()
        if save == "yes":
            out = os.path.join(_VOID_DIR, "data", "tokens-valid.txt")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                for v in valid:
                    f.write(f"{v['token']}  |  {v['user']}  |  {v['id']}\n")
            console.print(f"[{C_GOLD} bold]  * saved  {out}")
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def _check_username_available(username):
    import urllib.request, urllib.error
    payload = json.dumps({"username": username}).encode()
    try:
        req = urllib.request.Request(
            "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            body = json.loads(r.read())
            if body.get("taken") is True:
                return False, "taken"
            if body.get("taken") is False:
                return True, "available"
            return None, str(body)[:80]
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode(errors="ignore"))
            msg = str(body).lower()
            if "taken" in msg or body.get("code") == 50035:
                return False, "taken"
        except Exception:
            pass
        return None, f"http {e.code}"
    except Exception as ex:
        return None, str(ex)

def tool_username_sniper():
    _panel("USERNAME SNIPER", "Check dispo pseudo · bulk · mode snipe")
    console.print(Text.from_markup(
        f"[{C_SILVER}][1][/] 1 pseudo   [{C_SILVER}][2][/] liste bulk   [{C_SILVER}][3][/] snipe (watch)"
    ))
    mode = input(f"{_ansi(C_MID)}  mode >> \033[0m").strip() or "1"

    if mode == "3":
        name = input(f"{_ansi(C_MID)}  pseudo cible >> \033[0m").strip()
        if not name:
            return
        try:
            interval = float(input(f"{_ansi(C_MID)}  intervalle sec (default 5) >> \033[0m").strip() or "5")
        except ValueError:
            interval = 5.0
        console.print(Text.from_markup(f"\n[{C_NEON} bold] snipe actif  |  @{name}  |  ctrl+c stop\n"))
        n = 0
        try:
            while True:
                n += 1
                ok, status = _check_username_available(name)
                ts = time.strftime("%H:%M:%S")
                if ok is True:
                    console.print(f"[{C_GOLD} bold]  [{ts}]  DISPONIBLE  >>  @{name}  (claim now!)")
                    if os.name == "nt":
                        import winsound
                        winsound.Beep(880, 400)
                    break
                if ok is False:
                    console.print(f"  [{ts}]  #{n}  taken  @{name}", style=C_DIM)
                else:
                    console.print(f"  [{ts}]  #{n}  ?  {status}", style=C_DIM)
                time.sleep(max(1.0, interval))
        except KeyboardInterrupt:
            console.print(f"\n[{C_SILVER}]  snipe stopped")
        console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")
        return

    names = []
    if mode == "2":
        console.print(Text.from_markup(f"[{C_SILVER}]1 pseudo/ligne, ligne vide pour finir[/]"))
        while True:
            line = input().strip()
            if not line:
                break
            names.extend(x.strip() for x in line.replace(",", " ").split() if x.strip())
    else:
        u = input(f"{_ansi(C_MID)}  username >> \033[0m").strip()
        if u:
            names = [u]
    names = list(dict.fromkeys(names))
    if not names:
        console.print(f"[{C_NEON} bold]  [!] aucun pseudo")
        time.sleep(2)
        return

    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C_BLOOD)
    table.add_column("Username", style=C_WHITE)
    table.add_column("Status", width=14)
    table.add_column("Info", style=C_SILVER)
    avail = 0
    for name in names:
        ok, status = _check_username_available(name)
        if ok is True:
            st = f"[#00FF00 bold]AVAILABLE[/]"
            avail += 1
        elif ok is False:
            st = f"[{C_NEON} bold]TAKEN[/]"
        else:
            st = f"[{C_GOLD} bold]UNKNOWN[/]"
        table.add_row(f"@{name}", st, status)
        time.sleep(0.4)

    console.print(Padding(Panel(table, title=f"[{C_GOLD} bold]Username Sniper[/]", border_style=C_BLOOD), (1, 1)))
    console.print(Text.from_markup(
        f"\n[{C_SILVER}]available [{C_GOLD} bold]{avail}[/]  /  checked {len(names)}"
    ))
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")


def tool_nuker_config():
    cfg_dir = os.path.join(C.VOID_DIR, "config")
    os.makedirs(cfg_dir, exist_ok=True)
    cfg = C.NUKER_CFG_PATH
    _panel("NUKER CONFIG", "Token bot Discord + Server ID pour VOID-NUKE")
    token = input(f"{_ansi(C_MID)}  bot token >> \033[0m").strip()
    sid = input(f"{_ansi(C_MID)}  server id >> \033[0m").strip()
    if token and sid:
        with open(cfg, "w", encoding="utf-8") as f:
            json.dump({"token": token, "server_id": sid}, f, indent=2)
        _success_box("Config sauvegardée", cfg)
    _pause()


def tool_hash_cracker():
    _panel("HASH CRACKER", "Crack MD5 · SHA1 · SHA256 via lookup online")
    h = input(f"{_ansi(C_MID)}  hash >> \033[0m").strip()
    if not h: return
    console.print(Text.from_markup(f"[{C_NEON} bold] ┌── Hash : {h[:40]}{'...' if len(h)>40 else ''}"))
    _open_links([
        ("CrackStation", "https://crackstation.net/"),
        ("HashKiller",   "https://hashkiller.io/listmanager"),
        ("MD5Decrypt",   "https://md5decrypt.net/"),
        ("Hashes.com",   "https://hashes.com/en/decrypt/hash"),
        ("Nitrxgen",     f"https://www.nitrxgen.net/md5db/{h}"),
    ])

def tool_password_gen():
    _panel("PASSWORD GENERATOR", "Génère des mots de passe ultra-sécurisés")
    try: length = int(input(f"{_ansi(C_MID)}  length (default 20) >> \033[0m").strip() or "20")
    except ValueError: length = 20
    charset = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    console.print(); console.print(Text.from_markup(f"[{C_NEON} bold] ┌── 8 passwords  ·  length {length}"))
    for i in range(8):
        pwd = ''.join(random.choices(charset, k=length))
        t = Text()
        t.append(f" │   [{i+1:02d}] ", style=C_BLOOD)
        t.append(pwd, style=f"{C_WHITE} bold")
        console.print(t)
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def tool_temp_mail():
    _panel("TEMP MAIL", "Adresse mail jetable instantanée")
    console.print(Text.from_markup(f"[{C_NEON} bold] ┌── Temp Mail Services"))
    _open_links([
        ("10MinuteMail",  "https://10minutemail.com/"),
        ("Guerrilla Mail","https://guerrillamail.com/"),
        ("TempMail",      "https://temp-mail.org/"),
        ("Mailnull",      "https://www.mailnull.com/"),
        ("Dispostable",   "https://dispostable.com/"),
        ("FakeMail",      "https://www.fakemail.net/"),
    ])

def tool_base64():
    _panel("BASE64", "Encode / Decode texte")
    mode = input(f"{_ansi(C_MID)}  mode (encode/decode) >> \033[0m").strip().lower()
    txt = input(f"{_ansi(C_MID)}  text >> \033[0m").strip()
    if not txt: return
    import base64
    try:
        if mode.startswith("d"):
            out = base64.b64decode(txt).decode("utf-8", errors="replace")
        else:
            out = base64.b64encode(txt.encode()).decode()
        console.print(Panel(out, border_style=C_GOLD, title="Result"))
    except Exception as e:
        console.print(f"[{C_NEON} bold]  [!] {e}")
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def tool_qr_gen():
    _panel("QR GENERATOR", "Génère un QR code via lien")
    data = input(f"{_ansi(C_MID)}  text or URL >> \033[0m").strip()
    if not data: return
    import urllib.parse
    url = "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=" + urllib.parse.quote(data)
    console.print(f"\n[{C_GOLD} bold]  QR URL:\n[{C_WHITE}]{url}")
    webbrowser.open(url)
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def tool_url_shortener():
    import urllib.request, urllib.parse
    _panel("URL SHORTENER", "Raccourcir une URL (is.gd)")
    url = input(f"{_ansi(C_MID)}  long URL >> \033[0m").strip()
    if not url: return
    try:
        api = "https://is.gd/create.php?format=simple&url=" + urllib.parse.quote(url, safe="")
        with urllib.request.urlopen(api, timeout=10) as r:
            short = r.read().decode().strip()
        console.print(Panel(f"[bold white]{short}[/]", title="[gold]Short URL[/]", border_style=C_GOLD))
    except Exception as e:
        console.print(f"[{C_NEON} bold]  [!] {e}")
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def tool_json_fmt():
    _panel("JSON FORMATTER", "Pretty-print JSON")
    console.print(f"[{C_DIM}]  Colle le JSON, ligne vide pour finir[/]")
    lines, line = [], input()
    if line.strip():
        lines.append(line)
        while True:
            line = input()
            if not line.strip(): break
            lines.append(line)
    raw = "\n".join(lines).strip()
    if not raw: return
    try:
        obj = json.loads(raw)
        console.print(Panel(json.dumps(obj, indent=2, ensure_ascii=False), border_style=C_GOLD))
    except Exception as e:
        console.print(f"[{C_NEON} bold]  [!] JSON invalide: {e}")
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def tool_changelog():
    _panel("CHANGELOG", f"Void-Tools v{VERSION}")
    console.print(Panel(C.CHANGELOG, border_style=C_GOLD, padding=(1, 2)))
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def tool_credits():
    _panel("CREDITS", f"Void-Tools · by {C.AUTHOR}")
    console.print(Panel(
        Text.from_markup(
            f"[{C_GOLD} bold]VOID-TOOLS v{VERSION}[/]\n\n"
            f"[{C_WHITE}]Developer  : [bold]{C.AUTHOR}[/]\n"
            f"[{C_SILVER}]Discord    : {C.DISCORD}\n"
            f"[{C_SILVER}]Shop       : {C.SHOP}\n"
            f"[{C_SILVER}]GitHub     : {C.GITHUB}[/]"
        ), border_style=C_BLOOD, padding=(1, 3)))
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def tool_premium_shop():
    _panel("PREMIUM SHOP", "Acheter VOID PREMIUM")
    console.print(Text.from_markup(
        f"\n[{C_GOLD} bold]  * VOID PREMIUM\n"
        f"[{C_WHITE}]  Shop officiel · support Discord [bold]{C.AUTHOR}[/]\n"
        f"[{C_GOLD2}]{C.SHOP}[/]\n"
        f"[{C_DIM}]{C.DISCORD}[/]"
    ))
    open_premium_links()
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def tool_version_info():
    _panel("VERSION", "Void-Tools system info")
    console.print(Panel(
        Text.from_markup(
            f"[{C_WHITE}]Version    : [bold {C_GOLD}]{VERSION}[/]\n"
            f"[{C_WHITE}]Edition    : PRIME\n"
            f"[{C_WHITE}]Python     : {sys.version.split()[0]}\n"
            f"[{C_WHITE}]Platform   : {sys.platform}"
        ), border_style=C_GOLD, padding=(1, 2)))
    console.print(); input(f"\033[38;2;136;0;0m  press enter...\033[0m")

def tool_patch_notes():
    tool_changelog()

"""Remote — Discord, site GitHub, alertes MAJ (manifest GitHub)."""
import json
import os
import sys
import time
import urllib.error
import urllib.request

from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from rich import box

from . import constants as C
from .config import get_settings
from .void_common import ansi_hex, cls, console, error_box, pause, success_box

# Héberge Void/config/remote-manifest.json sur GitHub (branche main)
REMOTE_URL = os.environ.get(
    "VOID_REMOTE_URL",
    "https://raw.githubusercontent.com/V0id-v2/Void-Tools-v2.0/main/Void/config/remote-manifest.json",
)
LOCAL_MANIFEST = os.path.join(C.CONFIG_DIR, "remote-manifest.json")
CACHE_PATH = os.path.join(C.DATA_DIR, "remote-cache.json")

_manifest = {}
_loaded = False


def _ensure_dirs():
    os.makedirs(C.CONFIG_DIR, exist_ok=True)
    os.makedirs(C.DATA_DIR, exist_ok=True)


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_cache(data):
    _ensure_dirs()
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _rev_num(manifest):
    try:
        return int(str((manifest or {}).get("config_rev", "0")))
    except ValueError:
        return 0


def _fetch_url(url, timeout=8):
    sep = "&" if "?" in url else "?"
    url = f"{url}{sep}t={int(time.time())}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"Void-Tools/{C.VERSION}", "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _default_manifest():
    if os.path.isfile(LOCAL_MANIFEST):
        try:
            return _load_json(LOCAL_MANIFEST)
        except Exception:
            pass
    return {"config_rev": "0", "latest_version": C.VERSION, "links": {}}


def get_manifest():
    global _manifest, _loaded
    if not _loaded:
        _manifest = _default_manifest()
        if os.path.isfile(CACHE_PATH):
            try:
                _manifest = _load_json(CACHE_PATH)
            except Exception:
                pass
        _loaded = True
    return _manifest


def config_rev():
    return str(get_manifest().get("config_rev", "0"))


def apply_overrides(manifest=None):
    """Applique Discord + GitHub (site) + changelog."""
    m = manifest or get_manifest()
    links = m.get("links") or {}
    if links.get("discord"):
        C.DISCORD = str(links["discord"]).strip()
    if links.get("github"):
        C.GITHUB = str(links["github"]).strip()
    if links.get("shop"):
        C.SHOP = str(links["shop"]).strip()
    if m.get("changelog"):
        C.CHANGELOG = str(m["changelog"])


def sync(force=False):
    global _manifest, _loaded
    _ensure_dirs()
    manifest = None
    source = "local"

    try:
        manifest = _fetch_url(REMOTE_URL, timeout=8 if force else 5)
        source = "remote"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError):
        if os.path.isfile(CACHE_PATH):
            try:
                manifest = _load_json(CACHE_PATH)
                source = "cache"
            except Exception:
                pass
        if manifest is None and os.path.isfile(LOCAL_MANIFEST):
            try:
                manifest = _load_json(LOCAL_MANIFEST)
                source = "bundled"
            except Exception:
                pass

    if manifest is None:
        manifest = _default_manifest()
        source = "default"

    # raw.githubusercontent.com peut servir un vieux manifest (CDN) — bundled plus récent gagne
    if os.path.isfile(LOCAL_MANIFEST):
        try:
            bundled = _load_json(LOCAL_MANIFEST)
            if _rev_num(bundled) > _rev_num(manifest):
                manifest = bundled
                source = "bundled"
        except Exception:
            pass

    manifest["_fetched_at"] = time.time()
    manifest["_source"] = source
    _save_cache(manifest)
    _manifest = manifest
    _loaded = True
    apply_overrides(manifest)

    s = get_settings()
    s.set("last_remote_sync", int(time.time()))
    s.save()
    return True, source


def has_pending_update():
    s = get_settings()
    return config_rev() != str(s.get("last_seen_config_rev", ""))


def mark_seen():
    s = get_settings()
    s.set("last_seen_config_rev", config_rev())
    s.save()


def version_update_available():
    m = get_manifest()
    latest = str(m.get("latest_version", C.VERSION))
    if latest == C.VERSION:
        return False
    try:
        from packaging.version import parse as vparse
        return vparse(latest) > vparse(C.VERSION)
    except Exception:
        return latest != C.VERSION


def status_badge():
    if version_update_available():
        return "MAJ"
    if has_pending_update():
        return "NEW"
    return ""


def show_announcement_block():
    from .updater import version_prompt_was_shown

    link_pending = has_pending_update()
    version_pending = version_update_available() and not version_prompt_was_shown()
    if not link_pending and not version_pending:
        return
    s = get_settings()
    fr = s.lang == "fr"
    m = get_manifest()
    ann = m.get("announcement") or {}
    title = ann.get("title_fr" if fr else "title_en") or ("Mise à jour" if fr else "Update")
    body = ann.get("body_fr" if fr else "body_en") or ann.get("body_en") or ""
    extra = []
    if version_pending:
        latest = m.get("latest_version", "?")
        dl = m.get("download_url", C.GITHUB)
        if fr:
            extra.append(f"Nouvelle version [bold {C.C_GOLD}]{latest}[/] (tu as {C.VERSION}).")
        else:
            extra.append(f"New version [bold {C.C_GOLD}]{latest}[/] (you have {C.VERSION}).")
        extra.append(f"Télécharge : [{C.C_DIM}]{dl}[/]")
    if C.DISCORD or C.GITHUB or C.SHOP:
        extra.append(f"Discord : [{C.C_GOLD2}]{C.DISCORD}[/]")
        extra.append(f"Shop    : [{C.C_GOLD2}]{C.SHOP}[/]")
        extra.append(f"Site    : [{C.C_GOLD2}]{C.GITHUB}[/]")
    cls()
    console.print(Panel(
        Align.center(Text.from_markup(
            f"[bold {C.C_NEON}]{title}[/]\n\n{body}"
            + ("\n\n" + "\n".join(extra) if extra else "")
        )),
        title=f"[bold {C.C_GOLD}]VOID — LIENS & MAJ[/]",
        border_style=C.C_GOLD,
        box=box.DOUBLE,
        padding=(1, 2),
    ))
    msg = (
        f"{ansi_hex(C.C_MID)}  ► Entrée pour continuer… \033[0m"
        if fr else f"{ansi_hex(C.C_MID)}  ► Press Enter to continue… \033[0m"
    )
    input(msg)
    mark_seen()
    cls()


def tool_remote_sync():
    s = get_settings()
    fr = s.lang == "fr"
    cls()
    console.print(Panel(
        Align.center(Text.from_markup(
            f"[bold {C.C_GOLD}]{'LIENS & MAJ' if fr else 'LINKS & UPDATE'}[/]\n"
            f"[{C.C_DIM}]Discord · Shop · version[/]"
        )),
        border_style=C.C_BLOOD, box=box.DOUBLE_EDGE, padding=(0, 2),
    ))
    sync(force=True)
    rev = config_rev()
    latest = get_manifest().get("latest_version", C.VERSION)
    src = get_manifest().get("_source", "?")
    lines = [
        f"[{C.C_SILVER}]rev      : [{C.C_GOLD}]{rev}[/]",
        f"[{C.C_SILVER}]source  : [{C.C_DIM}]{src}[/]",
        f"[{C.C_SILVER}]version  : [{C.C_WHITE}]{C.VERSION}[/] → [{C.C_GOLD}]{latest}[/]",
        f"[{C.C_SILVER}]discord  : [{C.C_GOLD2}]{C.DISCORD}[/]",
        f"[{C.C_SILVER}]shop     : [{C.C_GOLD2}]{C.SHOP}[/]",
        f"[{C.C_SILVER}]site     : [{C.C_GOLD2}]{C.GITHUB}[/]",
    ]
    if version_update_available():
        lines.append(f"\n[bold {C.C_GOLD}]{'Mise à jour dispo !' if fr else 'Update available!'}[/]")
        lines.append(f"[{C.C_DIM}]{'Relance Void-Tools pour installer' if fr else 'Restart Void-Tools to install'}[/]")
    elif has_pending_update():
        lines.append(f"\n[bold {C.C_NEON}]{'Liens mis à jour' if fr else 'Links updated'}[/]")
    console.print(Panel(Text.from_markup("\n".join(lines)), border_style=C.C_BLOOD, padding=(1, 2)))
    if version_update_available():
        if fr:
            ask = "Mettre à jour maintenant ? (O/N) : "
        else:
            ask = "Update now? (Y/N): "
        try:
            ans = input(f"\n  {ansi_hex(C.C_MID)}► {ask}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = "n"
        if ans in ("o", "y", "oui", "yes"):
            from .updater import run_auto_update
            ok, msg = run_auto_update()
            if ok:
                success_box("VOID-TOOLS", msg)
                time.sleep(1)
                main_py = os.path.join(C.VOID_DIR, "main.py")
                os.execv(sys.executable, [sys.executable, "-u", main_py])
            else:
                error_box("Update", msg)
    pause()

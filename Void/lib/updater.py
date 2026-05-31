"""Auto-update — download GitHub ZIP, preserve user config, restart."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

from rich.align import Align
from rich.panel import Panel
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TextColumn
from rich.text import Text
from rich import box

from . import constants as C
from .config import get_settings
from .remote import get_manifest, version_update_available
from .void_common import ansi_hex, cls, console, error_box, success_box

_gate_shown = False
PRESERVE_VOID = {
    os.path.normpath("config/settings.json"),
    os.path.normpath("config/discord-nuker.json"),
}

_STRINGS = {
    "title": ("MISE À JOUR REQUISE", "UPDATE REQUIRED"),
    "body": (
        "Une nouvelle version de VOID-TOOLS est disponible.\n"
        "Tu dois mettre à jour pour continuer avec les derniers outils et correctifs.",
        "A new VOID-TOOLS version is available.\n"
        "You should update to get the latest tools and fixes.",
    ),
    "current": ("Version actuelle", "Current version"),
    "latest": ("Dernière version", "Latest version"),
    "ask": ("Voulez-vous mettre à jour maintenant ?", "Do you want to update now?"),
    "yes": ("OUI — mise à jour automatique", "YES — auto update"),
    "no": ("NON — continuer sans mettre à jour", "NO — continue without updating"),
    "hint": ("O / N", "Y / N"),
    "updating": ("Mise à jour en cours…", "Updating…"),
    "restart": ("Redémarrage…", "Restarting…"),
    "fail": ("Échec de la mise à jour", "Update failed"),
    "retry": ("Réessayer ? O/N", "Retry? Y/N"),
}


def _s(key, fr):
    return _STRINGS[key][0 if fr else 1]


def version_prompt_was_shown():
    return _gate_shown


def latest_version():
    return str(get_manifest().get("latest_version", C.VERSION))


def _zip_url():
    m = get_manifest()
    url = str(m.get("zip_url") or m.get("download_url") or "").strip()
    if url.endswith(".zip") and "github.com" in url:
        return url
    base = str(m.get("links", {}).get("github") or C.GITHUB).rstrip("/")
    if "github.com" in base:
        return f"{base}/archive/refs/heads/main.zip"
    return f"{C.GITHUB}/archive/refs/heads/main.zip"


def _void_rel(path, void_root):
    return os.path.normpath(os.path.relpath(path, void_root))


def _skip_void_file(rel):
    if rel in PRESERVE_VOID:
        return True
    return rel == "data" or rel.startswith("data" + os.sep)


def _download(url, dest, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": f"Void-Tools/{C.VERSION}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        total = int(resp.headers.get("Content-Length") or 0)
        chunk = 1024 * 256
        read = 0
        with open(dest, "wb") as out:
            with Progress(
                TextColumn("[bold red]{task.description}"),
                BarColumn(bar_width=40, complete_style="red"),
                DownloadColumn(),
                TransferSpeedColumn(),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("Download…", total=total or None)
                while True:
                    block = resp.read(chunk)
                    if not block:
                        break
                    out.write(block)
                    read += len(block)
                    if total:
                        progress.update(task, completed=read)


def _find_zip_root(extract_dir):
    entries = [e for e in os.listdir(extract_dir) if not e.startswith(".")]
    if len(entries) == 1:
        candidate = os.path.join(extract_dir, entries[0])
        if os.path.isdir(candidate) and os.path.isdir(os.path.join(candidate, "Void")):
            return candidate
    if os.path.isdir(os.path.join(extract_dir, "Void")):
        return extract_dir
    for name in entries:
        p = os.path.join(extract_dir, name)
        if os.path.isdir(p) and os.path.isdir(os.path.join(p, "Void")):
            return p
    return None


def _copy_tree(src_void, dst_void):
    copied = skipped = 0
    for root, dirs, files in os.walk(src_void):
        rel_root = _void_rel(root, src_void)
        if rel_root != "." and _skip_void_file(rel_root):
            dirs.clear()
            continue
        dirs[:] = [
            d for d in dirs
            if not _skip_void_file(os.path.join(rel_root, d) if rel_root != "." else d)
        ]
        for fname in files:
            rel = os.path.join(rel_root, fname) if rel_root != "." else fname
            rel = os.path.normpath(rel)
            if _skip_void_file(rel):
                skipped += 1
                continue
            src = os.path.join(root, fname)
            dst = os.path.join(dst_void, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
    return copied, skipped


def _copy_root_files(src_root, dst_root):
    for name in ("setup.bat", "start.bat", "README.md", ".gitignore"):
        src = os.path.join(src_root, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dst_root, name))


def _install_deps():
    req = os.path.join(C.VOID_DIR, "requirements.txt")
    if not os.path.isfile(req):
        return
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", req, "-q"],
        cwd=C.VOID_DIR,
        check=False,
    )


def run_auto_update():
    """Download and apply update. Returns (ok, message)."""
    url = _zip_url()
    if "github.com" not in url:
        return False, "URL de mise à jour non autorisée."

    tmp = tempfile.mkdtemp(prefix="void-update-")
    zip_path = os.path.join(tmp, "update.zip")
    try:
        _download(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp)
        src_root = _find_zip_root(tmp)
        if not src_root:
            return False, "Archive GitHub invalide (dossier Void introuvable)."
        src_void = os.path.join(src_root, "Void")
        if not os.path.isdir(src_void):
            return False, "Dossier Void absent dans l'archive."

        copied, skipped = _copy_tree(src_void, C.VOID_DIR)
        _copy_root_files(src_root, C.ROOT_DIR)
        _install_deps()
        return True, f"{copied} fichiers mis à jour ({skipped} configs conservées)."
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, zipfile.BadZipFile) as e:
        return False, str(e)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def handle_update_gate():
    """
    Bloque au lancement si une MAJ version est dispo.
    Returns True → redémarrer l'app après MAJ réussie.
    """
    global _gate_shown
    if not version_update_available():
        return False

    _gate_shown = True
    fr = get_settings().lang == "fr"
    latest = latest_version()

    while True:
        cls()
        console.print(Panel(
            Align.center(Text.from_markup(
                f"[bold {C.C_NEON}]{_s('title', fr)}[/]\n\n"
                f"[{C.C_WHITE}]{_s('body', fr)}[/]\n\n"
                f"[{C.C_SILVER}]{_s('current', fr)}[/]  [{C.C_DIM}]{C.VERSION}[/]\n"
                f"[{C.C_SILVER}]{_s('latest', fr)}[/]   [bold {C.C_GOLD}]{latest}[/]\n\n"
                f"[bold {C.C_GOLD}]{_s('ask', fr)}[/]\n\n"
                f"[bold #88FFAA]►[/] [bold {C.C_WHITE}]{_s('yes', fr)}[/]\n"
                f"   [dim {C.C_DIM}]{_s('no', fr)}[/]"
            )),
            title=f"[bold {C.C_GOLD}]VOID-TOOLS[/]",
            border_style=C.C_GOLD,
            box=box.DOUBLE,
            padding=(1, 2),
        ))
        console.print(Align.center(Text.from_markup(f"[{C.C_DIM}]{_s('hint', fr)}[/]")))
        try:
            ans = input(f"\n  {ansi_hex(C.C_MID)}► ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = "n"

        if ans in ("o", "y", "oui", "yes"):
            cls()
            console.print(Panel(
                Align.center(Text.from_markup(f"[bold {C.C_GOLD}]{_s('updating', fr)}[/]")),
                border_style=C.C_BLOOD,
            ))
            ok, msg = run_auto_update()
            if ok:
                success_box(_s("restart", fr), msg)
                time.sleep(1.2)
                return True
            error_box(_s("fail", fr), "Update", msg)
            try:
                retry = input(f"\n  {ansi_hex(C.C_MID)}► {_s('retry', fr)} ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                retry = "n"
            if retry not in ("o", "y", "oui", "yes"):
                cls()
                return False
            continue

        cls()
        return False

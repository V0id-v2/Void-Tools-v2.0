"""Unified tool runner — uses saved language, no repeated prompts."""
import os
import subprocess
import sys

from . import constants as C
from .config import get_settings
from .void_common import cls, console, error_box, pause, panel, success_box


SELF_PAUSE_DIRS = (
    f"{os.sep}tools{os.sep}discord{os.sep}",
    f"{os.sep}tools{os.sep}roblox{os.sep}",
    f"{os.sep}tools{os.sep}social{os.sep}",
)


def run_script(fr_path, en_path, tool_name=None, extra_args=None):
    """Run fr/en tool script with saved language."""
    s = get_settings()
    lang = s.lang if s.lang in ("fr", "en") else "fr"
    src = fr_path if lang == "fr" else en_path

    if not os.path.exists(src):
        error_box("Script absent", os.path.basename(src), src)
        pause()
        return

    try:
        cmd = [sys.executable, src]
        if tool_name:
            cmd.append(tool_name)
        if extra_args:
            cmd.extend(extra_args)
        result = subprocess.run(cmd, shell=False)
        if result.returncode not in (0, None):
            error_box("Tool error", tool_name or os.path.basename(src), f"exit {result.returncode}")
    except FileNotFoundError:
        error_box("Python introuvable", sys.executable or "python")
    except Exception as e:
        error_box("Runtime", tool_name or "tool", str(e))

    if not any(d in src for d in SELF_PAUSE_DIRS):
        pause()


def run(folder, fr_name="fr.py", en_name="en.py", tool_name=None):
    """Run standard folder tool (ip-lookup, email-info, etc.)."""
    run_script(C.sp(folder, fr_name), C.sp(folder, en_name), tool_name)


def run_discord(tool_key):
    run_script(C.sp_discord("fr.py"), C.sp_discord("en.py"), tool_key)


def run_roblox(tool_key):
    run_script(C.sp_roblox("fr.py"), C.sp_roblox("en.py"), tool_key)


def run_social(tool_key):
    run_script(C.sp_social("fr.py"), C.sp_social("en.py"), tool_key)


def run_premium(name):
    run("premium-tools", "fr.py", "en.py", name)


def run_nuker(action=None):
    cls()
    src = C.sp_nuker()
    if not os.path.exists(src):
        error_box("VOID-NUKE absent", "tools/void-nuke/", src)
        pause()
        return
    try:
        cmd = [sys.executable, src]
        if action:
            cmd.extend(["--action", action])
        result = subprocess.run(cmd, shell=False)
        if result.returncode not in (0, None):
            error_box("NUKER", action or "menu", f"exit {result.returncode}")
    except Exception as e:
        error_box("NUKER", action or "menu", str(e))
    pause()


def run_plugin(plugin_path):
    cls()
    if not os.path.isfile(plugin_path):
        error_box("Plugin", "introuvable", plugin_path)
        pause()
        return
    try:
        subprocess.run([sys.executable, plugin_path], shell=False)
    except Exception as e:
        error_box("Plugin", os.path.basename(plugin_path), str(e))
    pause()

#!/usr/bin/env python3
"""Verify all dashboard options — files, keys, syntax."""
import os
import py_compile
import re
import sys

VOID = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if VOID not in sys.path:
    sys.path.insert(0, VOID)

from lib import constants as C
from lib import tools as T
from lib.pages import build_pages_data, _NUKER_ACTIONS
from lib.remote import tool_remote_sync

ERRORS = []
WARNINGS = []
OK = []


def err(cat, key, label, msg):
    ERRORS.append((cat, key, label, msg))


def warn(cat, key, label, msg):
    WARNINGS.append((cat, key, label, msg))


def ok(cat, key, label, msg=""):
    OK.append((cat, key, label, msg))


def check_syntax(path):
    try:
        py_compile.compile(path, doraise=True)
        return None
    except py_compile.PyCompileError as e:
        return str(e)


def check_run_folder(folder, fr="fr.py", en="en.py"):
    issues = []
    fr_p = C.sp(folder, fr)
    en_p = C.sp(folder, en)
    if not os.path.isfile(fr_p):
        issues.append(f"missing {fr_p}")
    elif bad := check_syntax(fr_p):
        issues.append(f"syntax fr: {bad}")
    if fr != en:
        if not os.path.isfile(en_p):
            issues.append(f"missing {en_p}")
        elif bad := check_syntax(en_p):
            issues.append(f"syntax en: {bad}")
    return issues


def load_core_tools(sub):
    import importlib.util
    path = os.path.join(C.VOID_DIR, "tools", sub, "core.py")
    spec = importlib.util.spec_from_file_location(f"{sub}_core", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TOOLS


def closure_val(action, index=0):
    if not getattr(action, "__closure__", None):
        return None
    cell = action.__closure__[index]
    return cell.cell_contents


def classify_action(action):
    mod = getattr(action, "__module__", "")
    name = getattr(action, "__name__", "")

    if action is T.star:
        return ("star", None)
    if action in (
        T.tool_changelog, T.tool_credits, T.tool_premium_shop,
        T.tool_version_info, T.tool_patch_notes, T.tool_hash_cracker,
        T.tool_password_gen, T.tool_temp_mail, T.tool_base64,
        T.tool_qr_gen, T.tool_url_shortener, T.tool_json_fmt,
        T.tool_token_checker, T.tool_nuker_config,
    ):
        return ("builtin", name)
    if action is tool_remote_sync:
        return ("remote", None)

    if name == "<lambda>":
        inner = getattr(action, "__code__", None)
        if inner and inner.co_names:
            if inner.co_name == "<lambda>" and action.__closure__:
                # _nuker_action: lambda c=code: run_nuker(c)
                if "run_nuker" in inner.co_names and action.__closure__:
                    val = closure_val(action, 0)
                    return ("nuker", val or "menu")
                # _p/_d/_r/_s wrappers
                val = closure_val(action, 0)
                if val and "run_discord" in str(inner.co_names):
                    return ("discord", val)
        try:
            import inspect
            src = inspect.getsource(action).strip()
        except Exception:
            src = ""
        if "run_nuker()" in src.replace(" ", ""):
            return ("nuker", "menu")
        if "webbrowser.open" in src:
            return ("browser", src)
        if "run_setup_wizard" in src:
            return ("setup", None)
        if "sys.exit" in src:
            return ("quit", None)
        m = re.search(r'run\("([^"]+)"(?:,\s*"([^"]+)"(?:,\s*"([^"]+)")?)?', src)
        if m:
            return ("run", (m.group(1), m.group(2) or "fr.py", m.group(3) or "en.py"))

    # Partial functions from _d, _r, _s, _p, _nuker_action
    if name == "<lambda>" and action.__closure__:
        code_obj = action.__code__
        n = code_obj.co_names
        val = closure_val(action, 0)
        if "run_discord" in n:
            return ("discord", val)
        if "run_roblox" in n:
            return ("roblox", val)
        if "run_social" in n:
            return ("social", val)
        if "run_premium" in n:
            return ("premium", val)
        if "run_nuker" in n:
            return ("nuker", val)

    return ("unknown", name)


def verify_all():
    pages = build_pages_data()
    discord_tools = load_core_tools("discord")
    roblox_tools = load_core_tools("roblox")
    social_tools = load_core_tools("social")

    nuker_path = C.sp_nuker()
    if not os.path.isfile(nuker_path):
        err("core", "—", "void-nuke", f"missing {nuker_path}")
    elif bad := check_syntax(nuker_path):
        err("core", "—", "void-nuke", bad)
    else:
        ok("core", "—", "void-nuke", "syntax OK")

    for p in (C.sp("premium-tools", "fr.py"), C.sp("premium-tools", "en.py")):
        if not os.path.isfile(p):
            err("core", "—", "premium-tools", f"missing {p}")
        elif bad := check_syntax(p):
            err("core", "—", "premium-tools", bad)

    for cat, items in pages.items():
        for key, label, action in items:
            kind, data = classify_action(action)

            if kind == "star":
                ok(cat, key, label, "premium gate")
            elif kind == "builtin":
                ok(cat, key, label, data)
            elif kind == "remote":
                ok(cat, key, label, "remote sync")
            elif kind == "browser":
                ok(cat, key, label, "link")
            elif kind == "setup":
                ok(cat, key, label, "setup wizard")
            elif kind == "quit":
                ok(cat, key, label, "quit")
            elif kind == "nuker":
                ok(cat, key, label, f"action {data}")
            elif kind == "discord":
                if data not in discord_tools:
                    err(cat, key, label, f"missing discord core key: {data}")
                else:
                    ok(cat, key, label, f"discord:{data}")
            elif kind == "roblox":
                if data not in roblox_tools:
                    err(cat, key, label, f"missing roblox core key: {data}")
                else:
                    ok(cat, key, label, f"roblox:{data}")
            elif kind == "social":
                if data not in social_tools:
                    err(cat, key, label, f"missing social core key: {data}")
                else:
                    ok(cat, key, label, f"social:{data}")
            elif kind == "premium":
                ok(cat, key, label, f"premium:{data}")
            elif kind == "run":
                folder, fr, en = data
                issues = check_run_folder(folder, fr, en)
                if issues:
                    err(cat, key, label, "; ".join(issues))
                else:
                    ok(cat, key, label, folder)
            else:
                warn(cat, key, label, f"unclassified ({kind})")


def verify_nuker_map():
    path = C.sp_nuker()
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8", errors="ignore") as f:
        src = f.read()
    m = re.search(r"ACTIONS\s*=\s*\{", src)
    if not m:
        warn("nuker", "—", "ACTIONS", "dict not found")
        return
    for code, label in _NUKER_ACTIONS:
        if f"'{code}'" not in src and f'"{code}"' not in src:
            err("nuker", code, label, "not mapped in void-nuke main.py")
        else:
            ok("nuker-map", code, label, "OK")


def smoke_import_tools():
    """Import each standalone tool module entry (syntax + top-level imports)."""
    folders = set()
    pages = build_pages_data()
    for cat, items in pages.items():
        for key, label, action in items:
            kind, data = classify_action(action)
            if kind == "run":
                folders.add(data[0])

    for folder in sorted(folders):
        fr = C.sp(folder, "fr.py")
        if not os.path.isfile(fr):
            continue
        # dry-run: compile + ast parse only (imports may fail on missing input)
        if bad := check_syntax(fr):
            err("syntax", "—", folder, bad)


def main():
    print("VOID-TOOLS — full option verification\n")
    verify_all()
    verify_nuker_map()
    smoke_import_tools()

    print(f"OK:       {len(OK)}")
    print(f"WARNINGS: {len(WARNINGS)}")
    print(f"ERRORS:   {len(ERRORS)}\n")

    if ERRORS:
        print("=== ERRORS (must fix) ===")
        for cat, key, label, msg in ERRORS:
            print(f"  [{cat:10}] {key:3} {label:28} → {msg}")

    if WARNINGS:
        print("\n=== WARNINGS ===")
        for cat, key, label, msg in WARNINGS:
            print(f"  [{cat:10}] {key:3} {label:28} → {msg}")

    if not ERRORS and not WARNINGS:
        print("All options verified successfully.")

    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())

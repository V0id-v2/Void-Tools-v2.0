"""Check and optionally install Python dependencies."""
import importlib
import subprocess
import sys
import os

REQUIRED = [
    ("colorama", "colorama"),
    ("rich", "rich"),
]

OPTIONAL = [
    ("dns.resolver", "dnspython"),
    ("requests", "requests"),
]


def check_deps(auto_install=True) -> bool:
    missing = []
    for mod, pkg in REQUIRED + OPTIONAL:
        try:
            importlib.import_module(mod.split(".")[0] if "." in mod else mod)
        except ImportError:
            missing.append(pkg)

    if not missing:
        return True

    req_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "requirements.txt")
    if auto_install:
        pkgs = list(dict.fromkeys(missing))
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q"] + pkgs,
                check=False,
                capture_output=True,
            )
            return True
        except Exception:
            pass
    return len([p for p in missing if p in [x[1] for x in REQUIRED]]) == 0

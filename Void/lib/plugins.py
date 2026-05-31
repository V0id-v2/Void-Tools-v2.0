"""Load custom plugins from tools/custom/."""
import glob
import os

from . import constants as C
from .runner import run_plugin


def discover_plugins():
    """Return list of (code, label, action) from tools/custom/*.py"""
    os.makedirs(C.CUSTOM_TOOLS_DIR, exist_ok=True)
    items = []
    for i, path in enumerate(sorted(glob.glob(os.path.join(C.CUSTOM_TOOLS_DIR, "*.py"))), 1):
        name = os.path.splitext(os.path.basename(path))[0]
        if name.startswith("_"):
            continue
        label = name.replace("-", " ").replace("_", " ").title()
        code = f"P{i:02d}"
        items.append((code, f"{label} [PLUGIN]", lambda p=path: run_plugin(p)))
    return items

#!/usr/bin/env python3
"""Void-Tools — v2.0"""
import os
import sys

# Fix imports when launched via start.bat (cwd = Void-Tools root)
_VOID = os.path.dirname(os.path.abspath(__file__))
if _VOID not in sys.path:
    sys.path.insert(0, _VOID)

from lib.entry import run_void

if __name__ == "__main__":
    run_void()

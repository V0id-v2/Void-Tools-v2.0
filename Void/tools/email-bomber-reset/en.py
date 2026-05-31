import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core import main

TEXT = {
    "subtitle": " A M A Z O N · S T A C K · L E M O N D E   ·   V 5 ",
    "desc": "Intense spam — 3 sites only",
    "sites": "sites",
    "intense": "max burst",
    "loops": "rounds",
    "burst": "Burst",
    "burst_label": "req/site/round",
    "burst_prompt": "Simultaneous sends per site [1-100, default 20]:",
    "target": "Target",
    "round": "Round",
    "progress": "Progress",
    "sent": "Requests",
    "sites_per_round": "focus sites",
    "prompt": "Target email:",
    "invalid": "Invalid email address.",
    "rounds_prompt": "Number of rounds [1-200, default 20]:",
    "launch": "Intense bombardment…",
    "done": "COMPLETE",
    "note": "Amazon · Stack Overflow · Le Monde — Enter = default max.",
    "enter": "Press Enter to return to menu…",
}

if __name__ == "__main__":
    try:
        main(TEXT)
    except KeyboardInterrupt:
        print("\n  [!] Cancelled.")

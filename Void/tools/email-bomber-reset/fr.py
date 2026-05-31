import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core import main

TEXT = {
    "subtitle": " A M A Z O N · S T A C K · L E M O N D E   ·   V 5 ",
    "desc": "Spam intense — 3 sites uniquement",
    "sites": "sites",
    "intense": "rafale max",
    "loops": "tours",
    "burst": "Rafale",
    "burst_label": "req/site/tour",
    "burst_prompt": "Envois simultanés par site [1-100, défaut 20] :",
    "target": "Cible",
    "round": "Tour",
    "progress": "Progression",
    "sent": "Requêtes",
    "sites_per_round": "sites focus",
    "prompt": "Email cible :",
    "invalid": "Adresse email invalide.",
    "rounds_prompt": "Nombre de tours [1-200, défaut 20] :",
    "launch": "Bombardement intense…",
    "done": "TERMINÉ",
    "note": "Amazon · Stack Overflow · Le Monde — Entrée = défauts max.",
    "enter": "Entrée pour revenir au menu…",
}

if __name__ == "__main__":
    try:
        main(TEXT)
    except KeyboardInterrupt:
        print("\n  [!] Annulé.")

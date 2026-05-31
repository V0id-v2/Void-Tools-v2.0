#!/usr/bin/env python3
import sys
from core import set_language, run_tool

STRINGS = {
    "pause": "Entrée pour revenir au menu…",
    "yes": "Oui", "no": "Non", "hidden": "masqué", "never": "Jamais",
    "cancelled": "Annulé", "error_title": "Erreur", "unknown": "Outil inconnu :",
    "network": "Connexion impossible",
    "tk_title": "Token Checker", "tk_desc": "Vérifie la validité d'un token Discord",
    "token_prompt": "Token Discord", "token_invalid": "Token invalide",
    "token_ok": "Token valide", "user": "Utilisateur",
    "inv_title": "Invite Resolver", "inv_desc": "Code ou lien → infos du serveur",
    "inv_prompt": "Code ou lien (discord.gg/…)", "inv_invalid": "Invite invalide",
    "server": "Serveur", "members": "Membres", "online": "En ligne",
    "channel": "Salon", "expires": "Expiration",
    "user_title": "User Lookup", "user_desc": "ID utilisateur → profil (token optionnel)",
    "uid_prompt": "ID utilisateur", "uid_invalid": "ID utilisateur invalide",
    "token_optional": "Token bot/user (Entrée = ignorer)",
    "user_fail": "Utilisateur introuvable", "token_hint": "Un token bot ou user valide est souvent requis",
    "wh_title": "Webhook Info", "wh_desc": "URL webhook → détails",
    "wh_prompt": "URL webhook complète", "wh_invalid": "URL webhook invalide",
    "wh_fail": "Webhook introuvable", "name": "Nom", "type": "Type",
}

if __name__ == "__main__":
    set_language(STRINGS)
    run_tool(sys.argv[1] if len(sys.argv) > 1 else "")

#!/usr/bin/env python3
import sys
from core import set_language, run_tool

STRINGS = {
    "pause": "Press Enter to return…",
    "yes": "Yes", "no": "No", "hidden": "hidden", "never": "Never",
    "cancelled": "Cancelled", "error_title": "Error", "unknown": "Unknown tool:",
    "network": "Network unreachable",
    "tk_title": "Token Checker", "tk_desc": "Validate a Discord token",
    "token_prompt": "Discord token", "token_invalid": "Invalid token",
    "token_ok": "Valid token", "user": "User",
    "inv_title": "Invite Resolver", "inv_desc": "Code or link → server info",
    "inv_prompt": "Code or link (discord.gg/…)", "inv_invalid": "Invalid invite",
    "server": "Server", "members": "Members", "online": "Online",
    "channel": "Channel", "expires": "Expires",
    "user_title": "User Lookup", "user_desc": "User ID → profile (optional token)",
    "uid_prompt": "User ID", "uid_invalid": "Invalid user ID",
    "token_optional": "Bot/user token (Enter = skip)",
    "user_fail": "User not found", "token_hint": "A valid bot or user token is often required",
    "wh_title": "Webhook Info", "wh_desc": "Webhook URL → details",
    "wh_prompt": "Full webhook URL", "wh_invalid": "Invalid webhook URL",
    "wh_fail": "Webhook not found", "name": "Name", "type": "Type",
}

if __name__ == "__main__":
    set_language(STRINGS)
    run_tool(sys.argv[1] if len(sys.argv) > 1 else "")

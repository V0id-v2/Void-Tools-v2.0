"""Dashboard page definitions."""
import sys
import webbrowser

from . import constants as C
from . import tools as T
from .remote import tool_remote_sync
from .runner import run, run_discord, run_roblox, run_social, run_webhook, run_premium, run_nuker

_NUKER_ACTIONS = [
    ("01", "Nuke"), ("02", "Auto Raid"), ("03", "Ban All"), ("04", "Kick All"),
    ("05", "Mute All"), ("06", "Unban All"), ("07", "Del Channels"), ("08", "Del Emojis"),
    ("09", "Del Stickers"), ("10", "Create Channels"), ("11", "Create Roles"), ("12", "Create Cats"),
    ("13", "Rename Channels"), ("14", "Rename Roles"), ("15", "Edit Server"), ("16", "Rename Members"),
    ("17", "Fix Nicks"), ("18", "Get Admin"), ("19", "Impersonate"), ("20", "Ghost Ping"),
    ("21", "Remov Roles"), ("22", "Message All"), ("23", "DM Spam User"), ("24", "Webhook Spam"),
    ("25", "Server Info"), ("26", "Clone Server"), ("27", "Webhook Logs"), ("28", "Lockdown"),
    ("29", "Sourdine VC"), ("30", "Kick VC All"), ("31", "Move All VC"), ("32", "Invite Spam"),
    ("33", "Spam"), ("34", "Thread Spam"), ("35", "Reaction Spam"), ("36", "Voice Spam"),
    ("37", "Spoiler Spam"), ("38", "Poll Spam"), ("39", "Event Spam"),
]


def _d(key):
    return lambda: run_discord(key)


def _r(key):
    return lambda: run_roblox(key)


def _s(key):
    return lambda: run_social(key)


def _w(key):
    return lambda: run_webhook(key)


def _p(name):
    return lambda: run_premium(name)


def _nuker_action(code):
    return lambda c=code: run_nuker(c)


def _discord_pages():
    return [
        ("01", "Token Checker", _d("token-checker")),
        ("02", "User Lookup", _d("user-lookup")),
        ("03", "Invite Resolver", _d("invite-resolver")),
        ("04", "Token Bruteforce", _d("token-bruteforce")),
        ("05", "Token Login", _d("token-login")),
        ("06", "Status Rotator", _d("status-rotator")),
        ("07", "Token Onliner", _d("token-onliner")),
        ("08", "Guild Leaver", _d("guild-leaver")),
        ("12", "Token-Generator [PREMIUM]", _p("Token-Generator")),
        ("13", "Token-Joiner [PREMIUM]", _p("Token-Joiner")),
        ("14", "Token-Nuker [PREMIUM]", _p("Token-Nuker")),
        ("15", "Nitro Sniper [PREMIUM]", _p("Nitro Sniper")),
        ("16", "Username Sniper [PREMIUM]", _p("Username Sniper")),
        ("17", "Vanity Sniper [PREMIUM]", _p("Vanity Sniper")),
        ("18", "Mass DM [PREMIUM]", _p("Mass DM")),
        ("19", "Mass Report [PREMIUM]", _p("Mass Report")),
        ("20", "Token Checker Pro [PREMIUM]", _p("Token Checker Pro")),
        ("21", "Account Creator [PREMIUM]", _p("Account Creator")),
        ("22", "Boost Sniper [PREMIUM]", _p("Boost Sniper")),
        ("23", "Friend Spammer [PREMIUM]", _p("Friend Spammer")),
        ("24", "Server Cloner Pro [PREMIUM]", _p("Server Cloner Pro")),
        ("25", "Anti-Ban Token [PREMIUM]", _p("Anti-Ban Token")),
    ]


def _webhook_pages():
    return [
        ("01", "Webhook Info", _w("webhook-info")),
        ("02", "Webhook Spammer", _w("webhook-spam")),
        ("03", "GIF & Bad Word Spammer", _w("webhook-gif-spam")),
        ("04", "Bulk Checker", _w("webhook-bulk")),
        ("05", "Send Message", _w("webhook-send")),
        ("06", "Embed Sender", _w("webhook-embed")),
        ("07", "JSON Sender", _w("webhook-json")),
        ("08", "File Sender", _w("webhook-file")),
        ("09", "Ghost Ping", _w("webhook-ghost")),
        ("10", "Message Editor", _w("webhook-edit-msg")),
        ("11", "Message Deleter", _w("webhook-delete-msg")),
        ("12", "Webhook Editor", _w("webhook-edit")),
        ("13", "Webhook Cloner", _w("webhook-clone")),
        ("14", "URL Extractor", _w("webhook-extract")),
        ("15", "Webhook Library", _w("webhook-library")),
        ("16", "Curl Generator", _w("webhook-curl")),
        ("17", "Webhook Generator", _w("webhook-create")),
        ("18", "Webhook Destroyer", _w("webhook-destroyer")),
        ("19", "Keylogger Webhook", lambda: run("keylogger-webhook")),
    ]


def _social_pages():
    return [
        ("01", "Username Check", _s("username-check")),
        ("02", "YouTube Channel", _s("youtube-channel")),
        ("03", "YouTube Video", _s("youtube-video")),
        ("04", "X / Twitter Profile", _s("x-profile")),
        ("05", "TikTok Profile", _s("tiktok-profile")),
        ("06", "Instagram Profile", _s("instagram-profile")),
        ("07", "Snapchat Check", _s("snapchat-check")),
        ("08", "Telegram Channel", _s("telegram-channel")),
        ("09", "TikTok-Follow [PREMIUM]", _p("TikTok-Follow")),
        ("10", "TikTok-Like [PREMIUM]", _p("TikTok-Like")),
        ("11", "TikTok-Views [PREMIUM]", _p("TikTok-Views")),
        ("12", "Instagram-Follow [PREMIUM]", _p("Instagram-Follow")),
        ("13", "Instagram-Like [PREMIUM]", _p("Instagram-Like")),
        ("14", "YouTube-Views [PREMIUM]", _p("YouTube-Views")),
        ("15", "YouTube-Like [PREMIUM]", _p("YouTube-Like")),
        ("16", "X-Follow [PREMIUM]", _p("X-Follow")),
        ("17", "X-Like [PREMIUM]", _p("X-Like")),
        ("18", "Telegram-Member [PREMIUM]", _p("Telegram-Member")),
    ]


def _roblox_pages():
    return [
        ("01", "Cookie Checker", _r("cookie-checker")),
        ("02", "Username Lookup", _r("username-lookup")),
        ("03", "Profile Viewer", _r("profile-viewer")),
        ("04", "Friends List", _r("friends-list")),
        ("05", "Followers Count", _r("followers-count")),
        ("06", "Account Age", _r("account-age")),
        ("07", "Game Pass Lookup", _r("gamepass-lookup")),
        ("08", "Place → Universe", _r("place-universe")),
        ("09", "Catalog Search", _r("catalog-search")),
        ("10", "Multi Cookie Check", _r("multi-cookie")),
        ("11", "Export Profile JSON", _r("export-profile")),
        ("12", "Avatar Batch", _r("avatar-batch")),
        ("13", "Group Funds", _r("group-funds")),
        ("14", "Game Lookup", _r("game-lookup")),
        ("15", "Group Lookup", _r("group-lookup")),
        ("16", "Robux Checker", _r("robux-checker")),
        ("17", "Badge Checker", _r("badge-checker")),
        ("18", "Limited Price", _r("limited-price")),
        ("19", "Roblox-Stealer [PREMIUM]", _p("Roblox-Stealer")),
        ("20", "Roblox-Account Gen [PREMIUM]", _p("Roblox-Account Gen")),
        ("21", "Roblox-Mass Report [PREMIUM]", _p("Roblox-Mass Report")),
        ("22", "Roblox-Trade Bot [PREMIUM]", _p("Roblox-Trade Bot")),
        ("23", "Roblox-Anti-Ban [PREMIUM]", _p("Roblox-Anti-Ban")),
    ]


def _nuker_pages():
    items = [("00", "VOID-NUKE Menu", lambda: run_nuker())]
    for code, label in _NUKER_ACTIONS:
        items.append((code, label, _nuker_action(code)))
    items.extend([
        ("41", "Tkn Checker", T.tool_token_checker),
    ])
    return items


def build_pages_data(plugin_items=None):
    plugin_items = plugin_items or []
    pages = {
        "home": [
            ("01", "GitHub", lambda: webbrowser.open(C.GITHUB)),
            ("02", "Telegram", lambda: webbrowser.open(C.TELEGRAM)),
            ("03", "Discord", lambda: webbrowser.open(C.DISCORD)),
            ("04", "Star GitHub", lambda: webbrowser.open(C.GITHUB)),
            ("05", "Premium Shop", T.tool_premium_shop),
            ("06", "Changelog", T.tool_changelog),
            ("07", "Credits", T.tool_credits),
            ("08", "Setup Config", lambda: __import__("lib.setup", fromlist=["x"]).run_setup_wizard(force=True)),
            ("09", "Liens / MAJ", tool_remote_sync),
            ("Q", "Quit System", lambda: sys.exit(0)),
        ],
        "osint": [
            ("01", "Doxbin", lambda: webbrowser.open("https://doxbin.com/")),
            ("02", "OSINT Framework", lambda: webbrowser.open("https://osintframework.com/")),
            ("03", "Name Finder", lambda: run("name-tracker")),
            ("04", "Email Info", lambda: run("email-info")),
            ("05", "Number Info", lambda: run("number-info")),
            ("06", "Dox Creator", lambda: run("dox")),
            ("07", "Simple Dox", lambda: run("simple-dox")),
            ("08", "Search DB", lambda: run("search-database")),
            ("09", "IP Lookup", lambda: run("ip-lookup")),
            ("10", "Username Hunter", lambda: run("username-hunter")),
            ("11", "Domain Intel", lambda: run("domain-intel")),
            ("12", "IP VPN Detector", lambda: run("ip-vpn-detector")),
            ("13", "Breach Finder", lambda: run("breach-finder")),
            ("14", "Email OSINT", lambda: run("email-osint")),
            ("15", "EXIF Forensic", lambda: run("exif-forensic")),
            ("16", "ID-To-IP [PREMIUM]", _p("Discord ID-To-IP")),
        ],
        "attack": [
            ("01", "Email Bomber", lambda: run("email-bomber-reset")),
            ("02", "DDoS IP (Hub)", lambda: webbrowser.open("https://stresserai.ru/hub")),
            ("03", "Zip Cracker", lambda: run("zip-cracker")),
            ("04", "Keylogger Webhook", lambda: run("keylogger-webhook")),
            ("05", "Token-Grabber [PREMIUM]", _p("Token-Grabber")),
            ("06", "Rar Cracker [PREMIUM]", lambda: run("rar-cracker")),
            ("07", "DDOS [PREMIUM]", _p("DDOS")),
            ("08", "Token-Bomber [PREMIUM]", _p("Token Bomber")),
            ("09", "Admin-Panel [PREMIUM]", _p("Admin-Panel")),
            ("10", "Discord-SelfBot [PREMIUM]", _p("Discord-SelfBot")),
        ],
        "nuker": _nuker_pages(),
        "discord": _discord_pages(),
        "webhook": _webhook_pages(),
        "social": _social_pages(),
        "roblox": _roblox_pages(),
        "ip-web": [
            ("01", "IP Localise", lambda: run("ip-localisation")),
            ("02", "IP Operator", lambda: run("ip-operator")),
            ("03", "IP Open Ports", lambda: run("ip-open-ports")),
            ("04", "IP Pinger", lambda: run("ip-pinger")),
            ("05", "IP Gen", lambda: run("ip-generator")),
            ("06", "IP Oracle (v2)", lambda: run("ip-oracle")),
            ("07", "IP Lookup", lambda: run("ip-all-lookup")),
            ("08", "IP VPN Detector", lambda: run("ip-vpn-detector")),
            ("09", "IP Blacklist", lambda: run("ip-blacklist-checker")),
            ("10", "Website Info", lambda: run("website-info-scanner")),
            ("11", "URL Scanner", lambda: run("website-url-scanner")),
            ("12", "Vuln Scanner", lambda: run("website-vulnerability-scanner")),
            ("13", "Web Cloner", lambda: run("website-cloner")),
            ("14", "Subdomain BF", lambda: run("website-subdomain-bruteforcer")),
            ("15", "Basic Auth BF", lambda: run("website-basic-auth-bf")),
            ("16", "Admin Hunter", lambda: run("website-admin-hunter")),
            ("17", "Dir Buster", lambda: run("website-dir-buster")),
            ("18", "DDOS [PREMIUM]", _p("DDOS")),
        ],
        "generator": [
            ("01", "Nitro Gen", lambda: run("nitro-generator")),
            ("02", "Amazon Gen", lambda: run("generator")),
            ("03", "Netflix Gen", lambda: run("generator")),
            ("04", "Roblox Gen", lambda: run("generator")),
            ("05", "Discord Graphics", lambda: run("discord-graphics", "fr.py", "fr.py")),
        ],
        "crypto-utils": [
            ("01", "Hash Crack", T.tool_hash_cracker),
            ("02", "Passw Gen", T.tool_password_gen),
            ("03", "Temp Mail", T.tool_temp_mail),
            ("04", "Base64", T.tool_base64),
            ("05", "QR Gen", T.tool_qr_gen),
            ("06", "URL Short", T.tool_url_shortener),
            ("07", "JSON Format", T.tool_json_fmt),
            ("08", "Wallet Check", T.star),
            ("09", "Dnox Inject", T.star),
        ],
        "darkweb": [
            ("01", "Mail2Tor", lambda: webbrowser.open("http://mail2tor2zyjdctd.onion/")),
            ("02", "Hidden Wiki", lambda: webbrowser.open("http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion/")),
            ("03", "Doxbin", lambda: webbrowser.open("https://doxbin.net/")),
            ("04", "OSINT Ind", lambda: webbrowser.open("https://osint.industries/")),
            ("05", "Epieos", lambda: webbrowser.open("https://epieos.com/")),
        ],
        "about": [
            ("01", "Version Info", T.tool_version_info),
            ("02", "Patch Notes", T.tool_patch_notes),
            ("03", "Author Star", lambda: webbrowser.open(C.GITHUB)),
        ],
    }
    if plugin_items:
        pages["plugins"] = plugin_items
    return pages

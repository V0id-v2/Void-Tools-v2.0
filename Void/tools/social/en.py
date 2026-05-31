#!/usr/bin/env python3
import sys
from core import set_language, run_tool

STRINGS = {
    "pause": "Press Enter to return…",
    "yes": "Yes", "no": "No", "unknown": "Unknown", "maybe": "Maybe",
    "cancelled": "Cancelled", "check_manual": "Check manually",
    "open_links": "Open all links",
    "username": "username",
    "uc_title": "Username Check", "uc_desc": "12 platforms · profile links",
    "ytc_title": "YouTube Channel", "ytc_desc": "ID or @handle",
    "channel_id": "channel ID or @handle",
    "yt_tip": "Open page for subscriber stats",
    "yt_api_note": "Full stats need YouTube API key",
    "ytv_title": "YouTube Video", "ytv_desc": "Video ID or URL",
    "video_id": "video ID or URL",
    "x_title": "X Profile", "x_desc": "Public profile via mirror",
    "tt_title": "TikTok Profile", "tt_desc": "Public @user info",
    "ig_title": "Instagram Profile", "ig_desc": "Public profile (limited)",
    "ig_note": "Instagram limits scraping",
    "sc_title": "Snapchat Check", "sc_desc": "Add link / existence",
    "sc_tip": "HTTP 200 = page reachable",
    "tg_title": "Telegram Channel", "tg_desc": "Public channel info",
    "channel": "channel name (@)",
    "unknown": "Unknown tool:",
}

if __name__ == "__main__":
    set_language(STRINGS)
    run_tool(sys.argv[1] if len(sys.argv) > 1 else "")

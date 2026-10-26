"""
jarvis_actions.py - Windows-focused automation for daily workflow
"""

import subprocess
import re
import urllib.parse
import datetime
import os
import sys
import webbrowser
import jarvis_market

SITES = {
    "youtube": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "gmail": "https://mail.google.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "maps": "https://maps.google.com",
    "calendar": "https://calendar.google.com",
    "drive": "https://drive.google.com",
    "chatgpt": "https://chatgpt.com",
}

APPS = {
    "vs code": "code",
    "code": "code",
    "visual studio code": "code",
    "chrome": "chrome",
    "google chrome": "chrome",
    "notepad": "notepad",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "explorer": "explorer",
    "file explorer": "explorer",
    "calculator": "calc",
    "terminal": "wt",
    "settings": "ms-settings:",
    "control panel": "control",
    "task manager": "taskmgr",
    "command prompt": "cmd",
    "powershell": "powershell",
    "paint": "mspaint",
    "whatsapp": "whatsapp",
}


def _open_url(url: str) -> bool:
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False


def _open_app(name: str) -> bool:
    cmd = APPS.get(name.lower().strip(), name)
    try:
        if cmd.startswith("ms-settings:"):
            webbrowser.open(cmd)
            return True
        subprocess.Popen(f'start "" "{cmd}"', shell=True)
        return True
    except Exception:
        try:
            subprocess.Popen(cmd, shell=True)
            return True
        except Exception:
            return False


def send_whatsapp_message(contact_name, message="Hello from Jarvis"):
    encoded = urllib.parse.quote(message)
    _open_url(f"https://web.whatsapp.com/send?text={encoded}")
    return f"Opening WhatsApp for {contact_name}."


def get_mail_brief():
    cache = os.path.expanduser("~/.openjarvis/mail_cache.txt")
    if os.path.exists(cache):
        try:
            with open(cache, "r", errors="ignore") as f:
                content = f.read().strip()
                if content:
                    return "Mail briefing: " + content[:500]
        except Exception:
            pass
    return "I can open Gmail for you. Say 'open Gmail' to check your inbox."


def try_action(q: str):
    q_clean = q.lower().strip(" .,!?")

    if any(k in q_clean for k in ("stock", "market", "nifty", "sensex", "crypto", "bitcoin", "buy or sell")):
        for sym, name in jarvis_market.DEFAULT_TICKERS.items():
            if name.lower() in q_clean or sym.lower().replace(".ns", "") in q_clean:
                data = jarvis_market.analyze_ticker(sym)
                if data:
                    direction = "up" if data["pct_change"] >= 0 else "down"
                    return (
                        f"{data['name']} is at {data['currency']}{data['price']:,}, "
                        f"{direction} {abs(data['pct_change'])}%. "
                        f"Signal: {data['signal']}. {data['reason']}"
                    )
        return "Market overview: " + jarvis_market.market_briefing()

    m = re.search(
        r"(?:send|reply|message).*?(?:whatsapp\s+)?(?:to|for)\s+(.+?)(?:\s+(?:saying|that|message)\s+(.+))?$",
        q_clean,
    )
    if "whatsapp" in q_clean and m:
        contact = m.group(1).strip()
        msg = m.group(2).strip() if m.group(2) else "Hello from Jarvis."
        return send_whatsapp_message(contact, msg)

    if any(x in q_clean for x in ("open whatsapp", "check whatsapp", "whatsapp")):
        _open_url(SITES["whatsapp"])
        return "Opening WhatsApp Web."

    if any(k in q_clean for k in ("mail brief", "check mail", "read emails", "unread emails", "inbox")):
        return get_mail_brief()

    if "gmail" in q_clean or "open mail" in q_clean or "open email" in q_clean:
        _open_url(SITES["gmail"])
        return "Opening Gmail."

    m = re.search(r"(?:play|search|find|open)\s+(.+?)\s+(?:on|in)\s+youtube", q_clean)
    if m:
        query = m.group(1).strip()
        _open_url("https://www.youtube.com/results?search_query=" + urllib.parse.quote(query))
        return f"Playing {query} on YouTube."

    m = re.match(r"(?:search|google)(?: for)?\s+(.+)", q_clean)
    if m:
        query = m.group(1).strip()
        _open_url("https://www.google.com/search?q=" + urllib.parse.quote(query))
        return f"Searching Google for {query}."

    if "github" in q_clean:
        _open_url(SITES["github"])
        return "Opening GitHub."

    if any(x in q_clean for x in ("vs code", "visual studio code", "open code", "launch code")):
        if _open_app("code"):
            return "Opening Visual Studio Code."
        return "Could not open VS Code. Is it installed and in PATH?"

    if "chrome" in q_clean:
        if _open_app("chrome"):
            return "Opening Google Chrome."
        return "Could not open Chrome."

    if "notepad" in q_clean or "note pad" in q_clean or "open notes" in q_clean:
        if _open_app("notepad"):
            return "Opening Notepad."
        return "Could not open Notepad."

    m = re.match(r"(?:please\s+)?(?:open|launch|start)\s+(.+)", q_clean)
    if m:
        name = m.group(1).strip()
        if name in SITES:
            _open_url(SITES[name])
            return f"Opening {name}."
        if _open_app(name):
            return f"Opening {name}."
        return f"I couldn't find an application named {name}."

    if "time" in q_clean:
        return "It is currently " + datetime.datetime.now().strftime("%I:%M %p")
    if "date" in q_clean or "today" in q_clean:
        return "Today is " + datetime.datetime.now().strftime("%A, %B %d, %Y")

    return None

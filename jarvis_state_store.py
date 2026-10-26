"""
Shared live state written by jarvis_voice.py and read by jarvis_server.py.
File-based so both processes stay in sync on Windows.
"""

import json
import os
import time
import threading
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live_state.json")
_lock = threading.Lock()

_DEFAULT = {
    "state": "idle",
    "note": "Ready",
    "mode": "HYBRID",
    "last_you": "",
    "model": "Groq + Local Fallback",
    "t_rec": 0.0,
    "t_think": 0.0,
    "last_tool": "",
    "tools": 0,
    "facts": 0,
    "mail_age": None,
    "tool_active": False,
    "chat": [],
    "cards": [],
    "stocks": [],
    "sys": {},
    "mic": {"n": 0, "a": []},
    "updated": 0,
}


def _now_str():
    return datetime.now().strftime("%H:%M:%S")


def load():
    with _lock:
        if not os.path.exists(STATE_FILE):
            return dict(_DEFAULT)
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in _DEFAULT.items():
                data.setdefault(k, v)
            return data
        except Exception:
            return dict(_DEFAULT)


def save(data):
    data["updated"] = time.time()
    with _lock:
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, STATE_FILE)


def set_state(state, note=None):
    data = load()
    data["state"] = state
    if note is not None:
        data["note"] = note
    save(data)


def add_chat(kind, text):
    """kind: 'you' | 'jarvis' | 'sys'"""
    data = load()
    chat = data.get("chat") or []
    next_i = (chat[-1]["i"] + 1) if chat else 1
    chat.append({"i": next_i, "k": kind, "x": text, "t": _now_str()})
    # keep last 60 messages
    data["chat"] = chat[-60:]
    if kind == "you":
        data["last_you"] = text
    save(data)
    return next_i


def set_timings(t_rec=None, t_think=None):
    data = load()
    if t_rec is not None:
        data["t_rec"] = round(float(t_rec), 2)
    if t_think is not None:
        data["t_think"] = round(float(t_think), 2)
    save(data)


def bump_tools(name=""):
    data = load()
    data["tools"] = int(data.get("tools") or 0) + 1
    if name:
        data["last_tool"] = name
    data["tool_active"] = True
    save(data)


def clear_tool_active():
    data = load()
    data["tool_active"] = False
    save(data)


def push_mic_level(level):
    """Optional: push a 0..1 mic level sample for the waveform."""
    data = load()
    mic = data.get("mic") or {"n": 0, "a": []}
    mic["n"] = int(mic.get("n") or 0) + 1
    arr = list(mic.get("a") or [])
    arr.append(max(0.0, min(1.0, float(level))))
    mic["a"] = arr[-20:]
    data["mic"] = mic
    save(data)


def update_sys(cpu=None, ram=None, disk=None):
    data = load()
    sy = data.get("sys") or {}
    if cpu is not None:
        sy["cpu"] = cpu
    if ram is not None:
        sy["ram"] = ram
    if disk is not None:
        sy["disk"] = disk
    data["sys"] = sy
    save(data)

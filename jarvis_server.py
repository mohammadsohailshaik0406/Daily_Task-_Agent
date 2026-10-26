"""
jarvis_server.py - Serves the holographic HUD and live /api/state endpoint.
Run this in one terminal, then run jarvis_voice.py in another.
"""

import json
import os
import sys
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import jarvis_state_store as store

PORT = 8765
ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, fmt, *args):
        try:
            msg = fmt % args if args else str(fmt)
        except Exception:
            msg = str(fmt)
        if "/api/" in msg:
            return
        sys.stderr.write("%s - - [%s] %s\n" % (
            self.address_string(),
            self.log_date_time_string(),
            msg,
        ))

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path.startswith("/api/state"):
            data = store.load()
            try:
                import psutil
                if sys.platform == "win32":
                    drive = os.path.splitdrive(ROOT)[0] + os.sep
                    disk_pct = round(psutil.disk_usage(drive).percent, 1)
                else:
                    disk_pct = round(psutil.disk_usage("/").percent, 1)
                data["sys"] = {
                    "cpu": round(psutil.cpu_percent(interval=None), 1),
                    "ram": round(psutil.virtual_memory().percent, 1),
                    "disk": disk_pct,
                }
            except Exception:
                pass
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path in ("/favicon.ico", "/favicon.png"):
            self.send_response(204)
            self.end_headers()
            return

        if path in ("/", "/index.html", "/hud"):
            self.path = "/jarvis_workplace.html"

        return super().do_GET()


def main():
    store.set_state("idle", "HUD online — start voice agent")
    store.add_chat("sys", "Holographic interface online. Waiting for voice agent.")

    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}/"
    print("=" * 55)
    print("  JARVIS HOLOGRAPHIC HUD SERVER")
    print("=" * 55)
    print(f"  Open:  {url}")
    print("  Keep this window open.")
    print("  In another terminal run:  python jarvis_voice.py")
    print("=" * 55)

    def open_browser():
        time.sleep(0.6)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nHUD server stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
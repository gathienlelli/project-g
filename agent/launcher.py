import os
import sys
import time
import subprocess
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
import psutil
from PIL import Image, ImageDraw
import pystray

# ============================
# НАСТРОЙКИ
# ============================

AGENT_DIR = r"G:\agent"
PANEL_DIR = r"G:\agent\web_panel\static"
PYTHON_EXE = r"G:\tools\python_env\Scripts\python.exe"
MAIN_SCRIPT = "main.py"

API_HOST = "127.0.0.1"
API_PORT = 8181

PANEL_HOST = "127.0.0.1"
PANEL_PORT = 8123


# ============================
# ПОИСК ПРОЦЕССОВ СЕРВЕРА
# ============================

def find_server_processes():
    result = []
    for p in psutil.process_iter(["pid", "cmdline", "cwd"]):
        try:
            cmd = p.info.get("cmdline") or []
            cwd = p.info.get("cwd") or ""
            if MAIN_SCRIPT in " ".join(cmd) and AGENT_DIR.lower() in cwd.lower():
                result.append(p)
        except:
            continue
    return result


# ============================
# ОПЕРАЦИИ С СЕРВЕРОМ
# ============================

def start_server():
    procs = find_server_processes()
    if procs:
        return f"[INFO] Server already running (PID: {procs[0].pid})"

    try:
        subprocess.Popen(
            [PYTHON_EXE, MAIN_SCRIPT],
            cwd=AGENT_DIR,
            creationflags=subprocess.DETACHED_PROCESS
        )
        time.sleep(1)

        procs = find_server_processes()
        if procs:
            return f"[OK] Server started (PID: {procs[0].pid})"
        else:
            return "[WARN] Server start requested, but process not detected."

    except Exception as e:
        return f"[ERROR] Failed to start server: {e}"


def stop_server():
    procs = find_server_processes()
    if not procs:
        return "[INFO] Server is not running."

    for p in procs:
        try:
            p.terminate()
        except:
            pass

    gone, alive = psutil.wait_procs(procs, timeout=5)

    if alive:
        for p in alive:
            try:
                p.kill()
            except:
                pass
        return "[OK] Server stopped with force."
    else:
        return "[OK] Server stopped."


def restart_server():
    stop_msg = stop_server()
    time.sleep(1)
    start_msg = start_server()
    return stop_msg + "\n" + start_msg


def status_server():
    procs = find_server_processes()
    if not procs:
        return "[INFO] Server is not running."
    else:
        return f"[INFO] Server running (PID: {procs[0].pid})"


# ============================
# HTTP API ДЛЯ ПАНЕЛИ
# ============================

class LauncherAPI(BaseHTTPRequestHandler):
    def _send(self, code, text):
        data = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path == "/start":
            self._send(200, start_server())
        elif path == "/stop":
            self._send(200, stop_server())
        elif path == "/restart":
            self._send(200, restart_server())
        elif path == "/status":
            self._send(200, status_server())
        else:
            self._send(404, "Unknown endpoint.")

    def log_message(self, *args):
        return


def run_api():
    print("API STARTING...")
    try:
        server = HTTPServer((API_HOST, API_PORT), LauncherAPI)
        print("SERVER CREATED")
        server.serve_forever()
    except Exception as e:
        print("API ERROR:", e)

    server = HTTPServer((API_HOST, API_PORT), LauncherAPI)
    server.serve_forever()


# ============================
# МИНИ-СЕРВЕР ПАНЕЛИ
# ============================

class PanelHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split("?", 1)[0]
        full = os.path.join(PANEL_DIR, path.lstrip("/"))
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        return full

    def log_message(self, *args):
        return


def run_panel():
    os.chdir(PANEL_DIR)
    server = HTTPServer((PANEL_HOST, PANEL_PORT), PanelHandler)
    webbrowser.open(f"http://{PANEL_HOST}:{PANEL_PORT}")
    server.serve_forever()


# ============================
# ИКОНКА В ТРЕЕ
# ============================

def create_icon():
    img = Image.new("RGB", (32, 32), "black")
    draw = ImageDraw.Draw(img)
    draw.text((10, 6), "A", fill="white")
    return img


def tray_thread():
    icon = pystray.Icon("Agent", create_icon(), "Agent Control")

    def open_panel():
        webbrowser.open(f"http://{PANEL_HOST}:{PANEL_PORT}")

    def exit_launcher():
        icon.stop()
        os._exit(0)

    icon.menu = pystray.Menu(
        pystray.MenuItem("Открыть панель", lambda: open_panel()),
        pystray.MenuItem("Перезапустить сервер", lambda: restart_server()),
        pystray.MenuItem("Остановить сервер", lambda: stop_server()),
        pystray.MenuItem("Выход", lambda: exit_launcher())
    )

    icon.run()


# ============================
# MAIN
# ============================

def main():
    if len(sys.argv) < 2:
        print("Usage: launcher.py start")
        return

    cmd = sys.argv[1].lower()

    if cmd == "start":
        threading.Thread(target=run_api, daemon=True).start()
        threading.Thread(target=run_panel, daemon=True).start()
        threading.Thread(target=tray_thread, daemon=True).start()
        start_server()

        while True:
            time.sleep(1)

    else:
        print("Unknown command.")


if __name__ == "__main__":
    main()

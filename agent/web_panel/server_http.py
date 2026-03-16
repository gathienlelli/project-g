import asyncio
import json
import os
import subprocess
import psutil

from agent.core.utils.logger import get_logger
from agent.core.server_status import get_full_status
from agent.core.server.main import is_paused, set_paused

logger = get_logger("http")

BASE_DIR = r"G:\agent\web_panel"
STATIC_DIR = os.path.join(BASE_DIR, "static")

HOST = "127.0.0.1"
PORT = 8080

LOG_DIR = r"G:\agent\logs"
WATCHDOG_PATH = r"G:\agent\services\watchdog\watchdog.py"
AHK_CLIENT_PATH = r"G:\agent\ahk\client.ahk"


def http_response(body, content_type="text/html", status="200 OK"):
    return (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}; charset=utf-8\r\n"
        f"Content-Length: {len(body.encode('utf-8'))}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"{body}"
    ).encode("utf-8")


def load_file(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ============================
# HELPERS: ACTIONS
# ============================

def action_restart_watchdog():
    if not os.path.exists(WATCHDOG_PATH):
        return {"ok": False, "error": "watchdog.py not found"}

    try:
        subprocess.Popen(["python", WATCHDOG_PATH], creationflags=subprocess.DETACHED_PROCESS)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def action_restart_ahk():
    if not os.path.exists(AHK_CLIENT_PATH):
        return {"ok": False, "error": "AHK client not found"}

    try:
        subprocess.Popen([AHK_CLIENT_PATH], creationflags=subprocess.DETACHED_PROCESS)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def action_open_logs():
    if not os.path.exists(LOG_DIR):
        return {"ok": False, "error": "Log directory not found"}

    try:
        os.startfile(LOG_DIR)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def action_restart_server():
    return {"ok": False, "error": "Soft restart not implemented yet"}


def get_metrics():
    if is_paused():
        return {"ok": True, "paused": True}

    try:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        return {
            "ok": True,
            "paused": False,
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "memory_used": mem.used,
            "memory_total": mem.total,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ============================
# MAIN HTTP HANDLER
# ============================

async def handle_http(reader, writer):
    try:
        data = await reader.read(4096)
        request = data.decode(errors="ignore")

        if not request:
            writer.close()
            return

        line = request.split("\n")[0]
        parts = line.split()
        if len(parts) < 2:
            writer.close()
            return

        method, path = parts[0], parts[1]

        logger.info(f"HTTP {method} {path}")

        # ---------- API: STATUS ----------
        if path == "/status.json":
            status = get_full_status()
            status["paused"] = is_paused()
            body = json.dumps(status, ensure_ascii=False, indent=2)
            writer.write(http_response(body, "application/json"))
            await writer.drain()
            writer.close()
            return

        # ---------- API: METRICS ----------
        if path == "/api/metrics":
            body = json.dumps(get_metrics(), ensure_ascii=False)
            writer.write(http_response(body, "application/json"))
            await writer.drain()
            writer.close()
            return

        # ---------- API: ACTIONS ----------
        if path == "/api/restart_watchdog":
            body = json.dumps(action_restart_watchdog(), ensure_ascii=False)
            writer.write(http_response(body, "application/json"))
            await writer.drain()
            writer.close()
            return

        if path == "/api/restart_ahk":
            body = json.dumps(action_restart_ahk(), ensure_ascii=False)
            writer.write(http_response(body, "application/json"))
            await writer.drain()
            writer.close()
            return

        if path == "/api/open_logs":
            body = json.dumps(action_open_logs(), ensure_ascii=False)
            writer.write(http_response(body, "application/json"))
            await writer.drain()
            writer.close()
            return

        if path == "/api/restart_server":
            body = json.dumps(action_restart_server(), ensure_ascii=False)
            writer.write(http_response(body, "application/json"))
            await writer.drain()
            writer.close()
            return

        # ---------- API: PAUSE / RESUME ----------
        if path == "/api/pause":
            set_paused(True)
            body = json.dumps({"ok": True, "paused": True}, ensure_ascii=False)
            writer.write(http_response(body, "application/json"))
            await writer.drain()
            writer.close()
            return

        if path == "/api/resume":
            set_paused(False)
            body = json.dumps({"ok": True, "paused": False}, ensure_ascii=False)
            writer.write(http_response(body, "application/json"))
            await writer.drain()
            writer.close()
            return

        # ---------- STATIC ----------
        if path.startswith("/static/"):
            file_path = os.path.join(STATIC_DIR, path.replace("/static/", ""))
            content = load_file(file_path)

            if content is None:
                writer.write(http_response("Not found", "text/plain", "404 Not Found"))
            else:
                ext = file_path.split(".")[-1]
                mime = {
                    "css": "text/css",
                    "js": "application/javascript",
                    "html": "text/html"
                }.get(ext, "text/plain")

                writer.write(http_response(content, mime))

            await writer.drain()
            writer.close()
            return

        # ---------- INDEX ----------
        if path == "/":
            index_path = os.path.join(STATIC_DIR, "index.html")
            content = load_file(index_path)

            if content is None:
                writer.write(http_response("index.html missing", "text/plain", "500 Internal Server Error"))
            else:
                writer.write(http_response(content))

            await writer.drain()
            writer.close()
            return

        # ---------- UNKNOWN ----------
        writer.write(http_response("Not found", "text/plain", "404 Not Found"))
        await writer.drain()
        writer.close()

    except Exception as e:
        logger.error(f"HTTP error: {e}")
        writer.close()


async def start_http_server():
    server = await asyncio.start_server(handle_http, HOST, PORT)
    logger.info(f"HTTP server started on http://{HOST}:{PORT}")
    return server

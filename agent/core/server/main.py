import asyncio
import websockets
import json
import traceback
import os
import importlib
import sys
import socket
import ctypes

from agent.core.utils.logger import get_logger
from agent.core.super_menu import run_command

# HTTP server
from agent.web_panel.server_http import start_http_server

logger = get_logger("server")

# ============================
# КОНФИГУРАЦИЯ
# ============================

REQUIRED_DIRS = [
    r"G:\agent\logs",
    r"G:\agent\configs",
    r"G:\agent\workflows",
    r"G:\agent\updates"
]

REQUIRED_MODULES = {
    "pywin32": ["win32gui", "win32con", "win32api"],
    "requests": ["requests"],
    "psutil": ["psutil"],
    "websockets": ["websockets"]
}

VENV_PATH = r"G:\tools\python_env\Scripts\python.exe"

AHK_CLIENT_PATH = r"G:\agent\ahk\client.ahk"
WATCHDOG_PATH = r"G:\agent\services\watchdog\watchdog.py"

WS_HOST = "0.0.0.0"
WS_PORT = 8765

MODULE_STATUS = {
    "pywin32": False,
    "requests": False,
    "psutil": False,
    "websockets": False,
}

ENV_STATUS = {
    "python_version_ok": False,
    "admin": False,
    "port_free": False,
    "ahk_client_exists": False,
    "watchdog_exists": False,
}

# ============================
# РЕЖИМ ПАУЗЫ
# ============================

AGENT_PAUSED = False

def is_paused():
    return AGENT_PAUSED

def set_paused(value: bool):
    global AGENT_PAUSED
    AGENT_PAUSED = value
    if value:
        logger.info("AGENT PAUSED")
    else:
        logger.info("AGENT RESUMED")


# ============================
# ПРОВЕРКИ
# ============================

def check_directories():
    logger.info("Checking directories...")
    for d in REQUIRED_DIRS:
        if not os.path.exists(d):
            try:
                os.makedirs(d)
                logger.warning(f"Directory created: {d}")
            except Exception as e:
                logger.error(f"Cannot create directory {d}: {e}")
        else:
            logger.info(f"[OK] {d}")


def check_venv():
    logger.info("Checking virtual environment...")
    if not os.path.exists(VENV_PATH):
        logger.warning("Virtual environment NOT found")
        return False
    logger.info("[OK] Virtual environment detected")
    return True


def check_modules():
    logger.info("Checking Python modules...")
    for name, imports in REQUIRED_MODULES.items():
        ok = True
        for imp in imports:
            try:
                importlib.import_module(imp)
            except Exception as e:
                ok = False
                logger.warning(f"[MISSING] {imp} ({name}) — {e}")

        MODULE_STATUS[name] = ok
        if ok:
            logger.info(f"[OK] {name}")
        else:
            logger.warning(f"{name} is NOT available")
    return MODULE_STATUS


def win32_available():
    return MODULE_STATUS.get("pywin32", False)

def requests_available():
    return MODULE_STATUS.get("requests", False)

def psutil_available():
    return MODULE_STATUS.get("psutil", False)

def websockets_available():
    return MODULE_STATUS.get("websockets", False)


def check_python_version():
    logger.info("Checking Python version...")
    major, minor = sys.version_info.major, sys.version_info.minor
    if major > 3 or (major == 3 and minor >= 11):
        ENV_STATUS["python_version_ok"] = True
        logger.info(f"[OK] Python {major}.{minor}")
    else:
        ENV_STATUS["python_version_ok"] = False
        logger.warning(f"Python {major}.{minor} — recommended 3.11+")


def check_admin():
    logger.info("Checking admin rights...")
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logger.warning(f"Admin check failed: {e}")
        is_admin = False

    ENV_STATUS["admin"] = is_admin
    if is_admin:
        logger.info("[OK] Admin rights detected")
    else:
        logger.warning("Not running as admin — some features may be limited")


def check_port_free(host, port):
    logger.info(f"Checking port {port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
        s.close()
        ENV_STATUS["port_free"] = True
        logger.info(f"[OK] Port {port} is free")
        return True
    except OSError as e:
        ENV_STATUS["port_free"] = False
        logger.warning(f"Port {port} is in use: {e}")
        return False


def check_ahk_client():
    logger.info("Checking AHK client...")
    if os.path.exists(AHK_CLIENT_PATH):
        ENV_STATUS["ahk_client_exists"] = True
        logger.info(f"[OK] AHK client found")
    else:
        ENV_STATUS["ahk_client_exists"] = False
        logger.warning("AHK client NOT found")


def check_watchdog():
    logger.info("Checking watchdog...")
    if os.path.exists(WATCHDOG_PATH):
        ENV_STATUS["watchdog_exists"] = True
        logger.info(f"[OK] Watchdog found")
    else:
        ENV_STATUS["watchdog_exists"] = False
        logger.warning("Watchdog NOT found")


# ============================
# ОБРАБОТКА КОМАНД
# ============================

async def handle_message(message):
    try:
        if is_paused():
            return json.dumps({"error": "agent_paused", "paused": True}, ensure_ascii=False)

        data = json.loads(message)
        cmd = data.get("cmd")
        args = data.get("args", {})

        if not win32_available():
            if cmd.startswith("window.") or cmd.startswith("browser."):
                return json.dumps({"error": "pywin32 not installed"}, ensure_ascii=False)

        if not requests_available():
            if cmd.startswith("network.") or cmd.startswith("ai."):
                return json.dumps({"error": "requests not installed"}, ensure_ascii=False)

        result = run_command(cmd, args)
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error("handle_message error:")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ============================
# WEBSOCKET-СЕРВЕР
# ============================

async def client_handler(websocket):
    logger.info("Client connected")

    try:
        async for message in websocket:
            if is_paused():
                await websocket.send(json.dumps({"paused": True}, ensure_ascii=False))
                continue

            response = await handle_message(message)
            await websocket.send(response)

    except Exception as e:
        logger.error(f"Client handler error: {e}")

    finally:
        logger.info("Client disconnected")


async def start_ws_server():
    logger.info("Starting WebSocket server...")
    async with websockets.serve(client_handler, WS_HOST, WS_PORT):
        logger.info(f"WebSocket server started on ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()


# ============================
# MAIN
# ============================

async def main():
    logger.info("Server starting...")

    check_directories()
    check_venv()
    check_modules()
    check_python_version()
    check_admin()
    check_ahk_client()
    check_watchdog()
    check_port_free(WS_HOST, WS_PORT)

    if not websockets_available():
        logger.error("websockets module not available")
        return

    http_server = await start_http_server()

    await asyncio.gather(
        start_ws_server(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        logger.error("Fatal server error:")
        logger.error(traceback.format_exc())

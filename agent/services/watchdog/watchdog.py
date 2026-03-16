import time
import json
import subprocess
import websocket
import psutil
import traceback

from agent.core.utils.logger import get_logger

logger = get_logger("watchdog")

SERVER_PROCESS_NAME = "python.exe"
SERVER_MAIN = r"G:\agent\core\server\main.py"
VENV = r"G:\tools\python_env\Scripts\Activate.ps1"

CHECK_INTERVAL = 5
WS_URL = "ws://127.0.0.1:8765"


# ============================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================

def is_server_running():
    """Проверяет, запущен ли python-процесс сервера"""
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            if proc.info["name"] and "python" in proc.info["name"].lower():
                if proc.info["cmdline"] and SERVER_MAIN in " ".join(proc.info["cmdline"]):
                    return True
        except:
            pass
    return False


def start_server():
    """Запускает сервер через PowerShell"""
    logger.warning("Starting server...")
    try:
        cmd = f"& '{VENV}'; python '{SERVER_MAIN}'"
        subprocess.Popen(["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", cmd])
        return True
    except Exception as e:
        logger.error(f"Start error: {e}")
        return False


def kill_server():
    """Убивает все python-процессы сервера"""
    logger.warning("Killing server...")
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            if proc.info["name"] and "python" in proc.info["name"].lower():
                if proc.info["cmdline"] and SERVER_MAIN in " ".join(proc.info["cmdline"]):
                    proc.kill()
        except:
            pass


def ws_check():
    """Проверяет, отвечает ли WebSocket"""
    try:
        ws = websocket.create_connection(WS_URL, timeout=2)
        ws.send('{"cmd":"ping","args":{}}')
        resp = ws.recv()
        ws.close()
        return True
    except:
        return False


# ============================
# ОСНОВНОЙ ЦИКЛ WATCHDOG
# ============================

def run(args=None):
    logger.info("Watchdog started")

    while True:
        try:
            # 1. Проверка процесса
            if not is_server_running():
                logger.error("Server process not running")
                start_server()
                time.sleep(3)
                continue

            # 2. Проверка WebSocket
            if not ws_check():
                logger.error("WebSocket not responding — restarting server")
                kill_server()
                time.sleep(1)
                start_server()
                time.sleep(3)
                continue

            logger.info("Server OK")

        except Exception as e:
            logger.error("Watchdog error:")
            logger.error(traceback.format_exc())

        time.sleep(CHECK_INTERVAL)

import os
import json
import subprocess
import time

from agent.core.utils.logger import get_logger
from agent.modules.workflow import main as workflow
from agent.modules.network import main as network
from agent.modules.window_control import main as window_control
from agent.modules.browser_control import main as browser_control
from agent.modules.ai import main as ai

logger = get_logger("super_menu")

CONFIGS = r"G:\agent\configs"
LOGS = r"G:\agent\logs"
WORKFLOWS = r"G:\agent\workflows"
UPDATER = r"G:\agent\services\updater\updater.py"
SERVER = r"G:\agent\core\server\main.py"
VENV = r"G:\tools\python_env\Scripts\Activate.ps1"


# ============================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================

def _run_ps(cmd):
    """Запуск PowerShell-команды"""
    try:
        subprocess.Popen(["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", cmd])
        return "OK"
    except Exception as e:
        return str(e)


def _run_python(path):
    """Запуск Python-скрипта в виртуальном окружении"""
    cmd = f"& '{VENV}'; python '{path}'"
    return _run_ps(cmd)


# ============================
# СЕРВЕР
# ============================

def server_start(args):
    logger.info("server_start()")
    return _run_python(SERVER)


def server_restart(args):
    logger.info("server_restart()")
    _run_ps("Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force")
    time.sleep(0.5)
    return _run_python(SERVER)


def server_stop(args):
    logger.info("server_stop()")
    return _run_ps("Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force")


# ============================
# ОБНОВЛЕНИЯ
# ============================

def update_check(args):
    logger.info("update_check()")
    latest = os.path.join(r"G:\agent\updates", "latest.txt")
    if not os.path.exists(latest):
        return {"error": "latest.txt not found"}

    with open(latest, "r", encoding="utf-8") as f:
        version = f.read().strip()

    return {"latest": version}


def update_install(args):
    logger.info("update_install()")
    return _run_python(UPDATER)


# ============================
# ЛОГИ И КОНФИГИ
# ============================

def open_logs(args):
    logger.info("open_logs()")
    return _run_ps(f"Start-Process explorer.exe '{LOGS}'")


def open_configs(args):
    logger.info("open_configs()")
    return _run_ps(f"Start-Process explorer.exe '{CONFIGS}'")


# ============================
# WORKFLOW
# ============================

def workflow_run(args):
    logger.info("workflow_run()")
    return workflow.run(args)


def workflow_file(args):
    logger.info("workflow_file()")
    return workflow.run_file(args)


# ============================
# NETWORK
# ============================

def net_ping(args):
    return network.ping(args)


def net_port(args):
    return network.port_check(args)


def net_ip_local(args):
    return network.local_ip(args)


def net_ip_external(args):
    return network.external_ip(args)


def net_url(args):
    return network.url_check(args)


def net_diag(args):
    return network.diagnostics(args)


# ============================
# WINDOW CONTROL
# ============================

def win_list(args):
    return window_control.list(args)


def win_activate(args):
    return window_control.activate(args)


def win_minimize(args):
    return window_control.minimize(args)


def win_maximize(args):
    return window_control.maximize(args)


def win_restore(args):
    return window_control.restore(args)


def win_move(args):
    return window_control.move(args)


def win_resize(args):
    return window_control.resize(args)


# ============================
# BROWSER CONTROL
# ============================

def browser_open(args):
    return browser_control.open_url(args)


def browser_new_tab(args):
    return browser_control.new_tab(args)


def browser_close_tab(args):
    return browser_control.close_tab(args)


def browser_next(args):
    return browser_control.next_tab(args)


def browser_prev(args):
    return browser_control.prev_tab(args)


def browser_refresh(args):
    return browser_control.refresh(args)


def browser_type(args):
    return browser_control.type_text(args)


# ============================
# AI
# ============================

def ai_ask(args):
    return ai.ask(args)


def ai_short(args):
    return ai.short(args)


def ai_status(args):
    return ai.status(args)


# ============================
# WATCHDOG (заглушка)
# ============================

def watchdog_toggle(args):
    logger.info("watchdog_toggle()")
    return {"status": "toggled"}


# ============================
# МЕНЮ КОМАНД
# ============================

COMMANDS = {
    # Server
    "server.start": server_start,
    "server.restart": server_restart,
    "server.stop": server_stop,

    # Updates
    "update.check": update_check,
    "update.install": update_install,

    # Logs / Configs
    "open.logs": open_logs,
    "open.configs": open_configs,

    # Workflow
    "workflow.run": workflow_run,
    "workflow.file": workflow_file,

    # Network
    "network.ping": net_ping,
    "network.port": net_port,
    "network.ip.local": net_ip_local,
    "network.ip.external": net_ip_external,
    "network.url": net_url,
    "network.diagnostics": net_diag,

    # Window control
    "window.list": win_list,
    "window.activate": win_activate,
    "window.minimize": win_minimize,
    "window.maximize": win_maximize,
    "window.restore": win_restore,
    "window.move": win_move,
    "window.resize": win_resize,

    # Browser control
    "browser.open": browser_open,
    "browser.new_tab": browser_new_tab,
    "browser.close_tab": browser_close_tab,
    "browser.next_tab": browser_next,
    "browser.prev_tab": browser_prev,
    "browser.refresh": browser_refresh,
    "browser.type": browser_type,

    # AI
    "ai.ask": ai_ask,
    "ai.short": ai_short,
    "ai.status": ai_status,

    # Watchdog
    "watchdog.toggle": watchdog_toggle,
}


# ============================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================

def run_command(cmd, args):
    logger.info(f"super_menu.run_command: {cmd}")

    if cmd not in COMMANDS:
        return {"error": f"Unknown command '{cmd}'"}

    try:
        return COMMANDS[cmd](args)
    except Exception as e:
        logger.error(f"Command error: {e}")
        return {"error": str(e)}

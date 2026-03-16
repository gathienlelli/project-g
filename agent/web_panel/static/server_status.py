import os
from agent.core.server.main import (
    MODULE_STATUS,
    ENV_STATUS,
    REQUIRED_DIRS
)


def get_directories_status():
    result = {}
    for d in REQUIRED_DIRS:
        result[d] = os.path.exists(d)
    return result


def get_full_status():
    return {
        "python_version_ok": ENV_STATUS.get("python_version_ok", False),
        "admin": ENV_STATUS.get("admin", False),

        "modules": {
            "pywin32": MODULE_STATUS.get("pywin32", False),
            "requests": MODULE_STATUS.get("requests", False),
            "psutil": MODULE_STATUS.get("psutil", False),
            "websockets": MODULE_STATUS.get("websockets", False),
        },

        "port_free": ENV_STATUS.get("port_free", False),
        "ahk_client_exists": ENV_STATUS.get("ahk_client_exists", False),
        "watchdog_exists": ENV_STATUS.get("watchdog_exists", False),

        "directories": get_directories_status()
    }

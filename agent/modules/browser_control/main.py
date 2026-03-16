import win32gui
import win32con
import win32api
import win32process
import time
import subprocess
import webbrowser

from agent.core.utils.logger import get_logger
logger = get_logger("browser_control")


# ============================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================

BROWSER_KEYWORDS = [
    "chrome", "google chrome",
    "edge", "microsoft edge",
    "brave",
    "opera",
    "firefox", "mozilla firefox"
]


def _enum_windows():
    windows = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title.strip():
                windows.append({"hwnd": hwnd, "title": title})
        return True

    win32gui.EnumWindows(callback, None)
    return windows


def _find_browser_window():
    """Ищет окно браузера по ключевым словам"""
    for w in _enum_windows():
        title = w["title"].lower()
        for key in BROWSER_KEYWORDS:
            if key in title:
                return w["hwnd"]
    return None


def _activate_window(hwnd):
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        return True
    except Exception as e:
        logger.error(f"Activate error: {e}")
        return False


def _send_keys(keys):
    """Отправка клавиш в активное окно"""
    for key in keys:
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)


# ============================
# ОСНОВНЫЕ КОМАНДЫ
# ============================

def open_url(args):
    url = args.get("url")
    logger.info(f"open_url() called with url={url}")

    if not url:
        return "Missing 'url'"

    try:
        webbrowser.open(url)
        logger.info("URL opened")
        return "OK"
    except Exception as e:
        logger.error(f"open_url error: {e}")
        return str(e)


def activate(args):
    logger.info("activate() called")

    hwnd = _find_browser_window()
    if not hwnd:
        return "Browser not found"

    if _activate_window(hwnd):
        logger.info("Browser activated")
        return "OK"
    else:
        return "Activation failed"


def new_tab(args):
    logger.info("new_tab() called")

    hwnd = _find_browser_window()
    if not hwnd:
        return "Browser not found"

    if not _activate_window(hwnd):
        return "Activation failed"

    _send_keys([0x11, 0x54])  # CTRL + T
    logger.info("New tab opened")
    return "OK"


def close_tab(args):
    logger.info("close_tab() called")

    hwnd = _find_browser_window()
    if not hwnd:
        return "Browser not found"

    if not _activate_window(hwnd):
        return "Activation failed"

    _send_keys([0x11, 0x57])  # CTRL + W
    logger.info("Tab closed")
    return "OK"


def next_tab(args):
    logger.info("next_tab() called")

    hwnd = _find_browser_window()
    if not hwnd:
        return "Browser not found"

    if not _activate_window(hwnd):
        return "Activation failed"

    _send_keys([0x11, 0x09])  # CTRL + TAB
    logger.info("Next tab")
    return "OK"


def prev_tab(args):
    logger.info("prev_tab() called")

    hwnd = _find_browser_window()
    if not hwnd:
        return "Browser not found"

    if not _activate_window(hwnd):
        return "Activation failed"

    _send_keys([0x11, 0x10, 0x09])  # CTRL + SHIFT + TAB
    logger.info("Previous tab")
    return "OK"


def refresh(args):
    logger.info("refresh() called")

    hwnd = _find_browser_window()
    if not hwnd:
        return "Browser not found"

    if not _activate_window(hwnd):
        return "Activation failed"

    _send_keys([0x74])  # F5
    logger.info("Page refreshed")
    return "OK"


def type_text(args):
    text = args.get("text")
    logger.info(f"type_text() called with text={text}")

    if not text:
        return "Missing 'text'"

    hwnd = _find_browser_window()
    if not hwnd:
        return "Browser not found"

    if not _activate_window(hwnd):
        return "Activation failed"

    try:
        for ch in text:
            win32api.keybd_event(ord(ch.upper()), 0, 0, 0)
            win32api.keybd_event(ord(ch.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.02)

        logger.info("Text typed")
        return "OK"
    except Exception as e:
        logger.error(f"type_text error: {e}")
        return str(e)

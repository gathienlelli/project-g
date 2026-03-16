import win32gui
import win32con
import win32api
import win32process

from agent.core.utils.logger import get_logger
logger = get_logger("window_control")


# ============================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================

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


def _find_window(title_part):
    title_part = title_part.lower()
    for w in _enum_windows():
        if title_part in w["title"].lower():
            return w["hwnd"]
    return None


# ============================
# ОСНОВНЫЕ КОМАНДЫ
# ============================

def list(args):
    """Вернуть список всех видимых окон"""
    logger.info("list() called")
    return _enum_windows()


def activate(args):
    """Активировать окно по части названия"""
    title = args.get("title")
    logger.info(f"activate() called with title={title}")

    if not title:
        return "Missing 'title'"

    hwnd = _find_window(title)
    if not hwnd:
        logger.error("Window not found")
        return "Window not found"

    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        logger.info("Window activated")
        return "OK"
    except Exception as e:
        logger.error(f"Activate error: {e}")
        return str(e)


def minimize(args):
    title = args.get("title")
    logger.info(f"minimize() called with title={title}")

    hwnd = _find_window(title)
    if not hwnd:
        return "Window not found"

    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        logger.info("Window minimized")
        return "OK"
    except Exception as e:
        logger.error(f"Minimize error: {e}")
        return str(e)


def maximize(args):
    title = args.get("title")
    logger.info(f"maximize() called with title={title}")

    hwnd = _find_window(title)
    if not hwnd:
        return "Window not found"

    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        logger.info("Window maximized")
        return "OK"
    except Exception as e:
        logger.error(f"Maximize error: {e}")
        return str(e)


def restore(args):
    title = args.get("title")
    logger.info(f"restore() called with title={title}")

    hwnd = _find_window(title)
    if not hwnd:
        return "Window not found"

    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        logger.info("Window restored")
        return "OK"
    except Exception as e:
        logger.error(f"Restore error: {e}")
        return str(e)


def move(args):
    title = args.get("title")
    x = args.get("x")
    y = args.get("y")
    logger.info(f"move() called with title={title}, x={x}, y={y}")

    hwnd = _find_window(title)
    if not hwnd:
        return "Window not found"

    try:
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]

        win32gui.MoveWindow(hwnd, x, y, width, height, True)
        logger.info("Window moved")
        return "OK"
    except Exception as e:
        logger.error(f"Move error: {e}")
        return str(e)


def resize(args):
    title = args.get("title")
    width = args.get("width")
    height = args.get("height")
    logger.info(f"resize() called with title={title}, width={width}, height={height}")

    hwnd = _find_window(title)
    if not hwnd:
        return "Window not found"

    try:
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]

        win32gui.MoveWindow(hwnd, x, y, width, height, True)
        logger.info("Window resized")
        return "OK"
    except Exception as e:
        logger.error(f"Resize error: {e}")
        return str(e)

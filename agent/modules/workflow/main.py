import time
import json
import importlib

from agent.core.utils.logger import get_logger
logger = get_logger("workflow")


# ============================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================

def _load_module(module_name):
    try:
        module_path = f"agent.modules.{module_name}.main"
        return importlib.import_module(module_path)
    except Exception as e:
        logger.error(f"Module load error: {module_name} — {e}")
        return None


def _execute_step(step):
    """
    step = {
        "cmd": "window_control.activate",
        "args": {"title": "Chrome"},
        "delay": 1
    }
    """
    logger.info(f"Executing step: {step}")

    if "cmd" not in step:
        logger.error("Missing 'cmd' in step")
        return {"error": "Missing 'cmd'"}

    cmd = step["cmd"]
    args = step.get("args", {})
    delay = step.get("delay", 0)

    module_name = cmd.split(".")[0]
    action_name = cmd.split(".")[1]

    module = _load_module(module_name)
    if not module:
        return {"error": f"Module '{module_name}' not found"}

    if not hasattr(module, action_name):
        return {"error": f"Action '{action_name}' not found in module '{module_name}'"}

    action = getattr(module, action_name)

    try:
        result = action(args)
        logger.info(f"Step result: {result}")
    except Exception as e:
        logger.error(f"Step error: {e}")
        result = {"error": str(e)}

    if delay > 0:
        logger.info(f"Delay {delay}s")
        time.sleep(delay)

    return result


# ============================
# ОСНОВНАЯ КОМАНДА: RUN
# ============================

def run(args):
    """
    args = {
        "steps": [
            {"cmd": "window_control.activate", "args": {"title": "Chrome"}, "delay": 1},
            {"cmd": "browser_control.new_tab", "delay": 1},
            {"cmd": "browser_control.open_url", "args": {"url": "https://google.com"}, "delay": 2}
        ]
    }
    """
    logger.info(f"workflow.run() called with args={args}")

    steps = args.get("steps")
    if not steps:
        return {"error": "Missing 'steps'"}

    results = []

    for step in steps:
        result = _execute_step(step)
        results.append(result)

        if isinstance(result, dict) and "error" in result:
            logger.error("Workflow stopped due to error")
            break

    logger.info("Workflow finished")
    return {"results": results}


# ============================
# ВЛОЖЕННЫЕ СЦЕНАРИИ
# ============================

def load(args):
    """
    Загружает сценарий из файла JSON
    args = {"path": "G:\\agent\\workflows\\example.json"}
    """
    path = args.get("path")
    logger.info(f"workflow.load() called with path={path}")

    if not path:
        return {"error": "Missing 'path'"}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info("Workflow loaded")
        return data
    except Exception as e:
        logger.error(f"Load error: {e}")
        return {"error": str(e)}


def run_file(args):
    """
    Запускает сценарий из файла
    args = {"path": "G:\\agent\\workflows\\example.json"}
    """
    logger.info(f"workflow.run_file() called with args={args}")

    loaded = load(args)
    if "error" in loaded:
        return loaded

    return run(loaded)

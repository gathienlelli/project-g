import json
import importlib

from agent.core.utils.logger import get_logger
logger = get_logger("router")

def load_module(module_name):
    try:
        module_path = f"agent.modules.{module_name}.main"
        return importlib.import_module(module_path)
    except Exception as e:
        logger.error(f"Module load error: {module_name} — {e}")
        return None

async def route(message: str):
    try:
        data = json.loads(message)
    except:
        logger.error("Invalid JSON")
        return {"error": "Invalid JSON"}

    logger.info(f"Routing: {data}")

    if "cmd" not in data:
        logger.error("Missing 'cmd'")
        return {"error": "Missing 'cmd'"}

    cmd = data["cmd"]
    args = data.get("args", {})

    module_name = cmd.split(".")[0]
    action_name = cmd.split(".")[1] if "." in cmd else "run"

    module = load_module(module_name)
    if not module:
        logger.error(f"Module not found: {module_name}")
        return {"error": f"Module '{module_name}' not found"}

    if not hasattr(module, action_name):
        logger.error(f"Action not found: {action_name}")
        return {"error": f"Action '{action_name}' not found in module '{module_name}'"}

    action = getattr(module, action_name)

    try:
        result = action(args)
        logger.info(f"Result: {result}")
        return {"result": result}
    except Exception as e:
        logger.error(f"Action error: {e}")
        return {"error": str(e)}

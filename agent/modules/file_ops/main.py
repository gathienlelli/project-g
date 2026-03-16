from agent.core.utils.logger import get_logger
logger = get_logger("file_ops")

def read(args):
    path = args.get("path")
    logger.info(f"read() called with path={path}")

    if not path:
        logger.error("Missing 'path'")
        return "Missing 'path'"

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            logger.info(f"File read OK: {path}")
            return content
    except Exception as e:
        logger.error(f"File read error: {e}")
        return str(e)

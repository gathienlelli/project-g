import json
from pathlib import Path

COMMAND_FILE = Path(r"G:\agent\ahk\command.json")

def parse_json_command(json_text: str):
    """Парсинг JSON-команды"""
    try:
        data = json.loads(json_text)
        action = data.get("action")
        params = data.get("params", {})
        return action, params
    except Exception as e:
        return None, None

def send_to_ahk_json(action: str, params: dict):
    """Преобразование JSON-команды в формат AHK"""
    # временно: передаём только action:param
    # позже сделаем полноценный JSON для AHK
    param_value = list(params.values())[0] if params else ""
    COMMAND_FILE.write_text(f"{action}:{param_value}", encoding="utf-8")

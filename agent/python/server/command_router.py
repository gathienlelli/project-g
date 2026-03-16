import json
from pathlib import Path
from json_handler import send_to_ahk_json
from file_ops import (
    file_create, file_read, file_delete,
    file_append, file_replace
)
from workflow_engine import run_workflow

PROTOCOL_FILE = Path(r"G:\agent\python\config\protocol.json")

with PROTOCOL_FILE.open("r", encoding="utf-8") as f:
    PROTOCOL = json.load(f)


def validate_command(action: str, params: dict):
    """Проверка команды по протоколу"""
    if action not in PROTOCOL["actions"]:
        return False, f"Unknown action: {action}"

    required = PROTOCOL["actions"][action]["params"]

    for p in required:
        if p not in params:
            return False, f"Missing parameter: {p}"

    return True, "OK"


def execute_command(action: str, params: dict):
    """Выполнение команды"""

    valid, msg = validate_command(action, params)
    if not valid:
        return False, msg

    # Локальные команды Python (не требуют AHK)
    if action == "file_create":
        return file_create(params["path"], params["content"])

    if action == "file_read":
        return file_read(params["path"])

    if action == "file_delete":
        return file_delete(params["path"])

    if action == "file_append":
        return file_append(params["path"], params["content"])

    if action == "file_replace":
        return file_replace(params["path"], params["content"])

    # Workflow
    if action == "workflow":
        return run_workflow(params["name"])

    # Всё остальное — отправляем AHK
    send_to_ahk_json(action, params)
    return True, "Sent to AHK"

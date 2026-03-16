import json
from pathlib import Path

WORKFLOW_DIR = Path(r"G:\agent\python\workflows")

def run_workflow(name: str):
    from command_router import execute_command  # ← фикс циклического импорта

    wf_file = WORKFLOW_DIR / f"{name}.json"

    if not wf_file.exists():
        return False, f"Workflow not found: {name}"

    data = json.loads(wf_file.read_text(encoding="utf-8"))
    steps = data.get("steps", [])

    for step in steps:
        action = step.get("action")
        params = step.get("params", {})

        ok, msg = execute_command(action, params)
        if not ok:
            return False, f"Error in step '{action}': {msg}"

    return True, f"Workflow '{name}' completed"

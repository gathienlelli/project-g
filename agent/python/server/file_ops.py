from pathlib import Path

def file_create(path: str, content: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return True, f"File created: {path}"

def file_read(path: str):
    p = Path(path)
    if not p.exists():
        return False, "File not found"
    return True, p.read_text(encoding="utf-8")

def file_delete(path: str):
    p = Path(path)
    if not p.exists():
        return False, "File not found"
    p.unlink()
    return True, f"File deleted: {path}"

def file_append(path: str, content: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(content)
    return True, f"Appended to file: {path}"

def file_replace(path: str, content: str):
    p = Path(path)
    if not p.exists():
        return False, "File not found"
    p.write_text(content, encoding="utf-8")
    return True, f"File replaced: {path}"

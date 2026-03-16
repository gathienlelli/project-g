import sys
import base64
from github import Github, Auth

# 🔑 Вставь сюда свой токен
TOKEN = "my_token"
REPO_NAME = "gathienlelli/project-g"

auth = Auth.Token(TOKEN)
g = Github(auth=auth)
repo = g.get_repo(REPO_NAME)

# 📂 Список файлов (корень или папка)
def list_files(path=""):
    files = repo.get_contents(path)
    print(f"📂 Содержимое '{path or 'корня'}':")
    print(f"DEBUG: получено {len(files)} элементов")
    for f in files:
        print(f"- {f.path} ({f.type})")

# 📂 Чтение файла
def read_file(path):
    file = repo.get_contents(path)
    content = base64.b64decode(file.content).decode("utf-8", errors="ignore")
    print(f"--- {path} ---\n{content}\n")
    return content

# 📦 Вывод всей структуры и содержимого
def dump_repo(path=""):
    items = repo.get_contents(path)
    print(f"DEBUG: получено {len(items)} элементов в {path or 'корне'}")
    for item in items:
        if item.type == "dir":
            print(f"\n📂 Папка: {item.path}")
            dump_repo(item.path)
        elif item.type == "file":
            content = base64.b64decode(item.content).decode("utf-8", errors="ignore")
            print(f"\n📄 Файл: {item.path}\n--- Содержимое ---\n{content}\n")

# 🚀 Парсер команд
def parse_command(command):
    cmd = command.lower()

    if cmd.startswith("список") or cmd.startswith("list"):
        parts = command.split()
        path = parts[1] if len(parts) > 1 else ""
        list_files(path)

    elif cmd.startswith("прочитай") or cmd.startswith("read"):
        parts = command.split()
        if len(parts) >= 2:
            read_file(parts[1])

    elif cmd.startswith("выведи всё") or cmd.startswith("dump"):
        dump_repo()

    else:
        print("❌ Не удалось распознать команду")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python github_manager.py \"твоя команда\"")
        sys.exit(1)

    command = " ".join(sys.argv[1:])
    parse_command(command)

# script name: sync_repo.py
# purpose: полная синхронизация диска G и репозитория GitHub с логами изменений
# session: Default (Chrome)

import os
import subprocess
import datetime

repo_path = "G:/project-d"
log_path = "G:/logs/sync_repo.log"

def log(message):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")

def sync_with_repo(repo_path):
    try:
        # Получаем статус с подробностями
        result = subprocess.run(["git", "-C", repo_path, "status", "--short"], capture_output=True, text=True)
        changes = result.stdout.strip()
        if changes:
            log("Detected changes:\n" + changes)
        else:
            log("No changes detected.")

        # Добавляем все новые и изменённые файлы
        subprocess.run(["git", "-C", repo_path, "add", "-A"], check=True)
        log("Added all changes.")

        # Коммитим изменения
        subprocess.run(["git", "-C", repo_path, "commit", "-m", "Full sync with disk G"], check=True)
        log("Commit created: Full sync with disk G")

        # Отправляем изменения на GitHub
        subprocess.run(["git", "-C", repo_path, "push"], check=True)
        log("Push successful. Repo fully matches disk G.")

        print("Synchronization complete.")
    except subprocess.CalledProcessError as e:
        log("Error during sync: " + str(e))
        print("Error during sync:", e)

if __name__ == "__main__":
    sync_with_repo(repo_path)

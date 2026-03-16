import os
import json
import time
import zipfile
import urllib.request
from datetime import datetime

from agent.core.utils.logger import get_logger

logger = get_logger("updater")

SETTINGS_PATH = r"G:\agent\configs\settings.json"
LATEST_PATH   = r"G:\agent\updates\latest.txt"
UPDATE_ZIP    = r"G:\agent\updates\update.zip"
UPDATE_DIR    = r"G:\agent\updates\versions"

def load_current_version():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    except Exception as e:
        logger.error(f"Error reading settings.json: {e}")
        return "0.0.0"

def load_latest_version():
    try:
        with open(LATEST_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error reading latest.txt: {e}")
        return None

def version_to_tuple(v):
    try:
        return tuple(map(int, v.split(".")))
    except:
        return (0, 0, 0)

def is_update_available():
    current = load_current_version()
    latest  = load_latest_version()

    if not latest:
        logger.error("No latest version info")
        return False

    logger.info(f"Current version: {current}, Latest: {latest}")

    return version_to_tuple(latest) > version_to_tuple(current)

def download_update(url):
    try:
        logger.info(f"Downloading update from {url}")
        urllib.request.urlretrieve(url, UPDATE_ZIP)
        logger.info("Download complete")
        return True
    except Exception as e:
        logger.error(f"Download error: {e}")
        return False

def install_update():
    try:
        logger.info("Installing update...")

        with zipfile.ZipFile(UPDATE_ZIP, "r") as zip_ref:
            zip_ref.extractall(UPDATE_DIR)

        logger.info("Update extracted")

        return True
    except Exception as e:
        logger.error(f"Install error: {e}")
        return False

def update_settings_version(new_version):
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["version"] = new_version

        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        logger.info(f"Updated version in settings.json → {new_version}")

    except Exception as e:
        logger.error(f"Error updating settings.json: {e}")

def run_updater():
    logger.info("Updater started")

    if not is_update_available():
        logger.info("No updates available")
        return False

    latest = load_latest_version()

    # Заглушка URL — позже заменим на реальный
    update_url = f"https://example.com/updates/{latest}.zip"

    if not download_update(update_url):
        return False

    if not install_update():
        return False

    update_settings_version(latest)

    logger.info("Update installed successfully")
    return True

import psutil
import time
import json
import asyncio
from datetime import datetime

from agent.core.utils.logger import get_logger
from agent.core.server.main import connected_clients

logger = get_logger("monitor")

REPORT_PATH = r"G:\agent\logs\system\monitor.json"

last_tick = time.time()

async def heartbeat():
    global last_tick
    while True:
        last_tick = time.time()
        await asyncio.sleep(1)

async def detect_freeze():
    global last_tick
    while True:
        if time.time() - last_tick > 5:
            logger.error("Event loop freeze detected!")
        await asyncio.sleep(2)

async def monitor_loop():
    logger.info("Monitor started")

    asyncio.create_task(heartbeat())
    asyncio.create_task(detect_freeze())

    while True:
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            uptime = time.time() - psutil.boot_time()
            clients = len(connected_clients)

            report = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cpu": cpu,
                "ram": ram,
                "uptime_sec": int(uptime),
                "clients": clients
            }

            with open(REPORT_PATH, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4, ensure_ascii=False)

            logger.info(f"Monitor: CPU={cpu}% RAM={ram}% Clients={clients}")

        except Exception as e:
            logger.error(f"Monitor error: {e}")

        await asyncio.sleep(5)

import socket
import subprocess
import requests
import time

from agent.core.utils.logger import get_logger
logger = get_logger("network")


# ============================
# PING
# ============================

def ping(args):
    host = args.get("host")
    count = args.get("count", 1)

    logger.info(f"ping() called with host={host}, count={count}")

    if not host:
        return {"error": "Missing 'host'"}

    try:
        # Windows ping
        cmd = ["ping", host, "-n", str(count)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        logger.info("Ping executed")
        return {
            "host": host,
            "output": result.stdout
        }

    except Exception as e:
        logger.error(f"Ping error: {e}")
        return {"error": str(e)}


# ============================
# PORT CHECK
# ============================

def port_check(args):
    host = args.get("host")
    port = args.get("port")

    logger.info(f"port_check() called with host={host}, port={port}")

    if not host or not port:
        return {"error": "Missing 'host' or 'port'"}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        result = sock.connect_ex((host, int(port)))
        sock.close()

        if result == 0:
            logger.info("Port is open")
            return {"host": host, "port": port, "open": True}
        else:
            logger.info("Port is closed")
            return {"host": host, "port": port, "open": False}

    except Exception as e:
        logger.error(f"Port check error: {e}")
        return {"error": str(e)}


# ============================
# LOCAL IP
# ============================

def local_ip(args):
    logger.info("local_ip() called")

    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)

        logger.info(f"Local IP: {ip}")
        return {"hostname": hostname, "ip": ip}

    except Exception as e:
        logger.error(f"Local IP error: {e}")
        return {"error": str(e)}


# ============================
# EXTERNAL IP
# ============================

def external_ip(args):
    logger.info("external_ip() called")

    try:
        ip = requests.get("https://api.ipify.org").text
        logger.info(f"External IP: {ip}")
        return {"ip": ip}

    except Exception as e:
        logger.error(f"External IP error: {e}")
        return {"error": str(e)}


# ============================
# URL CHECK
# ============================

def url_check(args):
    url = args.get("url")
    logger.info(f"url_check() called with url={url}")

    if not url:
        return {"error": "Missing 'url'"}

    try:
        r = requests.get(url, timeout=5)
        logger.info(f"URL status: {r.status_code}")
        return {"url": url, "status": r.status_code}

    except Exception as e:
        logger.error(f"URL check error: {e}")
        return {"error": str(e)}


# ============================
# FULL DIAGNOSTICS
# ============================

def diagnostics(args):
    logger.info("diagnostics() called")

    results = {}

    # Local IP
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        results["local_ip"] = ip
    except:
        results["local_ip"] = None

    # External IP
    try:
        ext = requests.get("https://api.ipify.org").text
        results["external_ip"] = ext
    except:
        results["external_ip"] = None

    # DNS test
    try:
        socket.gethostbyname("google.com")
        results["dns"] = True
    except:
        results["dns"] = False

    logger.info(f"Diagnostics: {results}")
    return results

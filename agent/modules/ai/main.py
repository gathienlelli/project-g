import requests
import json
from agent.core.utils.logger import get_logger

logger = get_logger("ai")

# ============================
# НАСТРОЙКИ
# ============================

# Пример для локальной модели через LM Studio / Ollama
DEFAULT_ENDPOINT = "http://127.0.0.1:1234/v1/chat/completions"
DEFAULT_MODEL = "local-model"

# Если локальной модели нет — включается fallback
FALLBACK_ENABLED = True


# ============================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================

def _call_local_llm(prompt):
    """
    Отправляет запрос в локальную LLM.
    Совместимо с LM Studio, Ollama, text-generation-webui.
    """
    try:
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }

        logger.info(f"Sending request to LLM: {len(prompt)} chars")

        r = requests.post(DEFAULT_ENDPOINT, json=payload, timeout=30)
        r.raise_for_status()

        data = r.json()
        logger.info("LLM response received")

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"LLM error: {e}")
        return None


def _fallback_response(prompt):
    """
    Заглушка, если локальная модель недоступна.
    """
    logger.warning("Fallback AI response used")

    return (
        "AI-модуль сейчас недоступен. "
        "Но я могу ответить заглушкой:\n\n"
        f"Ваш запрос: {prompt[:200]}..."
    )


# ============================
# ОСНОВНАЯ КОМАНДА: ai.ask
# ============================

def ask(args):
    """
    args = {
        "prompt": "Привет, объясни квантовую механику"
    }
    """
    prompt = args.get("prompt")
    logger.info(f"ai.ask() called with prompt length={len(prompt) if prompt else 0}")

    if not prompt:
        return {"error": "Missing 'prompt'"}

    # 1) Пытаемся вызвать локальную модель
    result = _call_local_llm(prompt)

    # 2) Если не получилось — fallback
    if not result:
        if FALLBACK_ENABLED:
            result = _fallback_response(prompt)
        else:
            return {"error": "AI engine unavailable"}

    return {"response": result}


# ============================
# КОРОТКАЯ КОМАНДА: ai.short
# ============================

def short(args):
    """
    args = {"prompt": "Сделай краткое резюме текста"}
    """
    prompt = args.get("prompt")
    logger.info("ai.short() called")

    if not prompt:
        return {"error": "Missing 'prompt'"}

    short_prompt = f"Сделай краткое резюме:\n\n{prompt}"

    result = _call_local_llm(short_prompt)
    if not result:
        result = _fallback_response(prompt)

    return {"response": result}


# ============================
# СИСТЕМНАЯ КОМАНДА: ai.status
# ============================

def status(args):
    """
    Проверяет доступность локальной модели
    """
    logger.info("ai.status() called")

    try:
        test = _call_local_llm("ping")
        if test:
            return {"status": "online", "engine": "local", "model": DEFAULT_MODEL}
        else:
            return {"status": "offline", "engine": "fallback"}
    except:
        return {"status": "offline", "engine": "fallback"}

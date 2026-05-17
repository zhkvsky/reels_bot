import logging
import os
from typing import List

import httpx

from services.prompts import build_prompt

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nvidia/nemotron-nano-9b-v2:free"


async def generate_idea(previous_ideas: List[str]) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY не установлен в переменных окружения.")

    prompt = build_prompt(previous_ideas)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/zhkvsky/reels_bot",
        "X-Title": "Reels Idea Bot",
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5, # чем ниже температура - тем формальнее ответ
        "top_p": 0.8,
        "max_tokens": 2048,
    }

    logger.info(f"Запрос к OpenRouter (модель: {MODEL})...")

    timeout = httpx.Timeout(connect=30.0, read=90.0, write=30.0, pool=10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            url=OPENROUTER_API_URL,
            headers=headers,
            json=payload,
        )

    logger.info(f"Статус: {response.status_code}")

    if response.status_code == 401:
        raise ValueError("Неверный OPENROUTER_API_KEY. Проверь ключ на openrouter.ai/keys")

    if response.status_code == 429:
        raise ValueError(
            "Превышен лимит запросов. Подожди 1–2 минуты и попробуй снова."
        )

    if response.status_code != 200:
        raise ValueError(
            f"OpenRouter вернул ошибку {response.status_code}: {response.text[:300]}"
        )

    data = response.json()

    if "error" in data:
        msg = data["error"].get("message", str(data["error"]))
        raise ValueError(f"OpenRouter ошибка: {msg}")

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise ValueError(f"Неожиданная структура ответа: {data}")

    if not content or not content.strip():
        raise ValueError("Модель вернула пустой ответ. Попробуй ещё раз.")

    logger.info(f"Идея получена ({len(content)} символов).")
    return content.strip()
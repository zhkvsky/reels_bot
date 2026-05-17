"""
services/gemini_service.py — интеграция с Gemini API.
Отвечает за формирование промпта и вызов модели gemini-2.0-flash.
"""

import logging
import os
from typing import List

import google.generativeai as genai

from services.prompts import build_prompt

logger = logging.getLogger(__name__)


def _get_gemini_client() -> genai.GenerativeModel:
    """
    Создаёт и возвращает клиент Gemini.
    Конфигурация происходит через переменную окружения GEMINI_API_KEY.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY не установлен в переменных окружения.")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": 1.1,        # Высокая температура для разнообразия
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 2048,
        },
    )
    return model


async def generate_idea(previous_ideas: List[str]) -> str:
    """
    Генерирует уникальную идею ролика через Gemini API.

    Args:
        previous_ideas: Список последних идей из БД (для исключения повторов).

    Returns:
        Отформатированный текст идеи в HTML.
    """
    model = _get_gemini_client()
    prompt = build_prompt(previous_ideas)

    logger.info("Отправляем запрос к Gemini API...")

    try:
        # Используем синхронный метод в executor, т.к. google-generativeai
        # не имеет нативного async API в стабильной версии
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(prompt),
        )

        if not response or not response.text:
            raise ValueError("Gemini вернул пустой ответ.")

        logger.info("Идея успешно сгенерирована Gemini.")
        return response.text.strip()

    except Exception as e:
        logger.exception(f"Ошибка Gemini API: {e}")
        raise
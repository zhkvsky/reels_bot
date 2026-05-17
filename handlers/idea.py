"""
handlers/idea.py — обработчик генерации идей.
Включает защиту от спама, вызов Gemini API и сохранение в БД.
"""

import logging
import time
from typing import Dict

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.main_keyboard import get_main_keyboard
from services.db_service import get_recent_ideas, save_idea
from services.gemini_service import generate_idea

logger = logging.getLogger(__name__)
router = Router()

# Словарь для защиты от спама: {user_id: timestamp последнего запроса}
_last_request: Dict[int, float] = {}

# Минимальный интервал между запросами (в секундах)
RATE_LIMIT_SECONDS = 5


def _is_rate_limited(user_id: int) -> float:
    """
    Проверяет, не превышен ли лимит запросов.
    Возвращает 0 если запрос разрешён, иначе — сколько секунд осталось ждать.
    """
    now = time.monotonic()
    last = _last_request.get(user_id, 0)
    elapsed = now - last
    if elapsed < RATE_LIMIT_SECONDS:
        return RATE_LIMIT_SECONDS - elapsed
    return 0


def _update_rate_limit(user_id: int) -> None:
    """Обновляет временну́ю метку последнего запроса пользователя."""
    _last_request[user_id] = time.monotonic()


async def handle_idea_request(message: Message) -> None:
    """
    Общая логика генерации идеи.
    Вызывается как из /idea, так и из нажатия кнопки.
    """
    user_id = message.from_user.id if message.from_user else 0

    # --- Защита от спама ---
    wait_seconds = _is_rate_limited(user_id)
    if wait_seconds > 0:
        await message.answer(
            f"⏳ Подожди ещё <b>{wait_seconds:.1f} сек.</b> перед следующей генерацией."
        )
        return

    _update_rate_limit(user_id)

    # --- Индикатор загрузки ---
    thinking_msg = await message.answer(
        "🧠 Генерирую уникальную идею для вашего ролика...\n"
        "<i>Это займёт несколько секунд</i>"
    )

    try:
        # --- Получаем последние идеи из БД для контекста ---
        recent_ideas = await get_recent_ideas(limit=30)
        logger.info(
            f"Передаю в Gemini {len(recent_ideas)} предыдущих идей как контекст."
        )

        # --- Генерируем идею через Gemini ---
        idea_text = await generate_idea(previous_ideas=recent_ideas)

        # --- Сохраняем в БД ---
        await save_idea(idea_text)
        logger.info("Идея успешно сохранена в БД.")

        # --- Удаляем сообщение-заглушку ---
        await thinking_msg.delete()

        # --- Отправляем результат ---
        # Telegram ограничивает сообщение до 4096 символов.
        # Если идея длиннее — разбиваем на части.
        max_length = 4000  # чуть меньше лимита, с запасом
        chunks = [
            idea_text[i : i + max_length]
            for i in range(0, len(idea_text), max_length)
        ]

        for idx, chunk in enumerate(chunks):
            if idx == len(chunks) - 1:
                # Последний (или единственный) кусок — с клавиатурой
                await message.answer(
                    text=chunk,
                    reply_markup=get_main_keyboard(),
                )
            else:
                await message.answer(text=chunk)

    except Exception as e:
        logger.exception(f"Ошибка при генерации идеи: {e}")
        await thinking_msg.delete()
        await message.answer(
            "❌ <b>Произошла ошибка при генерации идеи.</b>\n\n"
            "Попробуй ещё раз через несколько секунд.\n"
            f"<i>Детали: {str(e)[:200]}</i>",
            reply_markup=get_main_keyboard(),
        )


# --- Обработчик команды /idea ---
@router.message(Command("idea"))
async def cmd_idea(message: Message) -> None:
    """Обработчик команды /idea."""
    await handle_idea_request(message)


# --- Обработчик нажатия кнопки ---
@router.message(F.text == "🎬 Сгенерировать идею")
async def btn_idea(message: Message) -> None:
    """Обработчик нажатия кнопки 'Сгенерировать идею'."""
    await handle_idea_request(message)
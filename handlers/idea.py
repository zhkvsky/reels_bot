import logging
import time
from typing import Dict

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.main_keyboard import get_main_keyboard
from services.db_service import get_recent_ideas, save_idea
from services.service import generate_idea

logger = logging.getLogger(__name__)
router = Router()

# Словарь для защиты от спама: {user_id: timestamp последнего запроса}
_last_request: Dict[int, float] = {}

# Минимальный интервал между запросами (в секундах)
RATE_LIMIT_SECONDS = 5


def _is_rate_limited(user_id: int) -> float:
    now = time.monotonic()
    last = _last_request.get(user_id, 0)
    elapsed = now - last
    if elapsed < RATE_LIMIT_SECONDS:
        return RATE_LIMIT_SECONDS - elapsed
    return 0


def _update_rate_limit(user_id: int) -> None:
    _last_request[user_id] = time.monotonic()


async def handle_idea_request(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0

    wait_seconds = _is_rate_limited(user_id)
    if wait_seconds > 0:
        await message.answer(
            f"⏳ Подожди ещё <b>{wait_seconds:.1f} сек.</b> перед следующей генерацией."
        )
        return

    _update_rate_limit(user_id)

    thinking_msg = await message.answer(
        "🧠 Генерирую уникальную идею для вашего ролика...\n"
        "<i>Это займёт несколько секунд</i>"
    )

    try:
        recent_ideas = await get_recent_ideas(limit=30)
        logger.info(
            f"Передаю в Gemini {len(recent_ideas)} предыдущих идей как контекст."
        )

        idea_text = await generate_idea(previous_ideas=recent_ideas)

        await save_idea(idea_text)
        logger.info("Идея успешно сохранена в БД.")

        await thinking_msg.delete()

        # Telegram ограничивает сообщение до 4096 символов.
        # Если идея длиннее - разбиваем на части.
        max_length = 4000  # чуть меньше лимита, с запасом
        chunks = [
            idea_text[i : i + max_length]
            for i in range(0, len(idea_text), max_length)
        ]

        for idx, chunk in enumerate(chunks):
            if idx == len(chunks) - 1:
                await message.answer(
                    text=chunk,
                    reply_markup=get_main_keyboard(),
                )
            else:
                await message.answer(text=chunk)

    except ValueError as e:
        logger.error(f"Ошибка генерации: {e}")
        await thinking_msg.delete()
        err = str(e)
        if "rate" in err.lower() or "429" in err or "недоступно" in err:
            user_msg = (
                "⏳ <b>Модель временно перегружена.</b>\n\n"
                "OpenRouter ограничил бесплатный доступ — это норма в часы пик.\n"
                "Подожди <b>1–2 минуты</b> и попробуй снова. 🙏"
            )
        else:
            user_msg = (
                f"❌ <b>Ошибка генерации.</b>\n\n<i>{err[:300]}</i>"
            )
        await message.answer(user_msg, reply_markup=get_main_keyboard())

    except Exception as e:
        logger.exception(f"Неожиданная ошибка: {e}")
        await thinking_msg.delete()
        await message.answer(
            "❌ <b>Что-то пошло не так.</b>\n\nПопробуй ещё раз.",
            reply_markup=get_main_keyboard(),
        )


@router.message(Command("idea"))
async def cmd_idea(message: Message) -> None:
    await handle_idea_request(message)


@router.message(F.text == "🎬 Сгенерировать идею")
async def btn_idea(message: Message) -> None:
    await handle_idea_request(message)
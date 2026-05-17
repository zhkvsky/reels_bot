from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_keyboard import get_main_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:

    user_name = message.from_user.full_name if message.from_user else "друг"

    welcome_text = (
        f"👋 Привет, <b>{user_name}</b>!\n\n"
        "🎬 Я бот для генерации идей коротких видео (<b>Reels / TikTok / Shorts</b>) "
        "для компании декоративных покрытий и красок.\n\n"
        "✨ Каждая идея — уникальная, с полным сценарием, хуком, CTA и советами по вирусности.\n\n"
        "📌 <b>Что я умею:</b>\n"
        "  • Генерировать идеи роликов в разных стилях\n"
        "  • Запоминать предыдущие идеи — не повторяюсь!\n"
        "  • Описывать кадры, текст на экране, музыку и CTA\n\n"
        "👇 Нажми кнопку ниже или используй команду /idea"
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard(),
    )
"""
keyboards/main_keyboard.py — главная reply-клавиатура бота.
"""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Возвращает главную reply-клавиатуру с кнопкой генерации идеи.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎬 Сгенерировать идею")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Нажми кнопку для генерации идеи",
    )
    return keyboard
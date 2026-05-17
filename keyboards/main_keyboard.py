from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎬 Сгенерировать идею")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Нажми кнопку для генерации идеи",
    )
    return keyboard
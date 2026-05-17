import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

from handlers.start import router as start_router
from handlers.idea import router as idea_router
from services.db_service import init_db

# Загружаем переменные окружения из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def main() -> None:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        sys.exit(1)

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        logger.error("GEMINI_API_KEY не найден в переменных окружения!")
        sys.exit(1)

    # Инициализируем базу данных
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("База данных готова.")

    # Создаём экземпляр бота с HTML parse mode по умолчанию
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Создаём диспетчер
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(idea_router)

    logger.info("Бот запускается... Нажмите Ctrl+C для остановки.")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания. Завершение работы.")
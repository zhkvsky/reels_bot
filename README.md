# reels_bot
Telegram-бот для генерации уникальных идей коротких видео (Reels / TikTok / Shorts) для компании декоративных покрытий и красок.

# Стек
 
- Python 3.13
- aiogram 3
- OpenRouter API (В качестве LLM используется nvidia/nemotron-nano-9b-v2:free)
- SQLite + aiosqlite
- httpx
## Установка
 
```bash
git clone https://github.com/zhkvsky/reels_bot
cd reels_bot
 
python3.13 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
 
pip install -r requirements.txt
```
 
## Настройка
 
```bash
cp .env.example .env
```
 
Открой `.env` и заполни два значения:
 
```env
BOT_TOKEN=        # токен от @BotFather в Telegram
OPENROUTER_API_KEY=   # ключ с openrouter.ai
```

## Запуск
 
```bash
python bot.py
```
 
## Команды бота
 
| Команда | Действие                       |
|---|--------------------------------|
| `/start` | Приветствие                    |
| `/idea` | Сгенерировать идею             |
| 🎬 Сгенерировать идею | Сгенерировать идею, но кнопкой |
 
## Структура
 
```
reels_bot/
├── bot.py
├── handlers/
│   ├── start.py
│   └── idea.py
├── services/
│   ├── service.py   # OpenRouter API
│   ├── prompts.py
│   └── db_service.py
├── keyboards/
│   └── main_keyboard.py
├── database/
│   └── ideas.db            # создаётся автоматически
├── .env
└── requirements.txt
```
 
## Заметки
 
- Идеи сохраняются в SQLite, последние 30 передаются в промпт. Так бот будет повторяться с идеями гораздо реже (но, увы, это не панацея)
- Антиспам: 1 запрос в 5 секунд на пользователя.
- Бесплатный лимит OpenRouter: ~200 запросов в день.
 
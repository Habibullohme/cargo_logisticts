import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from app.api_client import ApiClient
from app.config import get_settings
from app.handlers import build_router


async def main() -> None:
    settings = get_settings()
    if not settings.bot_token:
        logging.error(
            "BOT_TOKEN topilmadi. @BotFather dan token olib, .env fayliga BOT_TOKEN=... deb yozing."
        )
        sys.exit(1)

    api = ApiClient()
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(api=api)  # `api` har bir handlerga avtomatik uzatiladi
    dp.include_router(build_router())

    logging.info("Bot ishga tushdi (long polling).")
    try:
        await dp.start_polling(bot)
    finally:
        await api.close()
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())

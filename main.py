import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config_reader import config
from autopapabot.handlers.user import user_commands
from autopapabot.handlers.admin import admin_commands
from aiogram.enums import ParseMode

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(admin_commands.router)
    dp.include_router(user_commands.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, dct={})


if __name__ == "__main__":
    asyncio.run(main())

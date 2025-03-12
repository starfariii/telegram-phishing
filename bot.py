from loader import *

from data.config import *
import logging, asyncio
from aiohttp import web

from middlewares.throttling import *
from middlewares.middleware_users import *

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler,
    setup_application,
)

from services.api_session import *

from handlers.admin import admin_base
from handlers.user import baseuser

import logging
import os

from aiogram.types import *



def main_webhook():
    arSession = AsyncRequestSession()

    logging.basicConfig(level=logging.INFO)
    
    main_dispatcher = Dispatcher(storage=storage)
    main_dispatcher.include_router(adminRouter)
    main_dispatcher.include_router(userRouter)

    
    app = web.Application()
    SimpleRequestHandler(dispatcher=main_dispatcher, bot=bot).register(app, path=f'/webhook/main/{TOKEN}/')

    setup_application(app, main_dispatcher, bot=bot)

    web.run_app(app, host='localhost', port=8080)
    

async def on_startup_longpool():
    await db.setup()
    createSettings = await db.add_settings()

    logger.success('Настройки успешно созданы!') if createSettings else logger.info('Настройки уже созданы!')

    settingsNow = await db.get_settings()

    logger.info(f'Актулаьные настрйоки: {settingsNow}')

    logger.info(createSettings)
    logger.success('Бот успешно запущен!')


async def on_shutdown_longpool() -> None:
    await db.close()
    logger.success('Бот выключается...')


async def main_longpool():
    arSession = AsyncRequestSession()

    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher(storage=storage)
    dp.include_router(adminRouter)
    dp.include_router(userRouter)
    dp.startup.register(on_startup_longpool)
    dp.shutdown.register(on_shutdown_longpool)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
   

if __name__ == "__main__":
    if DOMAIN == '':
        asyncio.run(main_longpool())
    else:
        main_webhook()
    
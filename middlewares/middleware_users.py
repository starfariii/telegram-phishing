import re
from aiogram import BaseMiddleware
from aiogram.types import User, TelegramObject, CallbackQuery
from utils.misc_func.otherfunc import clear_html, get_date
from typing import Callable, Dict, Any, Awaitable
from loguru import logger
from data.config import db




class ExistsUserMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        this_user: User = data.get("event_from_user")

        if event.media_group_id != None:
            return await handler(event, data)

        if not this_user.is_bot:
            await self.process_user(this_user, event, data)
            return await handler(event, data)
        return await handler(event, data)

    

    async def process_user(self, this_user: User, event: TelegramObject, data: Dict[str, Any]):
        user_id = this_user.id
        user_name = clear_html(this_user.full_name) or ""
        user_login = this_user.username or ""

        try:
            await db.add_user(user_id, user_login, user_name)
            
        except Exception as e:
            logger.exception(e)



        

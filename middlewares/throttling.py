# - *- coding: utf- 8 - *-
import time
from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, User
from cachetools import TTLCache
from loguru import logger

# Антиспам
class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, default_rate: Union[int, float] = 0.5) -> None:
        self.default_rate = default_rate

        self.users = TTLCache(maxsize=10_000, ttl=600)

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data):
        this_user: User = data.get("event_from_user")

        if get_flag(data, "rate") is not None:
            self.default_rate = get_flag(data, "rate")

        if self.default_rate == 0:
            return await handler(event, data)
        
        if event.media_group_id != None:
            return await handler(event, data)


        if this_user.id not in self.users:
            self.users[this_user.id] = {
                'last_throttled': int(time.time()),
                'count_throttled': 0,
                'now_rate': self.default_rate,
            }

            return await handler(event, data)
        
        

        else:
            if int(time.time()) - self.users[this_user.id]['last_throttled'] >= self.users[this_user.id]['now_rate']:
                self.users.pop(this_user.id)

                return await handler(event, data)
            else:
                self.users[this_user.id]['last_throttled'] = int(time.time())

                if self.users[this_user.id]['count_throttled'] == 0:
                    self.users[this_user.id]['count_throttled'] = 1
                    self.users[this_user.id]['now_rate'] = self.default_rate + 2

                    return await handler(event, data)
                elif self.users[this_user.id]['count_throttled'] == 1:
                    self.users[this_user.id]['count_throttled'] = 2
                    self.users[this_user.id]['now_rate'] = self.default_rate + 3

                    await event.reply(
                        "<b>❗ Пожалуйста, не спамьте.\n"
                        "❗ Please, do not spam.</b>",
                    )
                elif self.users[this_user.id]['count_throttled'] == 2:
                    self.users[this_user.id]['count_throttled'] = 3
                    self.users[this_user.id]['now_rate'] = self.default_rate + 5

                    await event.reply(
                        "<b>❗ Бот не будет отвечать до прекращения спама.\n"
                        "❗ The bot will not respond until the spam stops.</b>",
                    )


class ThrottlingMiddlewareRateLimit(BaseMiddleware):
    def __init__(self) -> None:
        # Кэш с TTL 10 секунд для каждого пользователя
        self.users = TTLCache(maxsize=10_000, ttl=15)

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data):
        user_id = event.from_user.id
        if user_id in self.users:
            # Пользователь уже отправлял сообщение в течение последних 10 секунд
            await event.answer("Пожалуйста, подождите 15 секунд.", True)
            return
        self.users[user_id] = True # Записываем пользователя в кэш
        return await handler(event, data)
    

class UserThrottlingMiddlewareRateLimit(BaseMiddleware):
    def __init__(self) -> None:
        # Кэш с TTL 10 секунд для каждого пользователя
        self.users = TTLCache(maxsize=10_000, ttl=5)

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data):
        user_id = event.from_user.id
        if user_id in self.users:
            # Пользователь уже отправлял сообщение в течение последних 10 секунд
            await event.answer("Пожалуйста, подождите 5 секунд и попробуйте снова.", True)
            return
        self.users[user_id] = True # Записываем пользователя в кэш
        return await handler(event, data)
# - *- coding: utf- 8 - *-
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from data.config import ADMIN, db
from aiogram import Bot, Dispatcher, F, Router
from loguru import logger
from typing import *
from utils.misc_func.otherfunc import get_date


class IsAdmin(BaseFilter):
    async def __call__(self, message: Union[Message, CallbackQuery]) -> bool:
       
        try:
            user = await db.get_user_info(message.from_user.id)

        except:
            user = None

        if user is None:
            return True

        if message.from_user.id in ADMIN or user['role'] in ['admin', 'owner']:
            return True
        else:
            return False
        

    

# Проверка на админа
class IsNotAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in ADMIN:
            return False
        else:
            return True


class IsChat(BaseFilter):
    async def __call__(self, message: Union[Message, CallbackQuery]) -> bool:

        try:
            type_ = message.chat.type

        except:
            type_ = message.message.chat.type

        logger.info(type_)

        if str(type_) != 'private':
            return True
        else:
            return False



class IsPrivate(BaseFilter):
    async def __call__(self, message: Union[Message, CallbackQuery]) -> bool:
        
        try:
            if message.chat.type == 'private':
                return True
            else:
                return False
            
        except:

            if message.message.chat.type == 'private':
                return True
            else:
                return False
      

class IsBan(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        
        user = await db.get_user_info_dict(message.from_user.id)

        logger.info(user)

        if user is None:
            return True

        if message.from_user.id in ADMIN or user['role'] != 'ban':
            return True
        else:
            return False





            

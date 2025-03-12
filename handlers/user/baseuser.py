from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import *
from typing import Any, Dict, Union
from loader import *
from keyboards.inline.userinlinekey import *
from loguru import logger
from utils.misc_func.bot_models import *

from typing import *
from data.config import KEY_DOMAIN


@userRouter.message(Command('start'))
async def startUser(msg: Message, state: FSM):

	user_id = msg.from_user.id
	user_name = clear_html(msg.from_user.full_name) or ""
	user_login = msg.from_user.username or ""

	await db.add_user(user_id, user_login, user_name)

	text = f"""
<b>🔐 Get VPN — бесплатный VPN сервис внутри телеграма!</b>

📱 Что бы получить конфигурацию нажмите кнопку "<b>🌐 Моя конфигурация</b>", если вы делаете это первый раз нужно будет пройти процесс авторизации через телеграм

<i>Инструкции как использовать VPN есть по соответствующим кнопкам ниже 👇</i>
"""
	
	return msg.answer(text, reply_markup=webAppKey(f'{KEY_DOMAIN}/redir?type=auth_account'))


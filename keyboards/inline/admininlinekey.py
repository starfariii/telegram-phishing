from aiogram.types import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import *
from aiogram.types.web_app_info import WebAppInfo


setApiConfigKey = InlineKeyboardBuilder()
setApiConfigKey.row(InlineKeyboardButton(text='🔐 Сменить', callback_data=f'change_api_config'))
setApiConfigKey = setApiConfigKey.as_markup()



def backFuncKey(call):
    key = InlineKeyboardBuilder()
    key.row(InlineKeyboardButton(text='⬅️ Вернуться', callback_data=call))
    return key.as_markup()
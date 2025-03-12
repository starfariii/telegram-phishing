from aiogram.types import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import *
from aiogram.types.web_app_info import WebAppInfo


def webAppKey(url):
	key = InlineKeyboardBuilder()
	
	key.row(InlineKeyboardButton(text='🌐 Моя конфигурация', web_app=WebAppInfo(url=url)))
	key.row(InlineKeyboardButton(text='💻 Windows', url='https://telegra.ph/Photo-Cloud--pravila-02-25'),
		 	InlineKeyboardButton(text='💻 Linux', url='https://telegra.ph/Photo-Cloud--pravila-02-25'))
	key.row(InlineKeyboardButton(text='🍏 MacOS', url='https://telegra.ph/Photo-Cloud--pravila-02-25'),
		 	InlineKeyboardButton(text='🍏 IOS', url='https://telegra.ph/Photo-Cloud--pravila-02-25'))
	key.row(InlineKeyboardButton(text='📱 Andriod', url='https://telegra.ph/Photo-Cloud--pravila-02-25'))
	return key.as_markup()
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import *

from utils.misc_func.bot_models import *
from utils.misc_func.otherfunc import *

from keyboards.reply.adminkey import *
from keyboards.inline.admininlinekey import *

from loader import *
import shutil
from data.config import SESSIONS_STORAGE

from states.admin_state import *


@adminRouter.message(Command('admin'))
async def admin_main_page(msg: Message, state: FSM):

	await state.clear()
	
	text = f'''
Добро пожаловать в <b>панель администратора!</b>

<i>Воспользуйтесь кнопками ниже для управления ботом 👇</i>
'''
	
	return msg.answer(text, reply_markup=kbMainAdmin())



@adminRouter.callback_query(F.data=='cancel_call')
async def cancel_call_page(call: CallbackQuery, state: FSM):

	await state.clear()

	await call.message.delete()

	text = f'''
Добро пожаловать в <b>панель администратора!</b>

<i>Воспользуйтесь кнопками ниже для управления ботом 👇</i>
'''
	
	await bot.send_message(call.from_user.id, text, reply_markup=kbMainAdmin())


@adminRouter.message(F.text=='👤 Выгрузка')
async def get_accounts_page(msg: Message, state: FSM):

	await msg.answer('⏳ Архив создается...')

	try:
		current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
		ARCHIVE_NAME = f'archive_{current_time}.zip'

		shutil.make_archive(ARCHIVE_NAME.replace('.zip', ''), 'zip', SESSIONS_STORAGE)

		await msg.answer_document(FSInputFile(ARCHIVE_NAME, ARCHIVE_NAME))

	except Exception as e:
		logger.exception(e)
		await msg.answer('�� Произошла ошибка при создании архива!')


@adminRouter.message(F.text=='🆔 Конфигурация')
async def setup_bot_page(msg: Message, state: FSM):
	await state.clear()

	settings = await db.get_settings()

	text = f'''
<b>🆔 Конфигурация</b>    
	
В этом разделе вы можете добавить/сменить API HASH и API ID для работы аккаунтов
Официальный сайт где можео взять API ID и API HASH: my.telegram.org

⚙️ Ваша конфигурация выглдяит так:
<b>API ID:</b> <tg-spoiler>{settings["api_id"] if settings["api_id"] != None else "отсутствует"}</tg-spoiler>
<b>API HASH:</b> <tg-spoiler>{settings["api_hash"] if settings["api_hash"] != None else "отсутствует"}</tg-spoiler>
'''

	return msg.answer(text, reply_markup=setApiConfigKey)


@adminRouter.message(F.data=='api_hash_id')
async def api_hash_id_page(call: CallbackQuery, state: FSM):
	await state.clear()

	settings = await db.get_settings()

	text = f'''
<b>🆔 Конфигурация</b>    
	
В этом разделе вы можете добавить/сменить API HASH и API ID для работы аккаунтов
Официальный сайт где можео взять API ID и API HASH: my.telegram.org

⚙️ Ваша конфигурация выглдяит так:
<b>API ID:</b> <tg-spoiler>{settings["api_id"] if settings["api_id"] != None else "отсутствует"}</tg-spoiler>
<b>API HASH:</b> <tg-spoiler>{settings["api_hash"] if settings["api_hash"] != None else "отсутствует"}</tg-spoiler>
'''

	return call.message.edit_text(text, reply_markup=setApiConfigKey)


@adminRouter.callback_query(F.data=='change_api_config')
async def change_api_config_page(call: CallbackQuery, state: FSM):

    text = f'''
<b>🔐 Смена API HASH и API_ID</b>

Для того что бы сменить API HASH и API_ID отрпавьте их в следущем формате в одном сообщении:

<code>e0e5b9677beee1f4d92a857d44355948
27856152</code>

Где первоя строка — API HASH
Вторая строка — API ID
'''
    
    await state.set_state(updateApiConfig.api_config)

    return call.message.edit_text(text, reply_markup=backFuncKey('api_hash_id'))


@adminRouter.message(updateApiConfig.api_config)
async def valid_api_config_page(msg: Message, state: FSM):

    try:
        API_HASH, API_ID = str(msg.text.split('\n')[0]), int(msg.text.split('\n')[1])

        valid = await validate_telegram_credentials(API_ID, API_HASH)

        if valid:
            await db.update_api_config(API_ID, API_HASH)
            await state.clear()

            text = f'''
<b>✅ Данные успешно изменены</b>
'''
            key = backFuncKey('api_hash_id')

            return msg.answer(text, reply_markup=key)

        else:
            raise ValueError("Данные не валдины")

    except Exception as e:
        logger.warning(e)
        await state.set_state(updateApiConfig.api_config)

        return msg.reply('⚠️ Кажется, вы ввели данные в неверном формате, попробуйте снова:', reply_markup=backFuncKey('api_hash_id'))


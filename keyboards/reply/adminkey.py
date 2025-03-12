from aiogram.types import *



def kbMainAdmin():

    key = [
            [
                KeyboardButton(text="👤 Выгрузка"),
                KeyboardButton(text="🆔 Конфигурация")
            ],
    ]
       
    keyReplayAdmin = ReplyKeyboardMarkup(
        keyboard=key,
        resize_keyboard=True,
        input_field_placeholder="Действуйте!"
    )

    return keyReplayAdmin

from aiogram.fsm.state import StatesGroup,State
from typing import Union



class updateApiConfig(StatesGroup):
    api_config = State()

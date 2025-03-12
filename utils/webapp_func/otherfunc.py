from data.config import BAD_SYMBOLS
from loguru import logger
import asyncio

def clear_phone_number(phone_number: str) -> str:
    try:
        for symbol in phone_number:
            if symbol in BAD_SYMBOLS:
                phone_number.replace(symbol, '')

        phone_number = int(phone_number)
        return str(phone_number)

    except Exception as e:
        logger.exception(e)
        return False
    

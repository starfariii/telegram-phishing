from data.config import TOKEN, db
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from typing import Any, Dict, Union
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, F, Router
from services.api_session import *
from utils.misc_func.filters import *

from fastapi import FastAPI, Response, Request, HTTPException, status, Depends, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware import Middleware
from fastapi.responses import RedirectResponse
from fastapi.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio, pytz
from apscheduler.schedulers.background import BackgroundScheduler

from contextlib import asynccontextmanager

from middlewares.middleware_users import *
from middlewares.throttling import *



userRouter = Router()
userRouter.message.filter(IsPrivate())
userRouter.callback_query.filter(IsPrivate())
userRouter.message.filter(IsPrivate())
userRouter.message.filter(IsBan())
userRouter.callback_query.filter(IsBan())
userRouter.message.middleware(ThrottlingMiddleware())

adminRouter = Router()
adminRouter.callback_query.filter(IsPrivate())
adminRouter.message.filter(IsPrivate())
adminRouter.message.filter(IsAdmin())
adminRouter.callback_query.filter(IsAdmin())

session = AiohttpSession()
bot_settings = {"session": session, "parse_mode": "HTML"}

bot = Bot(token=TOKEN, **bot_settings)

storage = MemoryStorage()

async def startup_event() -> None:
    await db.setup()

async def shutdown_event() -> None:
    await db.close()

app = FastAPI(on_startup=[startup_event], on_shutdown=[shutdown_event])
templates = Jinja2Templates(directory="templates")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



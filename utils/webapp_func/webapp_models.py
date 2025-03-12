from pydantic import BaseModel
from typing import Optional


class SendCode(BaseModel):
    phone_number: str
    init_data: str

class VerifyCode(BaseModel):
    code: str
    init_data: str


class Auth2FARequest(BaseModel):
    two_fa_code: str
    init_data: str

class InitData(BaseModel):
    init_data: str
    type_: str
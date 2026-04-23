from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class FormSubmit(BaseModel):
    name: str
    contact: str
    note: Optional[str] = None

class CouponGrab(BaseModel):
    coupon_id: int

class QueryParams(BaseModel):
    type: str  # form or coupon
    keyword: Optional[str] = None
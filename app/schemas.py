# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import date


# ユーザー登録用のスキーマ
class UserCreate(BaseModel):
    username: str  # ユーザー名
    birthdate: date
    email: EmailStr  # メールアドレス（形式チェック付き）
    address: str
    password: str = Field(..., min_length=1, max_length=72)  # パスワード
    
    

    class Config:
        from_attributes = True

# ユーザーログイン用のスキーマ
class UserLogin(BaseModel):
    email: EmailStr  
    password: str  

    class Config:
        from_attributes = True

# ギフト登録用スキーマ
class GiftCreate(BaseModel):
    id: str
    name: str
    description: str
    price: float
    material: List[str]
    size: List[str]
    notes: List[str]
    tags: List[str]
    product_url: str
    image_url: str


class CustomerUpdate(BaseModel):
    username: str
    birthdate: date
    email: EmailStr
    address: str

class UserResponse(BaseModel):
    username: str
    birthdate: date
    email: EmailStr
    address: str

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    username: str
    birthdate: date
    email: EmailStr
    address: str


class PurchaseRequest(BaseModel):
    payment_method: str
    address: str



# app/main.py
from fastapi import FastAPI, Request
from . import models
from . import crud, schemas
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.auth import routes, utils
from app.database import Base, engine
from app.auth.routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.gift.gift_api import router as gift_router
from app.auth.router_cart import router as cart_router
from app.products.router_products import router as products_router


# データベースを作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class User(BaseModel):
    name: str
    dob: str
    email: str
    address: str
    password: str

# CORS ミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://itoyuki-snow.github.io"],  # 必要に応じて特定のオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],  # すべての HTTP メソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)


@app.post("/register")
async def register(user: User):
    # 仮処理：登録内容を表示（実際はDB保存など）
    print("登録ユーザー：", user.dict())
    return {"message": f"{user.name}さん、登録ありがとうございます！"}

# CORS の設定
origins = [
    "http://localhost",  # フロントエンドが動作しているドメイン
    "http://127.0.0.1:3000",  # 必要に応じて他のオリジンも追加
]


app.include_router(auth_router, prefix="/auth")

app.include_router(gift_router, prefix="/gift")

app.include_router(cart_router, prefix="/purchase")

app.include_router(products_router)

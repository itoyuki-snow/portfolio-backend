from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.schemas import UserCreate, UserLogin, CustomerUpdate, UserUpdate, UserResponse
from app.models import Cart, User, Product, Gift, Customer, Order
from app.database import get_db
from app.auth.utils import ALGORITHM, SECRET_KEY, verify_password, get_password_hash, create_access_token, get_current_user
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List
from jose import JWTError, ExpiredSignatureError, jwt
from fastapi.responses import JSONResponse

# 認証ルーターを作成
router = APIRouter(tags=["auth"])


@router.options("/signup")
async def options_signup():
    return JSONResponse(
        content={"message": "CORS preflight OK"},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "https://itoyuki-snow.github.io",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

# トークンを取得するためのエンドポイントのURL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ユーザー登録エンドポイント
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    新しいユーザーを登録する
    """
    # ユーザー名またはメールアドレスが既に存在するか確認
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    if not user.password or len(user.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="パスワードは15文字以内で入力してください")

    print("受け取ったパスワード:", user.password)
    print("バイト長:", len(user.password.encode("utf-8")))

    # パスワードをハッシュ化して新しいユーザーを作成
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        birthdate=user.birthdate,
        address=user.address
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "アカウントが作成されました"}


# ログインエンドポイント
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    ログインしてアクセストークンを取得する
    """
    # ユーザーをデータベースから取得
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # JWTトークンを生成して返す
    access_token = create_access_token(user_id=db_user.id, expires_delta=timedelta(minutes=30))
    return {"token": access_token}

# 現在のユーザーを取得するヘルパー関数
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # type: ignore
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="トークンにユーザー情報が含まれていません")
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        
        return user

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="トークンの有効期限が切れています")
    except JWTError:
        raise HTTPException(status_code=403, detail="トークンの検証に失敗しました")



#マイページ

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(update_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/customers/{customer_id}", response_model=CustomerUpdate)
def update_customer(customer_id: int, update_data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)
    return customer










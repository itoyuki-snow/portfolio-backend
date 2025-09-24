from jose import JWTError, jwt,  ExpiredSignatureError # type: ignore # JWTトークンの生成と検証
from passlib.context import CryptContext  # type: ignore # パスワードのハッシュ化
from datetime import datetime, timedelta
from typing import List
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models import User
from app.database import get_db

# 秘密鍵とアルゴリズムの設定
SECRET_KEY = "your_secret_key"  # 実際のプロジェクトでは環境変数で管理
ALGORITHM = "HS256"  # ハッシュアルゴリズム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# パスワードのハッシュ化コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 平文のパスワードとハッシュ化されたパスワードを比較
def verify_password(plain_password, hashed_password):   
    #平文のパスワードがハッシュと一致するかを検証
    return pwd_context.verify(plain_password, hashed_password)

# パスワードをハッシュ化
def get_password_hash(password):
    return pwd_context.hash(password)

# アクセストークンの生成
def create_access_token(user_id: int, expires_delta: timedelta = None):
    """
    JWTトークンを生成（ユーザーIDをsubとして含める）
    """
    to_encode = {"sub": str(user_id)}  # ← ここが重要！
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# アクセストークンのデコード
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired") # type: ignore
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token") # type: ignore

# recommendation.py
def calculate_match_score(gift_tags: List[str], query_tags: List[str]) -> int:
    score = 0
    for q in query_tags:
        for g in gift_tags:
            if q in g or g in q:
                score += 1
    return score



def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

#def create_access_token(data: dict):
    #return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
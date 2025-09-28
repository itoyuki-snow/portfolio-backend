from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.auth.utils_email import send_order_confirmation_email
from app.schemas import PurchaseRequest, UserCreate, UserLogin, CustomerUpdate, UserUpdate, UserResponse
from app.models import Cart, User, Product, Gift, Customer, Order
from app.database import get_db
from app.auth.utils import verify_password, get_password_hash, create_access_token, get_current_user
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm.attributes import flag_modified

router = APIRouter(tags=["purchase"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.options("/signup")
async def options_signup():
    return Response(status_code=200)


# カート

# auth/router_cart.py
@router.get("/cart")
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id, items=[])
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return {"items": cart.items}

@router.post("/cart")
def add_to_cart(
    item: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == item["itemId"]).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品が見つかりません")

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id, items=[])
        db.add(cart)
        db.commit()
        db.refresh(cart)

    for existing in cart.items:
        if existing["id"] == product.id:
            existing["quantity"] += item["quantity"]
            break
    else:
        cart.items.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": item["quantity"]
        })

    flag_modified(cart, "items") 
    db.commit()
    return {"message": "商品をカートに入れました"}

@router.delete("/cart/{item_id}")
def delete_cart_item(item_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="カートが見つかりません")

    cart.items = [item for item in cart.items if item["id"] != item_id]
    flag_modified(cart, "items")
    db.commit()
    return {"message": "商品を削除しました"}

#商品登録

@router.post("/products/register_bulk")
def register_products_bulk(db: Session = Depends(get_db)):
    products = [
        Product(
            id="product1",
            name="澄み切ったスカイブルーとクリスタルハート",
            category="水色 / ピアス / イヤリング",
            price=3300,
            image="/images/product1.jpg"
        ),
        Product(
            id="product2",
            name="気品を纏うラベンダーハート",
            category="紫 / ピアス / イヤリング",
            price=3300,
            image="/images/product2.jpg"
        ),
        Product(
            id="product3",
            name="純真無垢なベビーピンクハート",
            category="ピンク / ピアス / イヤリング",
            price=3300,
            image="/images/product3.jpg"
        ),
        Product(
            id="product4",
            name="安らぎ与えるミントグリーンハート",
            category="緑 / ピアス / イヤリング",
            price=3300,
            image="/images/product4.jpg"
        ),
        Product(
            id="product5",
            name="雨空を彩る紫陽花",
            category="水色 / イヤーカフ / ピアス / イヤリング",
            price=2500,
            image="/images/product5.jpg"
        ),
        Product(
            id="product6",
            name="季節を運ぶ桜リング-雪月花の冬桜-",
            category="水色 / リング",
            price=2200,
            image="/images/product6.jpg"
        ),
    ]

    db.add_all(products)
    db.commit()
    return {"message": f"{len(products)} 件の商品を登録しました"}

@router.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()



#購入ページ
@router.post("/purchase")
def purchase(
    request: PurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="カートが空です")

    total_price = sum(item["price"] * item["quantity"] for item in cart.items) + 185

    order = Order(
        user=current_user,
        items=cart.items,
        total_price=total_price,
        payment_method=request.payment_method,
        address=request.address,
        created_at=datetime.utcnow()
    )

    db.add(order)
    cart.items = []
    flag_modified(cart, "items")
    db.commit()

    # ✅ メール送信
    send_order_confirmation_email(current_user.email, current_user.username)

    return {"message": "注文が完了しました"}


#追加情報
@router.get("/products/{product_id}")
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    return product

# app/products/router_products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product
from pydantic import BaseModel
from typing import List
from fastapi import Body


router = APIRouter(tags=["products"])

class ProductCreate(BaseModel):
    id: str
    name: str
    category: str
    price: int
    image: str

@router.post("/products/register_bulk")
def register_products_bulk(
    products: List[ProductCreate] = Body(...)
    , db: Session = Depends(get_db)
):
    registered = []
    for product in products:
        print("登録対象:", product.dict()) 
        if db.query(Product).filter(Product.id == product.id).first():
            continue
        try:
            db_product = Product(**product.dict())
            db.add(db_product)
            registered.append(product.id)
        except Exception as e:
            print("登録エラー:", e)

    db.commit()
    return {
        "message": f"{len(registered)} 件の商品を登録しました",
        "registered_ids": registered
    }


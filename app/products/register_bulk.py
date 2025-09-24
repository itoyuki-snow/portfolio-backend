
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Product
from app.database import get_db

router = APIRouter(tags=["products"])

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

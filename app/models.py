# app/models.py
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Float
from sqlalchemy.types import TypeDecorator, TEXT
import json
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class JsonEncodedList(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    birthdate = Column(DateTime)
    email = Column(String, unique=True, index=True, nullable=False)
    address = Column(String)
    hashed_password = Column(String)
    cart = relationship("Cart", back_populates="user", uselist=False)

# models.py
class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    items = Column(JSON)  # 例：{"item_id": 2, "quantity": 3}
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cart")


class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True)
    name = Column(String)
    category = Column(String)
    description = Column(String)
    price = Column(Integer)
    image = Column(String)
    tags = Column(JSON) 

class Gift(Base):
    __tablename__ = "gifts"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float)
    material = Column(JsonEncodedList)
    size = Column(JsonEncodedList)
    notes = Column(JsonEncodedList)
    tags = Column(JsonEncodedList)
    product_url = Column(String)
    image_url = Column(String)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    birthdate = Column(DateTime)
    email = Column(String, unique=True, index=True)
    address = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    items = Column(JSON)
    total_price = Column(Integer)
    payment_method = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class PurchaseRequest(BaseModel):
    payment_method: str
    address: str




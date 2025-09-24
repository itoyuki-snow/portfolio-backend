from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Gift
from pydantic import BaseModel
from typing import List
from fastapi import Body
from app.auth.utils import calculate_match_score
from app.schemas import GiftCreate


router = APIRouter(tags=["gift"])

class TagQuery(BaseModel):
    tags: List[str]

@router.post("/recommend")
def recommend_gift(query:  TagQuery = Body(...), db: Session = Depends(get_db)):
    all_gifts = db.query(Gift).all()
    scored = []

    for gift in all_gifts:
        if not gift.tags:
            continue
        match_score = calculate_match_score(gift.tags, query.tags)
        scored.append((gift, match_score))

    # 一致度がゼロなら、タグ数が近いギフトを返す
    if not scored or all(score == 0 for _, score in scored):
        fallback = sorted(all_gifts, key=lambda g: abs(len(g.tags) - len(query.tags)))
        return fallback[:2]

    # スコア順に並べて上位を返す
    scored.sort(key=lambda x: x[1], reverse=True)
    return [g for g, _ in scored[:2]]

@router.post("/create")
def create_gift(gift: GiftCreate, db: Session = Depends(get_db)):
    db_gift = Gift(**gift.dict())
    db.add(db_gift)
    db.commit()
    db.refresh(db_gift)
    return db_gift

@router.delete("/gift/{gift_id}", response_model=dict)
def delete_gift(gift_id: str, db: Session = Depends(get_db)):
    gift = db.query(Gift).filter(Gift.id == gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="ギフトが見つかりません")
    
    db.delete(gift)
    db.commit()
    return {"message": f"ギフト '{gift_id}' を削除しました"}












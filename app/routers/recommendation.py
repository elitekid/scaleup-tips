from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.schemas import AllTopCardsResponse
from app.services.card_service import CardService
from app.core.database import get_db

router = APIRouter()

@router.get("/top5", response_model=AllTopCardsResponse)
def get_all_top_5_cards(db: Session = Depends(get_db)):
    service = CardService()
    categories = service.get_all_top_5_cards(db)
    return AllTopCardsResponse(categories=categories)
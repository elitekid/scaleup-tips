from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class BenefitType(str, Enum):
    DISCOUNT = "할인"
    CASHBACK = "적립"

class CardRecommendation(BaseModel):
    card_id: int
    profit_id: int
    category_name: str
    card_name: str
    card_company: str
    total_score: float = Field(..., ge=0.0, le=1.0, description="총 점수 (0-1)")
    benefit_details: Dict[str, Any]
    rank: int = Field(..., ge=1, description="카테고리 내 순위")
    annual_fee: Optional[int] = Field(None, ge=0, description="연회비")
    
    @validator('total_score')
    def validate_score(cls, v):
        return round(v, 4)

class BenefitTypeCards(BaseModel):
    benefit_type: BenefitType
    cards: List[CardRecommendation]
    count: int = Field(..., description="해당 혜택 타입의 카드 수")

class CardRecommendationResponse(BaseModel):
    profit_biz_kind_name: str = Field(..., description="업종명")
    discount_cards: BenefitTypeCards = Field(..., description="할인 혜택 상위 5개")
    cashback_cards: BenefitTypeCards = Field(..., description="적립 혜택 상위 5개")
    generated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database_connected: bool
    version: str
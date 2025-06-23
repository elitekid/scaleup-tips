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

class CardRecommendationResponse(BaseModel):
    benefit_type: BenefitType
    category: Optional[str] = None
    recommendations: List[CardRecommendation]
    total_count: int
    generated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CategoryInfo(BaseModel):
    name: str
    card_count: int = Field(..., ge=0)
    avg_score: float = Field(..., ge=0.0, le=1.0)
    max_score: float = Field(..., ge=0.0, le=1.0)

class CategoriesResponse(BaseModel):
    benefit_type: BenefitType
    categories: List[CategoryInfo]
    total_categories: int

class CategoryTopCards(BaseModel):
    category_name: str
    cards: List[CardRecommendation]

class CategoryRecommendationResponse(BaseModel):
    benefit_type: BenefitType
    categories: List[CategoryTopCards]
    total_categories: int

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database_connected: bool
    version: str
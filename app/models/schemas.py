from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class CardScore(BaseModel):
    card_id: int
    profit_id: int
    kind_name: str
    benefit_type: str
    kind_name_rank: int
    total_score: float

class AllTopCardsResponse(BaseModel):
    categories: Dict[str, List[CardScore]]

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database_connected: bool
    version: str
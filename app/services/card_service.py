from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.schemas import CardScore

class CardService:
    
    def get_all_top_5_cards(self, db: Session) -> Dict[str, List[CardScore]]:
        query = """
        SELECT card_id, profit_id, kind_name, benefit_type, kind_name_rank, total_score
        FROM solomon.card_category_scores
        WHERE kind_name_rank <= 5
        ORDER BY kind_name, kind_name_rank ASC
        """
        
        result = db.execute(text(query))
        rows = result.fetchall()
        
        categories = {}
        for row in rows:
            kind_name = row.kind_name
            if kind_name not in categories:
                categories[kind_name] = []
            
            categories[kind_name].append(CardScore(
                card_id=row.card_id,
                profit_id=row.profit_id,
                kind_name=row.kind_name,
                benefit_type=row.benefit_type,
                kind_name_rank=row.kind_name_rank,
                total_score=float(row.total_score)
            ))
        
        return categories
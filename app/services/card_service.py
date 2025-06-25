from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.models.schemas import CardRecommendation, BenefitType, BenefitTypeCards

logger = logging.getLogger(__name__)

class CardService:
    
    async def get_top_cards_by_kind(
        self,
        profit_biz_kind_name: str,
        db: Session,
        limit_per_type: int = 5
    ) -> Dict[str, BenefitTypeCards]:
        """업종별 할인/적립 상위 N개 카드 조회"""
        
        try:
            logger.info(f"업종별 카드 추천 조회: {profit_biz_kind_name}, 각 타입별 {limit_per_type}개")
            
            # 할인과 적립 각각 조회
            results = {}
            
            for benefit_type in ["할인", "적립"]:
                query = """
                SELECT 
                    s.card_id,
                    s.profit_id,
                    s.kind_name as category_name,
                    s.benefit_type,
                    s.kind_name_rank as `rank`,
                    s.total_score,
                    s.benefit_value_score,
                    s.convenience_score,
                    s.accessibility_score,
                    s.profit_biz_cate_name,
                    s.profit_biz_kind_name,
                    s.profit_type_name,
                    -- 카드 상세 정보 (임시 더미 데이터)
                    COALESCE(c.card_name, CONCAT('카드 ', s.card_id)) as card_name,
                    COALESCE(c.card_company, '카드사') as card_company,
                    COALESCE(c.annual_fee, 0) as annual_fee
                FROM solomon.card_category_scores s
                LEFT JOIN (
                    SELECT DISTINCT card_id, 
                        CONCAT('카드 ', card_id) as card_name,
                        '카드사' as card_company,
                        0 as annual_fee
                    FROM solomon.card_category_scores
                ) c ON s.card_id = c.card_id
                WHERE s.profit_biz_kind_name = :kind_name
                AND s.benefit_type = :benefit_type
                ORDER BY s.total_score DESC, s.kind_name_rank ASC
                LIMIT :limit
                """
                
                result = db.execute(text(query), {
                    "kind_name": profit_biz_kind_name,
                    "benefit_type": benefit_type,
                    "limit": limit_per_type
                })
                rows = result.fetchall()
                
                # CardRecommendation 객체 생성
                cards = []
                for row in rows:
                    cards.append(CardRecommendation(
                        card_id=row.card_id,
                        profit_id=row.profit_id,
                        category_name=row.category_name,
                        card_name=row.card_name,
                        card_company=row.card_company,
                        total_score=float(row.total_score),
                        benefit_details=self._extract_benefit_details(row),
                        rank=row.rank,
                        annual_fee=row.annual_fee
                    ))
                
                # BenefitTypeCards 객체 생성
                benefit_enum = BenefitType.DISCOUNT if benefit_type == "할인" else BenefitType.CASHBACK
                results[benefit_type] = BenefitTypeCards(
                    benefit_type=benefit_enum,
                    cards=cards,
                    count=len(cards)
                )
                
                logger.info(f"{benefit_type} 카드 {len(cards)}개 조회 완료")
            
            return results
            
        except Exception as e:
            logger.error(f"업종별 카드 추천 조회 중 오류: {e}")
            raise
    
    async def get_available_kinds(self, db: Session) -> List[str]:
        """이용 가능한 업종 목록 조회"""
        
        try:
            query = """
            SELECT DISTINCT profit_biz_kind_name
            FROM solomon.card_category_scores
            WHERE profit_biz_kind_name IS NOT NULL 
            AND profit_biz_kind_name != ''
            ORDER BY profit_biz_kind_name
            """
            
            result = db.execute(text(query))
            rows = result.fetchall()
            
            kinds = [row.profit_biz_kind_name for row in rows]
            logger.info(f"이용 가능한 업종 {len(kinds)}개 조회 완료")
            
            return kinds
            
        except Exception as e:
            logger.error(f"업종 목록 조회 중 오류: {e}")
            raise
            
    def _extract_benefit_details(self, row) -> Dict[str, Any]:
            """점수 상세 정보 추출"""
            return {
                "benefit_value_score": round(float(row.benefit_value_score), 4),
                "convenience_score": round(float(row.convenience_score), 4),
                "accessibility_score": round(float(row.accessibility_score), 4),
                "category": row.profit_biz_cate_name,
                "subcategory": row.profit_biz_kind_name,
                "benefit_type": row.profit_type_name
            }
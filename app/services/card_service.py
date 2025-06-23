from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
import logging

from app.models.schemas import CardRecommendation, BenefitType, CategoryInfo, CategoryTopCards

logger = logging.getLogger(__name__)

class CardService:
    
    async def get_top_recommendations(
        self,
        benefit_type: BenefitType,
        category: Optional[str],
        limit: int,
        db: Session
    ) -> List[CardRecommendation]:
        """카테고리별 상위 카드 조회"""
        
        try:
            # 기본 쿼리 - ETL 테이블에서 직접 조회
            base_query = """
            SELECT 
                s.card_id,
                s.profit_id,
                s.kind_name as category_name,
                s.benefit_type,
                s.kind_name_rank as rank,
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
            WHERE s.benefit_type = :benefit_type
            """
            
            params = {"benefit_type": benefit_type.value}
            
            # 카테고리 필터 추가
            if category:
                base_query += " AND s.kind_name = :category"
                params["category"] = category
            
            # 정렬 및 제한
            base_query += """
            ORDER BY s.total_score DESC, s.kind_name_rank ASC
            LIMIT :limit
            """
            params["limit"] = limit
            
            result = db.execute(text(base_query), params)
            rows = result.fetchall()
            
            # 응답 객체 생성
            recommendations = []
            for row in rows:
                recommendations.append(CardRecommendation(
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
            
            logger.info(f"추천 조회 완료: {len(recommendations)}개")
            return recommendations
            
        except Exception as e:
            logger.error(f"추천 조회 중 오류: {e}")
            raise
    
    async def get_available_categories(
        self, 
        benefit_type: BenefitType, 
        db: Session
    ) -> List[CategoryInfo]:
        """이용 가능한 카테고리 목록과 카드 수 조회"""
        
        try:
            query = """
            SELECT 
                kind_name,
                COUNT(DISTINCT card_id) as card_count,
                AVG(total_score) as avg_score,
                MAX(total_score) as max_score
            FROM solomon.card_category_scores
            WHERE benefit_type = :benefit_type
            GROUP BY kind_name
            ORDER BY avg_score DESC, card_count DESC
            """
            
            result = db.execute(text(query), {"benefit_type": benefit_type.value})
            rows = result.fetchall()
            
            categories = []
            for row in rows:
                categories.append(CategoryInfo(
                    name=row.kind_name,
                    card_count=row.card_count,
                    avg_score=round(float(row.avg_score), 4),
                    max_score=round(float(row.max_score), 4)
                ))
            
            return categories
            
        except Exception as e:
            logger.error(f"카테고리 조회 중 오류: {e}")
            raise
    
    async def get_all_categories_top_cards(
        self,
        benefit_type: BenefitType,
        top_n: int,
        db: Session
    ) -> List[CategoryTopCards]:
        """모든 카테고리별 상위 N개 카드 조회"""
        
        try:
            query = """
            SELECT 
                s.*,
                COALESCE(c.card_name, CONCAT('카드 ', s.card_id)) as card_name,
                COALESCE(c.card_company, '카드사') as card_company,
                COALESCE(c.annual_fee, 0) as annual_fee
            FROM (
                SELECT *,
                       ROW_NUMBER() OVER (PARTITION BY kind_name ORDER BY total_score DESC) as rn
                FROM solomon.card_category_scores
                WHERE benefit_type = :benefit_type
            ) s
            LEFT JOIN (
                SELECT DISTINCT card_id, 
                    CONCAT('카드 ', card_id) as card_name,
                    '카드사' as card_company,
                    0 as annual_fee
                FROM solomon.card_category_scores
            ) c ON s.card_id = c.card_id
            WHERE s.rn <= :top_n
            ORDER BY s.kind_name, s.total_score DESC
            """
            
            result = db.execute(text(query), {
                "benefit_type": benefit_type.value,
                "top_n": top_n
            })
            rows = result.fetchall()
            
            # 카테고리별로 그룹화
            categories_dict = {}
            for row in rows:
                category = row.kind_name
                if category not in categories_dict:
                    categories_dict[category] = CategoryTopCards(
                        category_name=category,
                        cards=[]
                    )
                
                categories_dict[category].cards.append(CardRecommendation(
                    card_id=row.card_id,
                    profit_id=row.profit_id,
                    category_name=row.kind_name,
                    card_name=row.card_name,
                    card_company=row.card_company,
                    total_score=float(row.total_score),
                    benefit_details=self._extract_benefit_details(row),
                    rank=row.kind_name_rank,
                    annual_fee=row.annual_fee
                ))
            
            return list(categories_dict.values())
            
        except Exception as e:
            logger.error(f"카테고리별 상위 카드 조회 중 오류: {e}")
            raise
    
    async def get_card_details(self, card_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """특정 카드의 상세 정보 조회"""
        
        try:
            query = """
            SELECT 
                s.card_id,
                s.profit_id,
                s.kind_name,
                s.benefit_type,
                s.total_score,
                s.benefit_value_score,
                s.convenience_score,
                s.accessibility_score,
                s.kind_name_rank,
                s.profit_biz_cate_name,
                s.profit_biz_kind_name,
                s.profit_type_name,
                COUNT(*) OVER() as total_benefits
            FROM solomon.card_category_scores s
            WHERE s.card_id = :card_id
            ORDER BY s.total_score DESC
            """
            
            result = db.execute(text(query), {"card_id": card_id})
            rows = result.fetchall()
            
            if not rows:
                return None
            
            # 카드 기본 정보 (첫 번째 행 기준)
            first_row = rows[0]
            
            card_details = {
                "card_id": first_row.card_id,
                "card_name": f"카드 {first_row.card_id}",
                "card_company": "카드사",
                "total_benefits": first_row.total_benefits,
                "benefits": []
            }
            
            # 혜택별 상세 정보
            for row in rows:
                card_details["benefits"].append({
                    "profit_id": row.profit_id,
                    "category": row.kind_name,
                    "benefit_type": row.benefit_type,
                    "total_score": float(row.total_score),
                    "rank": row.kind_name_rank,
                    "details": self._extract_benefit_details(row)
                })
            
            return card_details
            
        except Exception as e:
            logger.error(f"카드 상세 조회 중 오류: {e}")
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
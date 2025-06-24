from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List
from sqlalchemy.orm import Session
import logging

from app.models.schemas import CardRecommendationResponse
from app.services.card_service import CardService
from app.core.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

def get_card_service() -> CardService:
    return CardService()

@router.get("/{profit_biz_kind_name}", response_model=CardRecommendationResponse)
async def get_card_recommendations(
    profit_biz_kind_name: str = Path(..., description="업종명 (예: 편의점, 주유소, 마트)"),
    limit: int = Query(5, ge=1, le=10, description="각 혜택 타입별 추천 개수"),
    db: Session = Depends(get_db),
    card_service: CardService = Depends(get_card_service)
):
    """
    업종별 카드 추천 조회
    - 지정된 업종에 대해 할인/적립 혜택별로 상위 N개씩 추천
    - 각 혜택 타입별로 총점 기준 정렬된 카드 목록 반환
    """
    try:
        logger.info(f"카드 추천 요청: 업종={profit_biz_kind_name}, 개수={limit}")
        
        # 업종별 할인/적립 카드 조회
        results = await card_service.get_top_cards_by_kind(
            profit_biz_kind_name=profit_biz_kind_name,
            limit_per_type=limit,
            db=db
        )
        
        # 결과가 없는 경우 처리
        discount_result = results.get("할인")
        cashback_result = results.get("적립")
        
        if (not discount_result or discount_result.count == 0) and \
           (not cashback_result or cashback_result.count == 0):
            raise HTTPException(
                status_code=404, 
                detail=f"업종 '{profit_biz_kind_name}'에 대한 카드 데이터를 찾을 수 없습니다."
            )
        
        # 빈 결과 처리 (한쪽만 없는 경우 빈 객체 생성)
        from app.models.schemas import BenefitType, BenefitTypeCards
        
        if not discount_result or discount_result.count == 0:
            discount_result = BenefitTypeCards(
                benefit_type=BenefitType.DISCOUNT,
                cards=[],
                count=0
            )
            
        if not cashback_result or cashback_result.count == 0:
            cashback_result = BenefitTypeCards(
                benefit_type=BenefitType.CASHBACK,
                cards=[],
                count=0
            )
        
        # 응답 생성
        response = CardRecommendationResponse(
            profit_biz_kind_name=profit_biz_kind_name,
            discount_cards=discount_result,
            cashback_cards=cashback_result
        )
        
        logger.info(f"추천 완료: 할인 {discount_result.count}개, 적립 {cashback_result.count}개")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카드 추천 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"카드 추천 조회 실패: {str(e)}")

@router.get("/kinds", response_model=List[str])
async def get_available_kinds(
    db: Session = Depends(get_db),
    card_service: CardService = Depends(get_card_service)
):
    """이용 가능한 업종 목록 조회"""
    try:
        kinds = await card_service.get_available_kinds(db)
        return kinds
        
    except Exception as e:
        logger.error(f"업종 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"업종 목록 조회 실패: {str(e)}")
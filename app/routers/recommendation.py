from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from app.models.schemas import (
    CardRecommendationResponse, 
    BenefitType,
    CategoryRecommendationResponse,
    CategoriesResponse
)
from app.services.card_service import CardService
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

def get_card_service() -> CardService:
    return CardService()

@router.get("/recommend/{benefit_type}", response_model=CardRecommendationResponse)
async def get_recommendations(
    benefit_type: BenefitType,
    category: Optional[str] = Query(None, description="업종명 (예: 편의점, 주유소)"),
    limit: int = Query(
        settings.DEFAULT_RECOMMENDATION_LIMIT, 
        ge=1, 
        le=settings.MAX_RECOMMENDATION_LIMIT, 
        description="추천 개수"
    ),
    db: Session = Depends(get_db),
    card_service: CardService = Depends(get_card_service)
):
    """
    사전 계산된 카드 점수 기반 추천 조회
    - ETL로 생성된 card_category_scores 테이블에서 조회
    - 실시간 ML 추론 없이 빠른 응답
    """
    try:
        logger.info(f"추천 요청: benefit_type={benefit_type}, category={category}, limit={limit}")
        
        recommendations = await card_service.get_top_recommendations(
            benefit_type=benefit_type,
            category=category,
            limit=limit,
            db=db
        )
        
        logger.info(f"추천 결과: {len(recommendations)}개")
        
        return CardRecommendationResponse(
            benefit_type=benefit_type,
            category=category,
            recommendations=recommendations,
            total_count=len(recommendations)
        )
        
    except Exception as e:
        logger.error(f"추천 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"추천 조회 실패: {str(e)}")

@router.get("/categories/{benefit_type}", response_model=CategoriesResponse)
async def get_available_categories(
    benefit_type: BenefitType,
    db: Session = Depends(get_db),
    card_service: CardService = Depends(get_card_service)
):
    """이용 가능한 업종 카테고리 목록 조회"""
    try:
        categories = await card_service.get_available_categories(benefit_type, db)
        
        return CategoriesResponse(
            benefit_type=benefit_type,
            categories=categories,
            total_categories=len(categories)
        )
        
    except Exception as e:
        logger.error(f"카테고리 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"카테고리 조회 실패: {str(e)}")

@router.get("/categories/{benefit_type}/top-cards", response_model=CategoryRecommendationResponse)
async def get_category_top_cards(
    benefit_type: BenefitType,
    top_n: int = Query(3, ge=1, le=10, description="각 카테고리별 상위 N개"),
    db: Session = Depends(get_db),
    card_service: CardService = Depends(get_card_service)
):
    """모든 카테고리별 상위 N개 카드 조회 (메인 화면용)"""
    try:
        result = await card_service.get_all_categories_top_cards(benefit_type, top_n, db)
        
        return CategoryRecommendationResponse(
            benefit_type=benefit_type,
            categories=result,
            total_categories=len(result)
        )
        
    except Exception as e:
        logger.error(f"카테고리별 상위 카드 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"카테고리별 상위 카드 조회 실패: {str(e)}")

@router.get("/card/{card_id}")
async def get_card_details(
    card_id: int,
    db: Session = Depends(get_db),
    card_service: CardService = Depends(get_card_service)
):
    """특정 카드의 상세 정보 조회"""
    try:
        card_details = await card_service.get_card_details(card_id, db)
        
        if not card_details:
            raise HTTPException(status_code=404, detail="카드를 찾을 수 없습니다")
        
        return card_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카드 상세 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"카드 상세 조회 실패: {str(e)}")
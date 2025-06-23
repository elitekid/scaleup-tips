from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.models.schemas import HealthResponse
from app.core.database import get_db, test_db_connection

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """헬스체크 엔드포인트"""
    try:
        # 데이터베이스 연결 확인
        db_connected = test_db_connection()
        
        return HealthResponse(
            status="healthy" if db_connected else "unhealthy",
            timestamp=datetime.now(),
            database_connected=db_connected,
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"헬스체크 실패: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            database_connected=False,
            version="1.0.0"
        )

@router.get("/ready")
async def readiness_check():
    """쿠버네티스 readiness probe용"""
    return {"status": "ready"}

@router.get("/live")
async def liveness_check():
    """쿠버네티스 liveness probe용"""
    return {"status": "alive"}

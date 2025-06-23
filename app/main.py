from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.core.config import settings
from app.routers import recommendation, health

app = FastAPI(
    title="Card Recommendation API",
    description="Pre-computed Card Recommendation Service",
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None
)

# 보안 미들웨어
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(recommendation.router, prefix="/api/v1/card-recommendation", tags=["recommendation"])

@app.get("/")
async def root():
    return {"message": "Card Recommendation API", "version": "1.0.0", "status": "running"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
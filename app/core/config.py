from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
import os

# 현재 환경을 결정 (default: local)
env = os.getenv("ENV", "local")
env_file = f".env.{env}"

# 환경별 .env 파일 로드 (파일이 존재할 때만)
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"환경 파일 로드: {env_file}")
else:
    print(f"환경 파일 없음: {env_file}, 환경변수만 사용")

class Settings(BaseSettings):
    # 환경 설정
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 데이터베이스 설정
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW"))
    
    # 보안 설정 - 수동으로 파싱
    _allowed_hosts: str = os.getenv("ALLOWED_HOSTS")
    _allowed_origins: str = os.getenv("ALLOWED_ORIGINS")
    
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """쉼표로 구분된 문자열을 리스트로 변환"""
        if self._allowed_hosts:
            return [host.strip() for host in self._allowed_hosts.split(",")]
        return []
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """쉼표로 구분된 문자열을 리스트로 변환"""
        if self._allowed_origins:
            return [origin.strip() for origin in self._allowed_origins.split(",")]
        return []
    
    # API 설정
    API_PREFIX: str = "/api/v1"
    MAX_RECOMMENDATION_LIMIT: int = int(os.getenv("MAX_RECOMMENDATION_LIMIT"))
    DEFAULT_RECOMMENDATION_LIMIT: int = int(os.getenv("DEFAULT_RECOMMENDATION_LIMIT"))
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL")
    
    class Config:
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        current_env = os.getenv("ENV", "local")
        print(f"설정 로드 완료: ENV={current_env}, ENVIRONMENT={self.ENVIRONMENT}")
        print(f"DATABASE_URL={self.DATABASE_URL}")
        print(f"ALLOWED_HOSTS={self.ALLOWED_HOSTS}")
        print(f"ALLOWED_ORIGINS={self.ALLOWED_ORIGINS}")
        print(f"LOG_LEVEL={self.LOG_LEVEL}")

settings = Settings()
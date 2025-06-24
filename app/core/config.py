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
    ENVIRONMENT: str
    DEBUG: bool = False
    
    # 데이터베이스 설정
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int
    DATABASE_MAX_OVERFLOW: int
    
    # 보안 설정 - 문자열로 받고 property로 변환
    ALLOWED_HOSTS: str
    ALLOWED_ORIGINS: str
    
    # API 설정
    API_PREFIX: str = "/api/v1"
    MAX_RECOMMENDATION_LIMIT: int
    DEFAULT_RECOMMENDATION_LIMIT: int
    
    # 로깅 설정
    LOG_LEVEL: str
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """ALLOWED_HOSTS를 리스트로 변환"""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """ALLOWED_ORIGINS를 리스트로 변환"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        current_env = os.getenv("ENV", "local")
        print(f"설정 로드 완료: ENV={current_env}, ENVIRONMENT={self.ENVIRONMENT}")
        print(f"DATABASE_URL={self.DATABASE_URL}")
        print(f"ALLOWED_HOSTS={self.allowed_hosts_list}")
        print(f"ALLOWED_ORIGINS={self.allowed_origins_list}")
        print(f"LOG_LEVEL={self.LOG_LEVEL}")

settings = Settings()
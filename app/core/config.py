from typing import List
from dotenv import load_dotenv
import os
import sys

# 현재 환경을 결정 (default: local)
env = os.getenv("ENV", "local")
env_file = f".env.{env}"

# 환경별 .env 파일 로드
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"Loaded config from {env_file}")
else:
    print(f"Config file {env_file} not found, using defaults")

class Settings:
    def __init__(self):
        # 환경 설정
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        
        # 🔒 데이터베이스 설정 - 필수 환경변수 검증
        self.DATABASE_URL = self._get_required_env("DATABASE_URL")
        self.DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
        self.DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
        
        # 보안 설정
        allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
        self.ALLOWED_HOSTS = self._parse_list(allowed_hosts)
        
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        self.ALLOWED_ORIGINS = self._parse_list(allowed_origins)
        
        # API 설정
        self.API_PREFIX = "/api/v1"
        self.MAX_RECOMMENDATION_LIMIT = int(os.getenv("MAX_RECOMMENDATION_LIMIT", "50"))
        self.DEFAULT_RECOMMENDATION_LIMIT = int(os.getenv("DEFAULT_RECOMMENDATION_LIMIT", "10"))
        
        # 로깅 설정
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # 설정값 검증 및 로깅 (민감정보 마스킹)
        self._log_config()
    
    def _get_required_env(self, key: str) -> str:
        """필수 환경변수 검증"""
        value = os.getenv(key)
        if not value:
            print(f"❌ ERROR: Required environment variable '{key}' is not set!")
            print(f"Please set {key} in your .env.{self.ENVIRONMENT} file")
            sys.exit(1)
        return value
    
    def _parse_list(self, value: str) -> List[str]:
        """콤마 구분 문자열을 리스트로 변환"""
        return [item.strip() for item in value.split(",") if item.strip()]
    
    def _log_config(self):
        """설정값 로깅 (민감정보 마스킹)"""
        print(f"Environment: {self.ENVIRONMENT}")
        print(f"Debug: {self.DEBUG}")
        print(f"Database URL: {self._mask_url(self.DATABASE_URL)}")
        print(f"Allowed Hosts: {self.ALLOWED_HOSTS}")
        print(f"Allowed Origins: {self.ALLOWED_ORIGINS}")
    
    def _mask_url(self, url: str) -> str:
        """DB URL에서 비밀번호 마스킹"""
        if "@" in url and "://" in url:
            # mysql+pymysql://user:password@host:port/db -> mysql+pymysql://user:***@host:port/db
            parts = url.split("://")
            if len(parts) == 2:
                scheme = parts[0]
                remaining = parts[1]
                if "@" in remaining:
                    auth_part, host_part = remaining.split("@", 1)
                    if ":" in auth_part:
                        user, _ = auth_part.split(":", 1)
                        return f"{scheme}://{user}:***@{host_part}"
        return url

# 전역 설정 인스턴스
settings = Settings()
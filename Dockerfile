# Python 3.13 기반 이미지 사용
FROM python:3.13-slim

# 환경 변수 설정 (Docker 환경을 develop으로 설정)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV=develop

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# .env.develop 파일 복사
COPY .env.develop .env.develop

# 포트 노출
EXPOSE 8090

# 실행 명령어
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
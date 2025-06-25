# Card Recommendation API

FastAPI 기반의 카드 추천 서비스입니다. 업종별로 할인/적립 혜택이 우수한 카드들을 사전 계산된 점수 기준으로 추천합니다.

## 프로젝트 개요

### 핵심 기능
- **업종별 카드 추천**: 편의점, 주유소, 마트 등 업종별 최적 카드 추천
- **혜택 타입별 분류**: 할인형/적립형 카드를 구분하여 제공
- **사전 계산된 점수**: ETL 프로세스를 통해 미리 계산된 객관적 점수 기반 추천
- **고성능 API**: 실시간 계산 없이 빠른 응답 제공

### 기술 스택
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: MySQL
- **ETL**: Apache Airflow (별도 프로세스)
- **Environment**: Python 3.13, Docker

## 로컬 환경 구성

### 1. 환경 설정 파일 생성

프로젝트 루트에 `.env.local` 파일을 생성하세요:

```env
# .env.local
ENVIRONMENT=local
DEBUG=True
DATABASE_URL=mysql+pymysql://root:1234@localhost:3305/solomon
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
ALLOWED_HOSTS=localhost,127.0.0.1
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
MAX_RECOMMENDATION_LIMIT=50
DEFAULT_RECOMMENDATION_LIMIT=10
LOG_LEVEL=DEBUG
```

### 2. 의존성 설치 및 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
export ENV=local

# API 서버 실행
python -m app.main
```

서버가 실행되면 다음 주소에서 접근 가능합니다:
- API 서버: http://localhost:8090
- API 문서: http://localhost:8090/api/docs
- ReDoc: http://localhost:8090/api/redoc

## API 사용법

### 헬스체크 API

**시스템 상태 확인**
```bash
GET /api/v1/health/
```

**응답 예시:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00",
  "database_connected": true,
  "version": "1.0.0"
}
```

### 카드 추천 API

**업종별 카드 추천 조회**
```bash
GET /api/v1/card-recommendation/{profit_biz_kind_name}?limit=5
```

**파라미터:**
- `profit_biz_kind_name`: 업종명 (예: 편의점, 주유소, 마트)
- `limit`: 각 혜택 타입별 추천 개수 (1-10, 기본값: 5)

**사용 예시:**
```bash
# 편의점 추천 카드 조회 (각 타입별 5개씩)
curl "http://localhost:8090/api/v1/card-recommendation/세금?limit=5"

# 주유소 추천 카드 조회 (각 타입별 3개씩)
curl "http://localhost:8090/api/v1/card-recommendation/주유?limit=3"
```

**응답 예시:**
```json
{
  "profit_biz_kind_name": "세금",
  "discount_cards": {
    "benefit_type": "할인",
    "cards": [
      {
        "card_id": 1001,
        "profit_id": 2001,
        "category_name": "세금",
        "card_name": "카드 1001",
        "card_company": "카드사",
        "total_score": 0.8756,
        "benefit_details": {
          "benefit_value": 0.9200,
          "convenience": 0.8500,
          "accessibility": 0.8500
        },
        "rank": 1,
        "annual_fee": 0
      }
    ],
    "count": 5
  },
  "cashback_cards": {
    "benefit_type": "적립",
    "cards": [
      {
        "card_id": 1002,
        "profit_id": 2002,
        "category_name": "세금",
        "card_name": "카드 1002",
        "card_company": "카드사",
        "total_score": 0.8234,
        "benefit_details": {
          "benefit_value": 0.8800,
          "convenience": 0.7900,
          "accessibility": 0.8000
        },
        "rank": 1,
        "annual_fee": 0
      }
    ],
    "count": 5
  },
  "generated_at": "2025-01-15T10:30:00.123456"
}
```

**이용 가능한 업종 목록 조회**
```bash
GET /api/v1/card-recommendation/kinds
```

**응답 예시:**
```json
[
  "세금",
  "주유", 
  "마트",
  "카페",
  "온라인쇼핑"
]
```

## 점수 체계

카드 추천 점수는 다음 3가지 요소로 구성됩니다:

- **혜택 가치 (50%)**: 할인 한도, 적립률 등 실제 혜택의 크기
- **편의성 (30%)**: 이용 횟수 제한, 사용 편의성
- **접근성 (20%)**: 실적 조건, 가입 난이도

각 점수는 0-1 범위로 정규화되며, 높을수록 우수한 카드입니다.

## Docker 실행

```bash
# Docker 이미지 빌드
docker build -t card-recommendation-api .

# 컨테이너 실행
docker run -p 8090:8090 card-recommendation-api
```

Docker 환경에서는 자동으로 `.env.develop` 설정이 적용됩니다.

## 데이터 구조

### 주요 테이블
- `card_category_scores`: 사전 계산된 카드 점수 데이터
- `normalized_profit`: 정규화된 카드 혜택 데이터
- `raw_base_profit`: 원본 카드 혜택 데이터

### ETL 프로세스
데이터는 Apache Airflow를 통해 다음 단계로 처리됩니다:
1. Raw 데이터 추출 및 로드
2. Min-Max Scaling을 통한 데이터 정규화
3. 종합 점수 계산 및 랭킹 생성

## 문제 해결

### 일반적인 오류

**데이터베이스 연결 실패**
- DATABASE_URL 설정 확인
- MySQL 서버 실행 상태 확인
- 데이터베이스 권한 설정 확인

**업종 데이터 없음 (404 오류)**
- 해당 업종의 카드 데이터가 ETL 처리되었는지 확인
- `/api/v1/card-recommendation/kinds/list`로 이용 가능한 업종 목록 확인

**환경 설정 오류**
- ENV 환경변수가 올바르게 설정되었는지 확인
- 해당하는 .env 파일이 존재하는지 확인

## 개발 정보

- **개발 환경**: Python 3.13+, FastAPI 0.104+
- **테스트**: pytest (테스트 코드 추가 예정)
- **문서**: 자동 생성된 OpenAPI 문서 활용
- **로깅**: 구조화된 로깅을 통한 디버깅 지원
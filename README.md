# Aeterna Flask AI Service

Spring 백엔드와 통신하는 Flask 기반 AI 서비스입니다. 음식 사진 분석 기능을 제공합니다.

## 기능

1. **음식 이름 분석 API**: 음식 사진을 받아 음식 이름만 반환
2. **음식 영양 정보 분석 API**: 음식 사진을 받아 음식 이름, 칼로리, 탄단지 비율 반환

## 설치 및 실행

### 1. 가상 환경 생성 및 활성화

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example` 파일을 참고하여 `.env` 파일을 생성하고 OpenAI API 키를 설정하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### 4. 서버 실행

```bash
python app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

## API 엔드포인트

### 1. 음식 이름 분석

**POST** `/api/food/analyze-name`

**Request Body:**
```json
{
    "image_path": "/path/to/image.jpg"
}
```

**Response:**
```json
{
    "success": true,
    "food_name": "김치찌개"
}
```

### 2. 음식 영양 정보 분석

**POST** `/api/food/analyze-nutrition`

**Request Body:**
```json
{
    "image_path": "/path/to/image.jpg"
}
```

**Response:**
```json
{
    "success": true,
    "food_name": "김치찌개",
    "calories": 250.0,
    "nutrition": {
        "carbohydrate": 15.5,
        "protein": 12.3,
        "fat": 8.2
    }
}
```

## 프로젝트 구조

```
Aeterna_Flask/
├── app.py                      # Flask 애플리케이션 진입점
├── config.py                   # 설정 파일
├── requirements.txt            # Python 의존성
├── test_api.py                 # API 테스트 스크립트
├── routes/                     # API 라우트
│   ├── __init__.py
│   └── food_analysis.py        # 음식 분석 API 라우트
├── services/                   # 비즈니스 로직
│   ├── __init__.py
│   ├── ai_service.py           # Langchain OpenAI 서비스
│   └── food_analysis_service.py # 음식 분석 서비스
└── utils/                      # 유틸리티 함수
    ├── __init__.py
    ├── exceptions.py           # 커스텀 예외 클래스
    └── file_validator.py       # 파일 검증 유틸리티
```

## 테스트

`test_api.py` 스크립트를 사용하여 API를 테스트할 수 있습니다:

```bash
python test_api.py
```

이미지 파일 경로를 입력하면 두 API 엔드포인트를 모두 테스트합니다.

## 확장 가능한 구조

- **서비스 레이어 분리**: 비즈니스 로직을 서비스 클래스로 분리하여 재사용성 향상
- **블루프린트 패턴**: 기능별로 라우트를 분리하여 관리 용이
- **설정 관리**: 환경 변수를 통한 설정 관리로 배포 환경별 설정 가능
- **에러 처리**: 일관된 에러 응답 형식으로 클라이언트 통신 용이

## 향후 확장 가능한 기능

- 다른 AI 모델 지원 (Claude, Gemini 등)
- 배치 이미지 분석
- 음식 데이터베이스 연동
- 캐싱 기능 추가

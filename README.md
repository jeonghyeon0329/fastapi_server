# ⚡ FastMVC

> **MVC 기반으로 Python 모듈을 재사용할 수 있는 FastAPI 서버 프레임워크**  
> _모듈화된 구조를 통해 유지보수성과 확장성을 높인 경량 백엔드 아키텍처_

---

## ✨ 개요
**FastMVC**는 FastAPI를 기반으로 한 **MVC(Model–View–Controller)** 구조의 서버 프레임워크입니다.  
라우터, 모델, 서비스, 프로세서 단위를 명확히 분리하여 유지보수성과 재사용성을 높였습니다.

```
📦 app/
 ┣ 📂 routers/       → API 엔드포인트 (Controller)
 ┣ 📂 models/        → 요청/응답 스키마 정의 (Model)
 ┣ 📂 services/      → 핵심 비즈니스 로직 (Service)
 ┣ 📂 middleware/    → 접근 제어 및 보안 필터
 ┣ 📂 core/          → 로깅 및 설정 관리
 ┣ 📂 utils/         → 공통 유틸리티 및 헬퍼 함수
 ┗ 📜 main.py        → FastAPI 서버 진입점
```

---

## 🧠 아키텍처 구성

### 🧩 라우터 정의 (`app/routers/items.py`)
FastAPI의 `APIRouter`를 사용하여 엔드포인트를 정의합니다.
```python
@router.post("/~test")
async def run_test(user_id: str = Form(...), affiliation: Optional[str] = Form(None)):
    ...
```

---

### 📘 모델 정의 (`app/models/`)
요청 및 응답 스키마를 **Pydantic** 기반으로 작성합니다.
```python
class _testRequest(BaseModel):
    user_id: str
    affiliation: Optional[str]
    model: Optional[Dict[str, str]] = {
        "test": "_test",
    }
```
작업 모듈 일련화를 위해 인덱스 기반 operation 이름을 작성합니다.(ex. _test)

---

### ⚙️ 서비스 계층 (`app/services/`)
모델의 `operate_parameter.model` 딕셔너리에 정의된 키-값를 기준으로 동적으로 서비스 모듈을 로드합니다.
서비스 모듈은 자동으로 해당 프로세서를 불러옵니다.
```python
from app.services._test_operation import _testProcessor
```

---

### 🧮 프로세서 명명 규칙
서비스 모듈 내 클래스는 다음 규칙을 따릅니다.
```python
{ServiceName.capitalize()}Processor
```
예시: 
model: Optional[Dict[str, str]] = {
        "step1": "task",
    }
->TaskProcessor

각 프로세서는 다음의 단일 책임 원칙(SRP)을 따릅니다.
- 입력 데이터 검증  
- 비즈니스 로직 처리  
- 결과 생성 및 반환  

---

### 🧪 테스트 (Pytest)
서비스 로직이 구현된 후, **Pytest**를 사용하여 기능 단위 테스트를 진행합니다.
```bash
pytest -v
```

---

## 🧰 요구 사항
- **Python 3.11**
- **fastapi 0.115.11**
- **Uvicorn / Gunicorn**

---

## 🛠️ 설치 방법

```bash
# 1️⃣ 저장소 클론
git clone https://github.com/jeonghyeon0329/fastapi_server.git

# 2️⃣ 가상환경 생성 및 패키지 설치
python -m venv .venv
source .venv/bin/activate     # Windows: .\venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

---

## 🚀 서버 실행
```bash
python main.py
```

- 자동 리로드 모드 활성화  
- 콘솔 배너에 환경 정보 출력  
- 로그 레벨: `warning` (필요한 정보만 표시)

---

## 로그 예시
```
[2025-11-05 07:57:59] [INFO] [fastapi_server] 
[op=0152602f...] [user=test] [aff=test] [act=_testRequest] REQUEST_COMPLETED

> 디버깅과 운영 로그 모두 효율적으로 관리할 수 있습니다.
```
---

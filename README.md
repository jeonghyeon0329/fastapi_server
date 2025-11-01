# fastapi_server

## ✨ 기능 요약
**파편화된 python파일을 mvc기반으로 python 파일을 활용할 수 있는 Fastapi server**
- Router 정의
    app/routers/items.py의 ~test와 같이 routers/ 폴더에 엔드포인트를 정의합니다.
    각 router 파일은 APIRouter 객체를 생성하고, API 엔드포인트(path, method, response_model 등)를 등록합니다.

- Model 정의
    app/models/ 폴더에서 사용될 데이터 모델(엔티티명/DB 모델/스키마 참조용 이름)을 작성합니다.

- Service 모듈화
    model: Optional[Dict[str, str]] = {'a': 'b'} 와 같이 매핑 규칙을 정의하여, 특정 키('b')에 대응하는 처리 로직을 services/b_operation.py 파일에 구현합니다.
    서비스 로직은 컨트롤러(Router)에서 호출되며, 데이터 가공·연산·외부 자원 접근을 담당합니다.

- Processor 클래스 네이밍 규칙
    서비스 모듈 내 클래스는 BProcessor 와 같이 앞 글자를 대문자로 시작하는 명명 규칙을 따릅니다.
    각 Processor 클래스는 단일 책임 원칙을 지켜, 해당 기능의 입력 검증 → 처리 → 결과 반환 과정을 담당합니다.

- Pytest 기능 정의
    서비스 로직을 구현하고 Pytest 기능을 활용하여 기능 테스트를 진행합니다.

## 📦 요구 사항
- Python 3.11.0

## 🛠 설치
```bash
# 1) 저장소 클론
git clone https://github.com/jeonghyeon0329/fastapi_server.git

# 2) 가상환경 & 패키지 설치 (pip)
python -m venv .venv
source .venv/bin/activate     # Windows: .\venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

## MIT License

Copyright (c) 2025 Choi jeong hyeon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

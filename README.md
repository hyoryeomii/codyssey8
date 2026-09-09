# AI Agent 개발: 나만의 AI 비서 구축 (Daily Workout AI Assistant)
## 1. 프로젝트 개요

- **프로젝트명**: 운동 데이터 기반 맞춤형 AI 피트니스 트레이너 비서
- **개요**: 일반적인 LLM이 파악하지 못하는 개인의 시계열 데이터(운동 기록)를 백엔드 서버에서 분석·요약하고, 이를 시스템 프롬프트(Context Injection)에 주입하여 사용자 맞춤형 답변을 제공하는 웹 애플리케이션 개발
- **주요 해결 과제**: 개인 데이터 연동 AI 서비스 구축, 풀스택 백엔드/프론트엔드 연동, 클라우드 환경(Render/Vercel) 배포 및 CORS/환경 변수 보안 설정

## 2. 개발 환경 및 기술 스택

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic, Firebase Admin SDK, OpenAI API
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (Fetch API 기반)
- **Database**: Firebase Firestore (`exercise_data`, `conversations` 컬렉션)
- **Deployment & Infrastructure**:
    - **Backend**: Render Web Service
    - **Frontend**: Vercel
    - **Configuration**: `.env` 파일 및 클라우드 환경 변수를 통한 보안 키 관리 (`OPENAI_API_KEY`, `FIREBASE_SERVICE_ACCOUNT_JSON`)

## 3. 핵심 구현 내용 및 Architecture

### 가. 데이터 선정 및 분석 (시계열 데이터)

- **선정 데이터**: 개인 일별 운동 시간 및 메몰 기록 (`exercise_data`)
- **데이터 규모**: 100개 이상의 일별 시계열 포맷 데이터 (2024년 5월 ~ 8월 기준)
- **요약 알고리즘 (`GET /api/data/summary`)**:
    - 전체 데이터 기간 및 기록 일수(`count`) 산출
    - 총 운동 시간, 일평균 운동 시간, 최고/최저 운동 시간 통계 계산
    - 최근 10개 레코드의 평균과 전체 평균을 비교하여 최근 트렌드(`증가 추세` / `유지 추세` / `감소 추세`) 자동 추론

### 나. Backend API 구현 (FastAPI & Firestore)

1. **CORS & Global Exception Handling**:
    - 최상단 CORS 미들웨어 적용 (`allow_origins=["*"]`)
    - 백엔드 내부 예외(500 에러) 발생 시에도 브라우저에서 CORS 차단이 발생하지 않도록 `global_exception_handler` 구축
2. **데이터 CRUD API**:
    - `POST /api/data`: 운동 데이터 추가
    - `GET /api/data`: 전체 운동 데이터 목록 조회
    - `PUT /api/data/{id}`: 특정 데이터 수정
    - `DELETE /api/data/{id}`: 특정 데이터 삭제
3. **대화 기록 API**:
    - `POST /api/conversations`: AI 대화 세션 저장
    - `GET /api/conversations`: 전체 대화 히스토리 최신순 조회
    - `GET /api/conversations/{id}`: 특정 대화의 세부 메세지 객체 배열 포함 반환
    - `DELETE /api/conversations/{id}`: 대화 기록 삭제
4. **Context Injection 기반 AI Chat API (`POST /api/chat`)**:
    - `get_data_summary()`를 내부적으로 실행하여 최신 데이터를 요약
    - 요약된 통계 정보를 OpenAI `gpt-3.5-turbo`의 `system` 프롬프트에 동적으로 삽입
    - GPT 답변 생성 후 Firestore `conversations` 컬렉션에 자동 기록 저장

### 다. Frontend & 배포 (Vanilla JS + Render + Vercel)

- **UI 구성**: 채팅 인터페이스, 운동 데이터 통계 카드/목록 CRUD, 대화 히스토리 불러오기
- **Render (Backend)**: FastAPI 앱 배포 및 환경 변수 설정 완료
- **Vercel (Frontend)**: Vanilla JS 앱 배포 완료 (Render API 엔드포인트와 비동기 통신)

## 4. 과제 목표 달성 및 원리 설명

**1. 시계열 데이터 분석 및 요약 정보 활용 흐름**

- **데이터 로드 및 수치 정제**: Firestore DB의 `exercise_data` 컬렉션에서 일별 날짜와 운동 시간(`value`) 데이터를 전체 로드
- **통계 지표 계산**: 전체 데이터 개수(`count`), 기간(`period`), 총합, 평균, 최댓값, 최솟값 등의 수치 통계를 산출
- **추세 분석 및 가공**: 최근 데이터(예: 최근 10개)의 평균을 전체 평균과 비교하여 현재 운동량의 상태(`증가/유지/감소 추세`)를 추론
- **서비스 활용**: 계산된 요약 객체(JSON)를 API 응답으로 전달하거나, AI 챗봇 호출 시 프롬프트에 동적으로 삽입하여 사용자의 개별 상황을 반영하는 근거 자료로 활용

**2. FastAPI 프로젝트 구조 분리 기준 (Router/Service)**

- **단일 책임 원칙 (SRP)**: 엔드포인트 URL 정의, 비즈니스 로직, DB 접근 로직이 한 파일에 섞이면 코드 가독성이 떨어지고 유지보수가 어려워짐
- **Router (라우터)**: HTTP 요청 경로(URL)와 매핑, 요청/응답 스키마 정의, HTTP 상태 코드 반환 등 클라이언트와의 **접점 역할**만 담당
- **Service (서비스/비즈니스 로직)**: 데이터 요약 통계 계산, OpenAI API 호출, Firestore DB 조회/저장 등 **실제 백엔드 핵심 로직**을 처리하도록 분리

**3. Pydantic을 활용한 요청 데이터 검증의 이유와 방식**

- **적용 이유**: 클라이언트에서 들어오는 입력값의 타입 오류, 누락된 필수 필드, 잘못된 데이터 형식을 백엔드 로직 실행 전에 자동으로 쳐내어 서버 안정성을 확보
- **적용 방식**: `pydantic.BaseModel`을 상속받는 클래스(예: `DataItem`, `ChatRequest`)를 정의하고, 각 필드의 타입(`str`, `int`, `Optional` 등)을 지정함. FastAPI 라우터 함수의 매개변수에 해당 모델을 지정하면 프레임워크가 incoming JSON 데이터를 자동으로 파싱 및 검증

**4. Firestore 데이터 저장 및 CRUD 조작 방법**

- **초기화 및 계정 인증**: `firebase_admin` 라이브러리를 사용해 서비스 계정 인증 정보(JSON)를 읽어 `firestore.client()` 인스턴스를 생성
- **Create (POST)**: `db.collection('컬렉션명').add(data_dict)`를 사용하여 자동 생성된 ID와 함께 신규 문서를 생성
- **Read (GET)**: `db.collection('컬렉션명').stream()` 또는 `.document('ID').get()`으로 단일/전체 문서를 로드
- **Update (PUT)**: `db.collection('컬렉션명').document('ID').update(data_dict)`로 특정 문서 필드를 수정
- **Delete (DELETE)**: `db.collection('컬렉션명').document('ID').delete()`로 문서를 삭제

**5. 시스템 프롬프트 데이터 주입 (Context Injection) 원리**

- **개념**: LLM 모델 자체를 파인튜닝(재학습)하지 않고, 사용자 요청 시 백엔드가 DB에서 조회한 외부 실시간 데이터를 System Prompt(지시문) 영역에 문맥으로 함께 넣어 모델에 전달하는 기법
- **동작 원리**:
    1. 클라이언트 질문 수신 (`POST /api/chat`)
    2. 백엔드가 DB에서 최신 운동 요약 정보(`GET /api/data/summary`)를 내부 조율
    3. `system_prompt = f"당신은 피트니스 트레이너입니다. [사용자 요약: {summary}]"` 형태로 프롬프트 생성
    4. GPT API로 해당 system 메시지와 user 질문을 함께 전달하여 개인화된 답변을 생성

**6. 배포 환경에서 CORS / 환경변수 / 키 관리의 필요성**

- **CORS (Cross-Origin Resource Sharing)**: 브라우저의 보안 정책(Same-Origin Policy) 때문에 출처(Domain)가 다른 프론트엔드(Vercel)와 백엔드(Render) 간 HTTP 통신이 기본적으로 차단됨. 이를 해제하기 위해 백엔드에 명시적인 CORS 허용 헤더 설정 해야함
- **환경 변수 & 키 관리**: OpenAI API Key, Firebase Service Account Key 같은 민감한 보안 인증 정보가 GitHub 등 공용 코드에 노출되면 악의적인 무단 도용 및 과금 폭탄이 발생함. 따라서 코드 내부에는 변수 이름만 작성하고, 실제 값은 `.env` 파일 및 Cloud Platform(Render/Vercel)의 **Environment Variables** 영역에서 안전하게 이관 관리해야함

## 5. 실행 및 배포 주소

- **Frontend 배포 URL**: `https://codyssey8-p1wj3zdon-123-fcce.vercel.app`
  - 사용자가 직접 접속해서 사용하는 화면
  - HTML/CSS/JavaScript로 작성된 버튼, 입력창, 채팅 화면 등 표시
  - 사용자가 입력창에 글을 쓰거나 버튼을 누르면, 프론트엔드가 백엔드 URL로 데이터를 보내 응답을 받아옴
- **Backend 배포 URL**: `https://workout-backend-szc7.onrender.com`
  - 데이터베이스 조작, AI 호출 등 실제 로직을 실행하는 서버의 기본 주소
  - 브라우저 주소창에 기본 주소만 입력하면 화면이 따로 없어 {"detail":"Not Found"}가 뜨는 것이 정상 (/api/data처럼 뒤에 세부 경로를 붙여야 데이터가 출력)
- **Swagger API Docs**: `https://workout-backend-szc7.onrender.com/docs`
  - 백엔드 서버가 "우리 서버는 이런 기능(API)들을 제공합니다"라고 깔끔하게 보여주는 자동 생성 문서
  - 개발자나 평가자가 프론트엔드 화면 없이도 백엔드의 각 기능(GET, POST, PUT, DELETE)이 제대로 작동하는지 직접 버튼을 눌러 테스트해 볼 수 있음
 
## 6. 실행 결과
**- 데이터 기반 AI 채팅**
입력/요청: 사용자의 질문(자연어)
출력/화면: 저장된 데이터 요약을 반영한 AI 답변 + 로딩 표시
<img width="948" height="522" alt="스크린샷 2026-09-09 020801" src="https://github.com/user-attachments/assets/8479787f-0c37-44a2-9597-2be2b0ab9aea" />
<img width="985" height="343" alt="image" src="https://github.com/user-attachments/assets/e7778e6c-202f-47cf-b6bc-856d345ef275" />
<img width="958" height="524" alt="image" src="https://github.com/user-attachments/assets/4f867f0c-17af-4ee0-80fd-baf788bd3316" />


**데이터 관리(CRUD)**
입력/요청: (date, value, memo) 형태의 데이터 추가/수정/삭제
출력/화면: 데이터 목록 갱신 및 저장 결과 확인
<img width="974" height="834" alt="image" src="https://github.com/user-attachments/assets/981aea7a-5dc5-421b-bc65-f06069d0a3be" />


**대화 기록 저장 및 불러오기**
입력/요청: 대화 저장, 목록 조회, 특정 대화 불러오기
<img width="495" height="353" alt="image" src="https://github.com/user-attachments/assets/35e601f7-94f1-492e-81fa-9e9b0dabff6d" />

출력/화면: 대화 목록과 선택한 대화의 메시지 재표시
<img width="981" height="557" alt="image" src="https://github.com/user-attachments/assets/1130e2fe-9b97-4f6d-a1b8-8d21c683660f" />


**배포 및 문서화**
입력/요청: 배포 URL 접속(프론트/백엔드)
<img width="1820" height="1014" alt="image" src="https://github.com/user-attachments/assets/22ea8bf9-615f-4f88-9999-02b66f225bc6" />
<img width="561" height="149" alt="image" src="https://github.com/user-attachments/assets/163a4237-746a-4db8-a439-93a491c97f61" />
<img width="1899" height="738" alt="image" src="https://github.com/user-attachments/assets/613bef51-e11b-404b-a4b5-2e1b2f124a26" />
- /api/data

출력/화면: 서비스 접속 가능 + Swagger UI 확인 + README로 실행/환경변수 안내
<img width="1872" height="1007" alt="image" src="https://github.com/user-attachments/assets/f60a8277-c692-4a0f-8c41-6ca76deb2193" />

---

# 🏋️ Daily Workout AI Assistant

운동 데이터를 기반으로 개인 맞춤형 피트니스 조언을 제공하는 AI 비서 서비스입니다.

## 🔗 배포 링크
- **Frontend (Vercel)**: https://codyssey8-p1wj3zdon-123-fcce.vercel.app
- **Backend (Render)**: https://workout-backend-szc7.onrender.com
- **Swagger API Docs**: https://workout-backend-szc7.onrender.com/docs

## ⚙️ 환경변수 (Environment Variables)
백엔드 및 프론트엔드 구동을 위해 다음 환경변수가 필요합니다.

### Backend (`.env`)
- `OPENAI_API_KEY`: OpenAI API 인증 키
- `FIREBASE_SERVICE_ACCOUNT_JSON`: Firebase 서비스 계정 인증 JSON 문자열

## 🚀 로컬 실행 방법 (Local Execution)

1. **가상환경 생성 및 패키지 설치**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt

---

## 7. 결론 및 자체 평가

- **성과**: 데이터 수집, FastAPI 백엔드 구축, Firestore 연동, Context Injection 기법을 적용한 OpenAI 연동, 클라우드 배포까지 AI 비서 서비스의 전체 파이프라인 구축 완료
- **트러블슈팅 경험**: Render 무료 티어의 Cold Start 현상 및 Preflight CORS 에러 이슈를 글로벌 예외 처리기 추가 및 미들웨어 순서 조정을 통해 해결하며 클라우드 운영 환경에 대한 이해도를 높임

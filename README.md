# Rec Chart OCR - Enhanced Interview Analysis System

실시간 인터뷰 스크리닝 및 AI 기반 종합 분석 시스템 (PyQt6 데스크톱 애플리케이션)

## 📝 프로젝트 개요

Rec Chart OCR은 채용 담당자를 위한 실시간 인터뷰 보조 도구입니다. Zoom/Meet 등 온라인 인터뷰 중 화면의 텍스트를 실시간으로 캡처하여 AI 기반으로 자동 분석하고, 카테고리별 스크리닝 노트를 생성합니다. 인터뷰 완료 후에는 전체 스크립트를 종합 분석하여 전문적인 채용 리포트를 자동 생성합니다.

## 🎯 3단계 워크플로우

### 1️⃣ 템플릿 설정
- 후보자 기본 정보 입력 (이름, 포지션, 지역, 학력, 경력)
- 커스텀 스크리닝 카테고리 설정 (예: HR Expertise, Leadership, Cultural Fit)
- 💬 JUST TALK 빠른 시작 모드 지원

### 2️⃣ 실시간 인터뷰 진행
- 실시간 OCR로 화면 텍스트 자동 캡처 (2초 간격)
- AI 기반 자동 카테고리 분류 및 스크리닝 노트 생성
- 진행 상황 실시간 체크리스트 (대기중: 🔴 → 완료: ✅)
- 캡처 범위 제어 (전체 화면 / 드래그 선택)

### 3️⃣ 종합 분석 및 리포트
- **Enhanced Interview Analyzer**: 전체 인터뷰 스크립트 AI 분석
- 후보자 프로필 자동 추출 (이름, 회사, 연봉, 경력 등)
- 포지션별 맞춤 평가 (HR, Engineering, Sales, Marketing, Finance, Operations)
- 종합 분석 리포트 (강점/우려사항, 문화적합성, 최종 추천)

## 🚀 주요 기능

### 🔍 실시간 분석
- **실시간 OCR**: pytesseract 기반 화면 텍스트 추출
- **AI 카테고리 분류**: GPT 기반 자동 스크리닝 노트 생성
- **스마트 캡처**: 사용자 지정 영역 또는 전체 화면 캡처
- **진행 상황 추적**: 카테고리별 실시간 완료 체크

### 🤖 Enhanced Analysis
- **포지션별 분석 프레임워크**: 6개 전문 영역 지원
- **4단계 분석 파이프라인**: 프로필 추출 → 종합 분석 → 개선 제안 → 최종 리포트
- **자동 정보 추출**: 정규식 + AI 기반 후보자 정보 추출
- **구조화된 출력**: JSON 기반 일관된 분석 결과

### 💾 고급 리포트 시스템
- **종합 평가 리포트**: 후보자 프로필 + 상세 분석 + 최종 추천
- **영어 저장 지원**: 인코딩 문제 없는 안전한 파일 저장
- **다중 포맷**: .txt 기반 구조화된 리포트
- **전체 스크립트 포함**: 분석 결과 + 원본 인터뷰 텍스트

## 🛠️ 설치 방법

1. Python 3.12 이상 설치
2. Tesseract OCR 설치
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
3. 프로젝트 클론
   ```bash
   git clone [repository-url]
   cd Rec_Chart_OCR
   ```
4. 가상환경 생성 및 활성화
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
5. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ 환경 설정

1. `.env` 파일 생성
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## 🏃‍♂️ 실행 방법

```bash
python -m src.main
```

## 📁 프로젝트 구조

```
Rec_Chart_OCR/
├── src/
│   ├── main.py            # 메인 애플리케이션
│   ├── core/              # 핵심 기능 모듈
│   │   ├── ocr_engine.py  # OCR 엔진
│   │   └── screen_capture.py # 화면 캡처
│   ├── gpt/               # GPT 처리 모듈
│   │   └── summarizer.py  # 텍스트 요약
│   ├── ui/                # UI 컴포넌트
│   │   ├── main_window.py # 메인 윈도우
│   │   └── capture_widget.py # 캡처 위젯
│   └── utils/             # 유틸리티 함수
│       └── document_saver.py # 문서 저장
├── config/                # 설정 파일
└── requirements.txt       # 의존성 목록
```

## 🎯 사용 방법

### 📋 1단계: 템플릿 설정
1. 애플리케이션 실행
2. 후보자 기본 정보 입력 (이름, 포지션, 지역, 학력, 경력)
3. 커스텀 스크리닝 카테고리 추가/편집
4. "인터뷰 시작" 또는 "💬 JUST TALK" 클릭

### 🎬 2단계: 실시간 인터뷰
1. "📐 캡처 범위 선택"으로 화면 영역 설정
2. "🧪 테스트 캡처"로 OCR 동작 확인
3. 인터뷰 진행하며 실시간 스크리닝 노트 확인
4. 카테고리별 진행 상황 체크리스트 모니터링
5. "💾 스크리닝 결과 저장"으로 중간 저장

### 📊 3단계: 종합 분석
1. "📋 요약완성" 버튼으로 3번째 화면 이동
2. 전체 인터뷰 스크립트 붙여넣기
3. "🔍 Analyze Script" 클릭하여 Enhanced AI 분석 실행
4. 종합 분석 결과 확인 (프로필, 강점/우려사항, 최종 추천)
5. "💾 Save Final Report"로 완전한 리포트 저장

## 🔧 기술 스택

### 🎨 프론트엔드
- **GUI Framework**: PyQt6
- **UI 컴포넌트**: QSplitter, AutoResizeTextEdit, QStackedWidget
- **레이아웃**: 3단계 워크플로우, 반응형 분할 패널

### 🧠 AI & 분석
- **AI Engine**: OpenAI GPT-3.5-turbo / GPT-4
- **Enhanced Analyzer**: 포지션별 맞춤 분석 프레임워크
- **자연어 처리**: 정규식 기반 정보 추출 + AI 분석
- **카테고리 분류**: 템플릿 기반 실시간 컨텐츠 분석

### 🔍 OCR & 캡처
- **OCR Engine**: pytesseract + Pillow
- **화면 캡처**: mss (Multi-Screen Screenshot)
- **영역 선택**: 드래그 앤 드롭 범위 설정
- **실시간 처리**: 2초 간격 자동 캡처

### 💾 데이터 & 저장
- **설정 관리**: JSON 기반 템플릿 시스템
- **리포트 생성**: 구조화된 텍스트 리포트
- **인코딩**: UTF-8 지원, 영어 저장 폴백
- **파일 형식**: .txt (향후 .docx, .pdf 지원 예정)

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 

# 서울시 도서관 시공간 사각지대 및 맞춤 추천 시스템

Seoul Library Spatiotemporal Accessibility Dashboard

## 1. Project Overview

서울시 공공도서관 Open API 데이터를 활용하여
시간적·공간적 도서관 접근성을 분석하고,
사용자 조건에 적합한 도서관을 추천하는
객체지향 프로그래밍 기반 웹 대시보드입니다.

## 2. Main Features

### Data Overview
- 서울시 공공도서관 Open API 데이터 수집
- 데이터 유효성 검사 및 객체 변환
- 운영시간 데이터 품질 분석
- 자치구별 도서관 분포 시각화

### Temporal Analysis
- 요일 및 시간별 도서관 운영 현황
- 주간 운영률 Heatmap
- 자치구별 운영 현황 비교
- 학생 및 직장인 이용 가능성 비교

### Spatial Analysis & Recommendation
- Haversine 기반 거리 계산
- 1km, 3km, 5km, 10km 반경별 접근성 분석
- 검색 반경 및 운영 상태 지도 시각화
- 사용자 조건 기반 TOP 5 도서관 추천
- 모의 좌석 사용률 제공

## 3. Technology Stack

- Language: Python
- Web Framework: Streamlit
- Data Processing: Pandas
- Visualization: Altair, Pydeck
- External Data: Seoul Open API
- Testing: Pytest, Streamlit AppTest
- Version Control: Git, GitHub

## 4. System Architecture

Seoul Open API / CSV
        |
        v
LibraryRepository
        |
        v
SystemManager / LibraryParser
        |
        v
Library / Location / OperatingHours
        |
        v
AnalysisService
SpatialAnalysisService
RecommendationService
        |
        v
MapRenderer / ChartRenderer
        |
        v
Streamlit Dashboard

## 5. SOLID Principles

- SRP: 데이터 수집, 파싱, 분석, 시각화 책임 분리
- OCP: Repository 구현체 확장을 통한 데이터 소스 추가
- LSP: 공통 계약을 따르는 Repository 구현체 교체
- ISP: load() 중심의 최소 Repository 인터페이스
- DIP: SystemManager에 Repository 의존성 주입

## 6. Data Source

- 서울 열린데이터광장
- API: SeoulPublicLibraryInfo
- Format: JSON
- 수집 결과: 217개 레코드
- 유효 데이터: 217개
- 자치구: 25개
- 중복 ID: 0개

위 수치는 2026년 11월 27일 진단 결과입니다.
API 업데이트에 따라 변경될 수 있습니다.

## 7. Installation

    git clone https://github.com/gtsbd/oopTeamProject.git
    cd oopTeamProject
    pip install -r requirements.txt

## 8. Environment Variable

서울시 Open API 인증키를 환경변수로 설정합니다.

    SEOUL_API_KEY=YOUR_API_KEY

인증키는 소스코드에 직접 저장하지 않습니다.

## 9. Run

    streamlit run app.py

## 10. Testing

    python -m pytest -v

단위 테스트 및 Streamlit 통합 테스트를 수행합니다.

## 11. Limitations

- 거리는 Haversine 기반 지표면 거리이며
  실제 도보 및 대중교통 이동 거리가 아닙니다.
- 도서 보유 정보, 좌석 수 및 혼잡도는
  실제 데이터가 아닌 시뮬레이션입니다.
- 직장인의 이동시간은 1시간으로 가정합니다.
- 일부 운영시간 및 복잡한 휴관 규칙은
  완전히 해석되지 않을 수 있습니다.
- 접근성 분석은 API 수집 범위 내에서 수행합니다.

## 12. Course Information

- University: Kwangwoon University
- Course: Object-Oriented Programming
- Semester: 2026 Fall

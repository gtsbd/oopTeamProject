
import os
import streamlit as st
import pandas as pd
import altair as alt

from dotenv import load_dotenv
from services.analysis_service import AnalysisService
from models.user import OfficeWorker, Student
from data_manager import SystemManager
from repositories.seoul_api import SeoulAPIRepository
from services.recommendation_service import RecommendationService

load_dotenv()

st.set_page_config(
    page_title="서울시 도서관 사각지대 시뮬레이터",
    layout="wide"
)


# 데이터 로딩
@st.cache_resource(ttl=3600)
def load_manager():
    api_key = os.getenv("SEOUL_API_KEY")

    repository = SeoulAPIRepository(
        api_key=api_key,
        limit=None,
        page_size = 1000
    )

    return SystemManager(repository)


try:
    manager = load_manager()

except (ValueError, RuntimeError) as error:
    st.error(str(error))
    st.stop()


libraries = manager.get_libraries()


# 대시보드 제목
st.title("📚 서울시 도서관 시공간 사각지대 및 맞춤 추천")
st.markdown("객체지향 프로그래밍(OOP)을 활용한 정책 시뮬레이터")


# 탭 생성
tab1, tab2, tab3 = st.tabs([
    "1. 데이터 현황 파악",
    "2. 시간적 사각지대 시뮬레이션",
    "3. 내 맞춤 도서관 찾기"
])


# 첫 번째 탭
with tab1:
    st.header("서울시 공공도서관 데이터 현황")

    col1, col2, col3 = st.columns(3)

    col1.metric("API 수신 데이터", manager.raw_count)
    col2.metric("유효 데이터", len(libraries))
    col3.metric("제외된 데이터", manager.invalid_count)

    if not libraries:
        st.warning("유효한 도서관 데이터가 없습니다.")

    elif manager.invalid_count:
        st.warning("일부 데이터가 검증 과정에서 제외됐습니다.")

    else:
        st.success("도서관 데이터 로드 완료")

    st.caption(
        "데이터 출처: 서울 열린데이터광장 "
        "SeoulPublicLibraryInfo Open API (JSON)"
    )

    st.info(
        "도서 보유 정보, 좌석 수, 인기도 및 "
        "혼잡도는 실제 데이터가 아닌 시뮬레이션입니다."
    )

    st.subheader("운영시간 데이터 품질")

    quality = AnalysisService().get_data_quality(
        libraries
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "평일 운영시간 확인",
        quality["weekday_known"]
    )

    col2.metric(
        "주말 운영시간 확인",
        quality["weekend_known"]
    )

    col3.metric(
        "운영시간 일부 또는 전체 미확인",
        quality["incomplete_hours"]
    )

    st.caption(
        "운영시간 확인은 시간 범위 파싱 여부를 "
        "기준으로 하며 모든 휴관 규칙의 "
        "해석 성공을 의미하지 않습니다."
    )

    st.subheader("서울시 도서관 위치 분포")

    if libraries:
        map_data = pd.DataFrame([
            {
                "name": library.name,
                "lat": library.location.lat,
                "lon": library.location.lon,
                "district": library.district
            }
            for library in libraries
        ])

        st.map(
            map_data,
            latitude="lat",
            longitude="lon",
            zoom=10
        )

        district_counts = (
            map_data.groupby("district")
            .size()
            .sort_values(ascending=False)
            .rename("도서관 수")
        )

        st.subheader("자치구별 도서관 분포")

        st.bar_chart(district_counts)

    else:
        st.warning("지도에 표시할 데이터가 없습니다.")




# 아래부터 기존 with tab2: 코드 유지
# 기존 with tab3: 코드도 유지



with tab2:
    st.header("시간적 사각지대 분석")

    analysis = AnalysisService()

    col1, col2 = st.columns(2)

    with col1:
        selected_day = st.selectbox(
            "방문 요일",
            ["월", "화", "수", "목", "금", "토", "일"],
            index=0
        )

    with col2:
        selected_time = st.slider(
            "방문 시간",
            min_value=0.0,
            max_value=23.5,
            value=18.0,
            step=0.5
        )

    summary = analysis.get_summary(
        libraries,
        selected_day,
        selected_time
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("이용 가능", summary["open"])
    col2.metric("이용 불가", summary["closed"])
    col3.metric("판단 불가", summary["unknown"])

    rate = summary["open_rate"]

    col4.metric(
        "운영률",
        f"{rate:.1f}%" if rate is not None else "N/A"
    )

    st.subheader("시간대별 도서관 운영 현황")

    hourly = analysis.get_hourly_statistics(
        libraries,
        selected_day
    )

    hourly_df = pd.DataFrame(hourly)

    st.line_chart(
        hourly_df.set_index("hour")[
            ["open", "closed", "unknown"]
        ].rename(columns={
            "open": "이용 가능",
            "closed": "이용 불가",
            "unknown": "판단 불가"
        })
    )

    st.subheader("시간대별 도서관 운영률")

    st.line_chart(
        hourly_df.set_index("hour")[
            ["open_rate"]
        ].rename(columns={
            "open_rate": "운영률(%)"
        })
    )

    st.subheader("자치구별 운영 현황")

    districts = analysis.get_district_statistics(
        libraries,
        selected_day,
        selected_time
    )

    if districts:
        district_df = pd.DataFrame(districts)

        st.bar_chart(
            district_df.set_index("district")[
                ["open", "closed", "unknown"]
            ].rename(columns={
                "open": "이용 가능",
                "closed": "이용 불가",
                "unknown": "판단 불가"
            })
        )

        st.dataframe(
            district_df,
            hide_index=True
        )

    st.caption(
        "운영률은 운영 여부를 판단할 수 있는 "
        "도서관을 기준으로 계산합니다."
    )

    st.caption(
        "현재 수집된 API 표본을 기준으로 분석하며, "
        "서울 전체 도서관에 대한 전수조사가 아닙니다."
    )

    st.warning(
        "공휴일 및 복잡한 정기 휴관 규칙은 "
        "아직 완전히 반영되지 않았습니다."
    )

    st.subheader("요일·시간대별 도서관 운영률")

    weekly = analysis.get_weekly_statistics(
        libraries
    )

    weekly_df = pd.DataFrame(weekly)

    heatmap = (
        alt.Chart(weekly_df)
        .mark_rect()
        .encode(
            x=alt.X(
                "hour:O",
                title="시간"
            ),
            y=alt.Y(
                "day:O",
                sort=[
                    "월", "화", "수", "목",
                    "금", "토", "일"
                ],
                title="요일"
            ),
            color=alt.Color(
                "open_rate:Q",
                scale=alt.Scale(
                    scheme="redyellowgreen",
                    domain=[0, 100]
                ),
                title="운영률(%)"
            ),
            tooltip=[
                alt.Tooltip("day:N", title="요일"),
                alt.Tooltip("hour:O", title="시간"),
                alt.Tooltip("open:Q", title="이용 가능"),
                alt.Tooltip("closed:Q", title="이용 불가"),
                alt.Tooltip("unknown:Q", title="판단 불가"),
                alt.Tooltip(
                    "open_rate:Q",
                    title="운영률(%)",
                    format=".1f"
                )
            ]
        )
        .properties(height=250)
    )

    st.altair_chart(
        heatmap,
        use_container_width=True
    )

    st.caption(
        "운영률은 판단 가능한 도서관을 기준으로 "
        "계산합니다. 판단 가능한 도서관이 없는 "
        "시간대의 운영률은 표시하지 않습니다."
    )

    st.subheader("학생·직장인 이용 가능성 비교")

    comparison = analysis.compare_user_types(
        libraries,
        selected_day
    )

    comparison_df = pd.DataFrame(comparison)

    st.line_chart(
        comparison_df.set_index("hour")[
            ["student", "worker"]
        ].rename(columns={
            "student": "학생",
            "worker": "직장인"
        })
    )

    st.caption(
        "학생은 기준 시각에 방문하고, "
        "직장인은 1시간 후 방문한다는 "
        "가정에 따른 시뮬레이션입니다. "
        "거리 및 도서 보유 조건은 적용하지 않습니다."
    )



with tab3:
    st.header("🔍 내 조건에 맞는 도서관 찾기")
    
    col1, col2, col3 = st.columns(3)
    with col1: user_type = st.radio("사용자 유형", ["직장인", "학생"])
    with col2: user_time = st.number_input("퇴근/하교 시간", 0, 23, 18)
    with col3: search_book = st.selectbox("찾고 싶은 책", ["이기적 유전자", "사피엔스", "클린 코드", "코스모스", "총균쇠"])
    
    st.markdown("---")
    st.subheader("📍 출발 위치 설정")
    
    # 위치 선택 UI 추가
    location_choice = st.radio(
        "어디서 출발하시나요?", 
        ["광운대학교 (기본)", "강남역", "직접 입력(위/경도)"], 
        horizontal=True
    )
    
    # 선택에 따라 my_lat, my_lon 변수의 값을 동적으로 변경
    if location_choice == "광운대학교 (기본)":
        my_lat, my_lon = 37.6194, 127.0583
    elif location_choice == "강남역":
        my_lat, my_lon = 37.4980, 127.0276
    else:
        # 직접 입력할 수 있는 칸 생성
        loc_col1, loc_col2 = st.columns(2)
        with loc_col1: my_lat = st.number_input("위도(Latitude)", value=37.5665, format="%.4f")
        with loc_col2: my_lon = st.number_input("경도(Longitude)", value=126.9780, format="%.4f")
        
    if st.button("도서관 검색 알고리즘 실행", type="primary"):
        st.markdown("---")
        
        # 1. UI에서 동적으로 설정된 my_lat, my_lon을 User 객체에 주입!
        if user_type == "직장인":
            user = OfficeWorker(my_lat, my_lon, int(user_time))
        else:
            user = Student(my_lat, my_lon, int(user_time))
            
        avail_time = user.get_available_time()
        st.write(f"💡 {user_type} 객체 연산: {location_choice}에서 출발 시 도착 가능 시간은 **{avail_time}시**입니다.")
        
        # 2. 추천 서비스 호출 (비즈니스 로직 분리)
        service = RecommendationService()
        recommendation = service.recommend_libraries(
            user,
            libraries,
            search_book,
            day=recommend_day
        )
        
        total_count = recommendation["total_count"]
        results = recommendation["top_results"]
        
        if total_count > 0:
            st.success(f"총 {total_count}개의 도서관을 찾았습니다!")
            
            for item in results:
                lib = item["library"]
                dist = item["distance"]
                close_t = item["close_time"]
                # 도서관 객체 스스로 혼잡도를 계산하도록 메시지 전달
                congestion = lib.get_congestion_rate(
                    avail_time, recommend_day
                )

                crowded = lib.is_crowded(
                    avail_time, recommend_day
                )  

                status_icon = "🔴 혼잡 (자리 부족 우려)" if lib.is_crowded(avail_time) else "🟢 여유"
                
                st.markdown(f"### {lib.name}")
                st.write(f"📍 거리: {dist:.1f}km | 🕒 마감: {close_t}시 | {status_icon}")
                
                # Streamlit 프로그레스 바를 이용한 혼잡도 시각화
                st.progress(congestion / 100, text=f"예상 좌석 사용률: {congestion:.1f}% ({current_users}/{lib.max_seats}석)")
                st.write("---")
        else:
            st.error("조건에 완벽하게 일치하는 도서관이 없습니다.")
        recommend_day = st.selectbox(
            "도서관 방문 요일",
            ["월", "화", "수", "목", "금", "토", "일"],
            key="recommend_day"
        )    
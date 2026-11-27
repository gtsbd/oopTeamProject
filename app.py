
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
from models.location import Location

from services.spatial_analysis_service import (
    SpatialAnalysisService
)

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
    st.header("개인 맞춤 도서관 추천")

    st.caption(
        "요일, 방문 시간, 출발 위치, 검색 반경을 "
        "기반으로 도서관을 분석합니다."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        user_type = st.radio(
            "사용자 유형",
            ["학생", "직장인"],
            key="recommend_user_type"
        )

    with col2:
        recommend_day = st.selectbox(
            "도서관 방문 요일",
            ["월", "화", "수", "목", "금", "토", "일"],
            key="recommend_day"
        )

    with col3:
        user_time = st.number_input(
            "퇴근 / 하교 시간",
            min_value=0,
            max_value=23,
            value=18,
            step=1,
            key="recommend_time"
        )

    st.subheader("검색 조건")

    col1, col2 = st.columns(2)

    with col1:
        search_book = st.selectbox(
            "희망 도서 (모의 데이터)",
            [
                "도서 조건 없음",
                "이기적 유전자",
                "사피엔스",
                "클린 코드",
                "코스모스",
                "총균쇠"
            ]
        )

    with col2:
        radius = st.selectbox(
            "검색 반경 (km)",
            [1, 3, 5, 10],
            index=1
        )

    book_title = (
        None
        if search_book == "도서 조건 없음"
        else search_book
    )

    st.subheader("출발 위치 설정")

    location_choice = st.radio(
        "어디서 출발하시나요?",
        [
            "광운대학교",
            "강남역",
            "직접 입력"
        ],
        horizontal=True
    )

    if location_choice == "광운대학교":
        my_lat, my_lon = 37.6194, 127.0583

    elif location_choice == "강남역":
        my_lat, my_lon = 37.4980, 127.0276

    else:
        col1, col2 = st.columns(2)

        with col1:
            my_lat = st.number_input(
                "위도",
                min_value=-90.0,
                max_value=90.0,
                value=37.5665,
                format="%.4f"
            )

        with col2:
            my_lon = st.number_input(
                "경도",
                min_value=-180.0,
                max_value=180.0,
                value=126.9780,
                format="%.4f"
            )

    if st.button(
        "도서관 검색 알고리즘 실행",
        type="primary",
        key="recommend_search"
    ):
        # 1. 사용자 객체 생성
        if user_type == "직장인":
            user = OfficeWorker(
                my_lat, my_lon, int(user_time)
            )
        else:
            user = Student(
                my_lat, my_lon, int(user_time)
            )

        avail_time = user.get_available_time()

        if avail_time >= 24:
            st.warning(
                "도착 예정 시간이 자정을 넘어 "
                "당일 추천이 불가능합니다."
            )

        else:
            origin = Location(my_lat, my_lon)

            spatial = SpatialAnalysisService()
            service = RecommendationService()

            st.divider()

            st.info(
                f"{user_type} | "
                f"{recommend_day}요일 | "
                f"도착 예정 {avail_time:02.0f}:00 | "
                f"검색 반경 {radius}km"
            )

            # 2. 공간적 접근성 분석
            stats = spatial.get_radius_statistics(
                libraries,
                origin,
                recommend_day,
                avail_time,
                radii=(1, 3, 5, 10)
            )

            stats_df = pd.DataFrame(stats)

            nearby = spatial.get_nearby_libraries(
                libraries,
                origin,
                radius
            )

            selected_stats = next(
                row for row in stats
                if row["radius"] == radius
            )

            st.subheader("반경 내 접근성 분석")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "반경 내 도서관",
                selected_stats["total"]
            )

            col2.metric(
                "이용 가능",
                selected_stats["open"]
            )

            col3.metric(
                "이용 불가",
                selected_stats["closed"]
            )

            col4.metric(
                "판단 불가",
                selected_stats["unknown"]
            )

            if selected_stats["total"] == 0:
                st.warning(
                    "수집된 데이터에서 해당 반경 내 "
                    "도서관을 찾을 수 없습니다."
                )

            elif selected_stats["open"] == 0:
                st.warning(
                    "현재 조건에서 이용 가능한 것으로 "
                    "판단된 도서관이 없습니다."
                )

            st.bar_chart(
                stats_df.set_index("radius")[
                    ["open", "closed", "unknown"]
                ].rename(columns={
                    "open": "이용 가능",
                    "closed": "이용 불가",
                    "unknown": "판단 불가"
                })
            )

            st.caption(
                "각 반경의 집계값은 누적 값입니다. "
                "도서 보유 조건은 적용하지 않았습니다."
            )

            # 3. 운영 상태별 지도 데이터 생성
            colors = {
                "open": "#22C55E",
                "closed": "#EF4444",
                "unknown": "#94A3B8"
            }

            map_rows = [{
                "name": "출발 위치",
                "lat": my_lat,
                "lon": my_lon,
                "color": "#2563EB",
                "size": 100
            }]

            for item in nearby:
                lib = item["library"]

                status = lib.get_status(
                    avail_time, recommend_day
                )

                map_rows.append({
                    "name": lib.name,
                    "lat": lib.location.lat,
                    "lon": lib.location.lon,
                    "color": colors[status],
                    "size": 55
                })

            st.subheader("도서관 운영 상태 지도")

            st.map(
                pd.DataFrame(map_rows),
                latitude="lat",
                longitude="lon",
                color="color",
                size="size"
            )

            st.caption(
                "🔵 출발 위치 | "
                "🟢 이용 가능 | "
                "🔴 이용 불가 | "
                "⚪ 판단 불가"
            )

            # 4. 맞춤 추천 서비스 호출
            recommendation = service.recommend_libraries(
                user,
                libraries,
                book_title,
                day=recommend_day,
                radius_km=radius
            )

            total_count = recommendation["total_count"]
            results = recommendation["top_results"]

            st.divider()
            st.subheader("맞춤 도서관 추천 결과")

            if total_count == 0:
                st.warning(
                    "현재 검색 조건을 만족하는 "
                    "도서관이 없습니다."
                )

            else:
                st.success(
                    f"조건을 만족하는 도서관 "
                    f"{total_count}개 중 상위 "
                    f"{len(results)}개를 추천합니다."
                )

                recommendation_map = [{
                    "name": "출발 위치",
                    "lat": my_lat,
                    "lon": my_lon,
                    "color": "#2563EB",
                    "size": 100
                }]

                for rank, item in enumerate(
                    results, start=1
                ):
                    lib = item["library"]
                    dist = item["distance"]
                    close_t = item["close_time"]

                    close_minutes = round(close_t * 60)

                    close_label = (
                        f"{close_minutes // 60:02d}:"
                        f"{close_minutes % 60:02d}"
                    )

                    congestion = lib.get_congestion_rate(
                        avail_time, recommend_day
                    )

                    current_users = int(
                        lib.max_seats * congestion / 100
                    )

                    st.markdown(
                        f"### {rank}. {lib.name}"
                    )

                    st.write(
                        f"직선거리: {dist:.2f}km | "
                        f"마감시간: {close_label}"
                    )

                    st.caption(
                        f"{lib.district} | {lib.address}"
                    )

                    st.progress(
                        congestion / 100,
                        text=(
                            f"모의 좌석 사용률: "
                            f"{congestion:.1f}% "
                            f"({current_users}/"
                            f"{lib.max_seats}석)"
                        )
                    )

                    recommendation_map.append({
                        "name": lib.name,
                        "lat": lib.location.lat,
                        "lon": lib.location.lon,
                        "color": "#22C55E",
                        "size": 75
                    })

                    st.divider()

                st.subheader("추천 도서관 위치")

                st.map(
                    pd.DataFrame(recommendation_map),
                    latitude="lat",
                    longitude="lon",
                    color="color",
                    size="size"
                )

            st.caption(
                "거리는 Haversine 기반 지표면 거리이며 "
                "실제 도보 또는 대중교통 이동 거리가 아닙니다."
            )

            st.caption(
                "직장인 이동시간 1시간, 도서 보유 여부, "
                "좌석 수 및 혼잡도는 시뮬레이션 가정입니다."
            )

            st.caption(
                "공휴일 및 복잡한 휴관 규칙은 "
                "완전히 반영되지 않았습니다."
            )


import streamlit as st

from models.user import Student, OfficeWorker
from models.location import Location

from services.spatial_analysis_service import (
    SpatialAnalysisService
)
from services.recommendation_service import (
    RecommendationService
)

from views.map_renderer import MapRenderer
from views.chart_renderer import ChartRenderer


def render_recommendation(libraries):

    # ==========================================
    # 1. 화면 제목 및 사용자 입력
    # ==========================================

    st.header("공간적 사각지대 분석 및 맞춤 추천")

    st.caption(
        "사용자의 위치, 방문 시간, 검색 반경을 "
        "기반으로 이용 가능한 도서관을 분석합니다."
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

    # ==========================================
    # 2. 도서 및 검색 반경 설정
    # ==========================================

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

    # ==========================================
    # 3. 출발 위치 설정
    # ==========================================

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

    # ==========================================
    # 4. 검색 조건 저장 및 상태 관리
    # ==========================================

    search_signature = (
        user_type,
        recommend_day,
        user_time,
        search_book,
        radius,
        my_lat,
        my_lon
    )

    if st.button(
        "도서관 검색 알고리즘 실행",
        type="primary",
        key="recommend_search"
    ):
        st.session_state["last_search"] = (
            search_signature
        )

    last_search = st.session_state.get(
        "last_search"
    )

    # 아직 검색하지 않은 경우
    if last_search is None:
        st.info(
            "검색 조건을 설정한 뒤 "
            "검색 버튼을 눌러주세요."
        )
        return

    # 검색 이후 입력 조건이 변경된 경우
    if last_search != search_signature:
        st.info(
            "검색 조건이 변경되었습니다. "
            "검색 버튼을 다시 눌러주세요."
        )
        return

    # ==========================================
    # 5. 사용자 객체 생성
    # ==========================================

    if user_type == "직장인":
        user = OfficeWorker(
            my_lat,
            my_lon,
            int(user_time)
        )
    else:
        user = Student(
            my_lat,
            my_lon,
            int(user_time)
        )

    avail_time = user.get_available_time()

    if not 0 <= avail_time < 24:
        st.warning(
            "도착 예정 시간이 당일 범위를 넘어 "
            "추천할 수 없습니다."
        )
        return

    origin = Location(my_lat, my_lon)

    arrival_minutes = round(avail_time * 60)

    arrival_label = (
        f"{arrival_minutes // 60:02d}:"
        f"{arrival_minutes % 60:02d}"
    )

    st.divider()

    st.info(
        f"{user_type} | "
        f"{recommend_day}요일 | "
        f"도착 예정 {arrival_label} | "
        f"검색 반경 {radius}km"
    )

    # ==========================================
    # 6. 공간적 접근성 분석
    # ==========================================

    spatial = SpatialAnalysisService()

    stats = spatial.get_radius_statistics(
        libraries,
        origin,
        recommend_day,
        avail_time,
        radii=(1, 3, 5, 10)
    )

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
            "해당 반경 내 도서관을 "
            "수집된 데이터에서 찾을 수 없습니다."
        )

    elif selected_stats["open"] == 0:
        st.warning(
            "현재 조건에서 이용 가능한 것으로 "
            "판단된 도서관이 없습니다."
        )

    # ==========================================
    # 7. 맞춤 추천 알고리즘 실행
    # ==========================================

    service = RecommendationService()

    recommendation = service.recommend_libraries(
        user,
        libraries,
        book_title,
        day=recommend_day,
        radius_km=radius
    )

    total_count = recommendation["total_count"]
    results = recommendation["top_results"]

    # ==========================================
    # 8. 지도 및 추천 결과 좌우 배치
    # ==========================================

    st.divider()

    map_col, result_col = st.columns(
        [1.3, 1],
        gap="large"
    )

    # 왼쪽: 지도
    with map_col:

        st.subheader("공간적 접근성 지도")

        renderer = MapRenderer()

        renderer.render_accessibility(
            origin=origin,
            nearby=nearby,
            day=recommend_day,
            time=avail_time,
            radius_km=radius
        )

    # 오른쪽: 추천 목록
    with result_col:

        st.subheader("추천 도서관 TOP 5")

        if total_count == 0:

            st.warning(
                "현재 검색 조건을 만족하는 "
                "도서관이 없습니다."
            )

        else:

            st.success(
                f"조건을 만족하는 도서관 "
                f"{total_count}개 중 "
                f"{len(results)}개를 추천합니다."
            )

            for rank, item in enumerate(
                results, start=1
            ):
                lib = item["library"]
                dist = item["distance"]
                close_t = item["close_time"]

                # 마감시간 출력 형식 변환
                if close_t is not None:
                    close_minutes = round(close_t * 60)

                    close_label = (
                        f"{close_minutes // 60:02d}:"
                        f"{close_minutes % 60:02d}"
                    )
                else:
                    close_label = "미확인"

                # 모의 혼잡도 계산
                congestion = lib.get_congestion_rate(
                    avail_time,
                    recommend_day
                )

                current_users = int(
                    lib.max_seats * congestion / 100
                )

                st.markdown(
                    f"**{rank}. {lib.name}**"
                )

                st.write(
                    f"직선거리 {dist:.2f}km | "
                    f"마감 {close_label}"
                )

                st.caption(
                    f"{lib.district} | {lib.address}"
                )

                st.progress(
                    congestion / 100,
                    text=(
                        f"모의 좌석 사용률 "
                        f"{congestion:.1f}% "
                        f"({current_users}/"
                        f"{lib.max_seats}석)"
                    )
                )

                st.divider()

    # ==========================================
    # 9. 반경별 비교 그래프
    # ==========================================

    st.subheader("반경별 접근성 비교")

    ChartRenderer().render_radius_chart(stats)

    st.caption(
        "각 반경의 집계값은 누적 값이며 "
        "도서 보유 조건은 적용하지 않았습니다."
    )

    # ==========================================
    # 10. 데이터 및 분석 한계 안내
    # ==========================================

    with st.expander("분석 기준 및 데이터 한계"):

        st.write(
            "• 거리는 Haversine 공식으로 계산한 "
            "지표면 거리이며 실제 이동 거리가 아닙니다."
        )

        st.write(
            "• 직장인의 이동시간 1시간은 "
            "프로젝트에서 설정한 가정입니다."
        )

        st.write(
            "• 도서 보유 정보, 좌석 수 및 "
            "혼잡도는 모의 데이터입니다."
        )

        st.write(
            "• 공휴일 및 복잡한 정기 휴관 "
            "규칙은 완전히 반영되지 않았습니다."
        )

        st.write(
            "• 지도는 검색 반경 내 도서관의 "
            "운영 상태를 표시합니다. "
            "추천 목록은 추가 도서 조건을 "
            "만족하는 결과입니다."
        )

import os
import streamlit as st
import pandas as pd
import altair as alt
from views.chart_renderer import ChartRenderer
from views.map_renderer import MapRenderer
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

def render_overview(manager, libraries):
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


from views.overview import render_overview
from views.temporal import render_temporal
from views.recommendation import render_recommendation


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

st.sidebar.header("데이터 관리")

if st.sidebar.button(
    "API 데이터 새로고침",
    key="refresh_api"
):
    load_manager.clear()

    st.session_state.pop(
        "last_search",
        None
    )

st.sidebar.caption(
    "데이터 출처: 서울 열린데이터광장"
)

st.sidebar.caption(
    "API 데이터는 최대 1시간 동안 캐싱됩니다."
)


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
    render_overview(manager, libraries)




# 아래부터 기존 with tab2: 코드 유지
# 기존 with tab3: 코드도 유지



with tab2:
    render_temporal(libraries)




with tab3:
    render_recommendation(libraries)

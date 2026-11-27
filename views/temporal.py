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

def render_temporal(libraries):
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


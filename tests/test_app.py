
from pathlib import Path

import streamlit as st

from streamlit.testing.v1 import AppTest

from repositories.seoul_api import SeoulAPIRepository


APP_PATH = (
    Path(__file__).resolve().parents[1] / "app.py"
)


def test_app_recommendation_flow(monkeypatch):

    # 실제 API 대신 테스트용 데이터 사용
    monkeypatch.setenv(
        "SEOUL_API_KEY",
        "test-key"
    )

    def fake_load(self):
        return [{
            "LBRRY_NAME": "테스트 도서관",
            "CODE_VALUE": "노원구",
            "ADRES": "테스트 주소",
            "XCNTS": "37.6194",
            "YDNTS": "127.0583",
            "OP_TIME": (
                "평일 : 09:00~22:00, "
                "주말 : 09:00~18:00"
            ),
            "FDRM_CLOSE_DATE": ""
        }]

    monkeypatch.setattr(
        SeoulAPIRepository,
        "load",
        fake_load
    )

    st.cache_resource.clear()

    try:
        app = AppTest.from_file(
            str(APP_PATH),
            default_timeout=30
        )

        # 최초 화면 실행 검증
        app.run()

        assert len(app.exception) == 0

        # 실제 검색 버튼 실행 검증
        app.button(
            key="recommend_search"
        ).click().run()

        assert len(app.exception) == 0

        assert any(
            "조건을 만족하는 도서관" in item.value
            for item in app.success
        )

    finally:
        st.cache_resource.clear()

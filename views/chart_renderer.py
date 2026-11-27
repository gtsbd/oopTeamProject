
import altair as alt
import pandas as pd
import streamlit as st


class ChartRenderer:

    STATUS_COLORS = [
        "#16A34A",
        "#EF4444",
        "#94A3B8"
    ]

    STATUS_LABELS = [
        "이용 가능",
        "이용 불가",
        "판단 불가"
    ]

    def render_radius_chart(self, statistics):

        df = pd.DataFrame(statistics)

        df = df.rename(columns={
            "open": "이용 가능",
            "closed": "이용 불가",
            "unknown": "판단 불가"
        })

        df = df.melt(
            id_vars=["radius"],
            value_vars=self.STATUS_LABELS,
            var_name="status",
            value_name="count"
        )

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X(
                    "radius:O",
                    title="검색 반경 (km)",
                    sort="ascending"
                ),
                y=alt.Y(
                    "count:Q",
                    title="도서관 수 (개)",
                    stack="zero"
                ),
                color=alt.Color(
                    "status:N",
                    title="운영 상태",
                    scale=alt.Scale(
                        domain=self.STATUS_LABELS,
                        range=self.STATUS_COLORS
                    )
                ),
                tooltip=[
                    alt.Tooltip(
                        "radius:O",
                        title="반경(km)"
                    ),
                    alt.Tooltip(
                        "status:N",
                        title="운영 상태"
                    ),
                    alt.Tooltip(
                        "count:Q",
                        title="도서관 수"
                    )
                ]
            )
            .properties(height=280)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

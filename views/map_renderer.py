
import pydeck as pdk
import streamlit as st
import pandas as pd


class MapRenderer:

    COLORS = {
        "open": [22, 163, 74, 230],
        "closed": [239, 68, 68, 230],
        "unknown": [148, 163, 184, 230],
        "origin": [37, 99, 235, 255]
    }

    STATUS_LABELS = {
        "open": "이용 가능",
        "closed": "이용 불가",
        "unknown": "판단 불가"
    }

    @staticmethod
    def _get_zoom(radius_km):
        if radius_km <= 1:
            return 13
        if radius_km <= 3:
            return 11.5
        if radius_km <= 5:
            return 10.5

        return 9.5

    def render_accessibility(
        self,
        origin,
        nearby,
        day,
        time,
        radius_km
    ):
        points = []

        for item in nearby:
            library = item["library"]

            status = library.get_status(time, day)

            points.append({
                "name": library.name,
                "lat": library.location.lat,
                "lon": library.location.lon,
                "district": library.district,
                "distance": (
                    f'{item["distance"]:.2f}km'
                ),
                "status": self.STATUS_LABELS[status],
                "color": self.COLORS[status],
                "size": 45
            })

        points.append({
            "name": "출발 위치",
            "lat": origin.lat,
            "lon": origin.lon,
            "district": "-",
            "distance": "0km",
            "status": "검색 기준점",
            "color": self.COLORS["origin"],
            "size": 85
        })

        origin_df = pd.DataFrame([{
            "lat": origin.lat,
            "lon": origin.lon,
            "radius": radius_km * 1000
        }])

        radius_layer = pdk.Layer(
            "ScatterplotLayer",
            data=origin_df,
            get_position="[lon, lat]",
            get_radius="radius",
            get_fill_color=[37, 99, 235, 22],
            get_line_color=[37, 99, 235, 200],
            stroked=True,
            filled=True,
            line_width_min_pixels=2,
            radius_units="meters",
            pickable=False
        )

        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame(points),
            get_position="[lon, lat]",
            get_radius="size",
            get_fill_color="color",
            radius_min_pixels=4,
            radius_max_pixels=12,
            pickable=True,
            stroked=True,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=1
        )

        view_state = pdk.ViewState(
            latitude=origin.lat,
            longitude=origin.lon,
            zoom=self._get_zoom(radius_km),
            pitch=0
        )

        tooltip = {
            "text": (
                "{name}\n"
                "지역: {district}\n"
                "거리: {distance}\n"
                "상태: {status}"
            ),
            "style": {
                "backgroundColor": "#172B4D",
                "color": "white"
            }
        }

        deck = pdk.Deck(
            layers=[radius_layer, point_layer],
            initial_view_state=view_state,
            map_style="light",
            tooltip=tooltip
        )

        st.pydeck_chart(deck, height=480)

        st.caption(
            "🔵 출발 위치 및 검색 반경 | "
            "🟢 이용 가능 | 🔴 이용 불가 | "
            "⚪ 판단 불가"
        )

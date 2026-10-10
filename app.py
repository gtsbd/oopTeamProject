import streamlit as st
from models.user import OfficeWorker, Student
from data_manager import SystemManager

st.set_page_config(page_title="서울시 도서관 사각지대 시뮬레이터", layout="wide")

# 데이터 한 번만 로드하기 (캐싱)
@st.cache_resource
def load_manager():
    return SystemManager()

manager = load_manager()
libraries = manager.get_libraries()

st.title("📚 서울시 도서관 시공간 사각지대 및 맞춤 추천")
st.markdown("객체지향 프로그래밍(OOP)을 활용한 정책 시뮬레이터")

# 기획서의 흐름대로 탭 생성
tab1, tab2, tab3 = st.tabs(["1. 데이터 현황 파악", "2. 시간적 사각지대 시뮬레이션", "3. 내 맞춤 도서관 찾기 (다형성)"])

with tab1:
    st.header("📊 서울시 공공도서관 데이터 로드 완료")
    st.success(f"실시간 API를 통해 **{len(libraries)}개**의 도서관 객체와 더미 도서 데이터가 성공적으로 매핑되었습니다.")
    st.write("단순히 도서관 개수가 많다고 해서 모든 시민이 혜택을 누릴 수 있는 것은 아닙니다. 옆 탭에서 '시간'의 개념을 더해 진짜 사각지대를 찾아보세요.")

with tab2:
    st.header("⏳ 시간에 따른 도서관 활성화 시뮬레이션")
    test_time = st.slider("시간을 조절해보세요", 9, 23, 14)
    
    open_count = sum(1 for lib in libraries if lib.is_open(test_time))
    closed_count = len(libraries) - open_count
    
    st.metric(label=f"{test_time}시 기준 운영 중인 도서관", value=f"{open_count}개", delta=f"-{closed_count}개 (운영 종료)")
    if test_time >= 18:
        st.warning("퇴근 시간 이후 많은 도서관 객체의 is_open() 상태가 False로 변경되며 심각한 사각지대가 발생합니다.")

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
        
        # 2. 객체 간 메시지 패싱으로 필터링
        results = []
        for lib in libraries:
            dist = user.location.calculate_distance(lib.location)
            
            # 은닉화된 메서드 호출
            if lib.is_open(avail_time) and lib.has_book(search_book):
                # 객체 자체(lib)를 리스트에 담아줍니다.
                results.append((lib, dist, lib.close_time))
                
        # 3. 거리순 정렬 후 출력
        results.sort(key=lambda x: x[1])
        
        if results:
            st.success(f"총 {len(results)}개의 도서관을 찾았습니다!")
            
            for lib, dist, close_t in results[:5]: # 가장 가까운 5개만 추천
                # 도서관 객체 스스로 혼잡도를 계산하도록 메시지 전달
                congestion = lib.get_congestion_rate(avail_time)
                current_users = int(lib.max_seats * (congestion / 100))
                
                status_icon = "🔴 혼잡 (자리 부족 우려)" if lib.is_crowded(avail_time) else "🟢 여유"
                
                st.markdown(f"### {lib.name}")
                st.write(f"📍 거리: {dist:.1f}km | 🕒 마감: {close_t}시 | {status_icon}")
                
                # Streamlit 프로그레스 바를 이용한 혼잡도 시각화
                st.progress(congestion / 100, text=f"예상 좌석 사용률: {congestion:.1f}% ({current_users}/{lib.max_seats}석)")
                st.write("---")
        else:
            st.error("조건에 완벽하게 일치하는 도서관이 없습니다.")

import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="세계 유명 디저트 TOP 10",
    page_icon="🍰",
    layout="wide"
)

# 제목
st.title("🍰 세계 유명 디저트 TOP 10")
st.write(
    "세계 여러 도시의 대표 디저트와 관광지를 "
    "지도와 데이터로 알아보는 프로그램입니다."
)

st.divider()

# 디저트 데이터
data = {
    "순위": list(range(1, 11)),
    "도시": [
        "파리", "도쿄", "로마", "빈", "뉴욕",
        "이스탄불", "서울", "리스본", "멕시코시티", "방콕"
    ],
    "국가": [
        "프랑스", "일본", "이탈리아", "오스트리아",
        "미국", "튀르키예", "대한민국", "포르투갈",
        "멕시코", "태국"
    ],
    "디저트": [
        "마카롱", "말차 파르페", "티라미수",
        "자허토르테", "뉴욕 치즈케이크",
        "바클라바", "빙수", "파스텔 드 나타",
        "추로스", "망고 찹쌀밥"
    ],
    "관광지": [
        "에펠탑", "센소지", "콜로세움",
        "슈테판 대성당", "타임스스퀘어",
        "아야 소피아", "경복궁", "벨렝탑",
        "소칼로 광장", "방콕 왕궁"
    ],
    "latitude": [
        48.8584, 35.7148, 41.8902, 48.2085,
        40.7580, 41.0086, 37.5796, 38.6916,
        19.4326, 13.7500
    ],
    "longitude": [
        2.2945, 139.7967, 12.4922, 16.3731,
        -73.9855, 28.9802, 126.9770, -9.2160,
        -99.1332, 100.4913
    ],
    "설명": [
        "프랑스를 대표하는 알록달록하고 섬세한 디저트입니다. 에펠탑은 파리의 상징입니다.",
        "말차의 쌉싸름한 맛과 다양한 토핑이 특징입니다. 센소지는 도쿄의 유명 사찰입니다.",
        "커피와 마스카르포네 치즈가 어우러진 디저트입니다. 콜로세움은 고대 로마의 유적입니다.",
        "초콜릿과 살구잼을 활용한 오스트리아의 케이크입니다. 슈테판 대성당은 빈의 명소입니다.",
        "진하고 부드러운 치즈 맛이 특징입니다. 타임스스퀘어는 뉴욕의 대표 관광지입니다.",
        "얇은 페이스트리와 견과류, 시럽을 활용합니다. 아야 소피아는 이스탄불의 역사적 건축물입니다.",
        "얼음과 다양한 토핑을 함께 즐기는 한국의 디저트입니다. 경복궁은 조선 왕조의 궁궐입니다.",
        "바삭한 페이스트리와 커스터드 크림이 특징입니다. 벨렝탑은 리스본의 역사적인 명소입니다.",
        "튀긴 반죽에 설탕과 계피를 입힌 디저트입니다. 소칼로 광장은 멕시코시티의 중심 광장입니다.",
        "망고와 코코넛 밀크, 찹쌀을 함께 즐깁니다. 방콕 왕궁은 태국의 대표 관광지입니다."
    ]
}

df = pd.DataFrame(data)

# 세계 지도
st.subheader("🗺️ 세계 디저트 지도")
st.write("지도에서 각 도시의 위치를 확인할 수 있습니다.")

map_data = df[["latitude", "longitude"]].copy()
map_data.columns = ["lat", "lon"]

st.map(
    map_data,
    zoom=1,
    use_container_width=True
)

st.caption("지도에 표시된 위치는 각 도시의 대표 관광지 좌표입니다.")

st.divider()

# 국가 선택
st.subheader("🌍 국가별 디저트 검색")

countries = ["전체"] + sorted(df["국가"].unique().tolist())

selected_country = st.selectbox(
    "국가를 선택하세요.",
    countries
)

if selected_country == "전체":
    result = df
else:
    result = df[df["국가"] == selected_country]

# 요약 정보
col1, col2, col3 = st.columns(3)

col1.metric("소개 도시", f"{len(result)}곳")
col2.metric("디저트 종류", f"{result['디저트'].nunique()}종")
col3.metric("소개 국가", f"{result['국가'].nunique()}개국")

st.divider()

# 디저트 상세 정보
st.subheader("🍮 도시별 대표 디저트")

for _, row in result.iterrows():

    with st.expander(
        f"🏅 {row['순위']}위 | {row['도시']} ({row['국가']})"
    ):
        st.markdown(f"### 🍰 {row['디저트']}")
        st.write(f"📍 주요 관광지: {row['관광지']}")
        st.write(row["설명"])
        st.write(
            f"위도: {row['latitude']} / "
            f"경도: {row['longitude']}"
        )

st.divider()

# 국가별 도시 수 그래프
st.subheader("📊 국가별 디저트 도시 수")

country_count = (
    df["국가"]
    .value_counts()
    .reset_index()
)

country_count.columns = ["국가", "도시 수"]

st.bar_chart(
    country_count,
    x="국가",
    y="도시 수"
)

st.divider()

# 분석 결과
st.subheader("📝 분석 결과")

st.write("""
세계 여러 나라의 디저트는 각 나라의 식문화와
사용하는 재료에 따라 다양한 특징을 가지고 있습니다.

프랑스의 마카롱, 이탈리아의 티라미수,
일본의 말차 파르페처럼 같은 디저트라도
나라별로 독특한 문화가 반영되어 있습니다.

이번 분석을 통해 세계 디저트의 다양성과
각 도시의 대표 관광지를 함께 알아볼 수 있습니다.
""")

st.caption(
    "※ 교육용으로 선정한 세계 디저트 10종이며 "
    "공식적인 전 세계 인기 순위는 아닙니다."
)

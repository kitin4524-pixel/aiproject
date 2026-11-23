
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="세계 디저트 TOP 10",
    page_icon="🍰",
    layout="wide"
)

# 제목
st.title("🍰 세계 유명 디저트 TOP 10")
st.write(
    "세계 여러 도시의 대표 디저트와 유명 관광지를 "
    "세계 지도에서 확인해 보세요!"
)

st.divider()

# 디저트 데이터
data = {
    "순위": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
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
        "마카롱", "말차 파르페", "티라미수", "자허토르테",
        "뉴욕 치즈케이크", "바클라바", "빙수",
        "파스텔 드 나타", "추로스", "망고 찹쌀밥"
    ],
    "관광지": [
        "에펠탑", "센소지", "콜로세움", "슈테판 대성당",
        "타임스스퀘어", "아야 소피아", "경복궁",
        "벨렝탑", "소칼로 광장", "방콕 왕궁"
    ],
    "위도": [
        48.8584, 35.7148, 41.8902, 48.2085, 40.7580,
        41.0086, 37.5796, 38.6916, 19.4326, 13.7500
    ],
    "경도": [
        2.2945, 139.7967, 12.4922, 16.3731, -73.9855,
        28.9802, 126.9770, -9.2160, -99.1332, 100.4913
    ],
    "설명": [
        "프랑스를 대표하는 섬세하고 알록달록한 디저트입니다. 에펠탑은 파리의 상징적인 랜드마크입니다.",
        "말차의 쌉싸름한 맛과 다양한 토핑을 즐기는 디저트입니다. 센소지는 도쿄 아사쿠사의 유명 사찰입니다.",
        "커피와 마스카르포네 치즈가 어우러진 이탈리아 디저트입니다. 콜로세움은 고대 로마의 대표 유적입니다.",
        "초콜릿과 살구잼을 활용한 오스트리아의 유명 케이크입니다. 슈테판 대성당은 빈의 대표 명소입니다.",
        "진한 치즈의 풍미가 특징인 미국식 치즈케이크입니다. 타임스스퀘어는 뉴욕의 대표 관광지입니다.",
        "얇은 페이스트리와 견과류, 시럽을 활용한 튀르키예 디저트입니다. 아야 소피아는 이스탄불의 역사적 건축물입니다.",
        "얼음과 다양한 토핑을 함께 즐기는 한국의 대표적인 디저트입니다. 경복궁은 조선 왕조의 대표 궁궐입니다.",
        "바삭한 페이스트리와 달콤한 커스터드 크림이 특징인 포르투갈 디저트입니다. 벨렝탑은 리스본의 역사적인 명소입니다.",
        "튀긴 반죽에 설탕과 계피를 입힌 디저트입니다. 소칼로 광장은 멕시코시티의 중심 광장입니다.",
        "망고와 코코넛 밀크, 찹쌀을 함께 즐기는 태국 디저트입니다. 방콕 왕궁은 태국의 대표 관광지입니다."
    ]
}

df = pd.DataFrame(data)

# 세계 지도
st.subheader("🗺️ 세계 디저트 지도")
st.write("지도 위의 빨간색 마커를 클릭하면 디저트 정보를 볼 수 있습니다.")

world_map = folium.Map(
    location=[25, 10],
    zoom_start=2,
    tiles="OpenStreetMap"
)

for _, row in df.iterrows():

    popup_text = f"""
    <div style="width:220px">
        <h3>{row['순위']}위. {row['도시']}</h3>
        <b>국가:</b> {row['국가']}<br>
        <b>대표 디저트:</b> {row['디저트']}<br>
        <b>관광지:</b> {row['관광지']}<br>
        <p>{row['설명']}</p>
    </div>
    """

    folium.Marker(
        location=[row["위도"], row["경도"]],
        tooltip=f"{row['도시']} - {row['디저트']}",
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(
            color="red",
            icon="cutlery",
            prefix="fa"
        )
    ).add_to(world_map)

# 지도 화면 출력
st_folium(
    world_map,
    width=None,
    height=550,
    returned_objects=[]
)

st.divider()

# 국가 선택
st.subheader("🌍 국가별 디저트 검색")

country_list = ["전체"] + sorted(df["국가"].unique().tolist())

selected_country = st.selectbox(
    "확인하고 싶은 국가를 선택하세요.",
    country_list
)

if selected_country == "전체":
    result = df
else:
    result = df[df["국가"] == selected_country]

# 도시별 정보
st.subheader("🍮 세계 도시별 대표 디저트")

for _, row in result.iterrows():

    with st.container(border=True):

        col1, col2 = st.columns([1, 4])

        with col1:
            st.markdown(f"### 🏅 {row['순위']}위")
            st.write(row["도시"])
            st.caption(row["국가"])

        with col2:
            st.markdown(f"### 🍰 {row['디저트']}")
            st.write(f"📍 주요 관광지: {row['관광지']}")
            st.write(row["설명"])

st.divider()

# 국가별 도시 수 분석
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

# 마무리
st.divider()

st.subheader("📝 프로그램 분석 결과")

st.write("""
이 프로그램을 통해 세계 여러 나라의 대표 디저트와
관광지 정보를 확인할 수 있습니다.

국가마다 사용하는 식재료와 조리 방법이 다르며,
각 나라의 문화와 식생활이 디저트에도 반영된다는
점을 알 수 있습니다.
""")

st.caption(
    "※ 본 프로그램은 세계 디저트 문화를 소개하기 위한 "
    "교육용 자료이며, TOP 10은 공식적인 세계 인기 순위가 아닙니다."
)



import streamlit as st
import pandas as pd
import pydeck as pdk

# 페이지 설정
st.set_page_config(
    page_title="Seoul Travel Map",
    page_icon="🗺️",
    layout="wide"
)

# 서울 관광지 데이터
PLACES = [
    {
        "rank": 1,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·문화",
        "description": "조선 왕조의 대표 궁궐이에요. 근사한 전통 건축과 수문장 교대식을 볼 수 있어요.",
        "tip": "한복을 입고 방문하면 궁궐 무료입장 혜택을 확인해 보세요."
    },
    {
        "rank": 2,
        "name": "명동",
        "english": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "쇼핑·먹거리",
        "description": "화장품 매장과 패션 상점, 길거리 음식이 모여 있는 활기찬 쇼핑 거리예요.",
        "tip": "저녁에는 길거리 음식과 야경을 함께 즐기기 좋아요."
    },
    {
        "rank": 3,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·야경",
        "description": "남산 정상에서 서울 도심을 한눈에 내려다볼 수 있는 대표 전망 명소예요.",
        "tip": "해 질 무렵 올라가면 낮과 밤의 서울 풍경을 모두 볼 수 있어요."
    },
    {
        "rank": 4,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·문화",
        "description": "전통 한옥이 모여 있는 동네로, 서울의 옛 거리 풍경을 느낄 수 있어요.",
        "tip": "실제 주민들이 거주하는 곳이므로 조용히 관람해 주세요."
    },
    {
        "rank": 5,
        "name": "인사동",
        "english": "Insadong",
        "lat": 37.5742,
        "lon": 126.9855,
        "category": "전통·쇼핑",
        "description": "전통 공예품과 기념품 가게, 찻집이 모여 있어 한국 문화를 경험하기 좋아요.",
        "tip": "골목 안쪽의 작은 공방과 전통 찻집도 둘러보세요."
    },
    {
        "rank": 6,
        "name": "홍대 거리",
        "english": "Hongdae Street",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·엔터테인먼트",
        "description": "개성 있는 상점과 카페, 거리 공연으로 유명한 젊고 활기찬 거리예요.",
        "tip": "주말에는 거리 공연과 다양한 팝업 매장을 구경해 보세요."
    },
    {
        "rank": 7,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "시장·먹거리",
        "description": "빈대떡, 김밥 등 한국 시장 음식을 맛보고 활기찬 시장 분위기를 즐길 수 있어요.",
        "tip": "혼잡할 수 있으니 소지품을 잘 챙기고 이동하세요."
    },
    {
        "rank": 8,
        "name": "동대문디자인플라자(DDP)",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5671,
        "lon": 127.0095,
        "category": "건축·전시",
        "description": "독특한 곡선형 건축물로 유명하며 전시와 디자인 행사가 열리는 복합문화공간이에요.",
        "tip": "건물 외관과 주변 야경도 사진 찍기 좋아요."
    },
    {
        "rank": 9,
        "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5692,
        "lon": 126.9788,
        "category": "산책·휴식",
        "description": "도심 한가운데를 흐르는 산책로예요. 복잡한 거리에서 잠시 쉬어가기 좋아요.",
        "tip": "날씨가 좋은 날 가볍게 걸으며 주변 도심 풍경을 즐겨보세요."
    },
    {
        "rank": 10,
        "name": "롯데월드",
        "english": "Lotte World",
        "lat": 37.5111,
        "lon": 127.0982,
        "category": "테마파크",
        "description": "실내외 놀이시설과 퍼레이드를 즐길 수 있는 대형 테마파크예요.",
        "tip": "방문 전 운영시간과 놀이기구 대기 정보를 확인하세요."
    }
]

# 제목
st.title("🗺️ 외국인 관광객을 위한 서울 명소 TOP 10")
st.caption(
    "서울 여행에서 많이 찾는 대표 관광지를 지도에서 확인하고 "
    "아래에서 간단한 소개를 읽어보세요."
)

st.info(
    "아래 순위는 외국인 관광객에게 잘 알려진 서울의 대표 명소를 "
    "모은 추천 목록이며, 공식 방문객 통계 순위는 아닙니다."
)

# 데이터프레임 생성
df = pd.DataFrame(PLACES)

# 지도에 표시할 이름과 툴팁
df["label"] = df.apply(
    lambda r: f'{r["rank"]}. {r["name"]}',
    axis=1
)

df["tooltip"] = df.apply(
    lambda r: (
        f'<b>{r["rank"]}. {r["name"]}</b><br/>'
        f'{r["english"]}<br/>{r["category"]}'
    ),
    axis=1
)

# 마커 색상
df["color"] = [
    [220, 70, 70, 220] if rank == 1
    else [35, 120, 190, 210]
    for rank in df["rank"]
]

# 관광지 위치 마커 레이어
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position="[lon, lat]",
    get_fill_color="color",
    get_line_color=[255, 255, 255],
    get_radius=95,
    radius_min_pixels=6,
    radius_max_pixels=14,
    pickable=True,
    auto_highlight=True
)

# 지도 위 관광지 이름 표시
text_layer = pdk.Layer(
    "TextLayer",
    data=df,
    get_position="[lon, lat]",
    get_text="label",
    get_size=12,
    get_color=[25, 35, 45, 255],
    get_alignment_baseline="'bottom'",
    get_pixel_offset=[0, -12],
    pickable=False
)

# 서울 중심 지도 설정
view_state = pdk.ViewState(
    latitude=37.555,
    longitude=126.985,
    zoom=10.7,
    pitch=0,
    bearing=0
)

# 지도 생성
deck = pdk.Deck(
    layers=[layer, text_layer],
    initial_view_state=view_state,
    map_style=(
        "https://basemaps.cartocdn.com/"
        "gl/positron-gl-style/style.json"
    ),
    tooltip={
        "html": "{tooltip}",
        "style": {
            "backgroundColor": "#222",
            "color": "white"
        }
    }
)

# 지도 출력
st.subheader("📍 서울 관광지 지도")

st.pydeck_chart(
    deck,
    use_container_width=True,
    height=620
)

# 관광지 설명
st.subheader("✨ 관광지 소개")

# 두 개의 열로 카드 배치
for start in range(0, len(PLACES), 2):

    cols = st.columns(2)

    for col, place in zip(
        cols,
        PLACES[start:start + 2]
    ):

        with col:

            with st.container(border=True):

                st.markdown(
                    f"### {place['rank']}. {place['name']}"
                )

                st.caption(
                    f"{place['english']} · {place['category']}"
                )

                st.write(place["description"])

                st.markdown(
                    f"💡 **방문 팁:** {place['tip']}"
                )

# 하단 안내
st.divider()

st.caption(
    "※ 좌표는 지도 표시를 위한 대표 지점입니다. "
    "실제 출입구, 운영시간 및 휴무일은 방문 전에 공식 안내를 확인하세요."
)

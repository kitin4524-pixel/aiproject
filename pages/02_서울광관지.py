
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="Seoul Travel Map",
    page_icon="🗺️",
    layout="wide"
)

# 서울 관광지 데이터
PLACES = [
    {
        "rank": 1, "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796, "lon": 126.9770,
        "category": "역사·문화",
        "description": "조선 왕조의 대표 궁궐이에요. 전통 건축과 수문장 교대식을 볼 수 있어요.",
        "tip": "한복을 입고 방문하면 무료입장 혜택을 확인해 보세요."
    },
    {
        "rank": 2, "name": "명동",
        "english": "Myeongdong",
        "lat": 37.5636, "lon": 126.9869,
        "category": "쇼핑·먹거리",
        "description": "화장품 매장과 패션 상점, 길거리 음식이 모여 있는 쇼핑 거리예요.",
        "tip": "저녁에는 길거리 음식과 야경을 즐겨보세요."
    },
    {
        "rank": 3, "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512, "lon": 126.9882,
        "category": "전망·야경",
        "description": "남산 정상에서 서울 도심을 한눈에 내려다볼 수 있어요.",
        "tip": "해 질 무렵 방문하면 낮과 밤의 풍경을 모두 볼 수 있어요."
    },
    {
        "rank": 4, "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826, "lon": 126.9830,
        "category": "전통·문화",
        "description": "전통 한옥이 모여 있는 동네로 서울의 옛 모습을 느낄 수 있어요.",
        "tip": "주민들이 거주하는 곳이므로 조용히 관람해 주세요."
    },
    {
        "rank": 5, "name": "인사동",
        "english": "Insadong",
        "lat": 37.5742, "lon": 126.9855,
        "category": "전통·쇼핑",
        "description": "전통 공예품과 기념품 가게, 찻집이 모여 있는 문화 거리예요.",
        "tip": "골목 안쪽의 공방과 전통 찻집도 둘러보세요."
    },
    {
        "rank": 6, "name": "홍대 거리",
        "english": "Hongdae Street",
        "lat": 37.5563, "lon": 126.9236,
        "category": "문화·엔터테인먼트",
        "description": "개성 있는 상점과 카페, 거리 공연으로 유명한 거리예요.",
        "tip": "주말에는 거리 공연과 팝업 매장을 구경해 보세요."
    },
    {
        "rank": 7, "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700, "lon": 126.9997,
        "category": "시장·먹거리",
        "description": "빈대떡과 김밥 등 한국 시장 음식을 맛볼 수 있어요.",
        "tip": "혼잡할 수 있으니 소지품을 잘 챙기세요."
    },
    {
        "rank": 8, "name": "동대문디자인플라자(DDP)",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5671, "lon": 127.0095,
        "category": "건축·전시",
        "description": "독특한 곡선형 건축물과 다양한 디자인 전시로 유명해요.",
        "tip": "건물 외관과 주변 야경도 감상해 보세요."
    },
    {
        "rank": 9, "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5692, "lon": 126.9788,
        "category": "산책·휴식",
        "description": "도심 한가운데를 흐르는 물길로 산책하기 좋은 곳이에요.",
        "tip": "날씨가 좋은 날 여유롭게 걸어보세요."
    },
    {
        "rank": 10, "name": "롯데월드",
        "english": "Lotte World",
        "lat": 37.5111, "lon": 127.0982,
        "category": "테마파크",
        "description": "실내외 놀이시설과 퍼레이드를 즐길 수 있는 테마파크예요.",
        "tip": "방문 전 운영시간과 놀이기구 대기 정보를 확인하세요."
    }
]

# 1박 2일 여행 일정
ITINERARY = [
    # 1일 차
    ["1일 차", "09:00~10:30", "경복궁",
     "궁궐 관람 및 전통문화 체험", "개장 시간 확인"],

    ["1일 차", "10:45~11:45", "북촌한옥마을",
     "한옥 골목 산책 및 사진 촬영", "주민 거주 지역 정숙"],

    ["1일 차", "12:00~13:00", "인사동",
     "점심 식사 및 전통 기념품 구경", "전통 음식 추천"],

    ["1일 차", "13:00~14:00", "인사동 주변",
     "휴식 및 자유 관람", "이동 및 대기 여유 시간"],

    ["1일 차", "14:15~15:15", "청계천",
     "도심 산책 및 휴식", "날씨에 따라 조정"],

    ["1일 차", "15:30~16:45", "광장시장",
     "시장 구경 및 한국 길거리 음식 맛보기", "혼잡 시간대 주의"],

    ["1일 차", "17:00~18:00", "동대문디자인플라자(DDP)",
     "건축물 관람 및 전시 확인", "전시별 입장료 확인"],

    ["1일 차", "18:00~19:00", "동대문 주변",
     "저녁 식사", "식사 및 휴식"],

    ["1일 차", "19:00~22:00", "숙소 및 자유시간",
     "숙소 체크인 및 휴식", "다음 날 일정 준비"],

    # 2일 차
    ["2일 차", "09:00~10:00", "홍대 거리",
     "거리와 상점 둘러보기", "일부 매장 개점 시간 확인"],

    ["2일 차", "10:00~11:30", "홍대 주변",
     "카페 및 자유 관람", "이동 및 휴식"],

    ["2일 차", "11:30~12:30", "홍대 주변",
     "점심 식사", "자유롭게 식당 선택"],

    ["2일 차", "12:30~14:00", "이동 시간",
     "남산 방향으로 이동", "교통 상황에 따라 조정"],

    ["2일 차", "14:00~16:00", "N서울타워",
     "남산 산책 및 서울 전망 감상", "날씨와 운영 여부 확인"],

    ["2일 차", "16:00~17:00", "이동 및 휴식",
     "잠실 방향으로 이동", "교통 상황에 따라 조정"],

    ["2일 차", "17:00~20:30", "롯데월드",
     "놀이시설 및 퍼레이드 즐기기", "입장권과 운영시간 확인"],

    ["2일 차", "20:30~22:00", "롯데월드 주변",
     "저녁 식사 및 일정 마무리", "귀가 교통편 확인"]
]

# 제목
st.title("🗺️ 외국인 관광객을 위한 서울 명소 TOP 10")

st.caption(
    "서울 여행에서 많이 찾는 대표 관광지를 지도에서 확인하고 "
    "1박 2일 추천 일정도 살펴보세요."
)

st.info(
    "관광지 TOP 10은 대표 명소 추천 목록이며 "
    "공식 방문객 통계에 따른 순위는 아닙니다."
)

# 관광지 데이터프레임
df = pd.DataFrame(PLACES)

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

# 지도 마커
marker_layer = pdk.Layer(
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

# 지도 위 관광지 이름
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

# 서울 지도 위치
view_state = pdk.ViewState(
    latitude=37.555,
    longitude=126.985,
    zoom=10.7,
    pitch=0,
    bearing=0
)

# 지도 생성
deck = pdk.Deck(
    layers=[marker_layer, text_layer],
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

# 1박 2일 일정표
st.divider()

st.subheader("🧳 서울 1박 2일 추천 여행 일정")

st.write(
    "주요 관광지 10곳을 이틀에 나누어 둘러보는 일정이에요. "
    "매일 오전 9시에 시작하고 오후 10시에 마무리해요."
)

# 일정 데이터프레임
schedule_df = pd.DataFrame(
    ITINERARY,
    columns=["날짜", "시간", "장소", "일정", "참고 사항"]
)

# 1일 차
st.markdown("### ☀️ 1일 차 — 서울의 전통과 도심 즐기기")

day1 = schedule_df[
    schedule_df["날짜"] == "1일 차"
][["시간", "장소", "일정", "참고 사항"]]

st.table(day1)

# 2일 차
st.markdown("### 🌙 2일 차 — 서울의 트렌드와 전망 즐기기")

day2 = schedule_df[
    schedule_df["날짜"] == "2일 차"
][["시간", "장소", "일정", "참고 사항"]]

st.table(day2)

st.caption(
    "※ 일정은 추천 예시입니다. 실제 이동 시간은 교통 상황과 "
    "대기 시간에 따라 달라질 수 있습니다. "
    "숙소 위치와 관광지 운영시간을 확인한 뒤 조정해 주세요."
)

# 관광지 설명
st.divider()

st.subheader("✨ 관광지 소개")

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


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from pathlib import Path
from io import BytesIO

# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 서울시 연령별 인구 분석")
st.write(
    "행정구역, 성별, 연도를 선택하면 "
    "연령대별 인구수를 핫핑크 꺾은선 그래프로 확인할 수 있습니다."
)

# --------------------------------------------------
# 2. 한글 CSV 인코딩 자동 처리
# --------------------------------------------------
@st.cache_data
def read_population_csv(file_bytes):
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    last_error = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                BytesIO(file_bytes),
                encoding=encoding,
                dtype=str
            )
            return data, encoding

        except (UnicodeDecodeError, UnicodeError) as error:
            last_error = error

    raise ValueError(
        "CSV 파일의 인코딩을 읽을 수 없습니다. "
        f"UTF-8 또는 CP949 형식인지 확인해주세요. ({last_error})"
    )


# --------------------------------------------------
# 3. 데이터 불러오기
# CSV 파일은 app.py의 상위 폴더에 있음
# --------------------------------------------------
st.sidebar.header("⚙️ 분석 조건")

uploaded_file = st.sidebar.file_uploader(
    "인구 CSV 파일 업로드",
    type=["csv"]
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()

else:
    # pages 폴더의 상위 폴더에서 CSV 파일 찾기
    parent_folder = Path(__file__).resolve().parent.parent
    csv_path = parent_folder / "population.csv"

    if not csv_path.exists():
        st.error(
            "population.csv 파일을 찾을 수 없습니다. "
            "프로젝트 상위 폴더에 population.csv가 있는지 확인해주세요."
        )
        st.stop()

    file_bytes = csv_path.read_bytes()


try:
    df, used_encoding = read_population_csv(file_bytes)

except Exception as error:
    st.error(f"CSV 파일을 읽는 중 문제가 발생했습니다: {error}")
    st.stop()


# --------------------------------------------------
# 4. 데이터 정리
# --------------------------------------------------
df.columns = [str(column).strip() for column in df.columns]

if "행정구역" not in df.columns:
    st.error("'행정구역' 열을 찾을 수 없습니다.")
    st.stop()


# 행정구역 코드 제거
df["행정구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
    .str.strip()
)


# 연도 자동 추출
year_pattern = re.compile(r"(20\d{2})년")

years = sorted({
    match
    for column in df.columns
    for match in year_pattern.findall(column)
})

if not years:
    st.error("CSV 파일에서 연도 정보를 찾을 수 없습니다.")
    st.stop()


# 연령대 목록
age_groups = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]


# 숫자 데이터 변환
for column in df.columns:
    if column not in ["행정구역", "행정구역명"]:
        df[column] = pd.to_numeric(
            df[column]
            .astype(str)
            .str.replace(",", "", regex=False),
            errors="coerce"
        )


# --------------------------------------------------
# 5. 사용자 선택 메뉴
# --------------------------------------------------

# 행정구역 선택
areas = df["행정구역명"].dropna().unique().tolist()

areas = sorted(
    areas,
    key=lambda value: (value != "서울특별시", value)
)

selected_area = st.sidebar.selectbox(
    "📍 행정구역 선택",
    areas
)


# 성별 선택
gender_label = st.sidebar.selectbox(
    "👥 성별 선택",
    ["전체", "남성", "여성"]
)


# 연도 선택
selected_year = st.sidebar.selectbox(
    "📅 연도 선택",
    years,
    index=len(years) - 1
)


# --------------------------------------------------
# 6. 성별에 따른 데이터 열 선택
# --------------------------------------------------
gender_prefix = {
    "전체": f"{selected_year}년_거주자_",
    "남성": f"{selected_year}년_남_거주자_",
    "여성": f"{selected_year}년_여_거주자_"
}[gender_label]


# 선택한 지역 데이터 찾기
selected_rows = df[
    df["행정구역명"] == selected_area
]

if selected_rows.empty:
    st.error("선택한 행정구역의 데이터를 찾을 수 없습니다.")
    st.stop()

selected_row = selected_rows.iloc[0]


# --------------------------------------------------
# 7. 연령대별 인구수 추출
# --------------------------------------------------
values = []
missing_columns = []

for age in age_groups:

    column_name = gender_prefix + age

    if column_name in df.columns:

        value = selected_row[column_name]

        values.append(
            0 if pd.isna(value) else int(value)
        )

    else:
        values.append(0)
        missing_columns.append(column_name)


if missing_columns:
    st.warning(
        "일부 연령대 데이터가 없어 해당 값은 0으로 표시됩니다."
    )


chart_df = pd.DataFrame({
    "연령대": age_groups,
    "인구수": values
})


# --------------------------------------------------
# 8. 선택한 데이터 정보 표시
# --------------------------------------------------
st.subheader(
    f"📍 {selected_area} | {selected_year}년 | {gender_label}"
)

total_population = sum(values)

largest_age = chart_df.loc[
    chart_df["인구수"].idxmax(),
    "연령대"
]

metric1, metric2 = st.columns(2)

metric1.metric(
    "선택한 연령대 인구 합계",
    f"{total_population:,}명"
)

metric2.metric(
    "인구수가 가장 많은 연령대",
    largest_age
)


# --------------------------------------------------
# 9. 핫핑크 꺾은선 그래프
# --------------------------------------------------
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_df["연령대"],
        y=chart_df["인구수"],
        mode="lines+markers",

        line=dict(
            color="#FF1493",
            width=4
        ),

        marker=dict(
            color="#FF1493",
            size=9
        ),

        name="인구수",

        hovertemplate=(
            "%{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)


# 그래프 전체 디자인
fig.update_layout(
    title=f"{selected_area} {selected_year}년 {gender_label} 연령별 인구수",

    xaxis_title="나이 (10세 단위)",
    yaxis_title="인구수 (명)",

    template="plotly_white",
    height=520,

    hovermode="x unified",

    font=dict(
        family="Malgun Gothic, Apple SD Gothic Neo, sans-serif",
        size=13
    ),

    margin=dict(
        l=30,
        r=30,
        t=75,
        b=40
    )
)


# X축: 10세 단위 표시 및 세로 격자선
fig.update_xaxes(
    type="category",

    categoryorder="array",
    categoryarray=age_groups,

    showgrid=True,
    gridcolor="#E8D5E0",
    gridwidth=1,

    tickangle=0
)


# Y축: 인구수 표시 및 가로 격자선
fig.update_yaxes(
    rangemode="tozero",

    showgrid=True,
    gridcolor="#EEEEEE",

    tickformat=","
)


# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 10. 연령대별 인구수 표
# --------------------------------------------------
with st.expander("📋 연령대별 인구수 표 보기"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df[
        "인구수"
    ].map(lambda number: f"{number:,}명")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 11. CSV 인코딩 정보
# --------------------------------------------------
st.caption(
    f"CSV 인코딩: {used_encoding} · "
    "한글 깨짐 방지를 위해 UTF-8-SIG, UTF-8, "
    "CP949, EUC-KR 순서로 읽기를 시도합니다."
)

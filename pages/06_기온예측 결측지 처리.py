
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# ==================================
# 페이지 설정
# ==================================
st.set_page_config(
    page_title="월별 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("월별 평균기온 분석 및 예측")
st.write("과거 기온 데이터를 분석하고 세 가지 방법으로 미래 기온을 예측합니다.")

# ==================================
# CSV 파일 불러오기
# ==================================
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "tamperature.csv"

if not CSV_PATH.exists():
    st.error("tamperature.csv 파일을 찾을 수 없습니다.")
    st.info("프로젝트 최상위 폴더에 CSV 파일을 넣어주세요.")
    st.stop()

try:
    raw = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
except Exception:
    raw = pd.read_csv(CSV_PATH, encoding="cp949")

# ==================================
# 데이터 전처리
# ==================================
required_columns = ["일시", "평균기온(℃)"]

if not all(col in raw.columns for col in required_columns):
    st.error("CSV 파일에 '일시', '평균기온(℃)' 열이 필요합니다.")
    st.stop()

raw["날짜"] = pd.to_datetime(
    raw["일시"].astype(str),
    format="%b-%y",
    errors="coerce"
)

raw["평균기온(℃)"] = pd.to_numeric(
    raw["평균기온(℃)"],
    errors="coerce"
)

raw = raw.dropna(subset=["날짜", "평균기온(℃)"])

raw["연도"] = raw["날짜"].dt.year
raw["월"] = raw["날짜"].dt.month

if raw.empty:
    st.error("분석할 수 있는 데이터가 없습니다.")
    st.stop()

# ==================================
# 월 선택
# ==================================
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

selected_month = st.selectbox(
    "분석할 월을 선택하세요.",
    list(month_names.keys()),
    format_func=lambda x: month_names[x]
)

# ==================================
# 과거 데이터
# ==================================
month_data = raw[raw["월"] == selected_month].copy()

if month_data.empty:
    st.warning("선택한 월의 데이터가 없습니다.")
    st.stop()

year_data = (
    month_data.groupby("연도")["평균기온(℃)"]
    .mean()
    .reset_index()
)

year_data = year_data.sort_values("연도")

st.subheader(f"{month_names[selected_month]} 과거 평균기온")

fig_history = go.Figure()

fig_history.add_trace(go.Scatter(
    x=year_data["연도"],
    y=year_data["평균기온(℃)"],
    mode="lines+markers",
    name="실제 평균기온"
))

fig_history.update_layout(
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    hovermode="x unified"
)

st.plotly_chart(fig_history, use_container_width=True)

# ==================================
# 예측 연도 입력
# ==================================
st.subheader("미래 기온 예측")

latest_year = int(year_data["연도"].max())

target_year = st.number_input(
    "예측할 연도를 입력하세요.",
    min_value=latest_year + 1,
    max_value=2100,
    value=latest_year + 5,
    step=1
)

# ==================================
# 예측 함수
# ==================================
def linear_prediction(x, y, target):
    """단순 선형회귀"""
    slope, intercept = np.polyfit(x, y, 1)
    return slope * target + intercept


def polynomial_prediction(x, y, target):
    """2차 다항식 회귀"""
    if len(x) < 3:
        return linear_prediction(x, y, target)

    coefficients = np.polyfit(x, y, 2)
    return np.polyval(coefficients, target)


def moving_average_prediction(y, window=5):
    """최근 평균기온을 이용한 이동평균"""
    recent = y[-window:]
    return float(np.mean(recent))


# ==================================
# 데이터 준비
# ==================================
x = year_data["연도"].to_numpy(dtype=float)
y = year_data["평균기온(℃)"].to_numpy(dtype=float)

if len(x) < 2:
    st.warning("예측하려면 최소 2개 연도의 데이터가 필요합니다.")
    st.stop()

# ==================================
# 세 가지 예측
# ==================================
linear_result = linear_prediction(x, y, target_year)

polynomial_result = polynomial_prediction(x, y, target_year)

moving_result = moving_average_prediction(y)

# ==================================
# 예측 결과 표시
# ==================================
st.subheader(f"{target_year}년 {month_names[selected_month]} 예측 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선형회귀",
        f"{linear_result:.2f} ℃"
    )

with col2:
    st.metric(
        "다항회귀",
        f"{polynomial_result:.2f} ℃"
    )

with col3:
    st.metric(
        "이동평균",
        f"{moving_result:.2f} ℃"
    )

# ==================================
# 예측 그래프
# ==================================
fig_predict = go.Figure()

fig_predict.add_trace(go.Scatter(
    x=x,
    y=y,
    mode="lines+markers",
    name="실제 기온"
))

future_years = np.arange(
    int(x.min()),
    int(target_year) + 1
)

linear_values = [
    linear_prediction(x, y, year)
    for year in future_years
]

polynomial_values = [
    polynomial_prediction(x, y, year)
    for year in future_years
]

moving_values = [
    moving_average_prediction(y)
    for year in future_years
]

fig_predict.add_trace(go.Scatter(
    x=future_years,
    y=linear_values,
    mode="lines",
    name="선형회귀 예측"
))

fig_predict.add_trace(go.Scatter(
    x=future_years,
    y=polynomial_values,
    mode="lines",
    name="다항회귀 예측"
))

fig_predict.add_trace(go.Scatter(
    x=future_years,
    y=moving_values,
    mode="lines",
    name="이동평균 예측"
))

fig_predict.update_layout(
    title=f"{month_names[selected_month]} 평균기온 예측 비교",
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    hovermode="x unified"
)

st.plotly_chart(fig_predict, use_container_width=True)

# ==================================
# 알고리즘 설명
# ==================================
st.subheader("예측 알고리즘 설명")

with st.expander("1. 선형회귀"):
    st.write(
        "과거 기온의 전체적인 증가 또는 감소 추세를 "
        "직선으로 표현하여 미래 기온을 예측합니다."
    )

with st.expander("2. 다항회귀"):
    st.write(
        "과거 기온의 곡선 형태를 반영하는 방법입니다. "
        "기온 변화가 직선이 아닌 곡선 형태일 때 활용할 수 있습니다."
    )

with st.expander("3. 이동평균"):
    st.write(
        "가장 최근 5개 연도의 평균기온을 계산하여 "
        "미래에도 비슷한 수준이 유지된다고 가정합니다."
    )

st.caption(
    "주의: 이 결과는 과거 데이터에 기반한 단순 통계 예측이며 "
    "실제 미래 기온을 보장하지 않습니다."
)

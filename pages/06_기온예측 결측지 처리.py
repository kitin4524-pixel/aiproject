
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="월별 평균기온 분석 및 예측",
    layout="wide"
)

st.title("월별 평균기온 분석 및 예측")
st.write(
    "결측치 처리 방법과 예측 알고리즘에 따른 "
    "미래 평균기온의 차이를 분석합니다."
)

# ==========================================
# 2. CSV 파일 불러오기
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "tamperature.csv"

if not CSV_PATH.exists():
    st.error("tamperature.csv 파일을 찾을 수 없습니다.")
    st.stop()

try:
    raw = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
except Exception:
    raw = pd.read_csv(CSV_PATH, encoding="cp949")

required_columns = ["일시", "평균기온(℃)"]

if not all(col in raw.columns for col in required_columns):
    st.error("CSV 파일에 '일시', '평균기온(℃)' 열이 필요합니다.")
    st.stop()

# ==========================================
# 3. 데이터 전처리
# ==========================================
raw["날짜"] = pd.to_datetime(
    raw["일시"].astype(str),
    format="%b-%y",
    errors="coerce"
)

raw["평균기온(℃)"] = pd.to_numeric(
    raw["평균기온(℃)"],
    errors="coerce"
)

raw = raw.dropna(subset=["날짜"])

raw["연도"] = raw["날짜"].dt.year
raw["월"] = raw["날짜"].dt.month

if raw.empty:
    st.error("날짜 데이터가 없습니다.")
    st.stop()

# ==========================================
# 4. 월 선택
# ==========================================
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

st.sidebar.header("분석 설정")

selected_month = st.sidebar.selectbox(
    "분석할 월",
    list(month_names.keys()),
    format_func=lambda x: month_names[x]
)

# ==========================================
# 5. 연도별 평균기온 데이터 만들기
# ==========================================
month_data = raw[raw["월"] == selected_month]

year_data = (
    month_data.groupby("연도")["평균기온(℃)"]
    .mean()
)

# 전체 데이터의 시작 연도부터 마지막 연도까지
# 선택한 월의 데이터가 없는 연도도 결측치로 표시
start_year = int(raw["연도"].min())
end_year = int(raw["연도"].max())

all_years = pd.Index(
    range(start_year, end_year + 1),
    name="연도"
)

original_series = year_data.reindex(all_years)

if original_series.notna().sum() < 2:
    st.error("선택한 월에 유효한 데이터가 2개 이상 필요합니다.")
    st.stop()

# ==========================================
# 6. 결측치 처리 함수
# ==========================================
def handle_missing(series, method):

    result = series.copy()

    if method == "제거":
        result = result.dropna()

    elif method == "중앙값으로 대체":
        median_value = result.median()
        result = result.fillna(median_value)

    elif method == "선형보간법":
        result = result.interpolate(
            method="linear",
            limit_direction="both"
        )

    return result


# ==========================================
# 7. 예측 알고리즘 함수
# ==========================================
def predict_temperature(x, y, target_year, algorithm):

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    valid = np.isfinite(x) & np.isfinite(y)
    x = x[valid]
    y = y[valid]

    if len(x) < 2:
        return np.nan

    if algorithm == "선형회귀":

        slope, intercept = np.polyfit(x, y, 1)

        return slope * target_year + intercept

    elif algorithm == "다항회귀":

        if len(x) < 3:
            slope, intercept = np.polyfit(x, y, 1)
            return slope * target_year + intercept

        coefficients = np.polyfit(x, y, 2)

        return np.polyval(coefficients, target_year)

    elif algorithm == "이동평균":

        recent_data = y[-5:]

        return float(np.mean(recent_data))

    return np.nan


# ==========================================
# 8. 결측치 처리 방법 선택
# ==========================================
st.sidebar.subheader("결측치 처리 방법")

missing_method = st.sidebar.radio(
    "결측치 처리 방법을 선택하세요.",
    [
        "제거",
        "중앙값으로 대체",
        "선형보간법"
    ]
)

# ==========================================
# 9. 예측 알고리즘 선택
# ==========================================
st.sidebar.subheader("예측 알고리즘")

algorithm_options = [
    "선형회귀",
    "다항회귀",
    "이동평균"
]

selected_algorithms = st.sidebar.multiselect(
    "비교할 알고리즘을 선택하세요.",
    algorithm_options,
    default=algorithm_options
)

if not selected_algorithms:
    st.warning("예측 알고리즘을 하나 이상 선택해 주세요.")
    st.stop()

# ==========================================
# 10. 예측 연도 선택
# ==========================================
latest_year = int(original_series.last_valid_index())

target_year = st.sidebar.number_input(
    "예측할 연도",
    min_value=latest_year + 1,
    max_value=2100,
    value=min(latest_year + 5, 2100),
    step=1
)

# ==========================================
# 11. 결측치 처리 결과 계산
# ==========================================
missing_methods = [
    "제거",
    "중앙값으로 대체",
    "선형보간법"
]

processed_data = {}

for method in missing_methods:

    processed_data[method] = handle_missing(
        original_series,
        method
    )

selected_data = processed_data[missing_method]

# ==========================================
# 12. 결측치 현황
# ==========================================
st.header("1. 결측치 현황")

missing_count = int(original_series.isna().sum())
total_count = len(original_series)

col1, col2, col3 = st.columns(3)

col1.metric("전체 연도 수", f"{total_count}개")
col2.metric("결측치 수", f"{missing_count}개")
col3.metric(
    "결측치 비율",
    f"{missing_count / total_count * 100:.1f}%"
)

# ==========================================
# 13. 결측치 처리 전후 그래프
# ==========================================
st.subheader("결측치 처리 전후 비교")

fig_missing = go.Figure()

fig_missing.add_trace(go.Scatter(
    x=original_series.index,
    y=original_series.values,
    mode="lines+markers",
    name="처리 전 데이터",
    connectgaps=False
))

fig_missing.add_trace(go.Scatter(
    x=selected_data.index,
    y=selected_data.values,
    mode="lines+markers",
    name=f"처리 후: {missing_method}"
))

fig_missing.update_layout(
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    hovermode="x unified"
)

st.plotly_chart(fig_missing, use_container_width=True)

# ==========================================
# 14. 선택한 방법으로 예측
# ==========================================
st.header("2. 선택한 조건으로 미래 기온 예측")

st.write(f"선택한 월: **{month_names[selected_month]}**")
st.write(f"결측치 처리: **{missing_method}**")
st.write(f"예측 알고리즘: **{', '.join(selected_algorithms)}**")
st.write(f"예측 연도: **{target_year}년**")

selected_predictions = {}

for algorithm in selected_algorithms:

    prediction = predict_temperature(
        selected_data.index,
        selected_data.values,
        target_year,
        algorithm
    )

    selected_predictions[algorithm] = prediction

# 예측 결과 숫자로 표시
cols = st.columns(len(selected_predictions))

for col, (algorithm, prediction) in zip(
    cols,
    selected_predictions.items()
):

    with col:

        if np.isfinite(prediction):
            st.metric(
                algorithm,
                f"{prediction:.2f} ℃"
            )
        else:
            st.metric(algorithm, "계산 불가")

# ==========================================
# 15. 선택한 조건의 예측 그래프
# ==========================================
fig_prediction = go.Figure()

fig_prediction.add_trace(go.Scatter(
    x=original_series.index,
    y=original_series.values,
    mode="lines+markers",
    name="실제 기온",
    connectgaps=False
))

fig_prediction.add_trace(go.Scatter(
    x=selected_data.index,
    y=selected_data.values,
    mode="markers",
    name=f"결측치 처리 데이터 ({missing_method})"
))

future_years = np.arange(
    start_year,
    int(target_year) + 1
)

for algorithm in selected_algorithms:

    predictions = [
        predict_temperature(
            selected_data.index,
            selected_data.values,
            year,
            algorithm
        )
        for year in future_years
    ]

    fig_prediction.add_trace(go.Scatter(
        x=future_years,
        y=predictions,
        mode="lines",
        name=f"{algorithm} 예측"
    ))

fig_prediction.update_layout(
    title="선택한 조건에 따른 평균기온 예측",
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    hovermode="x unified"
)

st.plotly_chart(fig_prediction, use_container_width=True)

# ==========================================
# 16. 결측치 처리 방법에 따른 예측값 비교
# ==========================================
st.header("3. 결측치 처리 방법에 따른 예측값 비교")

st.write(
    "동일한 예측 알고리즘을 사용하더라도 "
    "결측치를 처리하는 방법에 따라 결과가 달라질 수 있습니다."
)

comparison_rows = []

for algorithm in selected_algorithms:

    for method in missing_methods:

        data = processed_data[method]

        prediction = predict_temperature(
            data.index,
            data.values,
            target_year,
            algorithm
        )

        comparison_rows.append({
            "결측치 처리 방법": method,
            "예측 알고리즘": algorithm,
            "예측 기온(℃)": prediction
        })

comparison_df = pd.DataFrame(comparison_rows)

# 그래프
fig_comparison = go.Figure()

for algorithm in selected_algorithms:

    algorithm_data = comparison_df[
        comparison_df["예측 알고리즘"] == algorithm
    ]

    fig_comparison.add_trace(go.Bar(
        x=algorithm_data["결측치 처리 방법"],
        y=algorithm_data["예측 기온(℃)"],
        name=algorithm
    ))

fig_comparison.update_layout(
    title=f"{target_year}년 결측치 처리 방법별 예측값 비교",
    xaxis_title="결측치 처리 방법",
    yaxis_title="예측 평균기온(℃)",
    barmode="group"
)

st.plotly_chart(fig_comparison, use_container_width=True)

# ==========================================
# 17. 예측 결과 표
# ==========================================
st.subheader("예측 결과 상세 표")

st.dataframe(
    comparison_df.round(2),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 18. 알고리즘 설명
# ==========================================
st.header("4. 예측 알고리즘 설명")

with st.expander("선형회귀"):

    st.write(
        "과거 기온 데이터의 전체적인 증가 또는 감소 추세를 "
        "직선으로 나타내 미래 기온을 예측합니다."
    )

with st.expander("다항회귀"):

    st.write(
        "과거 기온의 곡선 형태를 반영하는 방법입니다. "
        "2차 다항식을 이용하여 직선으로 표현하기 어려운 "
        "변화 추세를 분석합니다."
    )

with st.expander("이동평균"):

    st.write(
        "최근 5개 연도의 평균기온을 계산한 뒤 "
        "그 평균값을 미래의 예측값으로 사용합니다."
    )

# ==========================================
# 19. 결측치 처리 방법 설명
# ==========================================
st.header("5. 결측치 처리 방법 설명")

with st.expander("1. 제거"):

    st.write(
        "결측치가 있는 연도의 데이터를 분석에서 제외합니다. "
        "실제 관측된 값만 사용하지만 데이터가 줄어들 수 있습니다."
    )

with st.expander("2. 중앙값으로 대체"):

    st.write(
        "선택한 월의 전체 유효한 기온 데이터에서 중앙값을 계산하고 "
        "결측치를 해당 값으로 채웁니다."
    )

with st.expander("3. 선형보간법"):

    st.write(
        "앞뒤 연도의 기온을 이용해 결측치가 있는 연도의 값을 "
        "직선 형태로 추정하여 채웁니다. "
        "시작이나 끝의 결측치는 가장 가까운 유효값으로 채웁니다."
    )

# ==========================================
# 20. 주의사항
# ==========================================
st.caption(
    "※ 예측값은 과거 관측자료를 이용한 단순 통계 예측 결과입니다. "
    "실제 미래 기온이나 기후 변화를 보장하지 않습니다."
)

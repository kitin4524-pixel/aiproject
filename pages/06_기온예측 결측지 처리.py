streamlit>=1.35
pandas>=2.0
numpy>=1.24
plotly>=5.20
scikit-learn>=1.3
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

st.set_page_config(
    page_title="월별 평균기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("월별 평균기온 분석 및 미래 예측")
st.caption("과거 기온 분석 및 3가지 알고리즘 예측 비교")

MONTHS = {
    i: f"{i}월" for i in range(1, 13)
}


@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        raw = pd.read_csv(uploaded_file, encoding="cp949")
    else:
        raw = pd.read_csv("tamperature.csv", encoding="cp949")

    required = ["일시", "평균기온(℃)"]

    missing = [
        c for c in required
        if c not in raw.columns
    ]

    if missing:
        raise ValueError(
            f"필요한 열이 없습니다: {missing}"
        )

    raw["날짜"] = pd.to_datetime(
        raw["일시"],
        format="%b-%y",
        errors="coerce"
    )

    raw["평균기온(℃)"] = pd.to_numeric(
        raw["평균기온(℃)"],
        errors="coerce"
    )

    raw = raw.dropna(
        subset=["날짜", "평균기온(℃)"]
    ).copy()

    raw["연도"] = raw["날짜"].dt.year
    raw["월"] = raw["날짜"].dt.month

    raw = raw.sort_values("날짜")

    raw = raw.drop_duplicates(
        subset=["연도", "월"],
        keep="last"
    )

    return raw


uploaded = st.sidebar.file_uploader(
    "CSV 파일 업로드",
    type=["csv"]
)

try:
    data = load_data(uploaded)
except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()

if data.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()


min_year = int(data["연도"].min())
max_year = int(data["연도"].max())

st.sidebar.header("분석 조건")

selected_month = st.sidebar.selectbox(
    "분석할 월 선택",
    list(MONTHS.keys()),
    format_func=lambda x: MONTHS[x]
)

target_year = st.sidebar.number_input(
    "예측할 연도",
    min_value=max_year + 1,
    max_value=2200,
    value=min(max_year + 5, 2200),
    step=1
)

st.info(
    f"실제 관측 기간: {min_year}년 ~ {max_year}년"
)

# 과거 데이터
history = data[
    (data["월"] == selected_month) &
    (data["연도"] >= 1970) &
    (data["연도"] <= 2025)
].copy()

# 선택한 월의 전체 데이터
model_data = data[
    data["월"] == selected_month
].copy()

if len(model_data) < 5:
    st.error("예측에 필요한 데이터가 부족합니다.")
    st.stop()


X = model_data[["연도"]].values.astype(float)

y = model_data[
    "평균기온(℃)"
].values.astype(float)


# 예측 알고리즘 3가지
models = {

    "선형 회귀": LinearRegression(),

    "랜덤 포레스트": RandomForestRegressor(
        n_estimators=300,
        max_depth=4,
        min_samples_leaf=2,
        random_state=42
    ),

    "다항 회귀": make_pipeline(
        PolynomialFeatures(
            degree=2,
            include_bias=False
        ),
        LinearRegression()
    )
}


# 모델 학습
for model in models.values():
    model.fit(X, y)


# 미래 연도 생성
last_year = int(model_data["연도"].max())

future_years = np.arange(
    last_year + 1,
    int(target_year) + 1
)

if len(future_years) == 0:
    future_years = np.array([int(target_year)])

future_X = future_years.reshape(
    -1, 1
).astype(float)


# 월별 분석
st.subheader(
    f"{selected_month}월 평균기온 분석"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "선택 월",
    f"{selected_month}월"
)

col2.metric(
    "관측 데이터 수",
    f"{len(model_data)}개"
)

col3.metric(
    "마지막 관측 연도",
    f"{last_year}년"
)


# 과거 기온 그래프
if history.empty:

    st.warning(
        "1970~2025년 사이에 해당 월의 관측값이 없습니다."
    )

else:

    fig_history = go.Figure()

    fig_history.add_trace(
        go.Scatter(
            x=history["연도"],
            y=history["평균기온(℃)"],
            mode="lines+markers",
            name="실제 평균기온"
        )
    )

    fig_history.update_layout(
        title=f"{selected_month}월 실제 평균기온 (1970~2025)",
        xaxis_title="연도",
        yaxis_title="평균기온 (℃)",
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_history,
        use_container_width=True
    )


# 미래 예측 그래프
st.subheader(
    f"{target_year}년 {selected_month}월 기온 예측"
)

fig = go.Figure()

# 실제 관측값
fig.add_trace(
    go.Scatter(
        x=model_data["연도"],
        y=model_data["평균기온(℃)"],
        mode="lines+markers",
        name="실제 관측값",
        line=dict(color="black", width=2)
    )
)


colors = {
    "선형 회귀": "blue",
    "랜덤 포레스트": "green",
    "다항 회귀": "red"
}

predictions = {}

for name, model in models.items():

    pred = model.predict(future_X)

    predictions[name] = float(pred[-1])

    fig.add_trace(
        go.Scatter(
            x=future_years,
            y=pred,
            mode="lines+markers",
            name=name,
            line=dict(
                color=colors[name],
                width=3,
                dash="dash"
            )
        )
    )


fig.add_vline(
    x=last_year,
    line_dash="dot",
    annotation_text="예측 시작"
)

fig.update_layout(
    title="3가지 알고리즘 미래 기온 예측 비교",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# 예측 결과 표
st.subheader("예측 결과")

result = pd.DataFrame({
    "알고리즘": list(predictions.keys()),
    "예측 평균기온 (℃)": [
        round(v, 2)
        for v in predictions.values()
    ]
})

st.dataframe(
    result,
    use_container_width=True,
    hide_index=True
)


# 알고리즘 설명
st.subheader("알고리즘 작동 원리")


with st.expander("1. 선형 회귀"):

    st.markdown("""
    - 과거 연도와 평균기온의 관계를 직선으로 표현합니다.
    - 매년 일정한 폭으로 기온이 변한다고 가정합니다.
    - 장기적인 상승 및 하락 추세를 파악하기 좋습니다.
    """)


with st.expander("2. 랜덤 포레스트"):

    st.markdown("""
    - 여러 개의 결정 트리를 만들어 학습합니다.
    - 각 트리의 예측 결과를 평균하여 최종 예측값을 만듭니다.
    - 복잡한 과거 데이터 패턴을 학습할 수 있습니다.
    - 학습 범위를 벗어난 미래 추세를 잘 외삽하지 못합니다.
    """)


with st.expander("3. 다항 회귀"):

    st.markdown("""
    - 연도뿐 아니라 연도의 제곱 항을 활용합니다.
    - 직선이 아닌 곡선 형태의 변화를 학습합니다.
    - 장기 예측에서는 곡선이 과도하게 휘어질 수 있습니다.
    """)


# 모델 성능
st.subheader("모델 성능 비교")

st.caption(
    "아래 오차는 학습 데이터에 다시 적용한 값입니다."
)

metrics = []

for name, model in models.items():

    fitted = model.predict(X)

    mae = mean_absolute_error(
        y,
        fitted
    )

    rmse = np.sqrt(
        mean_squared_error(y, fitted)
    )

    metrics.append({
        "알고리즘": name,
        "MAE (℃)": round(mae, 3),
        "RMSE (℃)": round(rmse, 3)
    })


st.dataframe(
    pd.DataFrame(metrics),
    use_container_width=True,
    hide_index=True
)


st.divider()

st.caption(
    "본 프로그램의 예측은 교육 및 데이터 분석용 추정치이며 "
    "공식 기상 예보가 아닙니다."
)

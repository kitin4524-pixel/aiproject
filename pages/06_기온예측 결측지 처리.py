
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="월별 평균기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 미래 예측")

st.markdown("""
과거 기온 데이터를 분석하고
세 가지 머신러닝 알고리즘을 이용하여
미래 평균기온을 예측하는 프로그램입니다.
""")

st.divider()


# ==========================================
# 2. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(file_path=None, uploaded_file=None):

    if uploaded_file is not None:

        try:
            raw = pd.read_csv(
                uploaded_file,
                encoding="utf-8-sig"
            )

        except UnicodeDecodeError:

            uploaded_file.seek(0)

            raw = pd.read_csv(
                uploaded_file,
                encoding="cp949"
            )

    else:

        if file_path is None or not file_path.exists():
            raise FileNotFoundError(
                "tamperature.csv 파일을 찾을 수 없습니다."
            )

        try:
            raw = pd.read_csv(
                file_path,
                encoding="utf-8-sig"
            )

        except UnicodeDecodeError:

            raw = pd.read_csv(
                file_path,
                encoding="cp949"
            )

    required_columns = [
        "일시",
        "평균기온(℃)"
    ]

    for column in required_columns:

        if column not in raw.columns:
            raise ValueError(
                f"CSV에 '{column}' 열이 없습니다."
            )

    # 날짜 변환
    raw["날짜"] = pd.to_datetime(
        raw["일시"],
        format="%b-%y",
        errors="coerce"
    )

    # 평균기온 숫자 변환
    raw["평균기온(℃)"] = pd.to_numeric(
        raw["평균기온(℃)"],
        errors="coerce"
    )

    raw = raw.dropna(
        subset=["날짜", "평균기온(℃)"]
    ).copy()

    # 연도와 월 추출
    raw["연도"] = raw["날짜"].dt.year
    raw["월"] = raw["날짜"].dt.month

    raw = raw.sort_values("날짜")

    raw = raw.drop_duplicates(
        subset=["연도", "월"],
        keep="last"
    )

    return raw


# pages 폴더에서 실행하므로 프로젝트 최상위 폴더를 찾습니다.
BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "tamperature.csv"


# ==========================================
# 3. 데이터 업로드
# ==========================================

st.sidebar.header("데이터 설정")

uploaded_file = st.sidebar.file_uploader(
    "기온 데이터 CSV 업로드",
    type=["csv"]
)

try:

    data = load_data(
        file_path=CSV_PATH,
        uploaded_file=uploaded_file
    )

except Exception as e:

    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


if data.empty:

    st.error("분석할 데이터가 없습니다.")
    st.stop()


min_year = int(data["연도"].min())
max_year = int(data["연도"].max())


st.sidebar.success(
    f"데이터 로드 완료: {len(data)}개"
)


# ==========================================
# 4. 분석 조건 설정
# ==========================================

st.sidebar.header("분석 조건")

selected_month = st.sidebar.selectbox(
    "분석할 월 선택",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월"
)


target_year = st.sidebar.number_input(
    "예측할 미래 연도",
    min_value=max_year + 1,
    max_value=2200,
    value=min(max_year + 5, 2200),
    step=1
)


st.info(
    f"현재 데이터 관측 기간: "
    f"{min_year}년 ~ {max_year}년"
)


# ==========================================
# 5. 월별 데이터 분리
# ==========================================

history = data[
    (data["월"] == selected_month) &
    (data["연도"] >= 1970) &
    (data["연도"] <= 2025)
].copy()


model_data = data[
    data["월"] == selected_month
].copy()


if len(model_data) < 5:

    st.error(
        "선택한 월의 데이터가 부족합니다."
    )

    st.stop()


X = model_data[["연도"]].values.astype(float)

y = model_data[
    "평균기온(℃)"
].values.astype(float)


# ==========================================
# 6. 알고리즘 3가지 생성
# ==========================================

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


# ==========================================
# 7. 모델 학습
# ==========================================

for model in models.values():

    model.fit(X, y)


last_year = int(model_data["연도"].max())


future_years = np.arange(
    last_year + 1,
    int(target_year) + 1
)


future_X = future_years.reshape(
    -1, 1
).astype(float)


# ==========================================
# 8. 데이터 요약
# ==========================================

st.subheader("데이터 분석 현황")

col1, col2, col3 = st.columns(3)

col1.metric(
    "선택한 월",
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


# ==========================================
# 9. 과거 평균기온 그래프
# ==========================================

st.subheader(
    f"{selected_month}월 과거 평균기온 변화"
)

st.caption(
    "1970년부터 2025년까지의 실제 관측값을 표시합니다. "
    "자료가 없는 연도는 임의로 생성하지 않습니다."
)


if history.empty:

    st.warning(
        "1970~2025년 구간에 해당 월의 관측값이 없습니다."
    )

else:

    fig_history = go.Figure()

    fig_history.add_trace(
        go.Scatter(
            x=history["연도"],
            y=history["평균기온(℃)"],
            mode="lines+markers",
            name="실제 평균기온",
            line=dict(width=2),
            marker=dict(size=6)
        )
    )

    fig_history.update_layout(
        title=f"{selected_month}월 평균기온 (1970~2025)",
        xaxis_title="연도",
        yaxis_title="평균기온 (℃)",
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_history,
        use_container_width=True
    )


# ==========================================
# 10. 미래 평균기온 예측
# ==========================================

st.divider()

st.subheader(
    f"{target_year}년 {selected_month}월 평균기온 예측"
)

st.markdown("""
세 가지 알고리즘이 과거 데이터를 학습한 후
각각 다른 방식으로 미래 기온을 예측합니다.
""")


fig = go.Figure()


# 실제 관측 데이터
fig.add_trace(
    go.Scatter(
        x=model_data["연도"],
        y=model_data["평균기온(℃)"],
        mode="lines+markers",
        name="실제 관측값",
        line=dict(
            color="black",
            width=2
        ),
        marker=dict(size=5)
    )
)


colors = {

    "선형 회귀": "blue",

    "랜덤 포레스트": "green",

    "다항 회귀": "red"

}


predictions = {}


# ==========================================
# 11. 세 가지 알고리즘 예측 비교
# ==========================================

for name, model in models.items():

    prediction = model.predict(future_X)

    predictions[name] = float(
        prediction[-1]
    )

    fig.add_trace(
        go.Scatter(
            x=future_years,
            y=prediction,
            mode="lines+markers",
            name=name,
            line=dict(
                color=colors[name],
                width=3,
                dash="dash"
            ),
            marker=dict(size=6)
        )
    )


# 예측 시작 지점 표시
fig.add_vline(
    x=last_year,
    line_dash="dot",
    line_width=2,
    annotation_text="예측 시작"
)


fig.update_layout(
    title="실제 평균기온과 알고리즘별 미래 예측 비교",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    hovermode="x unified",
    legend=dict(
        orientation="h",
        y=1.15
    )
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 12. 예측 결과 비교표
# ==========================================

st.subheader("알고리즘별 예측 결과")


result_df = pd.DataFrame({

    "알고리즘": list(predictions.keys()),

    "예측 연도": [
        int(target_year)
    ] * 3,

    "예측 평균기온 (℃)": [
        round(value, 2)
        for value in predictions.values()
    ]

})


st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 13. 알고리즘 작동 원리 설명
# ==========================================

st.divider()

st.subheader("알고리즘별 작동 원리")


with st.expander(
    "1. 선형 회귀 (Linear Regression)",
    expanded=True
):

    st.markdown("""
    ### 작동 원리

    선형 회귀는 과거 연도와 평균기온 사이의
    관계를 직선으로 나타내는 방법입니다.

    수식:

    y = ax + b

    - x: 연도
    - y: 평균기온
    - a: 기온 변화의 기울기
    - b: 절편

    ### 그래프에서 확인할 특징

    - 직선 형태의 예측선이 나타납니다.
    - 매년 일정한 폭으로 기온이 변한다고 가정합니다.
    - 장기적인 상승 및 하락 추세를 확인하기 좋습니다.

    ### 장점과 한계

    장기적인 경향을 이해하기 쉽지만
    복잡한 곡선 형태의 변화를 표현하기 어렵습니다.
    """)


with st.expander(
    "2. 랜덤 포레스트 (Random Forest)"
):

    st.markdown("""
    ### 작동 원리

    랜덤 포레스트는 여러 개의 결정 트리를 만들어
    각각 학습한 후 예측값을 평균하여 결과를 만듭니다.

    ### 그래프에서 확인할 특징

    - 직선이 아닌 구간별 변화가 나타날 수 있습니다.
    - 여러 결정 트리의 결과를 결합합니다.
    - 과거 데이터의 비선형 패턴을 학습할 수 있습니다.

    ### 장점과 한계

    복잡한 데이터 패턴을 학습할 수 있지만
    학습 범위를 벗어난 미래 연도의 상승 또는 하락 추세를
    자연스럽게 연장하지 못하는 한계가 있습니다.
    """)


with st.expander(
    "3. 다항 회귀 (Polynomial Regression)"
):

    st.markdown("""
    ### 작동 원리

    다항 회귀는 연도뿐 아니라 연도의 제곱 항을
    활용하여 곡선 형태의 관계를 학습합니다.

    수식:

    y = ax² + bx + c

    ### 그래프에서 확인할 특징

    - 직선이 아닌 곡선 형태의 예측선이 나타납니다.
    - 기온 변화가 가속되거나 완만해지는 패턴을 표현할 수 있습니다.

    ### 장점과 한계

    곡선 형태의 변화를 표현할 수 있지만
    먼 미래를 예측할 때 곡선이 과도하게 휘어질 수 있습니다.
    """)


# ==========================================
# 14. 알고리즘 성능 비교
# ==========================================

st.divider()

st.subheader("알고리즘 성능 비교")

st.caption("""
MAE와 RMSE는 예측 오차를 측정하는 지표입니다.
아래 값은 학습 데이터에 다시 적용한 결과이므로
실제 미래 예측 성능과는 차이가 있을 수 있습니다.
""")


metric_results = []


for name, model in models.items():

    fitted = model.predict(X)

    mae = mean_absolute_error(
        y,
        fitted
    )

    rmse = np.sqrt(
        mean_squared_error(
            y,
            fitted
        )
    )

    metric_results.append({

        "알고리즘": name,

        "MAE (℃)": round(mae, 3),

        "RMSE (℃)": round(rmse, 3)

    })


metric_df = pd.DataFrame(
    metric_results
)


st.dataframe(
    metric_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 15. 마무리 안내
# ==========================================

st.divider()

st.info("""
### 분석 시 주의사항

본 프로그램은 선택한 월의 과거 평균기온과
연도 사이의 관계를 이용한 통계적 예측 프로그램입니다.

기후변화, 온실가스, 해류, 태양 활동 등
실제 기후에 영향을 주는 모든 요인을 반영하지는 않습니다.

따라서 예측 결과는 교육 및 데이터 분석을 위한
참고 자료로 활용해야 하며 공식 기상 예보로 사용할 수 없습니다.
""")

st.caption(
    "Monthly Temperature Analysis & Prediction"
)




import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 페이지 설정
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측 프로그램")
st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "인공지능이 붓꽃의 품종을 예측해 줍니다."
)

st.divider()

# 1. CSV 파일 불러오기
@st.cache_data
def load_data():
    file_path = Path(__file__).resolve().parent.parent / "Iris.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {file_path}"
        )

    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            return data
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

try:
    df = load_data()
except Exception as e:
    st.error(str(e))
    st.stop()

# 필요한 열 확인
required_columns = ["꽃잎길이", "꽃잎너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

# 2. 데이터 전처리
df = df.dropna(subset=required_columns)

X = df[["꽃잎길이", "꽃잎너비"]]
y = df["품종"]

# 3. 학습 데이터와 테스트 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 4. 랜덤 포레스트 모델 생성
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

# 정확도 평가용 학습
model.fit(X_train, y_train)

y_test_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_test_pred)

# 실제 예측용 모델은 전체 데이터로 학습
model.fit(X, y)

# 품종별 색상
species_colors = {
    "Iris-setosa": "#3498DB",
    "Iris-versicolor": "#F39C12",
    "Iris-virginica": "#9B59B6"
}

# 5. 사용자 입력
st.subheader("📝 꽃잎 크기 입력하기")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎길이 (cm)",
        min_value=0.0,
        max_value=8.0,
        value=1.5,
        step=0.1
    )

with col2:
    petal_width = st.number_input(
        "꽃잎너비 (cm)",
        min_value=0.0,
        max_value=4.0,
        value=0.3,
        step=0.1
    )

# 6. 품종 예측
if st.button("🌸 품종 예측하기", use_container_width=True):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎길이", "꽃잎너비"]
    )

    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]

    st.divider()
    st.subheader("🔍 AI 예측 결과")

    st.success(f"예측된 붓꽃 품종: {prediction}")

    st.metric(
        "모델의 예측 확률",
        f"{max(probabilities) * 100:.1f}%"
    )

    # 품종별 예측 확률
    st.write("### 품종별 예측 확률")

    probability_df = pd.DataFrame({
        "품종": model.classes_,
        "예측 확률(%)": probabilities * 100
    })

    st.bar_chart(
        probability_df.set_index("품종"),
        color="#2ECC71"
    )

    # 7. 그래프 영역 설정
    st.divider()
    st.subheader("📊 꽃잎 크기별 품종 분류 시각화")

    x_min = max(0, X["꽃잎길이"].min() - 0.5)
    x_max = X["꽃잎길이"].max() + 0.5
    y_min = max(0, X["꽃잎너비"].min() - 0.5)
    y_max = X["꽃잎너비"].max() + 0.5

    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 200),
        np.linspace(y_min, y_max, 200)
    )

    grid_data = pd.DataFrame({
        "꽃잎길이": xx.ravel(),
        "꽃잎너비": yy.ravel()
    })

    # 각 위치의 품종 예측
    grid_prediction = model.predict(grid_data)

    # 품종을 숫자로 변환
    class_to_num = {
        name: i for i, name in enumerate(model.classes_)
    }

    zz = np.array([
        class_to_num[name] for name in grid_prediction
    ]).reshape(xx.shape)

    # 품종별 분류 영역 색상
    colors = [
        "#3498DB",
        "#F39C12",
        "#9B59B6"
    ]

    colorscale = [
        [0.0, colors[0]],
        [1/3, colors[0]],
        [1/3 + 0.0001, colors[1]],
        [2/3, colors[1]],
        [2/3 + 0.0001, colors[2]],
        [1.0, colors[2]]
    ]

    fig = go.Figure()

    # 품종별 예측 영역
    fig.add_trace(go.Heatmap(
        x=np.linspace(x_min, x_max, 200),
        y=np.linspace(y_min, y_max, 200),
        z=zz,
        colorscale=colorscale,
        zmin=-0.5,
        zmax=2.5,
        opacity=0.25,
        showscale=False,
        hoverinfo="skip",
        name="품종 분류 영역"
    ))

    # 기존 데이터 표시
    for species in model.classes_:

        subset = df[df["품종"] == species]

        fig.add_trace(go.Scatter(
            x=subset["꽃잎길이"],
            y=subset["꽃잎너비"],
            mode="markers",
            name=species,
            marker=dict(
                color=species_colors.get(species, "#888888"),
                size=8,
                opacity=0.8
            )
        ))

    # 사용자 입력값: 초록색 별
    fig.add_trace(go.Scatter(
        x=[petal_length],
        y=[petal_width],
        mode="markers",
        name="내가 입력한 값 ★",
        marker=dict(
            color="green",
            size=22,
            symbol="star",
            line=dict(color="black", width=1)
        )
    ))

    fig.update_layout(
        title="랜덤 포레스트 품종 분류 결과",
        xaxis_title="꽃잎길이 (cm)",
        yaxis_title="꽃잎너비 (cm)",
        template="plotly_white",
        height=600,
        legend_title="데이터 구분",
        hovermode="closest"
    )

    st.plotly_chart(fig, use_container_width=True)

    # 8. 결과 해석
    st.subheader("💡 왜 이 품종으로 분류되었을까?")

    st.write(
        f"입력한 꽃잎길이는 {petal_length:.1f}cm, "
        f"꽃잎너비는 {petal_width:.1f}cm입니다."
    )

    st.write(
        f"그래프에서 초록색 별은 입력한 데이터의 위치를 "
        f"나타냅니다. 이 별이 위치한 분류 영역은 "
        f"{prediction}으로 예측되는 영역입니다."
    )

    st.write(
        "랜덤 포레스트는 여러 의사결정나무의 결과를 "
        "종합하여 품종을 예측합니다. "
        "아래 확률은 모델이 각 품종에 부여한 예측 확률입니다."
    )

    # 9. 모델 평가
    st.divider()
    st.subheader("🤖 AI 모델 성능")

    st.metric(
        "테스트 데이터 예측 정확도",
        f"{accuracy * 100:.1f}%"
    )

    st.caption(
        "전체 데이터 중 80%로 학습하고, "
        "나머지 20%로 예측 정확도를 평가했습니다."
    )

    # 두 가지 입력 특성의 중요도
    importance_df = pd.DataFrame({
        "특성": X.columns,
        "중요도": model.feature_importances_
    }).sort_values("중요도", ascending=False)

    st.write("### 품종 분류에 사용된 특성의 중요도")

    st.bar_chart(
        importance_df.set_index("특성"),
        color="#8E44AD"
    )

else:
    st.info(
        "꽃잎길이와 꽃잎너비를 입력한 다음 "
        "'품종 예측하기' 버튼을 눌러주세요."
    )

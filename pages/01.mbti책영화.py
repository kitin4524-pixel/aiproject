
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 AI가 품종을 예측합니다.")

# 1. 데이터 불러오기
@st.cache_data
def load_data():
    file_path = Path(__file__).resolve().parent.parent / "Iris.csv"

    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일 인코딩을 확인해 주세요.")

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 불러오기 실패: {e}")
    st.stop()

# 필요한 데이터 확인
columns = ["꽃잎길이", "꽃잎너비", "품종"]

if not all(col in df.columns for col in columns):
    st.error("CSV 파일의 열 이름이 올바르지 않습니다.")
    st.stop()

df = df.dropna(subset=columns)

# 2. 학습 데이터 준비
X = df[["꽃잎길이", "꽃잎너비"]].to_numpy(dtype=float)
y = df["품종"].to_numpy()

classes = np.unique(y)

# 3. KNN 알고리즘 직접 구현
# 가장 가까운 데이터 5개를 찾아 다수결로 분류

def knn_predict(input_data, k=5):

    distances = np.sqrt(
        np.sum((X - input_data) ** 2, axis=1)
    )

    nearest_indices = np.argsort(distances)[:k]

    nearest_species = y[nearest_indices]

    counts = {
        species: np.sum(nearest_species == species)
        for species in classes
    }

    prediction = max(counts, key=counts.get)

    probabilities = {
        species: counts[species] / k * 100
        for species in classes
    }

    return prediction, probabilities, nearest_indices, distances

# 4. 사용자 입력
st.divider()
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

# 5. 예측 버튼
if st.button("🌸 품종 예측하기", use_container_width=True):

    input_data = np.array([petal_length, petal_width])

    prediction, probabilities, nearest_indices, distances = (
        knn_predict(input_data, k=5)
    )

    st.divider()
    st.subheader("🔍 AI 예측 결과")

    st.success(f"예측된 붓꽃 품종: {prediction}")

    st.write("### 품종별 예측 비율")

    probability_df = pd.DataFrame({
        "품종": list(probabilities.keys()),
        "예측 비율(%)": list(probabilities.values())
    })

    st.bar_chart(
        probability_df.set_index("품종"),
        color="#2ECC71"
    )

    st.caption(
        "예측 비율은 가장 가까운 데이터 5개 중 "
        "각 품종이 차지하는 비율입니다."
    )

    # 6. 시각화
    st.divider()
    st.subheader("📊 꽃잎 크기별 품종 분류 그래프")

    x_min = max(0, X[:, 0].min() - 0.5)
    x_max = X[:, 0].max() + 0.5
    y_min = max(0, X[:, 1].min() - 0.5)
    y_max = X[:, 1].max() + 0.5

    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 150),
        np.linspace(y_min, y_max, 150)
    )

    grid = np.column_stack([
        xx.ravel(),
        yy.ravel()
    ])

    # 각 격자 위치의 품종 예측
    grid_distances = np.sqrt(
        np.sum(
            (grid[:, np.newaxis, :] - X[np.newaxis, :, :]) ** 2,
            axis=2
        )
    )

    nearest_grid = np.argsort(
        grid_distances, axis=1
    )[:, :5]

    nearest_labels = y[nearest_grid]

    # 다수결 분류
    grid_predictions = np.empty(len(grid), dtype=object)

    for i, labels in enumerate(nearest_labels):
        values, counts = np.unique(
            labels, return_counts=True
        )
        grid_predictions[i] = values[np.argmax(counts)]

    class_map = {
        name: i for i, name in enumerate(classes)
    }

    zz = np.array([
        class_map[name] for name in grid_predictions
    ]).reshape(xx.shape)

    colors = [
        "#3498DB",
        "#F39C12",
        "#9B59B6"
    ]

    colorscale = []

    for i, color in enumerate(colors[:len(classes)]):
        start = i / len(classes)
        end = (i + 1) / len(classes)

        colorscale.append([start, color])
        colorscale.append([end, color])

    fig = go.Figure()

    # 품종별 분류 영역
    fig.add_trace(go.Heatmap(
        x=np.linspace(x_min, x_max, 150),
        y=np.linspace(y_min, y_max, 150),
        z=zz,
        colorscale=colorscale,
        zmin=-0.5,
        zmax=len(classes) - 0.5,
        opacity=0.25,
        showscale=False,
        hoverinfo="skip",
        name="분류 영역"
    ))

    # 기존 붓꽃 데이터
    for i, species in enumerate(classes):

        subset = df[df["품종"] == species]

        fig.add_trace(go.Scatter(
            x=subset["꽃잎길이"],
            y=subset["꽃잎너비"],
            mode="markers",
            name=species,
            marker=dict(
                color=colors[i % len(colors)],
                size=8,
                opacity=0.8
            )
        ))

    # 사용자 입력값 초록색 별
    fig.add_trace(go.Scatter(
        x=[petal_length],
        y=[petal_width],
        mode="markers",
        name="내 입력값 ★",
        marker=dict(
            color="green",
            size=23,
            symbol="star",
            line=dict(color="black", width=1)
        )
    ))

    fig.update_layout(
        title="KNN 붓꽃 품종 분류 결과",
        xaxis_title="꽃잎길이 (cm)",
        yaxis_title="꽃잎너비 (cm)",
        template="plotly_white",
        height=600,
        legend_title="품종"
    )

    st.plotly_chart(fig, use_container_width=True)

    # 7. 예측 이유 설명
    st.divider()
    st.subheader("💡 왜 이 품종으로 분류되었을까?")

    st.write(
        f"입력한 꽃잎길이는 {petal_length}cm, "
        f"꽃잎너비는 {petal_width}cm입니다."
    )

    st.write(
        "AI는 입력한 값과 기존 붓꽃 데이터 사이의 "
        "거리를 계산했습니다."
    )

    st.write(
        "그중 가장 가까운 데이터 5개를 선택하고 "
        "가장 많이 등장한 품종을 최종 결과로 결정했습니다."
    )

    # 가장 가까운 데이터 5개 확인
    st.write("### 가장 가까운 붓꽃 데이터 5개")

    neighbor_df = df.iloc[nearest_indices][
        ["꽃잎길이", "꽃잎너비", "품종"]
    ].copy()

    neighbor_df["거리"] = distances[nearest_indices]

    st.dataframe(
        neighbor_df.reset_index(drop=True),
        use_container_width=True
    )

    # 8. 분석 결과
    st.divider()
    st.subheader("📌 분석 결과 정리")

    st.write(f"- 입력 꽃잎길이: {petal_length}cm")
    st.write(f"- 입력 꽃잎너비: {petal_width}cm")
    st.write(f"- 사용한 알고리즘: K-최근접 이웃(KNN)")
    st.write(f"- 비교한 가까운 데이터: 5개")
    st.write(f"- 최종 예측 품종: {prediction}")

else:
    st.info("꽃잎 크기를 입력하고 예측 버튼을 눌러주세요.")


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측 프로그램")
st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "인공지능이 붓꽃의 품종을 예측합니다."
)

st.divider()

# =====================================
# 2. 공개 Iris 데이터 자동 불러오기
# =====================================
@st.cache_data
def load_data():

    url = (
        "https://raw.githubusercontent.com/"
        "mwaskom/seaborn-data/master/iris.csv"
    )

    data = pd.read_csv(url)

    # 필요한 열만 선택하고 한글로 변경
    data = data.rename(columns={
        "petal_length": "꽃잎길이",
        "petal_width": "꽃잎너비",
        "species": "품종"
    })

    return data[
        ["꽃잎길이", "꽃잎너비", "품종"]
    ].dropna()


try:
    df = load_data()

except Exception as e:
    st.error("인터넷에서 붓꽃 데이터를 불러오지 못했습니다.")
    st.error("인터넷 연결을 확인한 후 다시 실행해 주세요.")
    st.stop()

st.success(f"붓꽃 데이터 {len(df)}개를 자동으로 불러왔습니다.")

# =====================================
# 3. 데이터 준비
# =====================================
X = df[["꽃잎길이", "꽃잎너비"]].to_numpy(dtype=float)
y = df["품종"].to_numpy()

classes = np.unique(y)

colors = {
    "setosa": "#3498DB",
    "versicolor": "#F39C12",
    "virginica": "#9B59B6"
}

# =====================================
# 4. KNN 알고리즘 직접 구현
# =====================================
def knn_predict(input_data, k=5):

    # 입력값과 기존 데이터 사이의 거리 계산
    distances = np.sqrt(
        np.sum((X - input_data) ** 2, axis=1)
    )

    # 가장 가까운 5개 데이터 선택
    nearest_indices = np.argsort(distances)[:k]

    nearest_species = y[nearest_indices]

    # 품종별 개수 계산
    counts = {
        species: np.sum(nearest_species == species)
        for species in classes
    }

    # 가장 많이 등장한 품종 선택
    prediction = max(
        classes,
        key=lambda species: counts[species]
    )

    # 품종별 예측 비율
    probabilities = {
        species: counts[species] / k * 100
        for species in classes
    }

    return prediction, probabilities, nearest_indices, distances


# =====================================
# 5. 사용자 입력
# =====================================
st.subheader("📝 꽃잎 크기 입력하기")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎길이 (cm)",
        min_value=0.1,
        max_value=8.0,
        value=1.5,
        step=0.1
    )

with col2:
    petal_width = st.number_input(
        "꽃잎너비 (cm)",
        min_value=0.1,
        max_value=4.0,
        value=0.3,
        step=0.1
    )

# =====================================
# 6. 예측 실행
# =====================================
if st.button("🌸 품종 예측하기", use_container_width=True):

    input_data = np.array([
        petal_length,
        petal_width
    ])

    prediction, probabilities, nearest_indices, distances = (
        knn_predict(input_data, 5)
    )

    st.divider()
    st.subheader("🔍 AI 예측 결과")

    st.success(f"예측된 붓꽃 품종: {prediction}")

    st.metric(
        "가장 높은 예측 비율",
        f"{probabilities[prediction]:.0f}%"
    )

    # =====================================
    # 7. 품종별 예측 비율 그래프
    # =====================================
    st.write("### 📊 품종별 예측 비율")

    probability_df = pd.DataFrame({
        "품종": list(probabilities.keys()),
        "예측 비율": list(probabilities.values())
    })

    fig_bar = go.Figure()

    fig_bar.add_trace(go.Bar(
        x=probability_df["품종"],
        y=probability_df["예측 비율"],
        marker_color=[
            colors[s] for s in probability_df["품종"]
        ],
        text=[
            f"{v:.0f}%"
            for v in probability_df["예측 비율"]
        ],
        textposition="outside"
    ))

    fig_bar.update_layout(
        yaxis_title="예측 비율 (%)",
        yaxis_range=[0, 110],
        template="plotly_white"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    st.caption(
        "가장 가까운 데이터 5개 중 각 품종이 차지하는 비율입니다."
    )

    # =====================================
    # 8. 품종별 분류 영역 계산
    # =====================================
    st.divider()
    st.subheader("📈 꽃잎 크기별 품종 분류 시각화")

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

    # 각 격자점에서 가장 가까운 데이터 5개 찾기
    grid_distances = np.sqrt(
        np.sum(
            (grid[:, None, :] - X[None, :, :]) ** 2,
            axis=2
        )
    )

    nearest_grid = np.argsort(
        grid_distances,
        axis=1
    )[:, :5]

    nearest_labels = y[nearest_grid]

    grid_predictions = []

    for labels in nearest_labels:

        values, counts = np.unique(
            labels,
            return_counts=True
        )

        grid_predictions.append(
            values[np.argmax(counts)]
        )

    class_map = {
        species: i
        for i, species in enumerate(classes)
    }

    zz = np.array([
        class_map[name]
        for name in grid_predictions
    ]).reshape(xx.shape)

    # =====================================
    # 9. 그래프 만들기
    # =====================================
    colorscale = []

    for i, species in enumerate(classes):

        colorscale.append([
            i / len(classes),
            colors[species]
        ])

        colorscale.append([
            (i + 1) / len(classes),
            colors[species]
        ])

    fig = go.Figure()

    # 품종별 분류 영역
    fig.add_trace(go.Heatmap(
        x=np.linspace(x_min, x_max, 150),
        y=np.linspace(y_min, y_max, 150),
        z=zz,
        colorscale=colorscale,
        zmin=-0.5,
        zmax=len(classes) - 0.5,
        opacity=0.3,
        showscale=False,
        hoverinfo="skip",
        name="분류 영역"
    ))

    # 기존 붓꽃 데이터
    for species in classes:

        subset = df[df["품종"] == species]

        fig.add_trace(go.Scatter(
            x=subset["꽃잎길이"],
            y=subset["꽃잎너비"],
            mode="markers",
            name=species,
            marker=dict(
                color=colors[species],
                size=8,
                opacity=0.8
            )
        ))

    # 사용자 입력값 초록색 별
    fig.add_trace(go.Scatter(
        x=[petal_length],
        y=[petal_width],
        mode="markers",
        name="내가 입력한 값 ★",
        marker=dict(
            color="green",
            size=25,
            symbol="star",
            line=dict(
                color="black",
                width=1
            )
        )
    ))

    fig.update_layout(
        title="KNN 붓꽃 품종 분류 결과",
        xaxis_title="꽃잎길이 (cm)",
        yaxis_title="꽃잎너비 (cm)",
        template="plotly_white",
        height=600,
        legend_title="품종",
        hovermode="closest"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================
    # 10. 예측 이유 설명
    # =====================================
    st.divider()
    st.subheader("💡 왜 이 품종으로 분류되었을까?")

    st.write(
        f"입력한 꽃잎길이: {petal_length:.1f}cm"
    )

    st.write(
        f"입력한 꽃잎너비: {petal_width:.1f}cm"
    )

    st.write(
        "AI는 입력한 꽃잎 크기와 기존 붓꽃 데이터의 "
        "거리를 계산했습니다."
    )

    st.write(
        f"가장 가까운 데이터 5개 중 "
        f"{prediction} 품종이 가장 많이 나타났기 때문에 "
        "해당 품종으로 분류했습니다."
    )

    # 가까운 데이터 5개
    st.write("### 🔎 가장 가까운 붓꽃 데이터 5개")

    neighbor_df = df.iloc[nearest_indices][
        ["꽃잎길이", "꽃잎너비", "품종"]
    ].copy()

    neighbor_df["거리"] = distances[nearest_indices]

    st.dataframe(
        neighbor_df.reset_index(drop=True),
        use_container_width=True
    )

    # =====================================
    # 11. 분석 결과
    # =====================================
    st.divider()
    st.subheader("📌 분석 결과 정리")

    st.write(f"- 전체 데이터 수: {len(df)}개")
    st.write(f"- 붓꽃 품종 수: {len(classes)}종")
    st.write("- 사용 알고리즘: KNN")
    st.write("- 비교 데이터 수: 5개")
    st.write(f"- 최종 예측 품종: {prediction}")

else:

    st.info(
        "꽃잎길이와 꽃잎너비를 입력하고 "
        "예측 버튼을 눌러주세요."
    )

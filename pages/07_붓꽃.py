
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import io

# ==================================
# 1. 페이지 설정
# ==================================
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 AI가 품종을 예측합니다.")

# ==================================
# 2. CSV 파일 자동 검색 및 업로드
# ==================================
def load_csv():

    current_dir = Path(__file__).resolve().parent

    # CSV 파일을 찾을 경로
    possible_paths = [
        current_dir.parent / "Iris.csv",
        current_dir / "Iris.csv",
        Path.cwd() / "Iris.csv",
        Path.cwd() / "data" / "Iris.csv"
    ]

    # 파일 자동 검색
    for file_path in possible_paths:
        if file_path.exists():
            for encoding in ["cp949", "utf-8-sig", "utf-8"]:
                try:
                    return pd.read_csv(
                        file_path,
                        encoding=encoding
                    )
                except UnicodeDecodeError:
                    continue

    return None


df = load_csv()

# 자동 검색 실패 시 직접 업로드
if df is None:

    st.warning("Iris.csv 파일을 자동으로 찾지 못했습니다.")

    uploaded_file = st.file_uploader(
        "📂 Iris.csv 파일을 업로드해 주세요.",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info(
            "GitHub 최상위 폴더에 Iris.csv를 올리거나 "
            "위에서 CSV 파일을 업로드해 주세요."
        )
        st.stop()

    file_bytes = uploaded_file.getvalue()

    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            df = pd.read_csv(
                io.BytesIO(file_bytes),
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        st.error("CSV 파일의 인코딩을 확인해 주세요.")
        st.stop()

# ==================================
# 3. 데이터 확인 및 정리
# ==================================
required_columns = [
    "꽃잎길이",
    "꽃잎너비",
    "품종"
]

if not all(col in df.columns for col in required_columns):
    st.error(
        "CSV 파일의 열 이름이 올바르지 않습니다. "
        "꽃잎길이, 꽃잎너비, 품종 열이 필요합니다."
    )
    st.stop()

df = df[required_columns].copy()

df["꽃잎길이"] = pd.to_numeric(
    df["꽃잎길이"], errors="coerce"
)

df["꽃잎너비"] = pd.to_numeric(
    df["꽃잎너비"], errors="coerce"
)

df["품종"] = df["품종"].astype("string").str.strip()

df = df.dropna()

df = df[
    (df["꽃잎길이"] > 0) &
    (df["꽃잎너비"] > 0) &
    (df["품종"] != "")
]

if len(df) < 5 or df["품종"].nunique() < 2:
    st.error("품종 예측에 필요한 데이터가 부족합니다.")
    st.stop()

X = df[["꽃잎길이", "꽃잎너비"]].to_numpy(dtype=float)
y = df["품종"].to_numpy()

classes = np.unique(y)

# 품종별 색상
color_palette = [
    "#3498DB",
    "#F39C12",
    "#9B59B6",
    "#E74C3C",
    "#16A085"
]

species_colors = {
    name: color_palette[i % len(color_palette)]
    for i, name in enumerate(classes)
}

# ==================================
# 4. KNN 알고리즘 구현
# ==================================
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

    return (
        prediction,
        probabilities,
        nearest_indices,
        distances
    )


# ==================================
# 5. 사용자 입력
# ==================================
st.divider()

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

# ==================================
# 6. 품종 예측
# ==================================
if st.button("🌸 품종 예측하기", use_container_width=True):

    input_data = np.array([
        petal_length,
        petal_width
    ])

    k = min(5, len(X))

    (
        prediction,
        probabilities,
        nearest_indices,
        distances
    ) = knn_predict(input_data, k)

    st.divider()

    st.subheader("🔍 AI 예측 결과")

    st.success(
        f"예측된 붓꽃 품종: {prediction}"
    )

    st.metric(
        "가장 많이 선택된 품종의 비율",
        f"{probabilities[prediction]:.1f}%"
    )

    # ==================================
    # 7. 품종별 예측 비율
    # ==================================
    st.write("### 📊 품종별 예측 비율")

    probability_df = pd.DataFrame({
        "품종": list(probabilities.keys()),
        "예측 비율(%)": list(probabilities.values())
    })

    fig_bar = go.Figure()

    fig_bar.add_trace(go.Bar(
        x=probability_df["품종"],
        y=probability_df["예측 비율(%)"],
        marker_color=[
            species_colors[s]
            for s in probability_df["품종"]
        ],
        text=[
            f"{v:.0f}%"
            for v in probability_df["예측 비율(%)"]
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
        "가장 가까운 붓꽃 데이터 5개 중 "
        "각 품종이 차지하는 비율입니다."
    )

    # ==================================
    # 8. 분류 영역 그래프
    # ==================================
    st.divider()

    st.subheader("🌈 꽃잎 크기별 품종 분류 그래프")

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

    # 모든 격자점과 기존 데이터 사이의 거리 계산
    grid_distances = np.sqrt(
        np.sum(
            (grid[:, np.newaxis, :] -
             X[np.newaxis, :, :]) ** 2,
            axis=2
        )
    )

    # 가장 가까운 데이터 5개 선택
    nearest_grid = np.argsort(
        grid_distances,
        axis=1
    )[:, :k]

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
        name: i
        for i, name in enumerate(classes)
    }

    zz = np.array([
        class_map[name]
        for name in grid_predictions
    ]).reshape(xx.shape)

    # 품종별 분류 영역 색상
    colorscale = []

    n = len(classes)

    for i, species in enumerate(classes):

        color = species_colors[species]

        colorscale.append([
            i / n,
            color
        ])

        colorscale.append([
            (i + 1) / n,
            color
        ])

    fig = go.Figure()

    # 분류 영역 표시
    fig.add_trace(go.Heatmap(
        x=np.linspace(x_min, x_max, 150),
        y=np.linspace(y_min, y_max, 150),
        z=zz,
        colorscale=colorscale,
        zmin=-0.5,
        zmax=n - 0.5,
        opacity=0.3,
        showscale=False,
        hoverinfo="skip",
        name="품종 분류 영역"
    ))

    # 기존 붓꽃 데이터 표시
    for species in classes:

        subset = df[df["품종"] == species]

        fig.add_trace(go.Scatter(
            x=subset["꽃잎길이"],
            y=subset["꽃잎너비"],
            mode="markers",
            name=species,
            marker=dict(
                color=species_colors[species],
                size=8,
                opacity=0.8
            )
        ))

    # 사용자 입력값 초록색 별 표시
    fig.add_trace(go.Scatter(
        x=[petal_length],
        y=[petal_width],
        mode="markers",
        name="사용자 입력값 ★",
        marker=dict(
            color="green",
            size=24,
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

    # ==================================
    # 9. 예측 이유 설명
    # ==================================
    st.divider()

    st.subheader("💡 왜 이 품종으로 분류되었을까?")

    st.write(
        f"입력한 꽃잎길이는 {petal_length:.1f}cm, "
        f"꽃잎너비는 {petal_width:.1f}cm입니다."
    )

    st.write(
        f"AI는 입력한 값과 가장 가까운 "
        f"붓꽃 데이터 {k}개를 찾았습니다."
    )

    st.write(
        f"가장 가까운 데이터 {k}개 중 "
        f"{prediction} 품종이 가장 많이 나타났기 때문에 "
        f"최종 품종으로 예측했습니다."
    )

    # 가까운 데이터 확인
    st.write("### 🔎 가장 가까운 데이터 5개")

    neighbor_df = df.iloc[
        nearest_indices
    ][
        ["꽃잎길이", "꽃잎너비", "품종"]
    ].copy()

    neighbor_df["거리"] = distances[nearest_indices]

    st.dataframe(
        neighbor_df.reset_index(drop=True),
        use_container_width=True
    )

    # ==================================
    # 10. 데이터 분석 결과
    # ==================================
    st.divider()

    st.subheader("📌 분석 결과")

    st.write(f"- 전체 데이터: {len(df)}개")
    st.write(f"- 붓꽃 품종: {len(classes)}종")
    st.write("- 분류 알고리즘: K-최근접 이웃(KNN)")
    st.write(f"- 비교 데이터: {k}개")
    st.write(f"- 예측 결과: {prediction}")

else:

    st.info(
        "꽃잎길이와 꽃잎너비를 입력한 후 "
        "'품종 예측하기' 버튼을 눌러주세요."
    )

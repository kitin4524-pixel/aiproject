
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------
# 1. 페이지 설정
# --------------------------------

st.set_page_config(
    page_title="서울 10년 단위 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 10년 단위 기온 분석")

st.write(
    "월을 선택하면 10년 단위로 평균 최고기온과 "
    "평균 최저기온을 비교할 수 있습니다."
)

# CSV 파일 경로
# 파이썬 파일은 pages 폴더 안에 있음
# CSV 파일은 프로젝트 최상위 폴더에 있음

CSV_PATH = (
    Path(__file__).resolve().parent.parent
    / "tamperature.csv"
)


# --------------------------------
# 2. 데이터 불러오기
# --------------------------------

@st.cache_data
def load_data(file_path):

    data = None

    # 한글 인코딩 자동 처리
    for encoding in ["utf-8-sig", "cp949", "euc-kr"]:

        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError(
            "CSV 파일의 인코딩을 확인해 주세요."
        )

    # 열 이름 공백 제거
    data.columns = (
        data.columns.astype(str).str.strip()
    )

    # 필요한 열 확인
    required_columns = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required_columns:

        if col not in data.columns:
            raise ValueError(
                f"CSV 파일에 {col} 열이 없습니다."
            )

    # 날짜 변환
    date_text = (
        data["일시"].astype(str).str.strip()
    )

    data["날짜"] = pd.to_datetime(
        date_text,
        format="%b-%y",
        errors="coerce"
    )

    # 다른 날짜 형식 처리
    invalid = data["날짜"].isna()

    if invalid.any():

        data.loc[invalid, "날짜"] = pd.to_datetime(
            date_text.loc[invalid],
            errors="coerce"
        )

    # 기온 데이터 숫자 변환
    data["최고기온(℃)"] = pd.to_numeric(
        data["최고기온(℃)"],
        errors="coerce"
    )

    data["최저기온(℃)"] = pd.to_numeric(
        data["최저기온(℃)"],
        errors="coerce"
    )

    # 날짜가 없는 행 제거
    data = data.dropna(
        subset=["날짜"]
    )

    # 연도와 월 추출
    data["연도"] = (
        data["날짜"].dt.year
    )

    data["월"] = (
        data["날짜"].dt.month
    )

    # 10년 단위 구분
    data["10년대"] = (
        data["연도"] // 10 * 10
    )

    return data


# --------------------------------
# 3. 메인 프로그램
# --------------------------------

try:

    # 데이터 불러오기
    df = load_data(CSV_PATH)

    if df.empty:

        st.warning(
            "분석할 데이터가 없습니다."
        )

        st.stop()

    # 월 이름
    month_names = {
        1: "1월",
        2: "2월",
        3: "3월",
        4: "4월",
        5: "5월",
        6: "6월",
        7: "7월",
        8: "8월",
        9: "9월",
        10: "10월",
        11: "11월",
        12: "12월"
    }

    # --------------------------------
    # 4. 월 선택
    # --------------------------------

    selected_month = st.selectbox(
        "📅 분석할 월을 선택하세요",
        options=list(range(1, 13)),
        format_func=lambda x: month_names[x]
    )

    # 선택한 월 데이터 추출
    monthly_data = df[
        df["월"] == selected_month
    ].copy()

    # --------------------------------
    # 5. 10년 단위 평균 계산
    # --------------------------------

    decade_data = (
        monthly_data
        .groupby("10년대", as_index=False)
        .agg({
            "최고기온(℃)": "mean",
            "최저기온(℃)": "mean"
        })
        .sort_values("10년대")
    )

    # 그래프 가로축 표시용 이름
    decade_data["기간"] = (
        decade_data["10년대"].astype(int).astype(str)
        + "년대"
    )

    # --------------------------------
    # 6. 그래프 출력
    # --------------------------------

    st.subheader(
        f"📊 {month_names[selected_month]} 10년 단위 기온 분석"
    )

    if decade_data.empty:

        st.warning(
            "선택한 월에 해당하는 데이터가 없습니다."
        )

    else:

        fig = go.Figure()

        # 최고기온 그래프
        fig.add_trace(
            go.Scatter(
                x=decade_data["기간"],
                y=decade_data["최고기온(℃)"],
                mode="lines+markers",
                name="평균 최고기온",
                line=dict(
                    color="#FF69B4",
                    width=3
                ),
                marker=dict(
                    size=9
                )
            )
        )

        # 최저기온 그래프
        fig.add_trace(
            go.Scatter(
                x=decade_data["기간"],
                y=decade_data["최저기온(℃)"],
                mode="lines+markers",
                name="평균 최저기온",
                line=dict(
                    color="#87CEEB",
                    width=3
                ),
                marker=dict(
                    size=9
                )
            )
        )

        # 그래프 디자인
        fig.update_layout(
            title="월 별 기온분석",
            xaxis_title="10년 단위",
            yaxis_title="온도 (℃)",
            legend_title="기온 구분",
            hovermode="x unified",
            template="plotly_white",
            height=550
        )

        # 가로축 설정
        fig.update_xaxes(
            type="category"
        )

        # 그래프 표시
        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # --------------------------------
        # 7. 분석 데이터 표
        # --------------------------------

        st.subheader(
            "📋 10년 단위 기온 데이터"
        )

        table_data = decade_data[
            [
                "기간",
                "최고기온(℃)",
                "최저기온(℃)"
            ]
        ].copy()

        table_data = table_data.rename(
            columns={
                "기간": "기간",
                "최고기온(℃)": "평균 최고기온(℃)",
                "최저기온(℃)": "평균 최저기온(℃)"
            }
        )

        # 소수점 둘째 자리까지 표시
        table_data[
            ["평균 최고기온(℃)", "평균 최저기온(℃)"]
        ] = table_data[
            ["평균 최고기온(℃)", "평균 최저기온(℃)"]
        ].round(2)

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------
        # 8. 분석 정보
        # --------------------------------

        st.info(
            "각 10년대에 속하는 선택 월의 최고기온과 "
            "최저기온을 각각 평균하여 표시했습니다."
        )


# --------------------------------
# 9. 오류 처리
# --------------------------------

except FileNotFoundError:

    st.error(
        "tamperature.csv 파일을 찾을 수 없습니다. "
        "프로젝트 최상위 폴더에 CSV 파일이 있는지 확인해 주세요."
    )

except Exception as error:

    st.error(
        f"데이터 처리 중 오류가 발생했습니다: {error}"
    )

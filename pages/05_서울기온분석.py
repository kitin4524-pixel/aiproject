
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="서울 월별 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 서울 월별 기온 분석")
st.write("월을 선택하면 전체 연도의 해당 월 최고기온과 최저기온을 비교합니다.")

# CSV 파일 경로
# 현재 파이썬 파일은 pages 폴더 안에 있음
# CSV 파일은 프로젝트 최상위 폴더에 있음
CSV_PATH = Path(__file__).resolve().parent.parent / "tamperature.csv"


# 데이터 불러오기 함수
@st.cache_data
def load_data(file_path):

    # 한글 인코딩 자동 처리
    data = None

    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError(
            "CSV 인코딩을 확인해 주세요. "
            "UTF-8 또는 CP949 파일이어야 합니다."
        )

    # 열 이름 공백 제거
    data.columns = data.columns.astype(str).str.strip()

    # 필요한 열 확인
    required_columns = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    missing = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            f"CSV에 필요한 열이 없습니다: {', '.join(missing)}\n"
            f"현재 열 이름: {', '.join(data.columns)}"
        )

    # 날짜 변환
    # 예: Oct-07, Nov-07
    date_text = data["일시"].astype(str).str.strip()

    data["날짜"] = pd.to_datetime(
        date_text,
        format="%b-%y",
        errors="coerce"
    )

    # 다른 날짜 형식도 처리
    invalid = data["날짜"].isna()

    if invalid.any():
        data.loc[invalid, "날짜"] = pd.to_datetime(
            date_text.loc[invalid],
            errors="coerce"
        )

    # 기온 데이터를 숫자로 변환
    data["최고기온(℃)"] = pd.to_numeric(
        data["최고기온(℃)"],
        errors="coerce"
    )

    data["최저기온(℃)"] = pd.to_numeric(
        data["최저기온(℃)"],
        errors="coerce"
    )

    # 날짜가 없는 행 제거
    data = data.dropna(subset=["날짜"])

    # 연도와 월 추출
    data["연도"] = data["날짜"].dt.year
    data["월"] = data["날짜"].dt.month

    return data


# 메인 프로그램
try:

    # 데이터 불러오기
    df = load_data(CSV_PATH)

    if df.empty:
        st.warning("분석할 수 있는 날짜 데이터가 없습니다.")
        st.stop()

    # 월 이름 설정
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

    # 월 선택
    selected_month = st.selectbox(
        "📅 분석할 월을 선택하세요",
        options=list(range(1, 13)),
        format_func=lambda month: month_names[month]
    )

    # 선택한 월의 데이터 추출
    selected_data = df[
        df["월"] == selected_month
    ].copy()

    # 연도별 최고기온과 최저기온 집계
    yearly_data = (
        selected_data.groupby("연도", as_index=False)
        .agg({
            "최고기온(℃)": "max",
            "최저기온(℃)": "min"
        })
        .sort_values("연도")
    )

    # 그래프 제목
    st.subheader(
        f"📊 {month_names[selected_month]} 기온 변화"
    )

    if yearly_data.empty:

        st.info(
            f"{month_names[selected_month]} 데이터가 없습니다."
        )

    else:

        # 그래프 생성
        fig = go.Figure()

        # 최고기온 그래프
        fig.add_trace(
            go.Scatter(
                x=yearly_data["연도"],
                y=yearly_data["최고기온(℃)"],
                mode="lines+markers",
                name="최고기온",
                line=dict(
                    color="#FF69B4",
                    width=3
                ),
                marker=dict(size=7)
            )
        )

        # 최저기온 그래프
        fig.add_trace(
            go.Scatter(
                x=yearly_data["연도"],
                y=yearly_data["최저기온(℃)"],
                mode="lines+markers",
                name="최저기온",
                line=dict(
                    color="#87CEEB",
                    width=3
                ),
                marker=dict(size=7)
            )
        )

        # 그래프 레이아웃 설정
        fig.update_layout(
            title="월 별 기온분석",
            xaxis_title="연도",
            yaxis_title="온도 (℃)",
            legend_title="범례",
            hovermode="x unified",
            template="plotly_white",
            height=550
        )

        # 가로축 연도 표시
        fig.update_xaxes(
            dtick=1
        )

        # 그래프 출력
        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # 데이터 표 출력
        st.subheader("📋 연도별 기온 데이터")

        table_data = yearly_data.rename(
            columns={
                "최고기온(℃)": "최고기온 (℃)",
                "최저기온(℃)": "최저기온 (℃)"
            }
        )

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )


# 파일을 찾을 수 없는 경우
except FileNotFoundError:

    st.error(
        "tamperature.csv 파일을 찾을 수 없습니다. "
        "프로젝트 최상위 폴더에 CSV 파일이 있는지 확인해 주세요."
    )


# 기타 오류 처리
except Exception as error:

    st.error(
        f"데이터 처리 중 오류가 발생했습니다: {error}"
    )


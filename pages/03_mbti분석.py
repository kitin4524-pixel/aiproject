import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 페이지 기본 설정
st.set_page_config(
    page_title="국가별 MBTI 비율 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 국가별 MBTI 분포 시각화 대시보드")
st.markdown("국가를 선택하여 해당 국가의 16가지 MBTI 유형별 비율과 1위 유형을 확인해 보세요.")

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # Streamlit Cloud 환경에서 CSV 파일 읽기
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ 'countriesMBTI_16types.csv' 파일을 찾을 수 없습니다. 코드와 같은 폴더에 파일을 업로드해주세요.")
    st.stop()

# 사이드바 설정: 국가 선택
st.sidebar.header("🔍 설정")
countries = sorted(df["Country"].unique())

# 기본값을 대한민국('South Korea') 또는 목록의 첫 번째 국가로 설정
default_country = "South Korea" if "South Korea" in countries else countries[0]
selected_country = st.sidebar.selectbox("국가를 선택하세요", countries, index=countries.index(default_country))

# 선택한 국가의 데이터 추출
country_data = df[df["Country"] == selected_country]

if not country_data.empty:
    # 데이터 변형 (Country 컬럼을 제외하고 MBTI 유형과 비율만 추출)
    mbti_columns = [col for col in df.columns if col != "Country"]
    ratios = country_data[mbti_columns].values.flatten()
    
    # 데이터프레임으로 정리 및 정렬 (비율이 높은 순)
    chart_df = pd.DataFrame({
        "MBTI": mbti_columns,
        "Ratio": ratios
    }).sort_values(by="Ratio", ascending=False).reset_index(drop=True)
    
    # 상단 요약 정보 표시
    st.subheader(f"📌 {selected_country}의 MBTI 분석 결과")
    top_mbti = chart_df.iloc[0]["MBTI"]
    top_ratio = chart_df.iloc[0]["Ratio"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🏆 가장 높은 비율의 MBTI", value=top_mbti, delta=f"{top_ratio:.4f}")
    with col2:
        st.metric(label="📊 분석된 MBTI 유형 수", value=f"{len(mbti_columns)}개")
    
    # 색상 설정 (1등은 빨간색, 나머지는 파란색 그라데이션)
    colors = []
    num_blues = len(chart_df) - 1
    blue_palette = sns.color_palette("Blues_r", n_colors=num_blues)
    
    for i in range(len(chart_df)):
        if i == 0:
            colors.append("#FF4B4B")  # 스트림릿 시그니처 레드 (1등)
        else:
            colors.append(blue_palette[i - 1])

    # 막대그래프 시각화
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(chart_df["MBTI"], chart_df["Ratio"], color=colors)
    
    ax.set_title(f"{selected_country} - MBTI Types Distribution", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("MBTI Type", fontsize=12, labelpad=10)
    ax.set_ylabel("Ratio", fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    
    # 그래프 테두리 및 여백 조정
    sns.despine(top=True, right=True)
    plt.tight_layout()
    
    # 스트림릿에 그래프 출력
    st.pyplot(fig)
    
    # 상세 데이터 테이블 보기 엑스팬더
    with st.expander("📋 상세 데이터 테이블 보기"):
        st.dataframe(chart_df, use_container_width=True)

else:
    st.warning("선택한 국가의 데이터를 불러올 수 없습니다.")

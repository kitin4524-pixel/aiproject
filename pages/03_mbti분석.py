import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 페이지 기본 설정 (가장 처음에 와야 합니다)
st.set_page_config(
    page_title="국가별 MBTI 비율 분석",
    page_icon="🌍",
    layout="wide"
)

# 2. 타이틀 및 안내 문구
st.title("🌍 국가별 MBTI 분포 시각화 대시보드")
st.markdown("국가를 선택하면 해당 국가의 16가지 MBTI 유형 비율을 막대그래프로 보여줍니다. (1위 유형: 빨간색, 나머지: 파란색 그라데이션)")

# 3. 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # CSV 파일 읽기 (파일명이 정확한지 확인해주세요)
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

# 데이터 로드 예외 처리
try:
    df = load_data()
except Exception as e:
    st.error(f"⚠️ 데이터 파일을 불러오는 중 오류가 발생했습니다. 'countriesMBTI_16types.csv' 파일이 코드와 같은 폴더에 있는지 확인해주세요.\n\n상세 에러: {e}")
    st.stop()

# 4. 사이드바 - 국가 선택
st.sidebar.header("🔍 검색 설정")
countries = sorted(df["Country"].unique())

# 기본값을 대한민국('South Korea')으로 설정, 없으면 첫 번째 국가
default_idx = countries.index("South Korea") if "South Korea" in countries else 0
selected_country = st.sidebar.selectbox("국가를 선택하세요", countries, index=default_idx)

# 5. 선택한 국가 데이터 필터링 및 가공
country_data = df[df["Country"] == selected_country]

if not country_data.empty:
    # Country 컬럼을 제외한 MBTI 열들만 추출
    mbti_columns = [col for col in df.columns if col != "Country"]
    ratios = country_data[mbti_columns].values.flatten()
    
    # 데이터프레임으로 정리 및 비율 높은 순 정렬
    chart_df = pd.DataFrame({
        "MBTI": mbti_columns,
        "Ratio": ratios
    }).sort_values(by="Ratio", ascending=False).reset_index(drop=True)
    
    # 상단 요약 지표 (Metric)
    st.subheader(f"📌 {selected_country}의 MBTI 분석 결과")
    top_mbti = chart_df.iloc[0]["MBTI"]
    top_ratio = chart_df.iloc[0]["Ratio"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🏆 가장 높은 비율의 MBTI", value=top_mbti, delta=f"{top_ratio:.4f}")
    with col2:
        st.metric(label="📊 분석된 MBTI 유형 수", value=f"{len(mbti_columns)}개")
    
    # 6. 색상 그라데이션 설정 (1등은 빨간색, 나머지는 파란색 그라데이션)
    colors = []
    num_blues = len(chart_df) - 1
    blue_palette = sns.color_palette("Blues_r", n_colors=num_blues)
    
    for i in range(len(chart_df)):
        if i == 0:
            colors.append("#FF4B4B")  # 1등: 스트림릿 레드
        else:
            colors.append(blue_palette[i - 1])  # 나머지: 파란색 그라데이션 (높을수록 진함)

    # 7. 막대그래프 시각화
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(chart_df["MBTI"], chart_df["Ratio"], color=colors)
    
    ax.set_title(f"{selected_country} - MBTI Types Distribution", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("MBTI Type", fontsize=12, labelpad=10)
    ax.set_ylabel("Ratio", fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    
    # 여백 및 테두리 정돈
    sns.despine(top=True, right=True)
    plt.tight_layout()
    
    # 스트림릿에 그래프 출력
    st.pyplot(fig)
    
    # 8. 상세 데이터 테이블
    with st.expander("📋 상세 데이터 테이블 보기"):
        st.dataframe(chart_df, use_container_width=True)

else:
    st.warning("선택한 국가의 데이터를 찾을 수 없습니다.")

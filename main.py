import streamlit as st
st.title('나의 첫 웹 서비스 만들기')
st.text_input('이름을 입력해주세요')
st.selectbox('좋아하는 음식을 선택하세요',['치킨','피자','햄버거'])
st.botton('인사말 생성')

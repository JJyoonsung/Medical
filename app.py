import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 페이지 기본 설정
st.set_page_config(
    page_title="폐의약품 수거 약국 찾기",
    page_icon="♥",
    layout="wide"
)

# 제목 및 설명
st.title("♥ 폐의약품 수거 약국 찾기")
st.markdown("원하는 폐의약품을 선택하면 해당 약국을 표와 지도에서 확인할 수 있어요!")

# 데이터 불러오기 함수 - 캐싱 적용
@st.cache_data
def load_data():
    df = pd.read_csv("cheonan_seobuk_pharmacy_with_items.csv", encoding='utf-8-sig')
    return df

# 데이터 로드
df = load_data()


all_items = []
df['수거약품목'].dropna().apply(lambda x: all_items.extend([i.strip() for i in x.split(',')]))

categories = list(sorted(set(all_items)))

st.subheader("♻수거 약품목 선택 (최대 3개)")
cols = st.columns(3)
selected = []


for i, cat in enumerate(categories):
    if cols[i % 3].checkbox(cat):
        selected.append(cat)

if len(selected) > 3:
    st.error("❗ 최대 3개까지만 선택할 수 있어요")
    selected = selected[:3]


if selected:
    mask = df['수거약품목'].apply(lambda x: any(tag in str(x) for tag in selected))
    result = df[mask]

    st.success(f"선택한 약품목: {selected} → 약국 {len(result)}곳")

    st.dataframe(result[['병원명', '주소', '전화번호','수거약품목']], use_container_width=True)
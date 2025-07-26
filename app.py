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

# 수거 약품목 리스트 만들기
all_items = []
df['수거약품목'].dropna().apply(lambda x: all_items.extend([i.strip() for i in x.split(',')]))

categories = sorted(set(all_items))

st.subheader("♻ 수거 약품목 선택 (최대 3개)")
cols = st.columns(3)
selected = []

for i, cat in enumerate(categories):
    if cols[i % 3].checkbox(cat):
        selected.append(cat)

if len(selected) > 3:
    st.error("❗ 최대 3개까지만 선택할 수 있어요")
    selected = selected[:3]

if selected:
    # 선택한 약품이 포함된 행 필터링
    mask = df['수거약품목'].apply(lambda x: any(tag in str(x) for tag in selected))
    result = df[mask]

    st.success(f"선택한 약품목: {selected} → 약국 {len(result)}곳")

    st.dataframe(result[['병원명', '주소', '전화번호', '수거약품목']], use_container_width=True)
else:
    result = pd.DataFrame()  # 빈 데이터프레임 초기화

st.subheader("🎈 약국 위치 지도")

# 선택 결과가 있을 때만 지도 표시 시도
if not result.empty:
    coords = result.dropna(subset=['위도', '경도'])

    if not coords.empty:
        # 중심 좌표 지정(중간값 또는 평균값도 가능)
        m = folium.Map(location=[coords['위도'].mean(), coords['경도'].mean()], zoom_start=12)

        # 지도의 보여줄 범위 지정
        bounds = [
            [coords['위도'].min(), coords['경도'].min()],
            [coords['위도'].max(), coords['경도'].max()]
        ]
        m.fit_bounds(bounds)

        for _, row in coords.iterrows():
            folium.Marker(
                [row['위도'], row['경도']],
                popup=f"{row['병원명']}<br>{row['수거약품목']}",
                tooltip=row['병원명']
            ).add_to(m)

        folium_static(m, width=800, height=500)
    else:
        st.info("위치 정보가 없습니다!")
else:
    st.info("위쪽에서 수거 약품목을 선택해주세요!")

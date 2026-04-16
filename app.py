import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="꼬꼬닥'S 컴퓨터 매입계산기", layout="wide")

# 2. CSS: 높이 균형 및 정렬 (최신 수정본 반영)
st.markdown("""
    <style>
    div[data-baseweb="select"], div[data-baseweb="input"], .stTextInput input, .stSelectbox div[role="button"] {
        height: 48px !important; min-height: 48px !important;
        display: flex !important; align-items: center !important;
    }
    div[data-baseweb="select"] > div { padding: 0 !important; display: flex !important; align-items: center !important; }
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 12px 0; font-weight: bold; border-radius: 4px; text-align: center; margin-bottom: 8px;
    }
    .header-item { flex: 1; border-right: 1px solid rgba(255,255,255,0.3); }
    .cell-center { text-align: center; display: flex; align-items: center; justify-content: center; height: 48px; border-right: 1px solid #f0f2f6; }
    .cell-left { display: flex; align-items: center; padding-left: 10px; height: 48px; border-right: 1px solid #f0f2f6; }
    div.stButton > button[key^="add_"] {
        width: 38px !important; min-width: 38px !important; height: 38px !important; 
        border-radius: 50% !important; margin: 0 auto !important; display: block !important;
    }
    .price-text { color: red; font-weight: bold; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로딩 (캐시)
@st.cache_data(ttl=3600)
def fetch_data():
    # ... (기존 URL 및 크롤링 로직 동일)
    URLS = ["https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4220"] # 예시
    all_rows = [{"분류": "[9세대]", "상품명": "커피I5 9400", "매입가": 70000}] # 샘플 데이터
    return pd.DataFrame(all_rows)

# 4. 세션 상태 초기화
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
for i in range(6):
    if f"nm_{i}" not in st.session_state: st.session_state[f"nm_{i}"] = ""
    if f"pr_{i}" not in st.session_state: st.session_state[f"pr_{i}"] = 0
if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0

# 5. 핵심: 부분 업데이트를 위한 프래그먼트 설정
@st.fragment
def render_calculator():
    st.subheader("🛒 매입 계산 리스트")
    
    # 라디오 버튼
    st.radio("항목 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

    total_sum = 0
    for i in range(6):
        st.write(f"**{labels[i]}**")
        c1, c2 = st.columns([3, 1])
        with c1:
            st.text_input(f"모델_{i}", key=f"nm_{i}", label_visibility="collapsed")
        with c2:
            st.number_input(f"가_{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total_sum += st.session_state[f"pr_{i}"]

    st.markdown(f"### 💰 최종 합계: :red[{total_sum:,}원]")

    if st.button("🗑️ 전체 초기화", use_container_width=True):
        for i in range(6):
            st.session_state[f"nm_{i}"], st.session_state[f"pr_{i}"] = "", 0
        st.rerun()

# --- 메인 화면 ---
st.title("🐔꼬꼬닥'S 컴퓨터 매입계산기🖥️")

df = fetch_data()
c_cat, c_search = st.columns([1, 2.5])
with c_cat:
    cat = st.selectbox("분류", ["전체보기"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with c_search:
    query = st.text_input("검색", placeholder="상품명 입력", label_visibility="collapsed")

# 조회 결과 테이블 영역
st.markdown('<div class="table-header"><div class="header-item" style="flex:1;">분류</div><div class="header-item" style="flex:2.5;">상품명</div><div class="header-item" style="flex:1.5;">금액</div><div class="header-item" style="flex:0.8; border-right:none;">담기</div></div>', unsafe_allow_html=True)

with st.container(height=350):
    for i, row in df.iterrows():
        cols = st.columns([1, 2.5, 1.5, 0.8])
        cols[0].write(row["분류"])
        cols[1].write(row["상품명"])
        cols[2].markdown(f'<p class="price-text">{row["매입가"]:,}</p>', unsafe_allow_html=True)
        with cols[3]:
            # 클릭 시 즉시 세션값 변경
            if st.button("➕", key=f"add_{i}"):
                idx = st.session_state['target_idx']
                st.session_state[f"nm_{idx}"] = row['상품명']
                st.session_state[f"pr_{idx}"] = row['매입가']
                st.session_state['target_idx'] = (idx + 1) % 6
                st.rerun() # 이 rerun은 프래그먼트 내부만 다시 그립니다.

st.divider()

# 프래그먼트 호출 (딜레이 해결의 핵심)
render_calculator()

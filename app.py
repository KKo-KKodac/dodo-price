import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="DODO 매입", layout="wide")

# 2. CSS 최적화 (높이 맞춤 및 버튼 글자 깨짐 방지)
st.markdown("""
    <style>
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stButton > button {
        height: 45px !important; min-height: 45px !important;
    }
    .stButton > button {
        min-width: 150px !important; /* 버튼 크기 확보 */
        font-weight: 600 !important;
    }
    /* 담기 버튼 전용 (둥글게) */
    div.stButton > button[key^="add_"] {
        width: 40px !important; min-width: 40px !important; height: 40px !important; border-radius: 50% !important; padding: 0 !important;
    }
    .price-text { color: red; font-weight: bold; text-align: center; font-size: 16px; margin: 0; }
    .table-header {
        display: flex; background-color: #4A90E2; color: white; padding: 12px 0;
        font-weight: bold; border-radius: 4px; text-align: center; margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 수집 (캐시 적용)
@st.cache_data(ttl=3600)
def fetch_data():
    # URL 리스트 및 크롤링 로직 (생략 없이 작동하도록 유지)
    all_rows = []
    # (여기에 기존 크롤링 URL들과 로직이 들어갑니다)
    # 테스트용 데이터 (실제 실행 시 위 크롤링 로직 활성화)
    return pd.DataFrame([{"분류": "CPU", "상품명": "인텔 i5-9400", "매입가": 70000}])

# 4. 세션 상태 관리 (초기화 로직 포함)
if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
for i in range(6):
    if f"nm_{i}" not in st.session_state: st.session_state[f"nm_{i}"] = ""
    if f"pr_{i}" not in st.session_state: st.session_state[f"pr_{i}"] = 0

def add_to_calc(name, price):
    idx = st.session_state['target_idx']
    st.session_state[f"nm_{idx}"] = name
    st.session_state[f"pr_{idx}"] = price
    st.session_state['target_idx'] = (idx + 1) % 6

def reset_calculator():
    for i in range(6):
        st.session_state[f"nm_{i}"], st.session_state[f"pr_{i}"] = "", 0
    st.session_state['target_idx'] = 0

# --- UI 레이아웃 시작 ---

# ★ 변경 1: 타이틀 바로 아래에 '시세 DB 갱신' 배치 ★
st.title("💻 DODO 매입 조회")
if st.button("🔄 시세 DB 갱신", type="primary"): 
    st.cache_data.clear()
    st.rerun()

st.divider()

# ★ 변경 2: 검색 영역에서 버튼 제거 (DB 버튼을 위로 옮겼기 때문) ★
df = fetch_data()
c_select, c_search = st.columns([1, 2.5])
with c_select:
    cat = st.selectbox("분류", ["전체보기"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with c_search:
    query = st.text_input("검색", placeholder="상품명 입력", label_visibility="collapsed")

# 리스트 필터링 및 출력
f_df = df.copy()
if cat != "전체보기": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

st.write(f"조회 결과: {len(f_df)}건")
st.markdown('<div class="table-header"><div style="flex:1.2;">분류</div><div style="flex:4;">상품명</div><div style="flex:2.2;">금액</div><div style="flex:1;">담기</div></div>', unsafe_allow_html=True)

with st.container(height=380):
    for i, row in f_df.iterrows():
        cols = st.columns([1.2, 4, 2.2, 1])
        cols[0].write(row['분류'])
        cols[1].write(row['상품명'])
        cols[2].markdown(f"<p class='price-text'>{row['매입가']:,}</p>", unsafe_allow_html=True)
        cols[3].button("➕", key=f"add_{i}", on_click=add_to_calc, args=(row['상품명'], row['매입가']))

st.divider()

# 하단 계산기 영역
st.subheader("🛒 매입 계산기")
st.radio("입력 항목 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

total_price = 0
cal_cols = st.columns(2)
for i in range(6):
    with cal_cols[i % 2]:
        st.write(f"**{labels[i]}**")
        st.text_input(f"m_name_{i}", key=f"nm_{i}", label_visibility="collapsed")
        st.number_input(f"m_price_{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total_price += st.session_state[f"pr_{i}"]

st.markdown(f"### 💰 최종 합계: :red[{total_price:,}원]")

# ★ 변경 3: 메뉴명을 '계산기 초기화'로 변경 ★
btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 2.5])
with btn_col1:
    st.button("🗑️ 계산기 초기화", use_container_width=True, on_click=reset_calculator)
with btn_col2:
    save_df = pd.DataFrame({"항목": labels, "모델": [st.session_state[f"nm_{k}"] for k in range(6)], "금액": [st.session_state[f"pr_{k}"] for k in range(6)]})
    st.download_button("💾 CSV 저장", data=save_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo_price.csv", use_container_width=True)

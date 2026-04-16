import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입", layout="wide")

# --- CSS: 버튼 크기 및 깨짐 방지 ---
st.markdown("""
    <style>
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stButton > button {
        height: 45px !important; min-height: 45px !important;
    }
    .stButton > button {
        min-width: 150px !important; /* 버튼 글자 깨짐 방지 */
        font-weight: 600 !important;
    }
    .price-text { color: red; font-weight: bold; text-align: center; font-size: 16px; margin: 0; }
    .table-header {
        display: flex; background-color: #4A90E2; color: white; padding: 12px 0;
        font-weight: bold; border-radius: 4px; text-align: center; margin-bottom: 8px;
    }
    /* 담기 버튼 둥글게 */
    div.stButton > button[key^="add_"] {
        width: 40px !important; min-width: 40px !important; height: 40px !important; border-radius: 50% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 수집 함수 (캐싱 적용) ---
@st.cache_data(ttl=3600)
def fetch_data():
    URLS = ["https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4220"] # 예시 URL
    # ... (기존 URL 리스트 동일)
    all_rows = []
    # 데이터 수집 로직 (기존과 동일)
    return pd.DataFrame([{"분류": "CPU", "상품명": "테스트 상품", "매입가": 10000}]) # 실제 운영시 위 로직 사용

# --- 세션 상태 관리 ---
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0
for i in range(6):
    if f"nm_{i}" not in st.session_state: st.session_state[f"nm_{i}"] = ""
    if f"pr_{i}" not in st.session_state: st.session_state[f"pr_{i}"] = 0

def add_to_calc_callback(name, price):
    idx = st.session_state['target_idx']
    st.session_state[f"nm_{idx}"] = name
    st.session_state[f"pr_{idx}"] = price
    st.session_state['target_idx'] = (idx + 1) % 6

def reset_calc():
    for i in range(6):
        st.session_state[f"nm_{i}"], st.session_state[f"pr_{i}"] = "", 0
    st.session_state['target_idx'] = 0

# --- 화면 레이아웃 시작 ---

# 1. 타이틀
st.title("💻 DODO 매입 조회")

# 2. [수정] 시세 DB 갱신 버튼 위치 (타이틀 바로 아래 단독 배치)
if st.button("🔄 시세 DB 갱신", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.write("---") # 구분선 추가

# 3. 검색 필터 (버튼 없이 깔끔하게 배치)
df = fetch_data()
col_cat, col_search = st.columns([1, 2])
with col_cat:
    cat = st.selectbox("분류", ["전체보기"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with col_search:
    query = st.text_input("검색", placeholder="상품명 입력", label_visibility="collapsed")

# 데이터 필터링 및 리스트 출력
f_df = df.copy()
if cat != "전체보기": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

st.write(f"조회 결과: {len(f_df)}건")
st.markdown('<div class="table-header"><div style="flex:1.2;">분류</div><div style="flex:4;">상품명</div><div style="flex:2.2;">금액</div><div style="flex:1;">담기</div></div>', unsafe_allow_html=True)

with st.container(height=350):
    for i, row in f_df.iterrows():
        c1, c2, c3, c4 = st.columns([1.2, 4, 2.2, 1])
        c1.write(row['분류'])
        c2.write(row['상품명'])
        c3.markdown(f"<p class='price-text'>{row['매입가']:,}</p>", unsafe_allow_html=True)
        c4.button("➕", key=f"add_{i}", on_click=add_to_calc_callback, args=(row['상품명'], row['매입가']))

st.divider()

# --- 하단 계산기 영역 ---
st.subheader("🛒 매입 계산기")
st.radio("입력 항목 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

total = 0
cal_cols = st.columns(2)
for i in range(6):
    with cal_cols[i % 2]:
        st.write(f"**{labels[i]}**")
        st.text_input(f"mod_{i}", key=f"nm_{i}", label_visibility="collapsed")
        st.number_input(f"val_{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total += st.session_state[f"pr_{i}"]

st.markdown(f"### 💰 최종 합계: :red[{total:,}원]")

# 4. [수정] 메뉴명 변경: '계산기 초기화'
btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 2])
with btn_col1:
    st.button("🗑️ 계산기 초기화", use_container_width=True, on_click=reset_calc) # 메뉴명 변경 확인
with btn_col2:
    res_df = pd.DataFrame({"항목": labels, "모델": [st.session_state[f"nm_{j}"] for j in range(6)], "금액": [st.session_state[f"pr_{j}"] for j in range(6)]})
    st.download_button("💾 CSV 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo.csv", use_container_width=True)

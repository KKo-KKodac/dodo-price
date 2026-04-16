import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 1. 페이지 기본 설정
st.set_page_config(page_title="컴퓨터매입계산기", layout="wide")

# 2. CSS 스타일 (버튼 크기 고정 및 정렬)
st.markdown("""
    <style>
    /* 입력창 및 일반 버튼 높이 조절 */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stButton > button {
        height: 45px !important; min-height: 45px !important;
    }
    /* 하단 초기화 버튼 글자 안 잘리도록 너비 확보 */
    .stButton > button {
        min-width: 160px !important;
        font-weight: 600 !important;
    }
    /* 리스트 내 ➕ 버튼 (동그랗게) */
    div.stButton > button[key^="add_"] {
        width: 40px !important; min-width: 40px !important; height: 40px !important; 
        border-radius: 50% !important; padding: 0 !important;
    }
    .price-text { color: red; font-weight: bold; text-align: center; font-size: 16px; margin: 0; }
    .table-header {
        display: flex; background-color: #4A90E2; color: white; padding: 12px 0;
        font-weight: bold; border-radius: 4px; text-align: center; margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 수집 함수 (기존 로직 유지)
@st.cache_data(ttl=3600)
def fetch_data():
    # 실제 운영 시에는 여기에 기존의 모든 URL 리스트를 넣으시면 됩니다.
    # 예시 데이터 구조
    data = [
        {"분류": "CPU", "상품명": "인텔 i5-9400 (커피레이크)", "매입가": 70000},
        {"분류": "메인보드", "상품명": "H310M", "매입가": 15000},
        {"분류": "메모리", "상품명": "DDR4 8G", "매입가": 12000}
    ]
    return pd.DataFrame(data)

# 4. 세션 상태 초기화
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0
for i in range(6):
    if f"nm_{i}" not in st.session_state: st.session_state[f"nm_{i}"] = ""
    if f"pr_{i}" not in st.session_state: st.session_state[f"pr_{i}"] = 0

def add_item(name, price):
    idx = st.session_state['target_idx']
    st.session_state[f"nm_{idx}"] = name
    st.session_state[f"pr_{idx}"] = price
    st.session_state['target_idx'] = (idx + 1) % 6

def clear_all():
    for i in range(6):
        st.session_state[f"nm_{i}"], st.session_state[f"pr_{i}"] = "", 0
    st.session_state['target_idx'] = 0

# --- 화면 레이아웃 구성 ---

# 변경 1: 타이틀 수정
st.title("💻 컴퓨터매입계산기")

# 변경 2: 시세 DB 갱신 버튼을 타이틀 바로 아래 단독 배치
if st.button("🔄 시세 DB 갱신", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.write("") # 간격 조절

# 검색 및 리스트 영역
df = fetch_data()
col1, col2 = st.columns([1, 2.5])
with col1:
    cat = st.selectbox("분류", ["전체보기"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with col2:
    query = st.text_input("검색", placeholder="상품명 입력", label_visibility="collapsed")

f_df = df.copy()
if cat != "전체보기": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

st.markdown('<div class="table-header"><div style="flex:1.2;">분류</div><div style="flex:4;">상품명</div><div style="flex:2.2;">금액</div><div style="flex:1;">담기</div></div>', unsafe_allow_html=True)
with st.container(height=350):
    for i, row in f_df.iterrows():
        c = st.columns([1.2, 4, 2.2, 1])
        c[0].write(row['분류'])
        c[1].write(row['상품명'])
        c[2].markdown(f"<p class='price-text'>{row['매입가']:,}</p>", unsafe_allow_html=True)
        c[3].button("➕", key=f"add_{i}", on_click=add_item, args=(row['상품명'], row['매입가']))

st.divider()

# 계산기 영역
st.subheader("🛒 매입 계산 리스트")
st.radio("입력 순서 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

total = 0
cal_col = st.columns(2)
for i in range(6):
    with cal_col[i % 2]:
        st.write(f"**{labels[i]}**")
        st.text_input(f"name_{i}", key=f"nm_{i}", label_visibility="collapsed")
        st.number_input(f"price_{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total += st.session_state[f"pr_{i}"]

st.markdown(f"### 💰 최종 합계: :red[{total:,}원]")

# 변경 3: 하단 버튼 명칭 수정
b1, b2, _ = st.columns([1.5, 1.5, 2.5])
with b1:
    # 버튼명을 명확히 '계산기 초기화'로 설정
    st.button("🗑️ 계산기 초기화", use_container_width=True, on_click=clear_all)
with b2:
    save_data = pd.DataFrame({"항목": labels, "모델": [st.session_state[f"nm_{k}"] for k in range(6)], "금액": [st.session_state[f"pr_{k}"] for k in range(6)]})
    st.download_button("💾 CSV 저장", data=save_data.to_csv(index=False).encode('utf-8-sig'), file_name="pc_purchase.csv", use_container_width=True)

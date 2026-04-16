import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정: 모바일 대응을 위해 레이아웃 고정
st.set_page_config(page_title="DODO 매입", layout="wide", initial_sidebar_state="collapsed")

# --- CSS: PC & 모바일 반응형 통합 디자인 ---
st.markdown("""
    <style>
    /* 전체 폰트 및 배경 최적화 */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Pretendard', sans-serif;
    }
    
    /* 테이블 헤더: 모바일에서 텍스트 크기 축소 */
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 8px 0; font-weight: bold; border-radius: 4px; text-align: center;
        margin-bottom: 5px; font-size: clamp(10px, 3vw, 14px);
    }
    .header-item { flex: 1; border-right: 1px solid rgba(255,255,255,0.3); }
    .header-item:last-child { border-right: none; }
    
    /* 모바일에서 컬럼이 밑으로 떨어지는 것 방지 (가로 유지) */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.1rem !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    [data-testid="column"] {
        min-width: 0px !important;
        flex: 1 !important;
    }

    /* 금액 텍스트 정렬 및 모바일 크기 */
    .price-text { 
        color: red; font-weight: bold; margin: 0; width: 100%; 
        text-align: center; font-size: clamp(10px, 3.5vw, 15px); 
    }

    /* 상품명 텍스트 말줄임 또는 크기 조절 */
    .item-name {
        font-size: clamp(10px, 3vw, 14px);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* 입력창 간격 축소 */
    .stTextInput, .stNumberInput { margin-bottom: -10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 수집 (캐시 유지) ---
@st.cache_data(ttl=3600)
def fetch_data():
    URLS = ["https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4220", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=967", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4221", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4083", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=31", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=993", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=1684", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3682", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3838", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3918", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=25", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4020", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4089", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4137", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4144", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3866", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=4141", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3608", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=7", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3784", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3775", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3768", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3808", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4075", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4145", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3901", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3902", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4085", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4146", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4218", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3701", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3932", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4021", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4090", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4029", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4139"]
    all_rows = []
    for url in URLS:
        try:
            res = requests.get(url, timeout=5)
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.select("tr")
            for row in rows:
                c = row.find("td", class_="price_table_ctgry_nm")
                n = row.find("td", class_="price_table_prduct_nm")
                p = row.find("td", class_="price_table_prduct_pc")
                if c and n and p:
                    price_num = int(re.sub(r'[^0-9]', '', p.text))
                    if price_num > 0:
                        all_rows.append({"분류": c.text.strip(), "상품명": n.text.strip(), "매입가": price_num})
        except: continue
    return pd.DataFrame(all_rows)

# --- 세션 상태 ---
labels = ["CPU", "MB", "RAM", "SSD", "HDD", "VGA"] # 모바일 대응 짧은 이름

if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0
for i in range(6):
    if f"nm_{i}" not in st.session_state: st.session_state[f"nm_{i}"] = ""
    if f"pr_{i}" not in st.session_state: st.session_state[f"pr_{i}"] = 0

# --- 콜백 함수 ---
def add_to_calc(name, price):
    t_idx = st.session_state['target_idx']
    st.session_state[f"nm_{t_idx}"] = name
    st.session_state[f"pr_{t_idx}"] = price
    st.session_state['target_idx'] = (t_idx + 1) % 6

def reset_calc():
    st.session_state['target_idx'] = 0
    for i in range(6):
        st.session_state[f"nm_{i}"] = ""
        st.session_state[f"pr_{i}"] = 0

# --- UI 레이아웃 ---
df = fetch_data()
st.title("💻 DODO 매입")

# 검색 필터
sc1, sc2 = st.columns([1.2, 2.8])
with sc1: cat = st.selectbox("분류", ["전체"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with sc2: query = st.text_input("검색", placeholder="상품명 입력...", label_visibility="collapsed")

f_df = df.copy()
if cat != "전체": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

# 1. 헤더 (모바일 가로폭 유지)
st.markdown(f"**결과: {len(f_df)}건**")
st.markdown("""
    <div class="table-header">
        <div class="header-item" style="flex:1.2;">분류</div>
        <div class="header-item" style="flex:4;">상품명</div>
        <div class="header-item" style="flex:2.5;">금액</div>
        <div class="header-item" style="flex:1;">+</div>
    </div>
""", unsafe_allow_html=True)

# 2. 결과 리스트 (반응형 폰트 적용)
with st.container(height=350):
    for i, row in f_df.iterrows():
        cols = st.columns([1.2, 4, 2.5, 1])
        cols[0].markdown(f"<div style='text-align:center; color:gray; font-size:10px;'>{row['분류']}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div class='item-name'>{row['상품명']}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<p class='price-text'>{row['매입가']:,}원</p>", unsafe_allow_html=True)
        cols[3].button("➕", key=f"add_{i}", on_click=add_to_calc, args=(row['상품명'], row['매입가']))

st.divider()

# 3. 계산기 (모바일 대응 2열 레이아웃)
st.subheader("🛒 매입 계산기")

# 라디오 버튼 (타겟 선택)
st.radio("입력 항목 선택:", range(6), 
         format_func=lambda x: labels[x], 
         key="target_idx", horizontal=True)

total_sum = 0
cal_cols = st.columns(2)
for i in range(6):
    with cal_cols[i % 2]:
        st.caption(f"**{labels[i]}**")
        st.text_input(f"n{i}", key=f"nm_{i}", label_visibility="collapsed")
        p_in = st.number_input(f"p{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total_sum += p_in

st.markdown(f"### 💰 합계: <span style='color:red;'>{total_sum:,}원</span>", unsafe_allow_html=True)

# 4. 하단 버튼
b1, b2 = st.columns(2)
b1.button("🗑️ 초기화", use_container_width=True, on_click=reset_calc)

res_names = [st.session_state[f"nm_{i}"] for i in range(6)]
res_prices = [st.session_state[f"pr_{i}"] for i in range(6)]
res_df = pd.DataFrame({"항목": labels, "모델": res_names, "금액": res_prices})

b2.download_button("💾 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo.csv", use_container_width=True)

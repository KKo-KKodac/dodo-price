import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입", layout="wide")

# --- CSS: 아이폰 가독성 및 레이아웃 교정 ---
st.markdown("""
    <style>
    /* 1. 전체 여백 제거 (가장 중요) */
    .block-container { padding: 10px 10px !important; }
    
    /* 2. 분류/검색창 한 줄 배치 시 짤림 방지 */
    div[data-testid="stHorizontalBlock"] {
        gap: 5px !important; flex-wrap: nowrap !important;
    }
    
    /* 3. 테이블 헤더: 글자 크기 복구 (가독성) */
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 10px 0; font-weight: bold; border-radius: 4px; text-align: center;
        font-size: 13px; margin-bottom: 5px;
    }
    .header-item { flex: 1; border-right: 1px solid rgba(255,255,255,0.3); }
    .header-item:last-child { border-right: none; }
    
    /* 4. 결과 리스트 높이 및 폰트 조절 */
    .row-item { font-size: 13px !important; }
    .price-text { color: red; font-weight: bold; text-align: center; font-size: 12px; }
    
    /* 5. 버튼 크기 최적화 */
    .stButton button { padding: 2px 10px !important; height: auto !important; }

    /* 6. 모바일에서 입력창이 커보이도록 조정 */
    input { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 수집 ---
@st.cache_data(ttl=3600)
def fetch_data():
    URLS = ["https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4220", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=967", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4221", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4083", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=31", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=993", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=1684", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3682", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3838", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3918", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=25", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4020", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4089", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4137", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4144", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3866", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=4141", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3608", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=7", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3784", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3775", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3768", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3808", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4075", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4145", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3901", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3902", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4085", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4146", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4218", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3701", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3932", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4021", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4090", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4029", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4139"]
    all_rows = []
    for url in URLS:
        try:
            res = requests.get(url, timeout=5); res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser"); rows = soup.select("tr")
            for row in rows:
                c, n, p = row.find("td", class_="price_table_ctgry_nm"), row.find("td", class_="price_table_prduct_nm"), row.find("td", class_="price_table_prduct_pc")
                if c and n and p:
                    price_num = int(re.sub(r'[^0-9]', '', p.text))
                    if price_num > 0: all_rows.append({"분류": c.text.strip(), "상품명": n.text.strip(), "매입가": price_num})
        except: continue
    return pd.DataFrame(all_rows)

# --- 세션 관리 ---
labels = ["CPU", "MB", "RAM", "SSD", "HDD", "VGA"]
if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0
for i in range(6):
    if f"nm_{i}" not in st.session_state: st.session_state[f"nm_{i}"] = ""
    if f"pr_{i}" not in st.session_state: st.session_state[f"pr_{i}"] = 0

def add_to_calc(name, price):
    t_idx = st.session_state['target_idx']
    st.session_state[f"nm_{t_idx}"] = name
    st.session_state[f"pr_{t_idx}"] = price
    st.session_state['target_idx'] = (t_idx + 1) % 6

def reset_calc():
    st.session_state['target_idx'] = 0
    for i in range(6): st.session_state[f"nm_{i}"] = ""; st.session_state[f"pr_{i}"] = 0

# --- 앱 실행 ---
df = fetch_data()

# 분류/검색창 (가로 배치 최적화)
c1, c2 = st.columns([1, 1.2])
with c1: cat = st.selectbox("분류", ["전체"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with c2: query = st.text_input("검색", placeholder="상품명 입력", label_visibility="collapsed")

f_df = df.copy()
if cat != "전체": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

# 결과 테이블 (글자 크기 키움)
st.markdown("""<div class="table-header"><div class="header-item" style="flex:1;">분류</div><div class="header-item" style="flex:3;">상품명</div><div class="header-item" style="flex:1.8;">매입가</div><div class="header-item" style="flex:0.7;">+</div></div>""", unsafe_allow_html=True)

with st.container(height=300):
    for i, row in f_df.iterrows():
        cols = st.columns([1, 3, 1.8, 0.7])
        cols[0].markdown(f"<div style='text-align:center; font-size:11px; color:#666;'>{row['분류']}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div style='font-size:12px; line-height:1.2;'>{row['상품명']}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<p class='price-text'>{row['매입가']:,}원</p>", unsafe_allow_html=True)
        cols[3].button("➕", key=f"a_{i}", on_click=add_to_calc, args=(row['상품명'], row['매입가']))

st.divider()

# 계산기 영역
st.radio("입력 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

total_sum = 0
cal_cols = st.columns(2)
for i in range(6):
    with cal_cols[i % 2]:
        st.write(f"**{labels[i]}**")
        st.text_input(f"n{i}", key=f"nm_{i}", label_visibility="collapsed")
        p_in = st.number_input(f"p{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total_sum += p_in

st.markdown(f"### 💰 합계: :red[{total_sum:,}원]")
b1, b2 = st.columns(2)
b1.button("🗑️ 초기화", use_container_width=True, on_click=reset_calc)
res_df = pd.DataFrame({"항목": labels, "모델": [st.session_state[f"nm_{i}"] for i in range(6)], "금액": [st.session_state[f"pr_{i}"] for i in range(6)]})
b2.download_button("💾 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo.csv", use_container_width=True)

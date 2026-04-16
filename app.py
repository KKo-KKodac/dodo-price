import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정: 뷰포트 조절 및 모바일 최적화
st.set_page_config(page_title="DODO 매입", layout="wide")

# --- CSS: 아이폰 전용 초밀착 레이아웃 ---
st.markdown("""
    <style>
    /* 1. 모바일 전체 여백 최소화 */
    .block-container { padding: 10px 15px !important; }
    
    /* 2. 분류/검색창 한 줄 정렬 */
    div[data-testid="stHorizontalBlock"] {
        gap: 5px !important; flex-wrap: nowrap !important;
    }
    
    /* 3. 테이블 헤더 & 리스트 폰트 최적화 */
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 5px 0; font-weight: bold; border-radius: 4px; text-align: center;
        font-size: 11px; margin-bottom: 3px;
    }
    .header-item { flex: 1; border-right: 1px solid rgba(255,255,255,0.3); }
    
    /* 4. 리스트 텍스트 줄바꿈 방지 및 크기 조절 */
    .row-container { font-size: 11px; align-items: center !important; height: 35px; border-bottom: 1px solid #eee; }
    .price-text { color: red; font-weight: bold; text-align: center; font-size: 11px; margin: 0; }
    
    /* 5. 매입 계산기 콤팩트화 (폰트 및 간격 줄임) */
    .stCaption { font-size: 10px !important; margin-bottom: -15px !important; }
    div[data-testid="stNumberInput"], div[data-testid="stTextInput"] { margin-bottom: -10px !important; }
    
    /* 6. 라디오 버튼(항목 선택) 크기 축소 */
    div[data-testid="stMarkdownContainer"] p { font-size: 12px !important; }
    
    /* 아이폰 크롬 특유의 하단 여백 대응 */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 수집 (생략 없이 유지) ---
@st.cache_data(ttl=3600)
def fetch_data():
    URLS = ["https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4220", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=967", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4221", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4083", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=31", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=993", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=1684", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3682", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3838", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3918", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=25", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4020", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4089", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4137", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4144", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3866", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=4141", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3608", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=7", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3784", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3775", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3768", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3808", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4075", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4145", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3901", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3902", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4085", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4146", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4218", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3701", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3932", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4021", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4090", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4029", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4139"]
    all_rows = []
    for url in URLS:
        try:
            res = requests.get(url, timeout=5)
            res.encoding = "utf-8"; soup = BeautifulSoup(res.text, "html.parser")
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
labels = ["CPU", "MB", "RAM", "SSD", "HDD", "VGA"]
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
        st.session_state[f"nm_{i}"] = ""; st.session_state[f"pr_{i}"] = 0

# --- 메인 화면 ---
df = fetch_data()

# 분류와 검색을 한 줄로 배치 (아이폰 가로폭 최적화)
c1, c2 = st.columns([1, 1.5])
with c1: cat = st.selectbox("분류", ["전체"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with c2: query = st.text_input("검색", placeholder="상품명...", label_visibility="collapsed")

f_df = df.copy()
if cat != "전체": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

# 조회 결과 테이블 (높이를 줄여서 계산기가 한 화면에 들어오도록 조정)
st.markdown("""<div class="table-header"><div class="header-item" style="flex:1;">분류</div><div class="header-item" style="flex:2.8;">상품명</div><div class="header-item" style="flex:1.8;">매입가</div><div class="header-item" style="flex:0.7;">+</div></div>""", unsafe_allow_html=True)

with st.container(height=220): # 높이를 220으로 축소
    for i, row in f_df.iterrows():
        cols = st.columns([1, 2.8, 1.8, 0.7])
        cols[0].markdown(f"<div style='text-align:center; font-size:9px; color:gray;'>{row['분류']}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div style='font-size:10px; overflow:hidden;'>{row['상품명']}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<p class='price-text'>{row['매입가']:,}원</p>", unsafe_allow_html=True)
        cols[3].button("➕", key=f"a_{i}", on_click=add_to_calc, args=(row['상품명'], row['매입가']))

st.markdown("---")

# 매입 계산기 (더 촘촘하게 배치)
st.radio("입력 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

total_sum = 0
cal_cols = st.columns(2)
for i in range(6):
    with cal_cols[i % 2]:
        st.caption(f"**{labels[i]}**")
        st.text_input(f"n{i}", key=f"nm_{i}", label_visibility="collapsed")
        p_in = st.number_input(f"p{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total_sum += p_in

# 합계 및 버튼
st.markdown(f"**합계: :red[{total_sum:,}원]**")
b1, b2 = st.columns(2)
b1.button("🗑️ 초기화", use_container_width=True, on_click=reset_calc)
res_df = pd.DataFrame({"항목": labels, "모델": [st.session_state[f"nm_{i}"] for i in range(6)], "금액": [st.session_state[f"pr_{i}"] for i in range(6)]})
b2.download_button("💾 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo.csv", use_container_width=True)

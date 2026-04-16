import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입", layout="wide")

# --- CSS: 입력창 높이 통일(사진1) 및 버튼 중앙 정렬(사진2) ---
st.markdown("""
    <style>
    /* 1. 분류/검색창 높이 통일 및 사이즈 축소 (검색창 기준) */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        height: 36px !important;
        min-height: 36px !important;
        display: flex; align-items: center; /* 텍스트 수직 중앙 */
    }
    
    /* 2. 테이블 헤더 및 구분선 | */
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 8px 0; font-weight: bold; border-radius: 4px; text-align: center;
        margin-bottom: 5px; font-size: 14px;
    }
    .header-item { flex: 1; border-right: 1px solid rgba(255,255,255,0.3); }
    .header-item:last-child { border-right: none; }
    
    /* 3. 데이터 줄 정렬: + 버튼을 정중앙으로 (가장 중요) */
    [data-testid="column"] { min-width: 0px !important; flex: 1 !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.2rem !important; flex-wrap: nowrap !important; }
    
    /* + 버튼 컬럼(마지막 컬럼)을 정중앙 배치 */
    div[data-testid="column"]:last-child {
        display: flex; justify-content: center !important; align-items: center !important;
    }
    .stButton>button { width: 30px !important; height: 30px !important; padding: 0 !important; }

    /* 4. 금액 강조 */
    .price-text { color: red; font-weight: bold; margin: 0; width: 100%; text-align: center; font-size: 14px; }
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

# --- 세션 상태 ---
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
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
st.title("💻 DODO 매입 조회")

# 상단 검색창 슬림 배치 (사진1 문제 해결: 높이 통일 및 사이즈 줄임)
sc1, sc2, _ = st.columns([1, 1.5, 1]) # 여백 컬럼 활용으로 슬림화
with sc1: cat = st.selectbox("분류", ["전체보기"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with sc2: query = st.text_input("검색", placeholder="상품명 입력", label_visibility="collapsed")

f_df = df.copy()
if cat != "전체보기": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

# 결과 테이블
st.write(f"조회 결과: {len(f_df)}건")
# 헤더 구분선 | 추가
st.markdown("""<div class="table-header"><div class="header-item" style="flex:1.2;">분류</div><div class="header-item" style="flex:4;">상품명</div><div class="header-item" style="flex:2.2;">매입가</div><div class="header-item" style="flex:0.8; border-right:none;">담기</div></div>""", unsafe_allow_html=True)

# 리스트 (사진2 문제 해결: + 버튼 중앙 정렬)
with st.container(height=380):
    for i, row in f_df.iterrows():
        # CSS에서 마지막 컬럼을 중앙 정렬 처리함
        cols = st.columns([1.2, 4, 2.2, 0.8])
        cols[0].markdown(f"<div style='text-align:center; color:gray; font-size:13px;'>{row['분류']}</div>", unsafe_allow_html=True)
        cols[1].write(row['상품명'])
        cols[2].markdown(f"<p class='price-text'>{row['매입가']:,}원</p>", unsafe_allow_html=True)
        # button 위젯 자체가 key=f"add_{i}"로 구분됨
        cols[3].button("➕", key=f"add_{i}", on_click=add_to_calc, args=(row['상품명'], row['매입가']))

st.divider()

# 계산기 영역
st.subheader("🛒 매입 계산기")
st.radio("항목 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

total_sum = 0
cal_cols = st.columns(2)
for i in range(6):
    with cal_cols[i % 2]:
        st.write(f"**{labels[i]}**")
        st.text_input(f"n{i}", key=f"nm_{i}", label_visibility="collapsed")
        p_in = st.number_input(f"p{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total_sum += p_in

st.markdown(f"### 💰 최종 합계: :red[{total_sum:,}원]")
b1, b2 = st.columns(2)
b1.button("🗑️ 전체 초기화", use_container_width=True, on_click=reset_calc)
res_df = pd.DataFrame({"항목": labels, "모델": [st.session_state[f"nm_{i}"] for i in range(6)], "금액": [st.session_state[f"pr_{i}"] for i in range(6)]})
b2.download_button("💾 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo.csv", use_container_width=True)

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입", layout="wide")

# --- CSS 최적화 ---
st.markdown("""
    <style>
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stButton > button {
        height: 45px !important; min-height: 45px !important;
    }
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 12px 0; font-weight: bold; border-radius: 4px; text-align: center;
        margin-bottom: 8px; font-size: 15px;
    }
    .header-item { flex: 1; border-right: 1px solid rgba(255,255,255,0.3); }
    .header-item:last-child { border-right: none; }
    
    [data-testid="column"]:nth-child(3), [data-testid="column"]:nth-child(4) {
        display: flex !important; justify-content: center !important; align-items: center !important;
    }
    
    .stButton > button { min-width: 130px !important; border-radius: 8px !important; font-weight: 600 !important; }
    div.stButton > button[key^="add_"] { width: 40px !important; min-width: 40px !important; height: 40px !important; border-radius: 50% !important; padding: 0 !important; }
    .price-text { color: red; font-weight: bold; margin: 0; width: 100%; text-align: center; font-size: 16px; }
    .block-container { padding-top: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 로딩 최적화 (ttl 유지) ---
@st.cache_data(ttl=3600)
def fetch_data():
    URLS = [
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4220",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=967",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4221",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4083",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=31",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=993",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=1684",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3682",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3838",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3918",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=25",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4020",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4089",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4137",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4144",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3866",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=4141",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3608",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=7",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3784",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3775",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3768",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3808",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4075",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4145",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3901",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3902",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4085",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4146",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4218",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3701",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3932",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4021",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4090",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4029",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4139"
    ]
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

# --- 세션 관리 (불필요한 rerun 억제용) ---
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0
for i in range(6):
    if f"nm_{i}" not in st.session_state: st.session_state[f"nm_{i}"] = ""
    if f"pr_{i}" not in st.session_state: st.session_state[f"pr_{i}"] = 0

def add_to_calc_callback(name, price):
    t_idx = st.session_state['target_idx']
    st.session_state[f"nm_{t_idx}"] = name
    st.session_state[f"pr_{t_idx}"] = price
    st.session_state['target_idx'] = (t_idx + 1) % 6

def reset_calc():
    for i in range(6):
        st.session_state[f"nm_{i}"], st.session_state[f"pr_{i}"] = "", 0
    st.session_state['target_idx'] = 0

# --- 화면 구성 ---
df = fetch_data()
st.title("💻 DODO 매입 조회")

if st.button("🔄 시세 DB 갱신", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.write("") 

# 필터링 로직 최적화 (검색창 입력 시에만 동작)
m1, m2 = st.columns([1, 2.5])
with m1: cat = st.selectbox("분류", ["전체보기"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with m2: query = st.text_input("검색", placeholder="상품명 입력", label_visibility="collapsed")

# 계산 최적화: 필터링 결과를 미리 변수에 할당
f_df = df
if cat != "전체보기": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

st.write(f"조회 결과: {len(f_df)}건")
st.markdown("""<div class="table-header"><div class="header-item" style="flex:1.2;">분류</div><div class="header-item" style="flex:4;">상품명</div><div class="header-item" style="flex:2.2;">금액</div><div class="header-item" style="flex:1.0; border-right:none;">담기</div></div>""", unsafe_allow_html=True)

# 리스트 렌더링 최적화
with st.container(height=380):
    for i, row in f_df.iterrows():
        cols = st.columns([1.2, 4, 2.2, 1.0])
        cols[0].markdown(f"<div style='text-align:center; color:gray; font-size:12px;'>{row['분류']}</div>", unsafe_allow_html=True)
        cols[1].write(row['상품명'])
        cols[2].markdown(f"<p class='price-text'>{row['매입가']:,}</p>", unsafe_allow_html=True)
        # 중요: args 전달 시 데이터 복사본 전달하여 속도 향상
        cols[3].button("➕", key=f"add_{i}", on_click=add_to_calc_callback, args=(row['상품명'], row['매입가']))

st.divider()

# --- 계산기 영역 (빠른 반응을 위해 key 직접 동기화) ---
st.subheader("🛒 매입 계산기")
st.radio("입력할 항목 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

total_sum = 0
cal_cols = st.columns(2)
for i in range(6):
    with cal_cols[i % 2]:
        st.write(f"**{labels[i]}**")
        # key를 통한 직접 업데이트는 반응 속도가 가장 빠름
        st.text_input(f"m_{i}", key=f"nm_{i}", label_visibility="collapsed")
        st.number_input(f"p_{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total_sum += st.session_state[f"pr_{i}"]

st.markdown(f"### 💰 최종 합계: :red[{total_sum:,}원]")

b_col1, b_col2, b_spacer = st.columns([1.5, 1.5, 2.5])
with b_col1:
    st.button("🗑️ 계산기 초기화", use_container_width=True, on_click=reset_calc)
with b_col2:
    res_df = pd.DataFrame({"항목": labels, "모델": [st.session_state[f"nm_{i}"] for i in range(6)], "금액": [st.session_state[f"pr_{i}"] for i in range(6)]})
    st.download_button("💾 CSV 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo_price.csv", use_container_width=True)

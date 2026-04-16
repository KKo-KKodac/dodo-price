import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입", layout="wide")

# --- CSS: 모든 디자인 문제 해결 (높이, 중앙정렬, 버튼 깨짐) ---
st.markdown("""
    <style>
    /* 1. 상단 입력창 높이 검색창에 맞춰 통일 */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        height: 42px !important;
        min-height: 42px !important;
    }

    /* 2. 테이블 헤더 스타일 및 구분선 */
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 10px 0; font-weight: bold; border-radius: 4px; text-align: center;
        margin-bottom: 8px; font-size: 14px;
    }
    .header-item { flex: 1; border-right: 1px solid rgba(255,255,255,0.3); }
    .header-item:last-child { border-right: none; }
    
    /* 3. 담기 버튼 및 리스트 데이터 중앙 정렬 */
    [data-testid="column"]:nth-child(3), [data-testid="column"]:nth-child(4) {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    /* 4. 초기화 버튼 글자 깨짐 방지 */
    .stButton > button {
        min-width: 110px !important;
        border-radius: 8px !important;
    }
    
    /* 리스트 내 ➕ 버튼 전용 크기 */
    div.stButton > button[key^="add_"] {
        width: 35px !important;
        min-width: 35px !important;
        height: 35px !important;
        padding: 0 !important;
    }

    .price-text { color: red; font-weight: bold; margin: 0; width: 100%; text-align: center; font-size: 15px; }
    .block-container { padding-top: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 수집 함수 (캐시 적용) ---
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

# --- 세션 초기화 ---
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0
for i in range(6):
    if f"nm_{i}" not in st.session_state: st.session_state[f"nm_{i}"] = ""
    if f"pr_{i}" not in st.session_state: st.session_state[f"pr_{i}"] = 0

# --- 함수: 담기 버튼 클릭 시 세션에 즉시 반영 ---
def add_to_calc_callback(name, price):
    t_idx = st.session_state['target_idx']
    # 입력 대상인 항목에 데이터 강제 주입
    st.session_state[f"nm_{t_idx}"] = name
    st.session_state[f"pr_{t_idx}"] = price
    # 다음 항목으로 자동 이동
    st.session_state['target_idx'] = (t_idx + 1) % 6

def reset_calc():
    for i in range(6):
        st.session_state[f"nm_{i}"] = ""
        st.session_state[f"pr_{i}"] = 0
    st.session_state['target_idx'] = 0

# --- 화면 구성 ---
df = fetch_data()

col_title, col_db_btn = st.columns([3, 1])
with col_title:
    st.title("💻 DODO 매입 조회")
with col_db_btn:
    # DB 새로고침 버튼 (캐시 삭제)
    if st.button("🔄 시세 DB 가져오기", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 검색 영역
sc1, sc2, _ = st.columns([1, 1.5, 1]) 
with sc1: cat = st.selectbox("분류", ["전체보기"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with sc2: query = st.text_input("검색", placeholder="상품명 입력", label_visibility="collapsed")

f_df = df.copy()
if cat != "전체보기": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

st.write(f"조회 결과: {len(f_df)}건")
st.markdown("""<div class="table-header"><div class="header-item" style="flex:1.2;">분류</div><div class="header-item" style="flex:4;">상품명</div><div class="header-item" style="flex:2.2;">금액</div><div class="header-item" style="flex:1.0; border-right:none;">담기</div></div>""", unsafe_allow_html=True)

# 리스트 출력
with st.container(height=350):
    for i, row in f_df.iterrows():
        cols = st.columns([1.2, 4, 2.2, 1.0])
        cols[0].markdown(f"<div style='text-align:center; color:gray; font-size:12px;'>{row['분류']}</div>", unsafe_allow_html=True)
        cols[1].write(row['상품명'])
        cols[2].markdown(f"<p class='price-text'>{row['매입가']:,}</p>", unsafe_allow_html=True)
        # 콜백 함수를 사용하여 데이터 유실 방지
        cols[3].button("➕", key=f"add_{i}", on_click=add_to_calc_callback, args=(row['상품명'], row['매ip가']))

st.divider()

# --- 계산기 영역 (핵심: on_change 없이 key만 활용) ---
st.subheader("🛒 매입 계산기")
st.radio("입력 대상 항목 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

total_sum = 0
cal_cols = st.columns(2)
for i in range(6):
    with cal_cols[i % 2]:
        st.write(f"**{labels[i]}**")
        # key를 세션 키와 완전히 일치시켜 직접 제어
        st.text_input(f"model_{i}", key=f"nm_{i}", label_visibility="collapsed")
        st.number_input(f"price_{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total_sum += st.session_state[f"pr_{i}"]

st.markdown(f"### 💰 최종 합계: :red[{total_sum:,}원]")

# 하단 버튼
b_col1, b_col2, b_spacer = st.columns([1.2, 1.2, 1.6])
with b_col1:
    st.button("🗑️ 전체 초기화", use_container_width=True, on_click=reset_calc)
with b_col2:
    res_df = pd.DataFrame({"항목": labels, "모델": [st.session_state[f"nm_{i}"] for i in range(6)], "금액": [st.session_state[f"pr_{i}"] for i in range(6)]})
    st.download_button("💾 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo_price.csv", use_container_width=True)

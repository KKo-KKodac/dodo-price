import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="꼬꼬닥'S 컴퓨터 매입계산기", layout="wide")

# 2. CSS 정밀 수정: 라인 일치 및 버튼 중앙 정렬
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
    .header-item:last-child { border-right: none; }

    .cell-center { 
        text-align: center; display: flex; align-items: center; justify-content: center; 
        height: 48px; border-right: 1px solid #f0f2f6; 
    }
    .cell-left { 
        display: flex; align-items: center; padding-left: 10px; 
        height: 48px; border-right: 1px solid #f0f2f6; 
    }
    .no-border { border-right: none !important; }

    div.stButton > button[key^="add_"] {
        width: 38px !important; min-width: 38px !important; height: 38px !important; 
        border-radius: 50% !important; margin: 0 auto !important; display: flex !important;
        align-items: center !important; justify-content: center !important;
    }
    
    .price-text { color: red; font-weight: bold; font-size: 16px; margin: 0; }
    .truncate-text { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; max-width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 3. 세션 상태 초기화
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0
for i in range(6):
    if f"nm_{i}" not in st.session_state: st.session_state[f"nm_{i}"] = ""
    if f"pr_{i}" not in st.session_state: st.session_state[f"pr_{i}"] = 0

# 4. 콜백 함수
def add_item_callback(name, price):
    idx = st.session_state['target_idx']
    st.session_state[f"nm_{idx}"] = name
    st.session_state[f"pr_{idx}"] = price
    st.session_state['target_idx'] = (idx + 1) % 6

def reset_callback():
    for i in range(6):
        st.session_state[f"nm_{i}"], st.session_state[f"pr_{i}"] = "", 0
    st.session_state['target_idx'] = 0

# 5. 데이터 수집
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
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4139",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=57",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3866",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=4141",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3608",
        "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=7"
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

# --- 메인 화면 ---
st.title("🐔꼬꼬닥'S 컴퓨터 매입계산기🖥️")

if st.button("🔄 시세 DB 갱신", type="primary"):
    st.cache_data.clear()
    st.rerun()

# 필독 문구 추가 (요청하신 위치)
st.info("💡 **필독!** 접속 후 **[시세DB갱신]** 버튼을 눌러 매입금액을 확인하세요.")

st.divider()

df = fetch_data()
c_cat, c_search = st.columns([1, 2.5])
with c_cat:
    cat = st.selectbox("분류", ["전체보기"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with c_search:
    query = st.text_input("검색", placeholder="상품명 입력", label_visibility="collapsed")

f_df = df.copy()
if cat != "전체보기": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

# 조회 테이블
st.markdown("""
    <div class="table-header">
        <div class="header-item" style="flex:1;">분류</div>
        <div class="header-item" style="flex:2.5;">상품명</div>
        <div class="header-item" style="flex:1.5;">금액</div>
        <div class="header-item" style="flex:0.8; border-right:none;">담기</div>
    </div>
    """, unsafe_allow_html=True)

with st.container(height=380):
    for i, row in f_df.iterrows():
        cols = st.columns([1, 2.5, 1.5, 0.8])
        cols[0].markdown(f'<div class="cell-center">{row["분류"]}</div>', unsafe_allow_html=True)
        cols[1].markdown(f'<div class="cell-left"><span class="truncate-text">{row["상품명"]}</span></div>', unsafe_allow_html=True)
        cols[2].markdown(f'<div class="cell-center price-text">{row["매입가"]:,}</div>', unsafe_allow_html=True)
        with cols[3]:
            st.button("➕", key=f"add_{i}", on_click=add_item_callback, args=(row['상품명'], row['매입가']))

st.divider()

# 하단 계산기 리스트
st.subheader("🛒 매입 계산 리스트")
st.radio("항목 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

total_sum = 0
for i in range(6):
    st.write(f"**{labels[i]}**")
    c1, c2 = st.columns([3, 1])
    with c1:
        st.text_input(f"모델명_{i}", key=f"nm_{i}", label_visibility="collapsed")
    with c2:
        st.number_input(f"금액_{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
    total_sum += st.session_state[f"pr_{i}"]

st.markdown(f"### 💰 최종 합계: :red[{total_sum:,}원]")

b_col1, b_col2, _ = st.columns([1.5, 1.5, 2.5])
with b_col1:
    st.button("🗑️ 전체 초기화", use_container_width=True, on_click=reset_callback)
with b_col2:
    res_df = pd.DataFrame({"항목": labels, "모델": [st.session_state[f"nm_{k}"] for k in range(6)], "금액": [st.session_state[f"pr_{k}"] for k in range(6)]})
    st.download_button("💾 CSV 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="purchase_list.csv", use_container_width=True)

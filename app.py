import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입가 조회", layout="wide")

# --- 모바일 최적화 및 스타일 설정 ---
st.markdown("""
    <style>
    /* 전체 폰트 크기 및 간격 조정 */
    html, body, [class*="css"] {
        font-size: 14px;
    }
    
    /* 리스트 영역 박스 스타일 */
    .item-row {
        display: flex;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #eee;
        gap: 5px;
    }
    
    /* 각 컬럼 너비 고정 (모바일 대응) */
    .col-cat { flex: 1.5; font-size: 11px; color: #666; overflow: hidden; }
    .col-name { flex: 4; font-weight: 500; font-size: 13px; }
    .col-price { flex: 2; text-align: right; font-weight: bold; color: #d32f2f; font-size: 13px; }
    .col-btn { flex: 1; text-align: center; }

    /* 버튼 스타일 조정 */
    div.stButton > button {
        padding: 2px 10px;
        height: auto;
        font-size: 12px;
    }
    
    /* 헤더 스타일 */
    .table-header {
        display: flex;
        background-color: #f0f2f6;
        padding: 10px 0;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
        gap: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 수집 함수 (기존과 동일) ---
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

@st.cache_data(show_spinner="시세 로딩 중...")
def fetch_data():
    all_rows = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in URLS:
        try:
            res = requests.get(url, headers=headers, timeout=10)
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

# --- 상태 관리 ---
if 'calc_data' not in st.session_state:
    st.session_state['calc_data'] = {i: {"name": "", "price": 0} for i in range(6)}
if 'next_idx' not in st.session_state:
    st.session_state['next_idx'] = 0

def add_to_calc(name, price):
    idx = st.session_state['next_idx']
    st.session_state['calc_data'][idx] = {"name": name, "price": price}
    st.session_state['next_idx'] = (idx + 1) % 6

# --- UI 레이아웃 ---
st.title("📂 DODO 매입가 조회")

if st.button("🔄 데이터 최신화"):
    st.cache_data.clear()
    st.session_state['df'] = fetch_data()

if 'df' in st.session_state:
    df = st.session_state['df']
    
    col_cat, col_src = st.columns([1, 1.5])
    with col_cat:
        selected_cat = st.selectbox("분류", ["전체보기"] + sorted(df["분류"].unique().tolist()))
    with col_src:
        search_query = st.text_input("검색", placeholder="상품명 입력...")

    filtered = df.copy()
    if selected_cat != "전체보기":
        filtered = filtered[filtered["분류"] == selected_cat]
    if search_query:
        filtered = filtered[filtered["상품명"].str.contains(search_query, case=False)]

    st.write(f"**조회 결과: {len(filtered)}건**")
    
    # --- 커스텀 HTML 테이블 헤더 ---
    st.markdown("""
        <div class="table-header">
            <div style="flex:1.5;">분류</div>
            <div style="flex:4; text-align:left; padding-left:10px;">상품명</div>
            <div style="flex:2; text-align:right;">매입가</div>
            <div style="flex:1;">담기</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 스크롤 영역 (HTML/CSS 사용으로 모바일 줄바꿈 방지) ---
    scroll_area = st.container(height=450)
    with scroll_area:
        for i, row in filtered.iterrows():
            # st.columns 대신 HTML 구조를 사용하여 강제로 가로 배치 유지
            cols = st.columns([1.5, 4, 2, 1])
            cols[0].caption(row['분류'])
            cols[1].write(row['상품명'])
            cols[2].markdown(f"<p style='text-align:right; font-weight:bold; color:red; margin:0;'>{row['매입가']:,}원</p>", unsafe_allow_html=True)
            if cols[3].button("➕", key=f"add_{i}"):
                add_to_calc(row['상품명'], row['매입가'])
                st.rerun()

    # --- 계산기 영역 ---
    st.divider()
    st.subheader("🛒 매입 계산기")
    labels = ["CPU", "메보", "RAM", "SSD", "HDD", "VGA"]
    total = 0
    
    # 계산기도 모바일에서 너무 길지 않게 2열 배치
    c_cols = st.columns(2)
    for i in range(6):
        with c_cols[i % 2]:
            st.caption(f"📍 {labels[i]}")
            st.session_state['calc_data'][i]['name'] = st.text_input(f"n_{i}", value=st.session_state['calc_data'][i]['name'], label_visibility="collapsed")
            st.session_state['calc_data'][i]['price'] = st.number_input(f"p_{i}", value=st.session_state['calc_data'][i]['price'], step=1000, label_visibility="collapsed")
            total += st.session_state['calc_data'][i]['price']

    st.markdown(f"### 💵 합계: <span style='color:red'>{total:,}원</span>", unsafe_allow_html=True)
    
    b1, b2 = st.columns(2)
    if b1.button("🗑️ 초기화", use_container_width=True):
        st.session_state['calc_data'] = {i: {"name": "", "price": 0} for i in range(6)}
        st.session_state['next_idx'] = 0
        st.rerun()
    
    csv_df = pd.DataFrame({"부품": labels, "모델": [st.session_state['calc_data'][i]['name'] for i in range(6)], "가": [f"{st.session_state['calc_data'][i]['price']:,}" for i in range(6)]})
    b2.download_button("💾 CSV", data=csv_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo.csv", use_container_width=True)

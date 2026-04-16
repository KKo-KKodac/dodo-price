import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입가 조회", layout="wide")

# --- 스타일 설정 (스크롤 박스용 CSS 커스텀) ---
st.markdown("""
    <style>
    .scroll-container {
        height: 450px;
        overflow-y: auto;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_stdio=True)

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

@st.cache_data(show_spinner="데이터 수집 중...")
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

# --- 메인 화면 ---
st.title("💻 DODO 매입가 통합 대시보드")

if st.button("🔄 시세 새로고침"):
    st.cache_data.clear()
    st.session_state['df'] = fetch_data()

if 'df' in st.session_state:
    df = st.session_state['df']
    
    # 상단 검색 바
    col_cat, col_src = st.columns([1, 2])
    with col_cat:
        selected_cat = st.selectbox("📂 분류 필터", ["전체보기"] + sorted(df["분류"].unique().tolist()))
    with col_src:
        search_query = st.text_input("🔍 상품명 검색")

    filtered = df.copy()
    if selected_cat != "전체보기":
        filtered = filtered[filtered["분류"] == selected_cat]
    if search_query:
        filtered = filtered[filtered["상품명"].str.contains(search_query, case=False)]

    # [핵심] 스크롤 가능한 리스트 영역
    st.subheader(f"📋 조회 결과 ({len(filtered)}건)")
    
    # 헤더 고정
    h_col1, h_col2, h_col3, h_col4 = st.columns([1.5, 4, 1.5, 1])
    h_col1.write("**분류**")
    h_col2.write("**상품명**")
    h_col3.write("**매입가**")
    h_col4.write("**담기**")
    
    # 스크롤 컨테이너 시작
    scroll_area = st.container(height=400) # Streamlit 최신 버전의 높이 고정 컨테이너
    
    with scroll_area:
        for i, row in filtered.iterrows():
            r_col1, r_col2, r_col3, r_col4 = st.columns([1.5, 4, 1.5, 1])
            r_col1.write(row['분류'])
            r_col2.text(row['상품명'])
            r_col3.write(f"{row['매입가']:,}원")
            if r_col4.button("➕", key=f"add_{i}"):
                add_to_calc(row['상품명'], row['매입가'])
                st.rerun()

    # 하단 계산기 (스크롤 영역 밖에 고정)
    st.divider()
    st.subheader("🛒 실시간 견적서")
    
    labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
    total = 0
    c_cols = st.columns(3) # 3열로 배치하여 더 콤팩트하게
    
    for i in range(6):
        with c_cols[i % 3]:
            st.caption(f"📍 {labels[i]}")
            name = st.text_input(f"n_{i}", value=st.session_state['calc_data'][i]['name'], label_visibility="collapsed")
            price = st.number_input(f"p_{i}", value=st.session_state['calc_data'][i]['price'], step=1000, label_visibility="collapsed")
            st.session_state['calc_data'][i]['name'] = name
            st.session_state['calc_data'][i]['price'] = price
            total += price

    # 합계 및 제어
    st.markdown(f"### 💵 최종 매입 합계: <span style='color:red'>{total:,}원</span>", unsafe_allow_html=True)
    
    b_col1, b_col2 = st.columns(2)
    if b_col1.button("🗑️ 전체 초기화", use_container_width=True):
        st.session_state['calc_data'] = {i: {"name": "", "price": 0} for i in range(6)}
        st.session_state['next_idx'] = 0
        st.rerun()
    
    csv_df = pd.DataFrame({"부품": labels, "모델명": [st.session_state['calc_data'][i]['name'] for i in range(6)], "단가": [f"{st.session_state['calc_data'][i]['price']:,}" for i in range(6)]})
    b_col2.download_button("💾 견적서 다운로드(CSV)", data=csv_df.to_csv(index=False).encode('utf-8-sig'), file_name="DODO_estimate.csv", use_container_width=True)

else:
    st.warning("🔄 위 버튼을 눌러 데이터를 로드해주세요.")

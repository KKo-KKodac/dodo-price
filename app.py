import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입가 조회", layout="wide")

# --- 설정 및 데이터 수집 함수 ---
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

@st.cache_data(show_spinner="데이터를 불러오는 중입니다...")
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
                        all_rows.append({
                            "분류": c.text.strip(),
                            "상품명": n.text.strip(),
                            "매입가": price_num
                        })
        except: continue
    return pd.DataFrame(all_rows)

# --- 상태 관리 (상태 유지용) ---
if 'calc_data' not in st.session_state:
    st.session_state['calc_data'] = {i: {"name": "", "price": 0} for i in range(6)}
if 'next_idx' not in st.session_state:
    st.session_state['next_idx'] = 0

def add_to_calc(name, price):
    idx = st.session_state['next_idx']
    st.session_state['calc_data'][idx] = {"name": name, "price": price}
    # 다음 인덱스로 이동 (0~5 순환)
    st.session_state['next_idx'] = (idx + 1) % 6

def reset_calc():
    st.session_state['calc_data'] = {i: {"name": "", "price": 0} for i in range(6)}
    st.session_state['next_idx'] = 0

# --- 메인 화면 구성 ---
st.title("💻 DODO 매입가 조회 & 견적기")

# 상단 버튼 레이아웃
t_col1, t_col2 = st.columns([1, 6])
with t_col1:
    if st.button("🔄 DB 갱신"):
        st.cache_data.clear()
        st.session_state['df'] = fetch_data()

if 'df' in st.session_state:
    df = st.session_state['df']
    
    # 필터 섹션
    f_col1, f_col2 = st.columns([1, 2])
    with f_col1:
        categories = ["전체보기"] + sorted(df["분류"].unique().tolist())
        selected_cat = st.selectbox("📂 분류", categories)
    with f_col2:
        search_query = st.text_input("🔍 상품명 검색")

    filtered_df = df.copy()
    if selected_cat != "전체보기":
        filtered_df = filtered_df[filtered_df["분류"] == selected_cat]
    if search_query:
        filtered_df = filtered_df[filtered_df["상품명"].str.contains(search_query, case=False)]

    # 리스트 출력 (+ 버튼 포함)
    st.subheader("📋 시세 목록")
    
    # 헤더
    h_col1, h_col2, h_col3, h_col4 = st.columns([1, 4, 1, 1])
    h_col1.write("**분류**")
    h_col2.write("**상품명**")
    h_col3.write("**매입가**")
    h_col4.write("**추가**")
    
    # 데이터 행 (최대 100개만 표시하여 속도 유지)
    for i, row in filtered_df.head(100).iterrows():
        r_col1, r_col2, r_col3, r_col4 = st.columns([1, 4, 1, 1])
        r_col1.write(row['분류'])
        r_col2.write(row['상품명'])
        r_col3.write(f"{row['매입가']:,}")
        if r_col4.button("➕", key=f"btn_{i}"):
            add_to_calc(row['상품명'], row['매입가'])
            st.rerun() # 화면 즉시 갱신

    # 하단 견적 계산기 (고정 영역 느낌)
    st.divider()
    st.subheader("🛒 매입 견적 계산기")
    
    part_labels = ["CPU", "메인보드", "램(메모리)", "SSD", "HDD", "그래픽카드"]
    total_sum = 0
    
    c_cols = st.columns(2)
    for i in range(6):
        with c_cols[i % 2]:
            st.markdown(f"**{part_labels[i]}**")
            # session_state와 연결하여 값 유지
            name_val = st.text_input(f"명칭_{i}", value=st.session_state['calc_data'][i]['name'], label_visibility="collapsed")
            price_val = st.number_input(f"가격_{i}", value=st.session_state['calc_data'][i]['price'], step=1000, label_visibility="collapsed")
            
            # 수동 입력 시에도 데이터 업데이트
            st.session_state['calc_data'][i]['name'] = name_val
            st.session_state['calc_data'][i]['price'] = price_val
            total_sum += price_val

    # 하단 합계 및 버튼
    b_col1, b_col2, b_col3 = st.columns([2, 1, 1])
    b_col1.markdown(f"### 💰 총 합계: `{total_sum:,}` 원")
    if b_col2.button("🗑️ 계산기 초기화", use_container_width=True):
        reset_calc()
        st.rerun()
    
    # CSV 다운로드 기능
    csv_data = pd.DataFrame({
        "구분": part_labels,
        "상품명": [st.session_state['calc_data'][i]['name'] for i in range(6)],
        "가격": [f"{st.session_state['calc_data'][i]['price']:,}" for i in range(6)]
    })
    csv_res = csv_data.to_csv(index=False).encode('utf-8-sig')
    b_col3.download_button("💾 CSV 저장", data=csv_res, file_name="매입견적.csv", mime="text/csv", use_container_width=True)

else:
    st.info("🔄 상단의 'DB 갱신' 버튼을 눌러 시세를 불러와주세요.")

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입가 조회", layout="wide")

# --- CSS: 모바일 가로 유지 및 디자인 최적화 ---
st.markdown("""
    <style>
    /* 리스트 영역 폰트 및 간격 */
    .stText, .stMarkdown p { font-size: 13px !important; margin-bottom: 0px !important; }
    
    /* 헤더 스타일 고정 */
    .header-box {
        display: flex; background-color: #f0f2f6; padding: 8px 0;
        font-weight: bold; border-radius: 4px; text-align: center; margin-bottom: 5px;
    }

    /* 모바일에서 컬럼 꺾임 방지 (핵심) */
    [data-testid="column"] { min-width: 0px !important; flex-shrink: 0 !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; }

    /* 활성화된 계산기 입력창 강조 */
    .active-input { border: 2px solid #ff4b4b !important; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 수집 함수 (기존 동일) ---
@st.cache_data(show_spinner="시세 로딩 중...")
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
if 'focus_idx' not in st.session_state:
    st.session_state['focus_idx'] = 0 # 현재 데이터를 넣을 위치

def update_focused_item(name, price):
    idx = st.session_state['focus_idx']
    st.session_state['calc_data'][idx] = {"name": name, "price": price}
    # 입력 후 다음 칸으로 자동 이동 (6칸 순환)
    st.session_state['focus_idx'] = (idx + 1) % 6

# --- UI 상단 ---
st.title("📂 DODO 통합 대시보드")

if st.button("🔄 시세 새로고침"):
    st.cache_data.clear()
    st.session_state['df'] = fetch_data()

if 'df' in st.session_state:
    df = st.session_state['df']
    
    col_cat, col_src = st.columns([1, 1.5])
    with col_cat:
        selected_cat = st.selectbox("분류 필터", ["전체보기"] + sorted(df["분류"].unique().tolist()))
    with col_src:
        search_query = st.text_input("검색", placeholder="상품명을 입력하세요...")

    filtered = df.copy()
    if selected_cat != "전체보기":
        filtered = filtered[filtered["분류"] == selected_cat]
    if search_query:
        filtered = filtered[filtered["상품명"].str.contains(search_query, case=False)]

    # --- 테이블 헤더 (HTML) ---
    st.markdown("""
        <div class="header-box">
            <div style="flex:1.8;">분류</div>
            <div style="flex:4; text-align:left; padding-left:10px;">상품명</div>
            <div style="flex:2.2; text-align:right; padding-right:10px;">매입가</div>
            <div style="flex:1;">담기</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 조회 결과 리스트 (스크롤 박스) ---
    with st.container(height=400):
        for i, row in filtered.iterrows():
            # 모바일에서도 4열 가로 유지
            cols = st.columns([1.8, 4, 2.2, 1])
            cols[0].caption(row['분류'])
            cols[1].write(row['상품명'])
            cols[2].markdown(f"<p style='text-align:right; font-weight:bold; color:red;'>{row['매입가']:,}원</p>", unsafe_allow_html=True)
            if cols[3].button("➕", key=f"add_{i}"):
                update_focused_item(row['상품명'], row['매입가'])
                st.rerun()

    # --- 견적 계산기 (하단 고정 느낌) ---
    st.divider()
    st.subheader("🛒 매입 견적 계산기")
    st.info(f"💡 현재 **'{['CPU','메보','RAM','SSD','HDD','VGA'][st.session_state['focus_idx']]}'** 항목이 선택됨. '➕' 누를 시 해당 칸에 입력됩니다.")
    
    labels = ["CPU", "메보", "RAM", "SSD", "HDD", "VGA"]
    total = 0
    
    calc_cols = st.columns(2)
    for i in range(6):
        with calc_cols[i % 2]:
            # 현재 포커스된 항목이면 배경색이나 라벨로 강조
            label_prefix = "👉 " if st.session_state['focus_idx'] == i else "📍 "
            if st.button(f"{label_prefix}{labels[i]} 선택하기", key=f"sel_{i}", use_container_width=True):
                st.session_state['focus_idx'] = i
                st.rerun()
            
            # 수동 입력 가능하도록 구성
            name_input = st.text_input(f"품명_{i}", value=st.session_state['calc_data'][i]['name'], label_visibility="collapsed")
            price_input = st.number_input(f"가_{i}", value=st.session_state['calc_data'][i]['price'], step=1000, label_visibility="collapsed")
            
            # 세션 상태 업데이트
            st.session_state['calc_data'][i]['name'] = name_input
            st.session_state['calc_data'][i]['price'] = price_input
            total += price_input

    st.markdown(f"### 💰 최종 합계: <span style='color:red; font-size:1.5em;'>{total:,}원</span>", unsafe_allow_html=True)
    
    b_reset, b_csv = st.columns(2)
    if b_reset.button("🗑️ 전체 비우기", use_container_width=True):
        st.session_state['calc_data'] = {i: {"name": "", "price": 0} for i in range(6)}
        st.session_state['focus_idx'] = 0
        st.rerun()
    
    # CSV 다운로드
    csv_df = pd.DataFrame({"구분": labels, "모델": [st.session_state['calc_data'][i]['name'] for i in range(6)], "매입가": [st.session_state['calc_data'][i]['price'] for i in range(6)]})
    b_csv.download_button("💾 견적 저장", data=csv_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo_price.csv", use_container_width=True)

else:
    st.warning("🔄 상단 버튼을 눌러 시세를 로딩해주세요.")

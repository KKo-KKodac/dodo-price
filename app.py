import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 1. 페이지 설정 및 타이틀 변경
st.set_page_config(page_title="컴퓨터매입계산기", layout="wide")

# 2. CSS 최적화: 상품명 줄임 처리 및 버튼 디자인
st.markdown("""
    <style>
    /* 입력창 및 버튼 높이 통일 */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stButton > button {
        height: 45px !important; min-height: 45px !important;
    }
    
    /* 상품명 말줄임표(...) 처리 - 너비를 줄이기 위해 max-width 조정 */
    .truncate-text {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block;
        max-width: 350px; /* 기존보다 훨씬 짧게 설정 */
    }

    /* 테이블 헤더 스타일 */
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 12px 0; font-weight: bold; border-radius: 4px; text-align: center;
        margin-bottom: 8px; font-size: 15px;
    }
    
    /* 리스트 내 담기(+) 버튼 (동그랗게) */
    div.stButton > button[key^="add_"] {
        width: 38px !important; min-width: 38px !important; height: 38px !important; 
        border-radius: 50% !important; padding: 0 !important;
    }

    /* 하단 버튼 글자 잘림 방지 */
    .stButton > button {
        min-width: 160px !important;
        font-weight: 600 !important;
    }

    .price-text { color: red; font-weight: bold; text-align: center; font-size: 16px; margin: 0; }
    .block-container { padding-top: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 수집 함수 (기존 URL 리스트 포함)
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

# 4. 세션 상태 관리 (초기화 및 담기 기능)
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0
for i in range(6):
    if f"nm_{i}" not in st.session_state: st.session_state[f"nm_{i}"] = ""
    if f"pr_{i}" not in st.session_state: st.session_state[f"pr_{i}"] = 0

def add_to_calc(name, price):
    idx = st.session_state['target_idx']
    st.session_state[f"nm_{idx}"] = name
    st.session_state[f"pr_{idx}"] = price
    st.session_state['target_idx'] = (idx + 1) % 6

def reset_calc():
    for i in range(6):
        st.session_state[f"nm_{i}"], st.session_state[f"pr_{i}"] = "", 0
    st.session_state['target_idx'] = 0

# --- 화면 구성 시작 ---

# 타이틀 수정
st.title("💻 컴퓨터매입계산기")

# 시세 DB 갱신 버튼 - 타이틀 바로 아래 단독 배치
if st.button("🔄 시세 DB 갱신", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.write("")

# 검색 필터
df = fetch_data()
col_cat, col_search = st.columns([1, 2.5])
with col_cat:
    cat = st.selectbox("분류", ["전체보기"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with col_search:
    query = st.text_input("검색", placeholder="상품명 입력", label_visibility="collapsed")

f_df = df.copy()
if cat != "전체보기": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

# 테이블 헤더: 비율 조정 (상품명 칸 비중 축소)
st.markdown('<div class="table-header"><div style="flex:1;">분류</div><div style="flex:2.2;">상품명</div><div style="flex:1.5;">금액</div><div style="flex:0.8;">담기</div></div>', unsafe_allow_html=True)

with st.container(height=380):
    for i, row in f_df.iterrows():
        # 열 너비 비율 수정 [1, 2.2, 1.5, 0.8]
        cols = st.columns([1, 2.2, 1.5, 0.8])
        cols[0].write(row['분류'])
        # 상품명: 'truncate-text' 클래스로 너비 제한 및 말줄임표 처리
        cols[1].markdown(f'<span class="truncate-text" title="{row["상품명"]}">{row["상품명"]}</span>', unsafe_allow_html=True)
        cols[2].markdown(f"<p class='price-text'>{row['매입가']:,}</p>", unsafe_allow_html=True)
        cols[3].button("➕", key=f"add_{i}", on_click=add_to_calc, args=(row['상품명'], row['매입가']))

st.divider()

# 하단 계산기 영역
st.subheader("🛒 매입 계산 리스트")
st.radio("항목 선택:", range(6), format_func=lambda x: labels[x], key="target_idx", horizontal=True)

total_sum = 0
cal_cols = st.columns(2)
for i in range(6):
    with cal_cols[i % 2]:
        st.write(f"**{labels[i]}**")
        st.text_input(f"name_input_{i}", key=f"nm_{i}", label_visibility="collapsed")
        st.number_input(f"price_input_{i}", step=1000, key=f"pr_{i}", label_visibility="collapsed")
        total_sum += st.session_state[f"pr_{i}"]

st.markdown(f"### 💰 최종 합계: :red[{total_sum:,}원]")

# 하단 버튼 명칭 수정
b_col1, b_col2, _ = st.columns([1.5, 1.5, 2.5])
with b_col1:
    st.button("🗑️ 계산기 초기화", use_container_width=True, on_click=reset_calc)
with b_col2:
    res_df = pd.DataFrame({"항목": labels, "모델": [st.session_state[f"nm_{k}"] for k in range(6)], "금액": [st.session_state[f"pr_{k}"] for k in range(6)]})
    st.download_button("💾 CSV 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="purchase_calc.csv", use_container_width=True)

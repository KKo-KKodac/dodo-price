import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입조회", layout="wide")

# --- CSS: 표 스타일 및 디자인 ---
st.markdown("""
    <style>
    /* 테이블 스타일 */
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 13px; }
    .custom-table th { background-color: #4A90E2; color: white; padding: 10px; text-align: center; }
    .custom-table td { padding: 8px 5px; border-bottom: 1px solid #eee; vertical-align: middle; }
    .price-text { color: red; font-weight: bold; text-align: right; }
    
    /* 모바일 대응: 상품명 칸을 넓게 */
    .col-cat { width: 60px; text-align: center; color: #888; font-size: 11px; }
    .col-name { width: auto; }
    .col-price { width: 80px; text-align: right; }
    .col-btn { width: 45px; text-align: center; }
    
    /* 버튼 스타일 */
    .stButton>button { width: 100%; padding: 2px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 수집 ---
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
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in URLS:
        try:
            res = requests.get(url, headers=headers, timeout=5)
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

# --- 세션 관리 ---
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]

if 'calc_names' not in st.session_state:
    st.session_state['calc_names'] = [""] * 6
if 'calc_prices' not in st.session_state:
    st.session_state['calc_prices'] = [0] * 6
if 'cur_idx' not in st.session_state:
    st.session_state['cur_idx'] = 0

# --- 앱 UI ---
df = fetch_data()
st.title("💻 DODO 매입가")

# 검색바
sc1, sc2 = st.columns([1, 2])
with sc1: cat_sel = st.selectbox("분류", ["전체"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with sc2: query_sel = st.text_input("검색", placeholder="상품명 입력...", label_visibility="collapsed")

f_df = df.copy()
if cat_sel != "전체": f_df = f_df[f_df["분류"] == cat_sel]
if query_sel: f_df = f_df[f_df["상품명"].str.contains(query_sel, case=False)]

# 조회 결과 (헤더 + 스크롤 테이블)
st.write(f"조회 결과: {len(f_df)}건")

# 진짜 테이블 구조 시작
st.markdown("""
    <table class="custom-table">
        <thead>
            <tr>
                <th class="col-cat">분류</th>
                <th class="col-name">상품명</th>
                <th class="col-price">금액</th>
                <th class="col-btn">담기</th>
            </tr>
        </thead>
    </table>
""", unsafe_allow_html=True)

with st.container(height=350):
    for i, row in f_df.iterrows():
        # 데이터 정렬을 위해 st.columns를 사용하되 너비를 강제 조정
        cols = st.columns([1.2, 4, 1.5, 0.8])
        cols[0].caption(row['분류'])
        cols[1].write(row['상품명'])
        cols[2].markdown(f"<p class='price-text'>{row['매입가']:,}</p>", unsafe_allow_html=True)
        
        # 버튼 작동 수정
        if cols[3].button("➕", key=f"btn_{i}"):
            idx = st.session_state['cur_idx']
            st.session_state['calc_names'][idx] = row['상품명']
            st.session_state['calc_prices'][idx] = row['매입가']
            # 입력 후 다음 칸으로 이동
            st.session_state['cur_idx'] = (idx + 1) % 6
            st.rerun()

st.divider()

# --- 계산기 영역 ---
st.subheader("🛒 매입 계산기")
total_sum = 0
c_cols = st.columns(2)

for i in range(6):
    with c_cols[i % 2]:
        focus_mark = "🔵" if st.session_state['cur_idx'] == i else "⚪"
        st.write(f"{focus_mark} **{labels[i]}**")
        
        # 이름 입력창
        n_val = st.text_input(f"n_{i}", value=st.session_state['calc_names'][i], key=f"name_input_{i}", label_visibility="collapsed")
        # 가격 입력창
        p_val = st.number_input(f"p_{i}", value=st.session_state['calc_prices'][i], step=1000, key=f"price_input_{i}", label_visibility="collapsed")
        
        # 사용자가 직접 타이핑하면 포커스 이동
        if n_val != st.session_state['calc_names'][i] or p_val != st.session_state['calc_prices'][i]:
            st.session_state['calc_names'][i] = n_val
            st.session_state['calc_prices'][i] = p_val
            st.session_state['cur_idx'] = i
            
        total_sum += p_val

st.markdown(f"### 💰 합계: <span style='color:red;'>{total_sum:,}원</span>", unsafe_allow_html=True)

# 하단 제어
b1, b2 = st.columns(2)
if b1.button("🗑️ 초기화", use_container_width=True):
    st.session_state['calc_names'] = [""] * 6
    st.session_state['calc_prices'] = [0] * 6
    st.session_state['cur_idx'] = 0
    st.rerun()

res_df = pd.DataFrame({"부품": labels, "모델": st.session_state['calc_names'], "단가": st.session_state['calc_prices']})
b2.download_button("💾 CSV 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo.csv", use_container_width=True)

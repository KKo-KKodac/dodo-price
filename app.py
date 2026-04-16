import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입조회", layout="wide")

# --- 모바일 가로 고정 및 심플 디자인 CSS ---
st.markdown("""
    <style>
    /* 모바일 컬럼 꺾임 방지 */
    [data-testid="column"] { min-width: 0px !important; flex: 1; }
    div[data-testid="stHorizontalBlock"] { gap: 0.3rem !important; flex-wrap: nowrap !important; }
    
    /* 표 헤더 스타일 */
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 8px 0; font-weight: bold; border-radius: 4px; text-align: center;
    }
    
    /* 입력창 강조 */
    .stTextInput input:focus { border-color: #4A90E2 !important; box-shadow: 0 0 5px rgba(74,144,226,0.5); }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 수집 (캐싱 적용으로 빠르게) ---
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

# --- 세션 상태 초기화 (계산기 데이터) ---
labels = ["CPU", "메인보드", "메모리", "SSD", "HDD", "그래픽카드"]
if 'calc_names' not in st.session_state:
    st.session_state['calc_names'] = [""] * 6
if 'calc_prices' not in st.session_state:
    st.session_state['calc_prices'] = [0] * 6
if 'last_focused' not in st.session_state:
    st.session_state['last_focused'] = 0 # 마지막으로 수정한 입력칸

# --- 메인 로직 ---
df = fetch_data()

st.title("💻 DODO 매입가")

# 검색 및 필터
c1, c2 = st.columns([1, 2])
with c1:
    cat = st.selectbox("분류", ["전체"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with c2:
    query = st.text_input("검색", placeholder="상품명 입력...", label_visibility="collapsed")

filtered = df.copy()
if cat != "전체": filtered = filtered[filtered["분류"] == cat]
if query: filtered = filtered[filtered["상품명"].str.contains(query, case=False)]

# 조회 결과 헤더
st.markdown(f"**조회 결과: {len(filtered)}건** (입력할 항목을 아래에서 먼저 선택하세요)")
st.markdown("""<div class="table-header"><div style="flex:2;">분류</div><div style="flex:4; text-align:left; padding-left:10px;">상품명</div><div style="flex:2.5; text-align:right; padding-right:10px;">금액</div><div style="flex:1;">담기</div></div>""", unsafe_allow_html=True)

# 리스트 출력 (스크롤)
with st.container(height=350):
    for i, row in filtered.iterrows():
        cols = st.columns([2, 4, 2.5, 1])
        cols[0].caption(row['분류'])
        cols[1].write(row['상품명'])
        cols[2].markdown(f"<p style='text-align:right; color:red; font-weight:bold; margin:0;'>{row['매입가']:,}원</p>", unsafe_allow_html=True)
        if cols[3].button("➕", key=f"add_{i}"):
            # 포커스된 위치에 값 넣고 다음 칸으로 이동
            f_idx = st.session_state['last_focused']
            st.session_state['calc_names'][f_idx] = row['상품명']
            st.session_state['calc_prices'][f_idx] = row['매입가']
            st.session_state['last_focused'] = (f_idx + 1) % 6
            st.rerun()

st.divider()

# --- 계산기 (pyw 방식의 심플함 재현) ---
st.subheader("🛒 매입 계산기")
total = 0
cal_cols = st.columns(2)

for i in range(6):
    with cal_cols[i % 2]:
        # 항목 라벨 + 현재 포커스 표시
        indicator = "🔵" if st.session_state['last_focused'] == i else "⚪"
        st.write(f"{indicator} **{labels[i]}**")
        
        # 입력창: 값을 직접 수정하면 last_focused가 여기로 고정됨
        name = st.text_input(f"n{i}", value=st.session_state['calc_names'][i], key=f"in_n{i}", label_visibility="collapsed")
        price = st.number_input(f"p{i}", value=st.session_state['calc_prices'][i], step=1000, key=f"in_p{i}", label_visibility="collapsed")
        
        # 값이 바뀌면 현재 포커스를 여기로 업데이트
        if name != st.session_state['calc_names'][i] or price != st.session_state['calc_prices'][i]:
            st.session_state['calc_names'][i] = name
            st.session_state['calc_prices'][i] = price
            st.session_state['last_focused'] = i
            
        total += price

st.markdown(f"### 💰 합계: <span style='color:red; font-size:1.4em;'>{total:,}원</span>", unsafe_allow_html=True)

# 하단 버튼
b1, b2 = st.columns(2)
if b1.button("🗑️ 전체 초기화", use_container_width=True):
    st.session_state['calc_names'] = [""] * 6
    st.session_state['calc_prices'] = [0] * 6
    st.session_state['last_focused'] = 0
    st.rerun()

csv_data = pd.DataFrame({"항목": labels, "내용": st.session_state['calc_names'], "금액": st.session_state['calc_prices']})
b2.download_button("💾 CSV 저장", data=csv_data.to_csv(index=False).encode('utf-8-sig'), file_name="dodo_price.csv", use_container_width=True)

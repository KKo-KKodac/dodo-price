import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입조회", layout="wide")

# --- CSS: 테이블 정렬 및 중앙 정렬 ---
st.markdown("""
    <style>
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 10px 0; font-weight: bold; border-radius: 4px; text-align: center;
        margin-bottom: 5px;
    }
    .header-item { flex: 1; border-right: 1px solid rgba(255,255,255,0.3); }
    .header-item:last-child { border-right: none; }
    
    /* 결과 행 정렬: 헤더와 동일한 flex 비율 사용 */
    .row-item { display: flex; align-items: center; justify-content: center; text-align: center; }
    .row-name { justify-content: flex-start; text-align: left; padding-left: 10px; }
    
    [data-testid="column"] { min-width: 0px !important; flex: 1 !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.2rem !important; flex-wrap: nowrap !important; }

    .price-text { color: red; font-weight: bold; margin: 0; width: 100%; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 수집 ---
@st.cache_data(ttl=3600)
def fetch_data():
    URLS = ["https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4220", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=967", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=10&ctgry_no2=966&ctgry_no3=4221", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4083", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=31", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=993", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=1684", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3682", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3838", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=3918", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=25", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4020", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4089", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4137", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=8&ctgry_no2=9&ctgry_no3=4144", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3866", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=4141", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=3608", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=1&ctgry_no2=2&ctgry_no3=7", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3784", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3775", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3768", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=3808", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4075", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=58&ctgry_no3=4145", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3901", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=3902", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4085", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4146", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=14&ctgry_no2=59&ctgry_no3=4218", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3701", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=3932", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4021", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=42&ctgry_no3=4090", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4029", "https://www.worldmemory.co.kr/price/computer.do?ctgry_no1=12&ctgry_no2=4026&ctgry_no3=4139"]
    all_rows = []
    for url in URLS:
        try:
            res = requests.get(url, timeout=5)
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
if 'names' not in st.session_state: st.session_state['names'] = [""] * 6
if 'prices' not in st.session_state: st.session_state['prices'] = [0] * 6
if 'target_idx' not in st.session_state: st.session_state['target_idx'] = 0

df = fetch_data()
st.title("💻 DODO 매입")

# 검색 영역
sc1, sc2 = st.columns([1, 2])
with sc1: cat = st.selectbox("분류", ["전체"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with sc2: query = st.text_input("검색", placeholder="상품명 입력...", label_visibility="collapsed")

f_df = df.copy()
if cat != "전체": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

# 1. 헤더 (중앙 정렬 및 구분선 | 추가)
st.markdown(f"조회 결과: {len(f_df)}건")
st.markdown("""
    <div class="table-header">
        <div class="header-item" style="flex:1.2;">분류</div>
        <div class="header-item" style="flex:4;">상품명</div>
        <div class="header-item" style="flex:2.2;">금액</div>
        <div class="header-item" style="flex:0.8;">담기</div>
    </div>
""", unsafe_allow_html=True)

# 2. 결과 리스트 (중앙 정렬 적용)
with st.container(height=380):
    for i, row in f_df.iterrows():
        cols = st.columns([1.2, 4, 2.2, 0.8])
        cols[0].markdown(f"<div style='text-align:center; color:gray; font-size:12px;'>{row['분류']}</div>", unsafe_allow_html=True)
        cols[1].write(row['상품명'])
        cols[2].markdown(f"<p class='price-text'>{row['매입가']:,}원</p>", unsafe_allow_html=True)
        if cols[3].button("➕", key=f"add_{i}"):
            # 타겟 인덱스에 데이터 직접 삽입
            t_idx = st.session_state['target_idx']
            st.session_state['names'][t_idx] = row['상품명']
            st.session_state['prices'][t_idx] = row['매입가']
            st.session_state['target_idx'] = (t_idx + 1) % 6 # 입력 후 다음 칸 자동 이동
            st.rerun()

st.divider()

# 3. 매입 계산기 (라디오 버튼으로 타겟 고정)
st.subheader("🛒 매입 계산기")

# 어떤 칸에 넣을지 선택하는 라디오 버튼 (이게 있어야 + 버튼이 정확히 작동합니다)
st.session_state['target_idx'] = st.radio("데이터를 입력할 항목을 선택하세요:", range(6), 
                                        format_func=lambda x: labels[x], 
                                        index=st.session_state['target_idx'],
                                        horizontal=True)

total_sum = 0
cal_cols = st.columns(2)
for i in range(6):
    with cal_cols[i % 2]:
        st.write(f"**{labels[i]}**")
        n_in = st.text_input(f"n{i}", value=st.session_state['names'][i], key=f"nm_{i}", label_visibility="collapsed")
        p_in = st.number_input(f"p{i}", value=st.session_state['prices'][i], step=1000, key=f"pr_{i}", label_visibility="collapsed")
        
        # 수동 수정 내용 반영
        st.session_state['names'][i] = n_in
        st.session_state['prices'][i] = p_in
        total_sum += p_in

st.markdown(f"### 💰 합계: <span style='color:red;'>{total_sum:,}원</span>", unsafe_allow_html=True)

# 4. 하단 제어
b1, b2 = st.columns(2)
if b1.button("🗑️ 초기화", use_container_width=True):
    st.session_state['names'] = [""] * 6
    st.session_state['prices'] = [0] * 6
    st.session_state['target_idx'] = 0
    st.rerun()

res_df = pd.DataFrame({"항목": labels, "모델": st.session_state['names'], "금액": st.session_state['prices']})
b2.download_button("💾 저장", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo.csv", use_container_width=True)

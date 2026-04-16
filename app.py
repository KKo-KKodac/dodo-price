import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 웹 페이지 설정
st.set_page_config(page_title="DODO 매입조회", layout="wide")

# --- CSS: 표 정렬 및 디자인 (헤더와 데이터 줄 완벽 일치) ---
st.markdown("""
    <style>
    .table-header {
        display: flex; background-color: #4A90E2; color: white; 
        padding: 8px 0; font-weight: bold; border-radius: 4px; text-align: center;
    }
    /* 모바일 가로 유지 및 줄바꿈 방지 */
    [data-testid="column"] { min-width: 0px !important; flex: 1 !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.2rem !important; flex-wrap: nowrap !important; }
    .price-tag { color: red; font-weight: bold; text-align: right; width: 100%; margin: 0; }
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

# --- 세션 상태 (pyw 스타일 단순 리스트) ---
labels = ["CPU", "메보", "메모리", "SSD", "HDD", "그래픽"]
if 'names' not in st.session_state: st.session_state['names'] = [""] * 6
if 'prices' not in st.session_state: st.session_state['prices'] = [0] * 6
if 'focus' not in st.session_state: st.session_state['focus'] = 0

# --- 화면 구성 ---
df = fetch_data()
st.title("💻 DODO 매입")

# 검색
c1, c2 = st.columns([1, 2])
with c1: cat = st.selectbox("분류", ["전체"] + sorted(df["분류"].unique().tolist()), label_visibility="collapsed")
with c2: query = st.text_input("검색", placeholder="상품명 입력...", label_visibility="collapsed")

f_df = df.copy()
if cat != "전체": f_df = f_df[f_df["분류"] == cat]
if query: f_df = f_df[f_df["상품명"].str.contains(query, case=False)]

# 조회 결과 테이블 헤더
st.markdown(f"**결과: {len(f_df)}건**")
st.markdown("""<div class="table-header"><div style="flex:1.2;">분류</div><div style="flex:4; text-align:left; padding-left:10px;">상품명</div><div style="flex:2.2; text-align:right; padding-right:15px;">금액</div><div style="flex:0.8;">담기</div></div>""", unsafe_allow_html=True)

# 리스트 출력
with st.container(height=350):
    for i, row in f_df.iterrows():
        cols = st.columns([1.2, 4, 2.2, 0.8])
        cols[0].caption(row['분류'])
        cols[1].write(row['상품명'])
        cols[2].markdown(f"<p class='price-tag'>{row['매입가']:,}원</p>", unsafe_allow_html=True)
        if cols[3].button("➕", key=f"btn_{i}"):
            idx = st.session_state['focus']
            st.session_state['names'][idx] = row['상품명']
            st.session_state['prices'][idx] = row['매입가']
            st.session_state['focus'] = (idx + 1) % 6
            st.rerun()

st.divider()

# --- 계산기 영역 (pyw 감성) ---
st.subheader("🛒 매입 계산기")
total = 0
cal_cols = st.columns(2)

for i in range(6):
    with cal_cols[i % 2]:
        # 포커스 표시 및 선택 버튼
        is_on = "🔵" if st.session_state['focus'] == i else "⚪"
        if st.button(f"{is_on} {labels[i]}", key=f"f_{i}", use_container_width=True):
            st.session_state['focus'] = i
            st.rerun()
        
        # 입력창
        n_val = st.text_input(f"n{i}", value=st.session_state['names'][i], key=f"in_n{i}", label_visibility="collapsed")
        p_val = st.number_input(f"p{i}", value=st.session_state['prices'][i], step=1000, key=f"in_p{i}", label_visibility="collapsed")
        
        # 상태 업데이트
        st.session_state['names'][i] = n_val
        st.session_state['prices'][i] = p_val
        total += p_val

st.markdown(f"### 💰 합계: <span style='color:red;'>{total:,}원</span>", unsafe_allow_html=True)

# 초기화 및 저장
b_res, b_csv = st.columns(2)
if b_res.button("🗑️ 전체 초기화", use_container_width=True):
    st.session_state['names'] = [""] * 6
    st.session_state['prices'] = [0] * 6
    st.session_state['focus'] = 0
    st.rerun()

final_df = pd.DataFrame({"부품": labels, "모델명": st.session_state['names'], "금액": st.session_state['prices']})
b_csv.download_button("💾 CSV 저장", data=final_df.to_csv(index=False).encode('utf-8-sig'), file_name="dodo.csv", use_container_width=True)

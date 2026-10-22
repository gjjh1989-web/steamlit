import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 기본 설정 및 디자인
# ---------------------------------------------------------
st.set_page_config(
    page_title="생명과학 독서활동 관리 웹앱",
    page_icon="🧬",
    layout="wide"
)

# ---------------------------------------------------------
# 2. 초기 데이터 및 세션 상태(Session State) 초기화
# ---------------------------------------------------------
if 'reading_logs' not in st.session_state:
    # 기본 샘플 데이터 설정
    st.session_state.reading_logs = pd.DataFrame([
        {
            "학생이름": "김생명",
            "도서명": "물고기는 존재하지 않는다",
            "저자": "룰루 밀러",
            "세부분야": "진화/생물학",
            "날짜": "2026-03-10",
            "핵심키워드": "분류학, 의지, 삶의의미",
            "느낀점/토론주제": "자연을 인간 중심적으로 분류하려는 시도가 지닌 한계와 과학적 사고방식에 대해 생각해보게 됨."
        },
        {
            "학생이름": "이유전",
            "도서명": "크리스퍼가 온다",
            "저자": "제니퍼 다우드나",
            "세부분야": "유전공학/바이오테크",
            "날짜": "2026-03-15",
            "핵심키워드": "유전자정제가위, 윤리, 크리스퍼",
            "느낀점/토론주제": "유전자 편집 기술의 생명윤리적 가이드라인 제정에 대해 학급 토론 진행을 제안함."
        }
    ])

# ---------------------------------------------------------
# 3. 사이드바 - 메인 메뉴
# ---------------------------------------------------------
st.sidebar.title("🧬 생명과학 독서 클럽")
menu = st.sidebar.radio(
    "메뉴를 선택하세요:",
    ["📚 최신 추천 도서", "✍️ 독서 기록 제출", "📊 독서 활동 대시보드", "📂 제출 기록 조회"]
)

# ---------------------------------------------------------
# 메뉴 1: 최신 생명과학 추천 도서
# ---------------------------------------------------------
if menu == "📚 최신 추천 도서":
    st.header("🧬 생명과학 최신 추천 도서 목록")
    st.write("학생들과 함께 읽기 좋은 최근 생명과학 및 바이오테크 분야 추천 도서입니다.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🧬 크리스퍼가 온다")
        st.caption("저자: 제니퍼 다우드나 외 | 분야: 유전공학")
        st.write("유전자 가위 기술 혁명과 생명윤리에 관한 생생한 현장 기록.")
        st.info("💡 **추천 토론 주제**: 배아 유전자 편집, 어디까지 허용해야 하는가?")

    with col2:
        st.subheader("🧠 뇌는 춤춘다")
        st.caption("저자: 카밀라 판스 외 | 분야: 뇌과학/신경생물학")
        st.write("신경과학과 인공지능, 인간 지능의 미래를 다룬 교양 과학서.")
        st.info("💡 **추천 토론 주제**: 뇌-컴퓨터 인터페이스(BCI)의 미래와 인류.")

    with col3:
        st.subheader("🦠 넥스트 판데믹")
        st.caption("저자: 앤소니 파우치 외 | 분야: 면역학/감염병")
        st.write("감염병과 인간 면역체계, 현대 바이오의학의 대응 전략.")
        st.info("💡 **추천 토론 주제**: 신종 바이러스에 대응하는 백신 개발과 분배 문제.")

# ---------------------------------------------------------
# 메뉴 2: 독서 기록 제출
# ---------------------------------------------------------
elif menu == "✍️ 독서 기록 제출":
    st.header("✍️ 생명과학 독서 활동 기록 작성")
    st.write("읽은 책의 내용과 느낀 점, 탐구 토론 주제를 제출해 주세요.")
    st.markdown("---")

    with st.form("reading_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            student_name = st.text_input("학생 이름 *", placeholder="예: 홍길동")
            book_title = st.text_input("도서명 *", placeholder="예: 물고기는 존재하지 않는다")
            author = st.text_input("저자", placeholder="예: 룰루 밀러")
            
        with col2:
            category = st.selectbox(
                "생명과학 세부 분야 *",
                ["유전공학/바이오테크", "뇌과학/신경생물학", "진화/생물학", "면역학/감염병", "생태학/환경", "의학/약학", "기타"]
            )
            read_date = st.date_input("읽은 날짜", datetime.now())
            keywords = st.text_input("핵심 키워드 (쉼표 구분)", placeholder="예: 유전자, 윤리, 크리스퍼")

        summary_review = st.text_area(
            "핵심 요약 및 느낀 점 / 탐구 토론 주제 *",
            height=150,
            placeholder="책에서 인상 깊었던 생명과학적 개념과 본인의 생각, 혹은 친구들과 나누고 싶은 토론 주제를 작성해 주세요."
        )

        submitted = st.form_submit_button("🚀 제출하기")

        if submitted:
            if not student_name or not book_title or not summary_review:
                st.error("이름, 도서명, 느낀 점은 필수 입력 항목입니다.")
            else:
                new_data = {
                    "학생이름": student_name,
                    "도서명": book_title,
                    "저자": author,
                    "세부분야": category,
                    "날짜": read_date.strftime("%Y-%m-%d"),
                    "핵심키워드": keywords,
                    "느낀점/토론주제": summary_review
                }
                # DataFrame에 데이터 추가
                st.session_state.reading_logs = pd.concat(
                    [st.session_state.reading_logs, pd.DataFrame([new_data])],
                    ignore_index=True
                )
                st.success(f"🎉 {student_name} 학생의 독서 기록이 성공적으로 제출되었습니다!")

# ---------------------------------------------------------
# 메뉴 3: 독서 활동 대시보드
# ---------------------------------------------------------
elif menu == "📊 독서 활동 대시보드":
    st.header("📊 생명과학 독서 활동 통계 대시보드")
    st.write("학생들이 탐구한 생명과학 분야와 독서 활동 현황입니다.")
    st.markdown("---")

    df = st.session_state.reading_logs

    if df.empty:
        st.info("아직 제출된 독서 기록이 없습니다.")
    else:
        # 요약 지표
        m1, m2, m3 = st.columns(3)
        m1.metric("총 제출 건수", f"{len(df)} 건")
        m2.metric("참여 학생 수", f"{df['학생이름'].nunique()} 명")
        m3.metric("가장 인기도 높은 분야", df['세부분야'].mode()[0] if not df.empty else "-")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📌 세부 분야별 독서 비율")
            category_counts = df['세부분야'].value_counts().reset_index()
            category_counts.columns = ['세부분야', '건수']
            fig_pie = px.pie(
                category_counts, 
                values='건수', 
                names='세부분야', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.subheader("📈 학생별 읽은 책 수")
            student_counts = df['학생이름'].value_counts().reset_index()
            student_counts.columns = ['학생이름', '읽은 책 수']
            fig_bar = px.bar(
                student_counts, 
                x='학생이름', 
                y='읽은 책 수',
                color='읽은 책 수',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------
# 메뉴 4: 제출 기록 조회 및 엑셀 다운로드
# ---------------------------------------------------------
elif menu == "📂 제출 기록 조회":
    st.header("📂 전체 독서 기록 조회 및 데이터 다운로드")
    st.write("제출된 독서 기록 목록을 확인하고 Excel/CSV 파일로 저장할 수 있습니다.")
    st.markdown("---")

    df = st.session_state.reading_logs

    # 검색/필터 기능
    search_keyword = st.text_input("🔍 학생 이름 또는 도서명 검색:", "")
    if search_keyword:
        filtered_df = df[
            df['학생이름'].str.contains(search_keyword, na=False) |
            df['도서명'].str.contains(search_keyword, na=False)
        ]
    else:
        filtered_df = df

    # 표 출력
    st.dataframe(filtered_df, use_container_width=True)

    # CSV 다운로드 버튼
    csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV 파일로 다운로드",
        data=csv_data,
        file_name=f"생명과학_독서기록_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

import streamlit as st
from openai import OpenAI
import pdfplumber

# 1. 페이지 설정
st.set_page_config(page_title="국멘 AI 학습 시스템", page_icon="🏫", layout="wide")

# 2. API 키 설정 (시크릿 or 입력)
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("OpenAI API Key", type="password")

if not api_key:
    st.warning("⚠️ API 키가 필요합니다.")
    st.stop()

client = OpenAI(api_key=api_key)

# 3. 사이드바 메뉴 (여기가 핵심!)
with st.sidebar:
    st.title("🎓 국멘 AI 시스템")
    menu = st.radio(
        "기능을 선택하세요:",
        ("📂 교재 분석 (PDF)", "🏆 데모 시뮬레이션 (예시)")
    )
    st.divider()

# --- [기능 1] 교재 분석 (PDF 업로드) ---
if menu == "📂 교재 분석 (PDF)":
    st.header("📂 나만의 교재 분석기")
    st.markdown("PDF를 업로드하면 AI가 지문을 분석하고 문제를 만들어줍니다.")
    
    uploaded_file = st.file_uploader("교재 PDF 업로드", type="pdf")

    if uploaded_file:
        def extract_text_from_pdf(file):
            with pdfplumber.open(file) as pdf:
                text = ""
                for i, page in enumerate(pdf.pages):
                    if i < 3: 
                        text += page.extract_text()
            return text

        if "pdf_text" not in st.session_state:
            with st.spinner("교재 분석 중... 🧐"):
                st.session_state["pdf_text"] = extract_text_from_pdf(uploaded_file)

        pdf_text = st.session_state["pdf_text"]

        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("📄 지문 내용")
            st.text_area("내용", pdf_text, height=600)
        with col2:
            st.subheader("🤖 AI 선생님")
            tab1, tab2 = st.tabs(["질의응답", "변형 문제"])
            with tab1:
                q = st.text_input("질문하세요:")
                if q:
                    with st.spinner("답변 중..."):
                        res = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": f"지문: {pdf_text}\n질문: {q}"}]
                        )
                        st.info(res.choices[0].message.content)
            with tab2:
                if st.button("문제 만들기 🚀"):
                    with st.spinner("출제 중..."):
                        res = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": f"지문: {pdf_text}\n수능형 3점 문제 1개 출제해줘."}]
                        )
                        st.markdown(res.choices[0].message.content)

# --- [기능 2] 데모 시뮬레이션 (아까 그 기능!) ---
elif menu == "🏆 데모 시뮬레이션 (예시)":
    st.header("🏆 실전 모의고사 피드백 데모")
    st.markdown("학생들이 문제를 틀렸을 때 제공되는 **초개인화 피드백** 예시입니다.")

    # 예시 데이터 (하드코딩)
    example_passage = """
    [2024 수능 - 검색 엔진]
    인터넷 검색 엔진은 중요도와 적합도를 고려해 순서를 정한다. 
    중요도는 댐핑 인자를 반영한 링크 분석 기법으로 계산하며, 댐핑 인자는 이동하지 않는 비율을 반영한다. 
    (중략)
    """
    
    st.info(example_passage)
    
    st.subheader("Q. 윗글을 통해 알 수 있는 내용으로 가장 적절한 것은?")
    choice = st.radio(
        "학생의 선택:",
        ("② 사용자가 링크를 따라 다른 웹 페이지로 이동하는 비율이 높을수록 댐핑 인자가 커진다.", 
         "④ 웹 페이지의 중요도는 다른 웹 페이지에서 받는 값과 다른 웹 페이지에 나눠 주는 값의 합이다.")
    )

    if st.button("제출 및 피드백 받기 ✨"):
        if "④" in choice:
            st.error("아쉽네요! 4번을 선택했군요. (정답: 2번)")
            
            # AI에게 페르소나 부여해서 피드백 생성
            prompt = f"""
            당신은 국어 강사 '도연쌤'입니다.
            학생이 '검색 엔진' 지문에서 '중요도 계산'을 헷갈려 4번을 골랐습니다.
            지문 내용: 중요도는 받는 값의 합이고, 주는 값은 포함되지 않음.
            
            [지시사항]
            1. 공감해주기
            2. [Fact Check]로 오개념 잡아주기
            3. [Tip]으로 기억하는 법 알려주기
            """
            with st.spinner("AI 도연쌤 분석 중..."):
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": "피드백 해줘"}]
                )
                st.markdown(res.choices[0].message.content)
        else:
            st.success("정답입니다! 완벽한 이해도네요. 🎉")

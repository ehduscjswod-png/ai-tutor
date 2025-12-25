import streamlit as st
from openai import OpenAI
import pdfplumber

# 1. 페이지 설정
st.set_page_config(page_title="국멘 AI 튜터", page_icon="🎓", layout="wide")

# 2. 제목
st.title("🎓 [국멘] AI 독서 튜터: 문제 생성기")
st.markdown("학생들은 PDF를 올릴 필요도 없습니다. 원장님이 올려둔 자료로 공부합니다.")

# --- [핵심 변경 사항] API 키 및 PDF 자동 처리 ---

# (1) API 키: 금고(Secrets)에 있으면 그거 쓰고, 없으면 물어봄 (이중 장치)
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    # 로컬 테스트용 (혹시 금고 설정 안 했을 때)
    with st.sidebar:
        api_key = st.text_input("OpenAI API Key", type="password")

# (2) 클라이언트 설정
if api_key:
    client = OpenAI(api_key=api_key)
else:
    st.warning("⚠️ API 키가 설정되지 않았습니다.")
    st.stop() # 키 없으면 여기서 멈춤

# --- [여기부터는 기능 로직] ---

# 사이드바: PDF 업로드 (학생은 안 건드려도 됨 / 원장님이 테스트용으로 올림)
with st.sidebar:
    st.header("📂 자료 업로드")
    uploaded_file = st.file_uploader("교재 PDF (학생에겐 안보이게 처리가능)", type="pdf")

# 메인 로직
if uploaded_file:
    # PDF 텍스트 추출 함수
    def extract_text_from_pdf(file):
        with pdfplumber.open(file) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages):
                if i < 3: # 3페이지만 (비용 절약)
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
            user_question = st.text_input("질문하세요:")
            if user_question:
                with st.spinner("답변 중..."):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": f"지문: {pdf_text}\n질문: {user_question}"}]
                    )
                    st.info(response.choices[0].message.content)

        with tab2:
            if st.button("문제 만들기 🚀"):
                quiz_prompt = f"지문: {pdf_text}\n수능형 3점 문제 1개 출제해줘."
                with st.spinner("출제 중..."):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": quiz_prompt}]
                    )
                    st.markdown(response.choices[0].message.content)

else:
    st.info("👈 왼쪽에서 PDF 파일을 업로드하면 수업이 시작됩니다.")

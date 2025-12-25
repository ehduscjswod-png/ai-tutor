import streamlit as st
from openai import OpenAI
import pdfplumber

# 1. 페이지 설정
st.set_page_config(page_title="국멘 AI 튜터 (Quiz 버전)", page_icon="📝", layout="wide")

# 2. 제목
st.title("🎓 [국멘] AI 독서 튜터: 문제 생성기")
st.markdown("교재 PDF를 분석하여 **변형 문제**를 즉석에서 만들어냅니다.")

# 3. 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.divider()
    st.header("📂 파일 업로드")
    uploaded_file = st.file_uploader("교재 PDF 파일을 올려주세요", type="pdf")

# 4. 메인 로직
if api_key and uploaded_file:
    client = OpenAI(api_key=api_key)

    # PDF 텍스트 추출 함수
    def extract_text_from_pdf(file):
        with pdfplumber.open(file) as pdf:
            text = ""
            # 너무 길면 비용이 많이 나오므로 앞쪽 3페이지만 테스트 (조절 가능)
            for i, page in enumerate(pdf.pages):
                if i < 3: # 0, 1, 2 페이지만 읽음
                    text += page.extract_text()
        return text

    # 텍스트 추출
    if "pdf_text" not in st.session_state:
        with st.spinner("PDF를 읽고 있습니다... (최대 3페이지) 🧐"):
            st.session_state["pdf_text"] = extract_text_from_pdf(uploaded_file)

    pdf_text = st.session_state["pdf_text"]

    # 화면 분할
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📄 지문 내용 확인")
        st.text_area("추출된 텍스트", pdf_text, height=600)

    with col2:
        st.subheader("🤖 AI 선생님 기능")
        
        # 탭을 나눠서 기능 분리
        tab1, tab2 = st.tabs(["💬 질의응답", "📝 변형 문제 생성"])
        
        # [기능 1] 질의응답
        with tab1:
            user_question = st.text_input("지문에 대해 궁금한 점을 물어보세요:")
            if user_question:
                system_prompt = "당신은 친절하고 논리적인 국어 강사 '도연쌤'입니다. 지문을 바탕으로 학생의 질문에 답하세요."
                with st.spinner("답변 생성 중..."):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"지문: {pdf_text}\n\n질문: {user_question}"}
                        ]
                    )
                    st.info(response.choices[0].message.content)

        # [기능 2] 문제 생성 (NEW!)
        with tab2:
            st.markdown("이 지문을 바탕으로 **수능형 변형 문제**를 만듭니다.")
            if st.button("문제 만들어줘! 🚀"):
                quiz_prompt = f"""
                당신은 수능 국어 출제 위원입니다.
                아래 [지문]을 읽고, 수능 국어 독서(비문학) 스타일의 4지 선다형 문제 1개를 출제하세요.
                
                [조건]
                1. 문제는 지문의 핵심 내용을 묻는 추론형 문제로 낼 것.
                2. <보기>가 포함된 3점짜리 고난도 스타일로 낼 것.
                3. 정답과 해설은 맨 아래에 따로 표기할 것. ("정답 및 해설" 섹션으로 분리)
                4. 말투는 실제 시험지처럼 건조하고 명확하게.

                [지문]
                {pdf_text}
                """
                
                with st.spinner("AI가 문제를 출제하고 있습니다... (약 10~20초 소요)"):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "당신은 수능 국어 문제 출제 전문가입니다."},
                            {"role": "user", "content": quiz_prompt}
                        ]
                    )
                    st.markdown(response.choices[0].message.content)

elif not api_key:
    st.warning("👈 왼쪽 사이드바에 API Key를 넣어주세요.")
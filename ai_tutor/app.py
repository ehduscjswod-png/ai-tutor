import streamlit as st
from openai import OpenAI
import pdfplumber
import base64

# 1. 페이지 설정
st.set_page_config(page_title="국멘 AI 학습 시스템", page_icon="🏫", layout="wide")

# 2. API 키 설정
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("OpenAI API Key", type="password")

if not api_key:
    st.warning("⚠️ API 키가 필요합니다.")
    st.stop()

client = OpenAI(api_key=api_key)

# 3. 사이드바 메뉴
with st.sidebar:
    st.title("🎓 국멘 AI 시스템")
    menu = st.radio(
        "기능을 선택하세요:",
        ("📂 교재 분석 (PDF)", "🔥 오답 노트 & 변형 문제 (사진)")
    )
    st.divider()
    st.markdown("Developed by **도연쌤**")

# --- [기능 1] 교재 분석 (PDF) ---
if menu == "📂 교재 분석 (PDF)":
    st.header("📂 교재 전체 분석기")
    st.markdown("교재 PDF를 업로드하면 AI가 내용을 학습하고 질문에 답합니다.")
    
    uploaded_file = st.file_uploader("교재 PDF 업로드", type="pdf")

    if uploaded_file:
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
            user_input = st.text_input("질문하세요:")
            if user_input:
                with st.spinner("답변 중..."):
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": f"지문: {pdf_text}\n질문: {user_input}"}]
                    )
                    st.info(res.choices[0].message.content)

# --- [기능 2] 오답 노트 & 변형 문제 (NEW!) ---
elif menu == "🔥 오답 노트 & 변형 문제 (사진)":
    st.header("🔥 나만의 오답 노트 & 쌍둥이 문제")
    st.markdown("""
    틀린 문제를 **사진 찍어 올리세요.** AI 도연쌤이 **오답 원인을 분석**해주고, 연습할 수 있는 **변형 문제**를 만들어줍니다.
    """)

    # 1. 이미지 업로드
    img_file = st.file_uploader("문제 사진 업로드 (jpg, png)", type=['png', 'jpg', 'jpeg'])
    
    # 2. 학생의 오답 선택
    student_answer = st.text_input("내가 고른 답은? (예: 4번)", placeholder="예: 4번")

    if img_file and student_answer:
        # 이미지를 base64로 변환 (AI에게 보내기 위해)
        img_bytes = img_file.getvalue()
        base64_image = base64.b64encode(img_bytes).decode('utf-8')

        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(img_file, caption="업로드한 문제", use_column_width=True)

        with col2:
            if st.button("분석 및 변형 문제 생성 🚀"):
                
                # AI에게 보낼 프롬프트
                prompt_text = f"""
                당신은 국어 입시 전문가 '도연쌤'입니다.
                학생이 이 문제를 틀렸고, 학생이 고른 답은 '{student_answer}'입니다.
                
                다음 순서로 완벽하게 피드백하세요:
                1. **[정답 및 해설]**: 이 문제의 정답과 풀이를 명확히 설명하세요.
                2. **[오답 진단]**: 학생이 왜 '{student_answer}'을 골랐을지 심리를 분석하고 교정해주세요.
                3. **[변형 문제 생성]**: 이 문제와 논리 구조가 유사한 '쌍둥이 변형 문제'를 1개 출제하세요. (정답 별도 표기)
                """

                with st.spinner("이미지를 분석하고 문제를 만드는 중... (약 15초)"):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt_text},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}"
                                            },
                                        },
                                    ],
                                }
                            ],
                        )
                        st.markdown(response.choices[0].message.content)
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")

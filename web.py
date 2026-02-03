import streamlit as st
from app import load_pdfs, ask_llm

st.set_page_config(
    page_title="AI PDF Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Chatbot đọc tài liệu PDF")
st.write("Chatbot trả lời **dựa trên file PDF trong thư mục data/**")

# Load data một lần
@st.cache_data
def load_data():
    return load_pdfs("data")

context = load_data()

question = st.text_input("💬 Nhập câu hỏi của anh:")

if st.button("Hỏi AI"):
    if not question.strip():
        st.warning("Anh hãy nhập câu hỏi")
    else:
        with st.spinner("AI đang suy nghĩ..."):
            answer = ask_llm(context, question)
        st.success("Câu trả lời")
        st.write(answer)
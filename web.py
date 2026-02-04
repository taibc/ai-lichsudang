import streamlit as st
from app import  ask_llm

st.set_page_config(
    page_title="AI LICH SU DANG",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI LICH SU DANG")
st.write("Chatbot trả lời **dựa trên các nguồn link trên mạng**")


question = st.text_input("💬 Nhập câu hỏi của anh:")

if st.button("Hỏi AI"):
    if not question.strip():
        st.warning("Anh hãy nhập câu hỏi")
    else:
        with st.spinner("AI đang suy nghĩ..."):
            answer = ask_llm(context, question)
        st.success("Câu trả lời")
        st.write(answer)
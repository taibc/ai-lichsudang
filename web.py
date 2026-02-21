import streamlit as st
from app import  ask_llm, build_context


st.set_page_config(
    page_title="AI LICH SU DANG",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI LICH SU DANG")
st.write("Chatbot trả lời **dựa trên các nguồn link trên mạng**")


question = st.text_input("💬 Nhập câu hỏi của anh:")

context = build_context(
    web_urls=[
       # "https://vnexpress.net/trien-khai-nghi-quyet-va-kien-toan-nhan-su-sau-dai-hoi-xiv-5010791.html",
       # "https://vnexpress.net/thoi-su/dai-hoi-dang-toan-quoc-lan-thu-14/van-kien"
       "https://tapchilichsudang.vn/",
       "https://tapchilichsudang.vn/nghien-cuu-ho-chi-minh.html",
       "https://tapchilichsudang.vn/tim-hieu-tu-tuong-ho-chi-minh-ve-giao-duc.html",
       "https://dangcongsan.vn/"
        
    ],
    youtube_urls=[
        "https://www.youtube.com/watch?v=EwqpeFvvzko&pp=0gcJCZEKAYcqIYzv"
    ]
)

if st.button("Hỏi AI"):
    if not question.strip():
        st.warning("Anh hãy nhập câu hỏi")
    else:
        with st.spinner("AI đang suy nghĩ..."):
            answer = ask_llm(context, question)
        #print(context[:3000])
        #st.text(context[:3000])
        st.success("Câu trả lời")
        st.write(answer)
       
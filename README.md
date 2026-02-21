# AI LỊCH SỬ ĐẢNG (Sư dụng OpenAI)

Chatbot web sử dụng OpenAI để đọc và trả lời câu hỏi về lịch sử Đảng.

Sử dụng các bước dưới đây để chạy ứng dụng

1. Crawl data về máy local
D:\4. R&D\Github\ai-lichsudang> python crawl.py
2. Build FAISS index từ các file txt crawed, sẵn sàng cho Streamlit cloud
python build_embeddings.py
3. Commit changed source from local to Github
4. Reboot project Streamlit cloud
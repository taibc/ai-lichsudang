import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_websites(urls: list[str]) -> str:
    texts = []

    for url in urls:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # bỏ script, style
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        texts.append(text)

    return "\n".join(texts)

def extract_video_id(url: str) -> str | None:
    match = re.search(r"(v=|youtu.be/)([^&?/]+)", url)
    return match.group(2) if match else None


def load_youtube(video_urls: list[str]) -> str:
    texts = []

    for url in video_urls:
        video_id = extract_video_id(url)
        if not video_id:
            continue

        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=["vi", "en"]
            )
            texts.append(" ".join(item["text"] for item in transcript))

        except TranscriptsDisabled:
            # Video không có subtitle → bỏ qua
            continue

        except Exception:
            continue

    return "\n".join(texts)

def build_context(web_urls=None, youtube_urls=None) -> str:
    parts = []

    if web_urls:
        parts.append(load_websites(web_urls))

    if youtube_urls:
        parts.append(load_youtube(youtube_urls))

    return "\n".join(parts)

 

def ask_llm(context: str, question: str) -> str:
    
    
    prompt = f"""
Bạn là một AI tra cứu thông tin KHÉP KÍN.

QUY TẮC BẮT BUỘC:
- CHỈ được sử dụng thông tin trong <CONTEXT>
- TUYỆT ĐỐI KHÔNG sử dụng kiến thức bên ngoài
- Nếu thông tin không có trong CONTEXT, hãy trả lời đúng nguyên văn:
  "Không tìm thấy thông tin trong các nguồn đã cấu hình."

<CONTEXT>
{context}
</CONTEXT>

Câu hỏi: {question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def ask_llm_public(context: str, question: str) -> str:
    
    
    prompt = f"""
Chỉ trả lời dựa trên thông tin sau:

{context}

Câu hỏi: {question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a closed-domain question answering system."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
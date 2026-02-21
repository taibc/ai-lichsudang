import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import hashlib
import json

# -----------------------------
# CONFIG
# -----------------------------

START_URLS = [
    "https://tapchilichsudang.vn/nghien-cuu-ho-chi-minh.html",
    "https://dangcongsan.vn/"
]

ALLOWED_DOMAINS = [
    "tapchilichsudang.vn",
    "dangcongsan.vn"
]

MAX_ARTICLES_PER_SOURCE = 30
OUTPUT_DIR = "data/web"
REQUEST_DELAY = 1  # seconds

KEYWORDS = [
    "Hồ Chí Minh",
    "Đại hội",
    "Cách mạng",
    "lịch sử Đảng",
    "biên niên"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# -----------------------------
# UTILITIES
# -----------------------------

def is_allowed_domain(url):
    domain = urlparse(url).netloc
    return any(allowed in domain for allowed in ALLOWED_DOMAINS)


def contains_keywords(text):
    text_lower = text.lower()
    return any(k.lower() in text_lower for k in KEYWORDS)


def clean_text(soup):
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n").strip()


def generate_filename(url):
    h = hashlib.md5(url.encode()).hexdigest()
    return h + ".txt"


def save_article(text, metadata):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = generate_filename(metadata["url"])
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("----- METADATA -----\n")
        f.write(json.dumps(metadata, ensure_ascii=False, indent=2))
        f.write("\n\n----- CONTENT -----\n\n")
        f.write(text)

    print(f"Saved: {filepath}")


# -----------------------------
# MAIN CRAWL LOGIC
# -----------------------------

def crawl_source(start_url):
    print(f"\nCrawling source: {start_url}")

    try:
        res = requests.get(start_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        print("Error fetching:", e)
        return

    links = set()

    for a in soup.find_all("a", href=True):
        full_url = urljoin(start_url, a["href"])
        if is_allowed_domain(full_url):
            links.add(full_url)

    count = 0

    for link in links:
        if count >= MAX_ARTICLES_PER_SOURCE:
            break

        try:
            res = requests.get(link, headers=HEADERS, timeout=10)
            page = BeautifulSoup(res.text, "html.parser")
            text = clean_text(page)

            if len(text) < 500:
                continue

            if not contains_keywords(text):
                continue

            metadata = {
                "source": urlparse(link).netloc,
                "url": link,
                "crawl_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            save_article(text, metadata)
            count += 1
            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print("Skip:", link, "| Error:", e)


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    for url in START_URLS:
        crawl_source(url)

    print("\nCrawl finished.")
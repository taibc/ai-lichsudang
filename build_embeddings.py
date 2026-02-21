import os
import json
import faiss
import numpy as np
from tqdm import tqdm
from openai import OpenAI

# -----------------------------
# CONFIG
# -----------------------------

DATA_DIR = "data/web"
INDEX_DIR = "vector_store"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
EMBED_MODEL = "text-embedding-3-small"

client = OpenAI()


# -----------------------------
# TEXT SPLITTING
# -----------------------------

def split_text(text, chunk_size=800, overlap=150):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# -----------------------------
# LOAD DOCUMENTS
# -----------------------------

def load_documents():
    documents = []

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(DATA_DIR, filename)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            metadata_part = content.split("----- CONTENT -----")[0]
            content_part = content.split("----- CONTENT -----")[1]

            metadata_json = metadata_part.replace("----- METADATA -----", "").strip()
            metadata = json.loads(metadata_json)

        except Exception:
            metadata = {"source": "unknown", "url": "unknown"}
            content_part = content

        documents.append((content_part.strip(), metadata))

    return documents


# -----------------------------
# BUILD EMBEDDINGS
# -----------------------------

def embed_texts(texts):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )
    return [np.array(e.embedding, dtype="float32") for e in response.data]


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    print("Loading documents...")
    docs = load_documents()

    all_chunks = []
    all_metadata = []

    print("Splitting into chunks...")
    for text, metadata in docs:
        chunks = split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadata.append(metadata)

    print(f"Total chunks: {len(all_chunks)}")

    print("Generating embeddings...")
    embeddings = []

    # batch processing (important)
    BATCH_SIZE = 50

    for i in tqdm(range(0, len(all_chunks), BATCH_SIZE)):
        batch = all_chunks[i:i+BATCH_SIZE]
        batch_embeddings = embed_texts(batch)
        embeddings.extend(batch_embeddings)

    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    os.makedirs(INDEX_DIR, exist_ok=True)

    faiss.write_index(index, os.path.join(INDEX_DIR, "index.faiss"))

    with open(os.path.join(INDEX_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump({
            "chunks": all_chunks,
            "metadata": all_metadata
        }, f, ensure_ascii=False)

    print("Embedding build complete.")
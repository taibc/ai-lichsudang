import streamlit as st
import faiss
import numpy as np
import json
from openai import OpenAI

# -----------------------------
# CONFIG
# -----------------------------

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 5

client = OpenAI()

# -----------------------------
# LOAD VECTOR STORE
# -----------------------------

@st.cache_resource
def load_vector_store():
    index = faiss.read_index("vector_store/index.faiss")

    with open("vector_store/metadata.json", "r", encoding="utf-8") as f:
        store = json.load(f)

    chunks = store["chunks"]
    metadata = store["metadata"]

    return index, chunks, metadata


index, chunks, metadata = load_vector_store()

# -----------------------------
# EMBED QUERY
# -----------------------------

def embed_query(query):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=query
    )
    return np.array(response.data[0].embedding, dtype="float32").reshape(1, -1)


# -----------------------------
# RETRIEVE CONTEXT
# -----------------------------

def retrieve_context(query):
    query_vector = embed_query(query)

    distances, indices = index.search(query_vector, TOP_K)

    results = []
    for i in indices[0]:
        results.append({
            "text": chunks[i],
            "metadata": metadata[i]
        })

    return results


# -----------------------------
# GENERATE ANSWER
# -----------------------------

def generate_answer(query, contexts):
    context_text = "\n\n".join([c["text"] for c in contexts])

    system_prompt = """
You are a political-history research assistant.
Answer based only on provided context.
If information is not in context, say you do not know.
Cite sources by referencing their domain.
"""

    user_prompt = f"""
Context:
{context_text}

Question:
{query}
"""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


# -----------------------------
# STREAMLIT UI
# -----------------------------

st.set_page_config(page_title="Political History Research AI")
st.title("📚 Political History Research AI")

query = st.text_input("Ask a question about political history:")

if query:
    with st.spinner("Searching..."):
        contexts = retrieve_context(query)
        answer = generate_answer(query, contexts)

    st.subheader("Answer")
    st.write(answer)

    st.subheader("Sources")

    shown = set()
    for c in contexts:
        source = c["metadata"].get("source", "unknown")
        url = c["metadata"].get("url", "")

        if url not in shown:
            st.markdown(f"- **{source}**: {url}")
            shown.add(url)
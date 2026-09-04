# index.py
import json
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
#from langchain_ollama import OllamaEmbeddings
# pyrefly: ignore [missing-import]
from langchain_huggingface import HuggingFaceEmbeddings   # ← add
from chunking import chunk_sections


def build_index(strategy: str = "paragraphs") -> InMemoryVectorStore:
    with open("10k_aapl.json") as f:
        data = json.load(f)

    chunks = chunk_sections(data, strategy)
    docs = [
        Document(page_content=c["text"], metadata=c)   # whole dict rides along
        for c in chunks
    ]

    store = InMemoryVectorStore(
    HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")             # ← add
)
    store.add_documents(docs)
    print(f"indexed {len(docs)} chunks ({strategy})")
    return store


if __name__ == "__main__":
    store = build_index("paragraphs")
    for h in store.similarity_search("total net sales fiscal 2025", k=3):
        print(h.metadata["id"], "→", h.page_content[:80].replace("\n", " "))
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import json

def by_paragraphs(text: str, max_chars: int = 1800) -> list[str]:
    paragraphs = text.split("\n")
    chunks = []
    current = ""                      # the chunk being built

    for para in paragraphs:
        would_overflow = len(current) + len(para) > max_chars
        if would_overflow and current:
            chunks.append(current)    # close the full chunk
            current = ""              # start a new one
        current += para + "\n"

    if current:                       # don't lose the last one
        chunks.append(current)

    return chunks


def fixed_size(text: str, max_chars: int = 1800, overlap: int = 150) -> list[str]:
    """Structure-blind: cut every max_chars, stepping back `overlap`
    so neighbouring chunks share some context across the cut."""
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start : start + max_chars])
        start += max_chars - overlap
    return chunks


STRATEGIES = {
    "paragraphs": by_paragraphs,
    "fixed": fixed_size,
}


def chunk_sections(data: dict, strategy: str = "paragraphs", **kw) -> list[dict]:
    splitter = STRATEGIES[strategy]
    chunks = []
    for section, text in data["sections"].items():
        for i, piece in enumerate(splitter(text, **kw)):chunks.append({
                "id": f"{data['ticker']}-{section}-{i}",
                "text": piece,
                "ticker": data["ticker"],
                "accession": data["accession"],
                "section": section,
                "strategy": strategy,
            })
    return chunks


if __name__ == "__main__":
    import json
    with open("10k_aapl.json") as f:
        data = json.load(f)
    for name in STRATEGIES:
        print(name, len(chunk_sections(data, name)), "chunks")



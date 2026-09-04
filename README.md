# Filing Desk — a grounded RAG over SEC filings, scored against real ground truth

A small retrieval-augmented generation (RAG) system that answers financial questions
about Apple's latest annual report (10-K), with two properties most RAG demos skip:

1. **It refuses when it doesn't know.** Answers come only from retrieved passages,
   with citations. If the passages don't contain the answer, the system replies
   `INSUFFICIENT_CONTEXT` instead of guessing.
2. **It is evaluated against machine-readable ground truth, not vibes.** Every
   numeric answer is checked against SEC XBRL `companyfacts` data — the same
   figures Apple filed, pulled straight from the SEC API — pinned to the exact
   filing (accession number) the RAG indexed. No LLM judges the LLM.

## Pipeline

```
ingest.py                fetch the latest 10-K from SEC EDGAR (edgartools) -> 10k_aapl.json
chunking.py              split sections into chunks (two swappable strategies: paragraphs, fixed-size)
index.py                 embed chunks (BAAI/bge-small-en-v1.5, local) -> in-memory vector store
retrieval.py             ask(question): retrieve top-k chunks -> Gemini answers with citations or refuses
retrieval_validation.py  ground truth: 9 financial concepts from the SEC XBRL companyfacts API
golden_set.py            builds the test set: 9 answerable + 3 deliberately unanswerable questions
evals.py                 runs every question through the RAG and scores it automatically
```

## Results (Apple 10-K, FY2025, k=5)

| Metric | Score |
|---|---|
| Numeric accuracy vs XBRL (0.5% relative tolerance) | **8/9** |
| Correct refusals on unanswerable questions | **3/3** |

Answerable and unanswerable questions are scored separately on purpose: a system
that refuses everything gets perfect refusals and zero accuracy, and a blended
score would hide that.

## Failure analysis

The first eval run scored 7/9. Both failures were diagnosed by walking backwards
through the pipeline: answer → retrieved chunks → chunk store → source text.

**Gross profit (fixed).** The model refused (`INSUFFICIENT_CONTEXT`). The correct
chunk — the MD&A gross margin table — existed in the index but ranked 4th, just
outside the original top-3 retrieval window. A vocabulary mismatch contributed:
the question says "gross profit," Apple's filing calls the same line "gross
margin." Raising k from 3 to 5 fixed it. This is a recall@k problem, and the
trade-off is real: each increment of k adds tokens (cost) and noise to every call.

**Cost of sales (documented, not fixed).** Also a refusal. The figure exists in
the index — inside the consolidated income statement chunk — but that chunk ranks
15th for the question. Chunks that are mostly tables of bare numbers produce weak,
generic embeddings, so prose chunks that merely *discuss* costs outrank the table
that contains the answer. This is a well-known weakness of pure semantic search.
The standard fixes are hybrid retrieval (keyword/BM25 + embeddings) or
table-aware chunking; both are deliberately out of scope for v1 rather than
papered over by raising k to 16.

Notably, both failures were honest refusals, not hallucinated numbers — the
grounding prompt held even when retrieval failed.

## Running it

```bash
pip install edgartools langchain langchain-huggingface langchain-google-genai python-dotenv
echo "GOOGLE_API_KEY=your-key-here" > .env   # never commit .env

python ingest.py                 # fetch and cache the 10-K
python retrieval_validation.py   # fetch XBRL ground truth
python golden_set.py             # build golden_set.json
python evals.py                  # run the evaluation -> eval_results.json
```

Embeddings run locally (sentence-transformers); generation uses Gemini
(`gemini-3.6-flash`, temperature 0). SEC APIs require a descriptive
User-Agent with a real email address.

## Known limitations / future work

- Hybrid retrieval or table-aware chunking to fix the cost-of-sales case
- A numeric grounding guard: parse every figure out of an answer and reject it
  unless it appears in a cited chunk (in progress)
- recall@k as a first-class metric (requires labeling which chunk holds each answer)
- A second company and a chunking-strategy ablation using this same eval harness

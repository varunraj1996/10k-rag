from langchain_core.prompts import ChatPromptTemplate
import index
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import guardrails
from dotenv import load_dotenv

load_dotenv()

store = index.build_index()

def build_chain():
    PROMPT = ChatPromptTemplate.from_template(
    "Answer using ONLY the passages below. Cite them as [n].\n"
    "If the passages do not contain the answer, reply exactly: INSUFFICIENT_CONTEXT\n\n"
    "{context}\n\nQuestion: {question}"
    )
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)
    return PROMPT | llm | StrOutputParser()

def ask(question, k=5):
    if not guardrails.check_input(question):
        return "REFUSED", []
    docs = store.similarity_search(question, k=k)
    context = "\n\n".join(f"[{i}] {d.page_content}" for i, d in enumerate(docs, 1))
    answer = build_chain().invoke({"context": context, "question": question})
    if "INSUFFICIENT_CONTEXT" not in answer and not guardrails.grounded(answer, docs):
        return "INSUFFICIENT_CONTEXT", docs
    return answer, docs

if __name__ == "__main__":
    for q in ["What was Apple's total net sales in fiscal 2025?",
              "What was Apple's employee attrition rate in fiscal 2025?"]:
        answer, docs = ask(q)
        print("Q:", q)
        print("A:", answer)
        print("cited from:", [d.metadata["id"] for d in docs], "\n")
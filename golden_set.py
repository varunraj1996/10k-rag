import json
from retrieval_validation import get_facts

QUESTIONS = {
    "total_net_sales": "What was Apple's total net sales in fiscal 2025?",
    "net_income": "What was Apple's net income in fiscal 2025?",
    "operating_income": "What was Apple's operating income in fiscal 2025?",
    "gross_profit": "What was Apple's gross profit in fiscal 2025?",
    "rd_expense": "How much did Apple spend on research and development in fiscal 2025?",
    "total_assets": "What were Apple's total assets at the end of fiscal 2025?",
    "total_liabilities": "What were Apple's total liabilities at the end of fiscal 2025?",
    "cash_and_equivalents": "How much cash and cash equivalents did Apple hold at the end of fiscal 2025?",
    "cost_of_sales": "What was Apple's cost of sales in fiscal 2025?",
}

UNANSWERABLE = [
    "What was Apple's employee attrition rate in fiscal 2025?",
    "What will Apple's revenue be in fiscal 2026?",
    "What was Apple's revenue from customers in Brazil in fiscal 2025?",
]

def build_golden_set() -> list[dict]:
    facts = get_facts("AAPL", 2025)
    cases = []
    for name, question in QUESTIONS.items():
        cases.append({
            "question": question,
            "answer": facts[name]["value"],
            "kind": "answerable"
        })

    for question in UNANSWERABLE:
        cases.append({
            "question": question,
            "answer": "INSUFFICIENT_CONTEXT",
            "kind": "unanswerable"
        })
    return cases


if __name__ == "__main__":
    cases = build_golden_set()
    with open("golden_set.json", "w") as f:
        json.dump(cases, f, indent=2)
    print(f"saved {len(cases)} cases "
          f"({sum(c['kind'] == 'answerable' for c in cases)} answerable)")
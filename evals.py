# evals.py
import json
import re

import retrieval

SCALE = {"thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12}


def extract_numbers(text: str) -> list[float]:
    out = []
    for m in re.finditer(r"\$?(\d[\d,]*(?:\.\d+)?)\s*(thousand|million|billion|trillion)?",
                         text.lower()):
        value = float(m.group(1).replace(",", ""))
        if m.group(2):
            value *= SCALE[m.group(2)]
        out.append(value)
    return out


def similar_numbers(got: float, expected: float, tol: float = 0.005) -> bool:
    return abs(got - expected) <= tol * abs(expected)


def run_eval() -> None:
    with open("golden_set.json") as fh:                    
        cases = json.load(fh)                              

    correct_ans = total_ans = 0                            
    correct_ref = total_ref = 0                            

    for obj in cases:
        answer, docs = retrieval.ask(obj["question"])

        if obj["kind"] == "answerable":
            total_ans += 1
            nums = extract_numbers(answer)
            expected = obj["answer"]                       
            ok = any(similar_numbers(n, expected)          
                     for n in nums)                        
            if ok:
                correct_ans += 1
        else:  # unanswerable
            total_ref += 1
            ok = "INSUFFICIENT_CONTEXT" in answer
            if ok:
                correct_ref += 1

        result = "PASS" if ok else "FAIL"
        obj["model_answer"] = answer                       
        obj["result"] = result                             
        print(f"{result} | {obj['kind']:12} | {obj['question']}")

    print(f"\naccuracy: {correct_ans}/{total_ans}   "
          f"correct refusals: {correct_ref}/{total_ref}")

    with open("eval_results.json", "w") as fh:
        json.dump(cases, fh, indent=2)


if __name__ == "__main__":                                 
    run_eval()                                             
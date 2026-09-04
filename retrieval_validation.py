# answer_key.py
import json
import urllib.request

EMAIL = "varunrajvavilala@gmail.com"

CIK = {"AAPL": "0000320193"}         # ticker -> SEC id, zero-padded to 10 digits

# friendly name -> the official XBRL tag
XBRL_TAGS = {
    "total_net_sales": "RevenueFromContractWithCustomerExcludingAssessedTax",
    "net_income": "NetIncomeLoss",
    "operating_income": "OperatingIncomeLoss",
    "gross_profit": "GrossProfit",
    "rd_expense": "ResearchAndDevelopmentExpense",
    "total_assets": "Assets",
    "total_liabilities": "Liabilities",
    "cash_and_equivalents": "CashAndCashEquivalentsAtCarryingValue",
    "cost_of_sales": "CostOfGoodsAndServicesSold",
    "services_gross_revenue": "SalesRevenueServicesGross"    
}


def get_facts(ticker: str, fiscal_year: int) -> dict:
    """Official figures from SEC XBRL — used to validate results of RAG."""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK[ticker]}.json"
    req = urllib.request.Request(url, headers={"User-Agent": EMAIL})
    with urllib.request.urlopen(req) as resp:
        raw = json.load(resp)

    facts = {}
    for name, tag in XBRL_TAGS.items():
        entries = raw["facts"]["us-gaap"][tag]["units"]["USD"]
        # keep: from a 10-K, for our fiscal year, covering the FULL year ("FY")
        matches = [e for e in entries
                   if e.get("form") == "10-K"
                   and e.get("fy") == fiscal_year
                   and e.get("fp") == "FY"]
        if matches:
            best = matches[-1]           # last one = most recently filed
            facts[name] = {
                "value": best["val"],
                "accession": best["accn"],   # WHICH filing said this
            }
    return facts


if __name__ == "__main__":
    facts = get_facts("AAPL", 2025)
    for name, f in facts.items():
        print(f"{name}: ${f['value']:,}   (from filing {f['accession']})")
        
      # grep by keyword
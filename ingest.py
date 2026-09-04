# ingest.py
# pyrefly: ignore [missing-import]
from edgar import Company, set_identity
import json

EMAIL = "varunrajvavilala@gmail.com"   # EDGAR requires a real contact


def fetch_10k(ticker: str) -> dict:
    """Fetch the latest 10-K for `ticker` from SEC EDGAR."""
    set_identity(EMAIL)

    filing = Company(ticker).get_filings(form="10-K").latest(1)
    tenk = filing.obj()                      # parse into Item sections

    sections = {}
    for item in tenk.items:                  # ["Item 1", "Item 1A", ...]
        text = tenk[item]
        if text:                              # some items are empty — skip them
            sections[item] = text

    return {
        "ticker": ticker,
        "accession": filing.accession_no,    # pins WHICH document, forever
        "period": str(filing.period_of_report),  # fiscal year end — NOT filing date
        "sections": sections,
    }


if __name__ == "__main__":
    data = fetch_10k("AAPL")
    with open('10k_aapl.json', 'w') as f:
        json.dump(data, f)
    print(data["accession"], data["period"], len(data["sections"]), "sections")

# MADT 7202 mid-term: 13F fund-similarity network

Question: which four US managers should a Thai equity fund follow each quarter, given that some managers hold near-identical books?

Source: SEC EDGAR Form 13F-HR information tables (public filings), quarters ended 2026-03-31 and 2026-06-30, 24 managers.
Access: data.sec.gov submissions API and www.sec.gov/Archives/edgar/data (allowed by sec.gov/robots.txt), declared User-Agent, at most 4 requests/s.

## Reproduce
```bash
export SEC_UA="Your Name your@email.com"          # SEC fair-access policy: declare a contact
python3 scripts/resolve.py data/resolved.json                # 13F-HR accession numbers per fund
python3 scripts/fetch13f.py data/resolved.json data/raw      # download + parse -> data/raw/holdings_raw.csv
python3 scripts/prep.py data                                 # drop options/ETFs, fix $-thousands filers -> data/holdings_clean.csv
python3 scripts/analyze2.py data scripts                     # raw vs IDF cosine, cutoff sweep, Q1 vs Q2, hub-drop check
python3 scripts/figure2.py data scripts .                    # network.png
python3 scripts/build_pdf2.py report.pdf network.png "<repo url>"
```
`data/` already holds the outputs used in the report, so the first three steps can be skipped.
To re-run for Q3 2026, change the two period dates (`2026-06-30`, `2026-03-31`) in `scripts/resolve.py`, `scripts/analyze2.py` and `scripts/figure2.py`.

## Method
- Node = fund. Edge weight = cosine of portfolio-weight vectors; each issuer weighted by IDF = ln(24 / funds holding it); issuer = first 6 CUSIP digits.
- Alternative tested: raw count of shared issuers (rewards portfolio breadth; see report section 4).
- Pruning: cosine >= 0.10 (31 of 276 pairs). Robustness: cutoffs 0.05/0.10/0.15, Q1 vs Q2, dropping issuers held by 8+ funds.
- Limits: long US-listed equity only, up to 45-day filing lag, hand-picked managers, no return back-test.

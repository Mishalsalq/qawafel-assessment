# Verification record

Verified on 24 October 2026 using Python 3.12 on Windows.

## Automated checks

- `python -m pytest -q`: **35 passed** on the completed prototype.
- `python -m pip check`: **No broken requirements found**.
- Generator checks: deterministic rows with seed 42; 667 unique invoice IDs; 24 fictional customers; all 12 months; exact net + VAT = gross; valid payment chronology.
- Hand-calculated four-invoice fixture: gross SAR 1,150; settlements SAR 575; outstanding SAR 575; overdue SAR 230. Results match.
- Arithmetic edge cases: aging boundaries, all-paid/all-unpaid cohorts, zero denominators, date equal to snapshot, and total reconciliation.
- Ingestion checks: missing/unsupported columns, duplicate IDs and CSV/XLSX headers, conflicting customer names, nonfinite/negative/over-precision amounts, invalid/out-of-range dates, and CSV/XLSX equivalence.
- AI checks: reproducible results, no mutation of financial records, finite scores, a sensitivity case with an extreme synthetic amount, and small-cohort skip. These do not establish fraud/default accuracy.
- Streamlit AppTest: sample loads, expected cards display, a customer filter runs, and the upload empty state displays without an exception.

## Actual browser review

Verified the running Streamlit application using Microsoft Edge/Playwright:

- Sample page and both rendered charts load.
- At 1440x1100, no horizontal document overflow and no clipped metric values after typography correction.
- AI review table displays.
- Reviewer summary downloads and contains exact sample totals and the bank-verification limitation.
- Sample XLSX upload succeeds and displays 667 validated invoices.
- Uploading a duplicate-invoice CSV displays validation issues and removes all financial metrics after the rerun completes.
- No browser JavaScript errors in that scenario.

A synthetic overview screenshot is included under `docs/assets/`.

## Written artifact

Generated the written assessment with reportlab and verified extracted text and rendered page layouts. The PDF includes all assessment tasks, the process figure, assumptions/boundaries, candidate attribution, and AI disclosure.

## Public delivery verified

- Published to [Mishalsalq/qawafel-assessment](https://github.com/Mishalsalq/qawafel-assessment), a public repository.
- Anonymous HTTP requests, with no authentication or stored session, returned 200 for the repository, README, sample CSV, dashboard screenshot, and [written PDF](https://raw.githubusercontent.com/Mishalsalq/qawafel-assessment/main/output/pdf/qawafel-assessment.pdf).
- Downloaded PDF bytes exactly match the locally rendered/reviewed PDF.
- Published files were matched to the local Git tree using object hashes.
- Following candidate-attribution text changes, the existing app and analysis checks passed: `python -m pytest tests/test_app.py tests/test_analysis.py -q` (**5 passed**).

## Verification boundaries

- No live deployment, real bank calls, production security, PDF statement extraction, or receipt reconciliation was implemented or tested.
- No labeled financial ML evaluation or credit-policy validation was performed.

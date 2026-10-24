# Verification record

Executed on 24 October 2026 using Python 3.12 on Windows. These are actual local results, not claims about untested hosting.

## Automated checks

- `python -m pytest -q`: **35 passed** on the final code revision before packaging.
- `python -m pip check`: **No broken requirements found**.
- Generator checks: deterministic rows with seed 42; 667 unique invoice IDs; 24 fictional customers; all 12 months; exact net + VAT = gross; valid payment chronology.
- Hand-calculated four-invoice fixture: gross SAR 1,150; settlements SAR 575; outstanding SAR 575; overdue SAR 230. Results match.
- Arithmetic edge cases: aging boundaries, all-paid/all-unpaid cohorts, zero denominators, date equal to snapshot, and total reconciliation.
- Ingestion checks: missing/unsupported columns, duplicate IDs and CSV/XLSX headers, conflicting customer names, nonfinite/negative/over-precision amounts, invalid/out-of-range dates, and CSV/XLSX equivalence.
- AI checks: reproducible results, no mutation of financial records, finite scores, a sensitivity case with an extreme synthetic amount, and small-cohort skip. These do not establish fraud/default accuracy.
- Streamlit AppTest: sample loads, expected cards display, a customer filter runs, and the upload empty state displays without an exception.

## Actual browser review

Started Streamlit locally on loopback port 8501. Used headless Microsoft Edge/Playwright because the in-app browser control did not respond. Verified:

- Sample page and both rendered charts load.
- At 1440x1100, no horizontal document overflow and no clipped metric values after typography correction.
- AI review table displays.
- Reviewer summary downloads and contains exact sample totals and the bank-verification limitation.
- Sample XLSX upload succeeds and displays 667 validated invoices.
- Uploading a duplicate-invoice CSV displays validation issues and removes all financial metrics after the rerun completes.
- No browser JavaScript errors in that scenario.

Local QA images and temporary bad-file fixtures are excluded from Git. A synthetic overview screenshot is included under `docs/assets/` for convenience.

## Written artifact

Generated the written assessment with reportlab, extracted its text, rendered all **8 pages**, and visually inspected the complete page set plus the dense data-model table and process figure at readable resolution. Corrected separated headings, numbered lists, an orphan final page, and clipped dashboard values. The final PDF includes all assessment tasks, the process figure, assumptions/boundaries, and AI disclosure.

## Not verified / remaining delivery checks

- Public repository/PDF URLs and anonymous access must be checked after publishing; local app verification does not prove hosting.
- No live deployment, real bank calls, production security, PDF statement extraction, or receipt reconciliation was implemented or tested.
- No labeled financial ML evaluation or credit-policy validation was performed.
- The submission form has not been sent. The candidate must review the work and provide any personal/application fields themselves before submission.

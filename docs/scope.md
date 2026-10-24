# Assessment scope and delivery checkpoints

Status: checkpoints 1-9 complete locally; checkpoint 10 awaits publication and public-link checks. Consult `verification.md` for actual results rather than treating planned scope as implemented behavior.

## Verified brief

- Deadline: 24 October 2026, 23:59, Asia/Riyadh (UTC+3).
- Task 1: user stories and acceptance criteria, discovery questions, data risks.
- Task 2: data model, API specification, end-to-end process diagram.
- Task 3: working financing-insights prototype, believable synthetic invoices spanning 12 months, sample data, documented assumptions. This task carries the most weight.
- Task 4: safe bank integration despite 3% incorrect status responses and no sandbox; include a bank-call message.
- Task 5: optional automation roadmap; omission is explicitly not penalized.
- Written answers: one publicly accessible Google Doc, Notion page, or PDF link.
- Prototype: accessible GitHub repository or live link, plus README and AI-use disclosure.
- Fictional business and customer data only. AI tools are permitted.

## MVP decision

Build Wholesaler Financing Insights using Python, pandas, and Streamlit. Target the Qawafel financing reviewer preparing evidence for a bank. Use a fictional wholesaler's sales invoices; keep those separate from the applicant's purchases and financing disbursements.

Provide CSV/XLSX sample data and upload, explicit validation, sales and collection metrics, receivables aging, customer concentration, monthly trends, and an exportable reviewer summary. Clearly label recorded collections as unverified against bank statements. Keep arithmetic deterministic and explain every material metric.

Proposed AI feature: lightweight unsupervised invoice anomaly detection if dependencies and time permit. Flags prioritize manual inspection and must never be described as fraud findings or credit decisions. The brief names an AI prototype but does not prescribe an LLM or a trained credit model. Document the final implemented approach accurately.

Bank-statement extraction, bank reconciliation, real bank submission, authentication, and durable storage belong to the proposed production design. They are outside the initial invoice-analysis prototype. Do not claim these are implemented.

## Working assumptions to validate in implementation

- Use the last 12 completed calendar months: October 2025 through September 2026, with a fixed as-of date of 30 September 2026 for reproducibility.
- One fictional seller, SAR, sales invoices only. Document tax treatment explicitly; never call gross invoice value net revenue.
- Model full payment or unpaid invoices initially; partial payments and credit notes require explicit future handling rather than fabricated support.
- Derive paid/open/overdue status from dates and settlement evidence as of the snapshot date.
- Avoid a fabricated credit score or approval recommendation. Present evidence, limitations, and reviewer questions.
- A company partnership mentioned in public marketing does not establish the assessment bank's identity or API contract.

## Ten approximate checkpoints

| Completion | Deliverable | Evidence |
| --- | --- | --- |
| 10% | Read brief, review transferred context, research company, agree focused scope | This scope and company research notes |
| 20% | Environment and reproducible synthetic invoices | Generator, CSV/XLSX, 12-month checks |
| 30% | Import validation and data-quality reporting | Invalid dates, amounts, IDs, and duplicate cases exercised |
| 40% | Financial analysis | Hand-checkable arithmetic tests and reconciled totals |
| 50% | Usable dashboard | App launches, sample data loads, charts display |
| 60% | Anomaly review and summary export | Explainable flags, downloadable evidence, honest limitations |
| 70% | Task 1 and production technical specification | Stories, acceptance criteria, model, APIs, process diagram |
| 80% | Integration judgment and concise bonus | Unknown-state handling, no unsafe resubmission, bank call |
| 90% | End-to-end verification and submission packaging | Tests, interface review, README, written PDF, AI disclosure |
| 100% | Accessible links and interview walkthrough | Access checks, submission checklist, explanation grounded in implementation |

Each checkpoint receives a short Saudi Arabic explanation of what changed, why, and what was verified. Percentages describe milestones, not measured effort. Prioritize a reliable complete core before optional polish. Check publication/authentication availability early enough to avoid a last-minute delivery blocker.

## Current environment check

Bundled Python, pandas, openpyxl, pypdf, pypdfium2, and reportlab are available. Streamlit, Plotly, scikit-learn, and pytest are absent from the bundled Python environment at initial inspection. Dependency installation and application execution have not yet been attempted. Do not report tests or application behavior as verified.

Update: a project-local Python 3.12 virtual environment was subsequently created and dependencies installed. Streamlit, pandas, NumPy, Altair, openpyxl, and scikit-learn support the app; pytest and reportlab support verification and the PDF. Plotly was unnecessary. All 35 tests and actual browser scenarios in `verification.md` passed locally.

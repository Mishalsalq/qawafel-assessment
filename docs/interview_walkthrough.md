# Technical walkthrough and interview preparation

**Prepared for Mishal Saad**

## Five-minute demonstration

1. State the business problem: help a financing reviewer understand a wholesaler's sales and collections without confusing invoices with bank-confirmed income.
2. Open the default sample. Explain the fixed snapshot, 12-month coverage, 667 fictional invoices, and 24 customers.
3. Explain the four cards. Net sales exclude VAT. Recorded settlements include VAT. Outstanding includes not-yet-due invoices; overdue is only the late subset.
4. Open receivables. Trace the aging bins and collection denominators. Mention that the on-time-paid ratio excludes unpaid invoices and must be interpreted alongside overdue balances.
5. Open invoice review. Show the AI queue and source invoice table. Flags mean unusual, not fraudulent, and never change totals or decide loans.
6. Export the summary. Explain missing bank reconciliation, costs, and debt. Show the production process diagram and describe the unknown-bank-outcome rule.

## Ten likely questions

**1. Why Python and Streamlit?** The highest-weight task is a useful working prototype. Python makes data processing and tests straightforward; Streamlit provides uploads, charts, and exports without a separate frontend or API service. Production boundaries are documented separately.

**2. How did you make the data believable?** Seeded code generates repeat customers with different sizes, monthly variation, multiple payment terms, delayed payments, current/overdue balances, and a few valid unusual records. It is an illustrative scenario, not a fitted model of real Qawafel customers.

**3. Why integer halalas?** Binary floating-point can introduce rounding differences. We validate two-decimal inputs and sum integer minor units; formatted SAR values are for display. Net plus VAT must equal gross exactly.

**4. What can invoices prove about financing?** They describe recorded sales, buyer concentration, and receivables behavior. They cannot alone establish bank cash inflows, profitability, authenticity, or affordability. Those need additional evidence and bank review.

**5. Why is this an AI prototype?** The application includes a fitted Isolation Forest to prioritize unusual invoices. Financial ratios and summaries stay deterministic. It uses no LLM runtime because the core task benefits more from reproducible arithmetic and reviewable evidence.

**6. Why choose 5% of invoices for review?** It is an illustrative review-workload setting, not a learned fraud rate. A real deployment would calibrate thresholds with reviewers, labeled outcomes where appropriate, and false-positive monitoring. No accuracy claim is made here.

**7. How do you handle bad data?** Schema and semantic checks run before calculation. Any blocking row error stops the entire analysis; the user receives specific errors. Missing months are warnings because zero activity and missing records require different explanations.

**8. What if the bank times out after receiving an application?** Preserve the submission reference and mark the outcome unknown. Reconcile through a bank-agreed lookup or operations process. Never generate a new key and automatically resend a possibly accepted application.

**9. Why not trust two identical bank responses?** The error may be systematic or correlated. Two matching responses are not necessarily independent evidence. Final status needs agreed authoritative confirmation; otherwise keep verification pending.

**10. What changes for production?** Add identity and consent, tenant authorization, secure document storage, isolated parsing workers, partial-payment/credit models, bank-statement reconciliation, versioned approvals, durable submission intents, monitoring, and bank-agreed contracts. Validate usefulness and operational controls before scaling.

## Honest limitation statement

"I built and tested the invoice review prototype. The bank and document-processing services are a proposed design. The sample is entirely synthetic, and the AI queue has no validated relationship to default or fraud. I would use the tool to organize evidence for a reviewer, not to automatically approve financing."

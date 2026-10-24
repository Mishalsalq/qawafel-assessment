# Assumptions and limitations

**Assessment submission by Mishal Saad**

## Synthetic data contract

- One entirely fictional Saudi wholesaler sells goods to 24 numbered, explicitly synthetic retailers. These are the applicant's **sales** invoices, not purchase invoices.
- The fixed review period is 1 October 2025 through 30 September 2026, the last 12 completed months before the assessment deadline. The snapshot date is 30 September 2026. Results do not change with the machine's current date.
- Seed 42 makes the CSV contents reproducible. Generate the XLSX from the same rows.
- Roughly 48-62 invoices per month, log-normal order sizes, larger repeat customers, modest seasonal factors, and varied 15/30/45/60-day terms illustrate ordinary wholesale behavior. Two unusual invoices have larger amounts and longer terms. These are deliberate illustrative scenarios, not a calibrated economic simulation.
- Amounts are in SAR, with two decimal places. `net_amount_sar` excludes VAT; `vat_amount_sar` is an illustrative 15% of that net amount rounded half up; `invoice_amount_sar` is the VAT-inclusive gross amount. This simplified dataset is not a tax-compliance or ZATCA implementation.
- `payment_date` means the entire gross amount was recorded as settled that day. A blank means unpaid at the snapshot. Recorded settlement is **not bank-verified cash**. No real bank transactions are included.
- Some invoices remain open because they are not due; others are deliberately overdue. No payment occurs before issue or after the snapshot.
- Partial payments, credit notes, returns, canceled invoices, opening balances, costs, debt obligations, collateral, and profitability are not represented. Uploading these requires a richer schema; do not coerce them into this full-payment model.
- All source dates use ISO `YYYY-MM-DD`. IDs are nonempty and unique within this one-seller dataset. Cross-business ingestion would require a tenant key.

## Review boundaries

- Invoice totals support a preliminary evidence review; they do not prove affordability, bank-confirmed income, or loan eligibility.
- Collection rate is recorded settled gross value divided by gross invoiced value for this invoice cohort. It is not a same-period bank cashflow ratio. Recent invoices can still be within terms.
- Aging is based on days past due at the snapshot date. Outstanding includes both not-yet-due and overdue invoices. A due date equal to the snapshot is not yet overdue.
- No real bank submission, PDF extraction, bank reconciliation, identity verification, production access control, or persistent customer storage is implemented in the invoice prototype.
- Written APIs and data entities describe a proposed production service, not endpoints exposed by the Streamlit app.
- Any AI anomaly flags indicate unusual records relative to the uploaded dataset. They do not prove fraud or default risk and require human verification. No lending model has been validated.
- Public company context informs product understanding; the assessment's unspecified Bank Partner remains generic.

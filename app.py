"""A focused financing-review prototype. Run: python -m streamlit run app.py."""

from datetime import date
from pathlib import Path
import zipfile

import altair as alt
import pandas as pd
import streamlit as st

from src.analysis import analyze_invoices, reviewer_summary
from src.anomalies import review_anomalies
from src.data_generation import AS_OF
from src.validation import read_invoices, safe_csv, validate_invoices

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Wholesaler Financing Insights", page_icon="📊", layout="wide")
st.markdown("""
<style>
[data-testid="stHeader"], [data-testid="stSidebarHeader"] {background-color: #040815; border-bottom: 1px solid #172033;}
[data-testid="stSidebarHeader"] {box-shadow: -2rem 0 0 #040815, 2rem 0 0 #040815;}
:is([data-testid="stHeader"], [data-testid="stSidebarHeader"]) button {color: #F7F4ED; background-color: transparent;}
:is([data-testid="stHeader"], [data-testid="stSidebarHeader"]) button:hover {color: #FFFFFF; background-color: rgba(255, 255, 255, 0.10);}
:is([data-testid="stHeader"], [data-testid="stSidebarHeader"]) button:focus-visible {outline: 2px solid #B38B45; outline-offset: 2px;}
:is([data-testid="stHeader"], [data-testid="stSidebarHeader"]) button svg {color: inherit;}
[data-testid="stSidebarHeader"] [data-testid="stIconMaterial"] {color: #F7F4ED;}
.block-container {max-width: 1400px; padding-top: 4rem;}
[data-testid="stMetric"] {background: white; border: 1px solid #e1e5eb; border-radius: 12px; padding: 18px;}
[data-testid="stMetricValue"] {font-size: clamp(1.2rem, 2vw, 1.65rem);}
h1 {letter-spacing: -0.035em;}
.eyebrow {font-size: 12px; letter-spacing: .17em; color: #87632b; font-weight: 700;}
</style>
""", unsafe_allow_html=True)


def money(amount: float) -> str:
    return f"SAR {amount:,.0f}"


def percent(value: float | None) -> str:
    return f"{value:.1%}" if value is not None else "N/A"


with st.sidebar:
    st.title("Review workspace")
    st.caption("Qawafel graduate assessment · Independent prototype")
    source = st.radio("Invoice source", ["Synthetic sample", "Upload fictional invoices"])
    snapshot = st.date_input("Review snapshot", value=AS_OF, help="All payments and aging are evaluated as of this date. The review covers this month and the preceding 11 months.")
    st.caption("Sample snapshot: 30 Sep 2026. Review window: Oct 2025–Sep 2026.")
    uploaded = None
    if source == "Upload fictional invoices":
        uploaded = st.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"], help="Fictional data only. 5 MB, 10,000 rows maximum. First Excel sheet only.")
        st.caption("Use the sample as a column template. Dates: YYYY-MM-DD. A payment date means full settlement; blank means unpaid.")
    st.divider()
    st.download_button("Download sample Excel", (ROOT / "data/synthetic_invoices.xlsx").read_bytes(), "synthetic_invoices.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Download sample CSV", (ROOT / "data/synthetic_invoices.csv").read_bytes(), "synthetic_invoices.csv", mime="text/csv")
    st.info("Fictional data only. This tool supports review; the bank makes the financing decision.")

st.markdown('<div class="eyebrow">FINANCING EVIDENCE / SALES INVOICE REVIEW</div>', unsafe_allow_html=True)
st.title("Wholesaler Financing Insights")
st.write("Turn 12 months of invoices into a clear, traceable review package.")
st.caption("Prepared by Mishal Saad · Qawafel Graduate Software Engineer Assessment")
st.caption(f"Snapshot {snapshot:%d %b %Y} · SAR · {'Demo Wholesale Co. (Synthetic)' if source == 'Synthetic sample' else 'Uploaded fictional invoice cohort'}")

if source == "Upload fictional invoices" and uploaded is None:
    st.info("Upload a fictional invoice file, or switch to the synthetic sample to explore the dashboard.")
    st.stop()

try:
    if uploaded is not None:
        raw = read_invoices(uploaded.getvalue(), uploaded.name)
    else:
        raw = read_invoices((ROOT / "data/synthetic_invoices.csv").read_bytes(), "synthetic_invoices.csv")
except (ValueError, UnicodeError, OSError, KeyError, zipfile.BadZipFile) as exc:
    st.error(f"Could not read the invoice file: {exc}")
    st.stop()

validation = validate_invoices(raw, snapshot)
if not validation.valid:
    st.error("Validation failed. No financial analysis was calculated. Resolve the following issues and upload again.")
    st.dataframe(validation.errors, hide_index=True, width="stretch")
    st.download_button("Download validation issues", safe_csv(validation.errors), "validation_issues.csv", mime="text/csv")
    st.stop()

data = validation.data
result = analyze_invoices(data, snapshot)
m = result.metrics
ai = review_anomalies(data, snapshot)
flagged = ai.invoices[ai.invoices.needs_review]
st.success(f"Validated {len(data):,} invoices · {m['customer_count']} customers · {m['months_present']}/12 months represented")
if validation.warnings:
    with st.expander(f"Data quality warnings ({len(validation.warnings)})", expanded=True):
        for warning in validation.warnings[:30]:
            st.warning(warning)
        if len(validation.warnings) > 30:
            st.caption("Additional warnings omitted from this view; review long payment terms in the source file.")

st.info("Payment records are self-reported full settlements, not bank-verified cash inflows. Amounts below cover the whole uploaded invoice cohort.")
cards = st.columns(4)
cards[0].metric("Net invoiced sales", money(m["net_sales_sar"]), help="Sales before VAT; this is invoiced value, not collected cash or profit.")
cards[1].metric("Recorded settlements", money(m["recorded_collections_sar"]), help="Full invoice settlements including VAT; not reconciled to bank statements.")
cards[2].metric("Outstanding incl. VAT", money(m["outstanding_sar"]), help="Unpaid invoices, including those still within terms.")
cards[3].metric("Overdue incl. VAT", money(m["overdue_sar"]), help="Unpaid invoices whose due date is before the snapshot. A subset of outstanding.")
st.caption(f"Gross invoiced value: {money(m['gross_invoiced_sar'])} = net sales {money(m['net_sales_sar'])} + VAT {money(m['vat_sar'])}. Display cards round to whole SAR; exports preserve 2 decimals.")

overview, receivables, invoices, exports = st.tabs(["Business overview", "Receivables & collection", "Invoice review", "Export & methodology"])

with overview:
    left, right = st.columns([1.55, 1])
    with left:
        st.subheader("Invoice value and recorded settlements")
        chart_data = result.monthly.rename(columns={"gross_invoiced_sar": "Gross invoiced", "recorded_collections_sar": "Recorded settlements"})
        st.line_chart(chart_data, x="month", y=["Gross invoiced", "Recorded settlements"], color=["#142A43", "#B38B45"], y_label="SAR incl. VAT", height=300)
        st.caption("Invoice values use issue month; settlements use payment month. Both include VAT and cover only this invoice cohort. Missing months mean no records, not confirmed zero activity.")
    with right:
        st.subheader("Customer concentration")
        top = result.customers.head(8).copy()
        chart = alt.Chart(top).mark_bar(color="#193A53", cornerRadiusEnd=4).encode(
            x=alt.X("gross_invoiced_sar:Q", title="Gross invoiced (SAR)"),
            y=alt.Y("customer_id:N", sort="-x", title=None),
            tooltip=["customer_name", alt.Tooltip("gross_invoiced_sar:Q", format=",.2f"), alt.Tooltip("share:Q", format=".1%")],
        ).properties(height=300)
        st.altair_chart(chart, width="stretch")
        st.caption(f"Largest customer: {percent(m['top_customer_share'])} · Top 3: {percent(m['top_three_customer_share'])} of gross invoiced value.")
    st.subheader("Reviewer observations")
    for observation in result.observations:
        st.write("• " + observation)

with receivables:
    stats = st.columns(3)
    stats[0].metric("Settled share of due value", percent(m["matured_collection_ratio"]), help="Gross value settled / gross value of invoices due on or before the snapshot. Not a default rate.")
    stats[1].metric("On-time among paid invoices", percent(m["on_time_paid_ratio"]), help="Paid invoice count settled by due date / paid invoice count. Unpaid invoices are excluded; interpret alongside overdue balances.")
    stats[2].metric("Overdue / outstanding", percent(m["overdue_share_of_outstanding"]), help="Overdue gross amount / all outstanding gross amount.")
    left, right = st.columns(2)
    with left:
        st.subheader("Outstanding by days past due")
        aging_chart = alt.Chart(result.aging).mark_bar(color="#B38B45", cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("aging_bucket:N", sort=list(result.aging.aging_bucket), title=None),
            y=alt.Y("outstanding_sar:Q", title="Outstanding (SAR incl. VAT)"),
            tooltip=["aging_bucket", "invoice_count", alt.Tooltip("outstanding_sar:Q", format=",.2f")],
        ).properties(height=280)
        st.altair_chart(aging_chart, width="stretch")
    with right:
        st.subheader("Balance breakdown")
        st.dataframe(result.aging[["aging_bucket", "invoice_count", "outstanding_sar"]], hide_index=True, width="stretch", column_config={"outstanding_sar": st.column_config.NumberColumn("Outstanding SAR", format="%.2f")})
        st.caption("Within terms includes invoices due on the snapshot date. Paid invoices never contribute to outstanding aging.")
    st.subheader("Monthly evidence")
    st.dataframe(result.monthly, hide_index=True, width="stretch")

with invoices:
    st.subheader("AI-assisted review queue")
    st.caption(ai.explanation)
    if ai.fitted:
        st.write(f"**{len(flagged)} unusual invoices flagged for review.** These are not fraud findings or loan recommendations.")
        st.dataframe(flagged[["invoice_id", "customer_name", "invoice_amount_sar", "anomaly_score", "context"]], hide_index=True, width="stretch", column_config={"invoice_amount_sar": st.column_config.NumberColumn("Gross SAR", format="%.2f"), "anomaly_score": st.column_config.NumberColumn("Unusualness score", format="%.3f")})
    else:
        st.info(ai.explanation)
    st.divider()
    st.subheader("Trace every number back to an invoice")
    c1, c2 = st.columns(2)
    status = c1.multiselect("Invoice status", sorted(data.status.unique()), default=sorted(data.status.unique()))
    customer = c2.selectbox("Customer", ["All customers"] + sorted(data.customer_id.unique()))
    view = data[data.status.isin(status)]
    if customer != "All customers":
        view = view[view.customer_id.eq(customer)]
    display_columns = ["invoice_id", "customer_name", "invoice_date", "due_date", "payment_date", "invoice_amount_sar", "status"]
    st.caption(f"Showing {len(view):,} invoices. Table filters do not change the full-cohort metrics above.")
    st.dataframe(view[display_columns], hide_index=True, width="stretch")

with exports:
    st.subheader("Review package")
    summary = reviewer_summary(result, snapshot, len(flagged) if ai.fitted else None)
    st.download_button("Download reviewer summary", summary, "financing_review_summary.md", mime="text/markdown")
    st.download_button("Download monthly metrics", safe_csv(result.monthly), "monthly_metrics.csv", mime="text/csv")
    st.download_button("Download validated invoice evidence", safe_csv(data), "validated_invoice_evidence.csv", mime="text/csv")
    st.download_button("Download AI review queue", safe_csv(flagged), "ai_review_queue.csv", mime="text/csv")
    st.markdown(summary)
    with st.expander("Calculation rules and limits"):
        st.markdown("""
- **Net sales** = sum of net amounts. **Gross invoiced** = net + VAT.
- **Recorded settlements** = full gross amounts with a payment date on/before the snapshot.
- **Outstanding** = gross invoiced minus recorded settlements. **Overdue** = unpaid gross value due before the snapshot.
- **Concentration** = a customer's gross invoice value divided by the cohort gross value.
- **MoM growth** compares gross invoiced value with the previous month; undefined when the previous month is zero or absent.
- Currency sums use integer halalas. Settlement is full-or-unpaid; partial payments, credits, and opening balances require a richer model.
- Uploaded files are processed in server memory without writing them to disk. This demo has no production authentication or persistence; use fictional data only.
- Bank-statement extraction, bank reconciliation, and bank submission are proposed in the written design, outside this working prototype.
        """)

"""Deterministic calculations on validated invoices; money sums use integer halalas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass
class Analysis:
    metrics: dict
    monthly: pd.DataFrame
    customers: pd.DataFrame
    aging: pd.DataFrame
    observations: list[str]


def _ratio(numerator: int | float, denominator: int | float) -> float | None:
    return float(numerator / denominator) if denominator else None


def analyze_invoices(data: pd.DataFrame, as_of: date) -> Analysis:
    """Amounts are a cohort view of uploaded sales, not complete bank cashflow."""
    paid = data[data["is_paid"]]
    outstanding = data[~data["is_paid"]].copy()
    overdue = outstanding[outstanding["status"].eq("Overdue")]
    matured = data[data["due_date"].le(pd.Timestamp(as_of))]
    gross = int(data["gross_cents"].sum())
    collected = int(paid["gross_cents"].sum())
    open_amount = int(outstanding["gross_cents"].sum())
    overdue_amount = int(overdue["gross_cents"].sum())
    metrics = {
        "invoice_count": len(data),
        "customer_count": int(data["customer_id"].nunique()),
        "months_present": int(data["invoice_date"].dt.to_period("M").nunique()),
        "gross_invoiced_sar": gross / 100,
        "net_sales_sar": int(data["net_cents"].sum()) / 100,
        "vat_sar": int(data["vat_cents"].sum()) / 100,
        "recorded_collections_sar": collected / 100,
        "outstanding_sar": open_amount / 100,
        "overdue_sar": overdue_amount / 100,
        "collection_ratio": _ratio(collected, gross),
        "matured_collection_ratio": _ratio(int(matured.loc[matured["is_paid"], "gross_cents"].sum()), int(matured["gross_cents"].sum())),
        "overdue_share_of_outstanding": _ratio(overdue_amount, open_amount),
        "average_invoice_sar": gross / len(data) / 100,
        "paid_invoice_count": len(paid),
        "overdue_invoice_count": len(overdue),
        "on_time_paid_ratio": _ratio(int(paid["payment_date"].le(paid["due_date"]).sum()), len(paid)),
        "average_days_to_pay": float((paid["payment_date"] - paid["invoice_date"]).dt.days.mean()) if len(paid) else None,
    }
    customers = data.groupby(["customer_id", "customer_name"], as_index=False).agg(
        gross_cents=("gross_cents", "sum"), invoice_count=("invoice_id", "size"),
    ).sort_values(["gross_cents", "customer_id"], ascending=[False, True]).reset_index(drop=True)
    customers["gross_invoiced_sar"] = customers["gross_cents"] / 100
    customers["share"] = customers["gross_cents"] / gross
    metrics["top_customer_share"] = float(customers.iloc[0]["share"])
    metrics["top_three_customer_share"] = float(customers.head(3)["share"].sum())

    cutoff = pd.Timestamp(as_of)
    periods = pd.period_range(end=cutoff.to_period("M"), periods=12, freq="M")
    monthly = pd.DataFrame(index=periods)
    monthly.index.name = "month"
    monthly["gross_invoiced_sar"] = data.groupby(data["invoice_date"].dt.to_period("M"))["gross_cents"].sum().reindex(periods, fill_value=0) / 100
    monthly["net_sales_sar"] = data.groupby(data["invoice_date"].dt.to_period("M"))["net_cents"].sum().reindex(periods, fill_value=0) / 100
    monthly["recorded_collections_sar"] = paid.groupby(paid["payment_date"].dt.to_period("M"))["gross_cents"].sum().reindex(periods, fill_value=0) / 100
    monthly["invoice_count"] = data.groupby(data["invoice_date"].dt.to_period("M")).size().reindex(periods, fill_value=0)
    previous = monthly["gross_invoiced_sar"].shift(1).replace(0, float("nan"))
    monthly["mom_growth_pct"] = (monthly["gross_invoiced_sar"] / previous - 1) * 100
    monthly = monthly.reset_index()
    monthly["month"] = monthly["month"].astype(str)

    labels = ["Within terms", "1-30 days", "31-60 days", "61-90 days", "91+ days"]
    outstanding["aging_bucket"] = pd.cut(outstanding["days_past_due"], bins=[-1, 0, 30, 60, 90, float("inf")], labels=labels)
    aging = outstanding.groupby("aging_bucket", observed=False).agg(
        gross_cents=("gross_cents", "sum"), invoice_count=("invoice_id", "size"),
    ).reindex(labels, fill_value=0).reset_index()
    aging["outstanding_sar"] = aging["gross_cents"] / 100
    aging["aging_bucket"] = aging["aging_bucket"].astype(str)

    observations = [
        "Recorded payments are self-reported invoice settlements and have not been reconciled to bank statements.",
        "Costs, existing debt, opening receivables, and partial payments are unavailable; affordability cannot be established.",
    ]
    if metrics["months_present"] == 12:
        observations.append("Invoices are present in all 12 review months; this does not prove the records are complete.")
    else:
        observations.append("Some review months have no invoices; confirm zero activity versus missing records before relying on trends.")
    if overdue_amount:
        observations.append(f"SAR {overdue_amount / 100:,.2f} is overdue across {len(overdue)} invoices; obtain a collection explanation and supporting evidence.")
    if metrics["top_customer_share"] >= 0.20:
        observations.append(f"The largest customer accounts for {metrics['top_customer_share']:.1%} of gross invoice value; review dependence on that customer.")
    if len(customers) < 3:
        observations.append("Fewer than three customers are represented; concentration may be material.")
    observations.append("Any 20% concentration attention threshold is illustrative and is not bank underwriting policy.")
    return Analysis(metrics, monthly, customers, aging, observations)


def reviewer_summary(result: Analysis, as_of: date, anomaly_count: int | None = None) -> str:
    m = result.metrics
    percent = lambda value: f"{value:.1%}" if value is not None else "N/A"
    ai_line = f"- AI review flags: {anomaly_count} unusual invoices, requiring human verification.\n" if anomaly_count is not None else "- AI anomaly review was not run.\n"
    return (
        f"# Preliminary financing evidence summary\n\n"
        f"Snapshot: {as_of.isoformat()}. Scope: uploaded sales invoice cohort only.\n\n"
        f"- Invoices: {m['invoice_count']}; customers: {m['customer_count']}; months represented: {m['months_present']}/12.\n"
        f"- Net invoiced sales, excluding VAT: SAR {m['net_sales_sar']:,.2f}.\n"
        f"- Gross invoiced value, including VAT: SAR {m['gross_invoiced_sar']:,.2f}.\n"
        f"- Recorded full settlements, including VAT: SAR {m['recorded_collections_sar']:,.2f} (not bank verified).\n"
        f"- Outstanding: SAR {m['outstanding_sar']:,.2f}; of this, SAR {m['overdue_sar']:,.2f} is overdue.\n"
        f"- Settled share of invoices due by the snapshot, by value: {percent(m['matured_collection_ratio'])}.\n"
        f"- Largest customer share of gross invoices: {percent(m['top_customer_share'])}.\n"
        + ai_line
        + "\n## Reviewer observations\n\n"
        + "\n".join(f"- {item}" for item in result.observations)
        + "\n\n## Next evidence required\n\n"
        "Obtain consented bank statements and reconcile receipts; confirm missing months, returns/credits, partial payments, and outstanding disputes. Obtain costs and existing debt before assessing repayment capacity.\n\n"
        "This prototype does not approve or reject financing. The bank retains the decision.\n"
    )

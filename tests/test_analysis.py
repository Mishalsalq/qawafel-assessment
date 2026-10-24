import pandas as pd
import pytest

from src.analysis import analyze_invoices, reviewer_summary
from src.data_generation import AS_OF, generate_invoices
from src.validation import validate_invoices


def fixture_invoices():
    rows = []
    for key, customer, net, due, paid in [
        ("A", "C1", 100, "2026-09-15", "2026-09-20"),
        ("B", "C1", 200, "2026-08-31", ""),
        ("C", "C2", 300, "2026-09-30", ""),
        ("D", "C3", 400, "2026-10-15", "2026-09-25"),
    ]:
        rows.append({"invoice_id": key, "customer_id": customer, "customer_name": customer,
                     "invoice_date": "2026-08-01", "due_date": due, "payment_date": paid,
                     "net_amount_sar": f"{net:.2f}", "vat_amount_sar": f"{net * .15:.2f}",
                     "invoice_amount_sar": f"{net * 1.15:.2f}", "currency": "SAR"})
    valid = validate_invoices(pd.DataFrame(rows), AS_OF)
    assert valid.valid, valid.errors.to_dict("records")
    return valid.data


def test_hand_calculated_totals_and_ratios():
    report = analyze_invoices(fixture_invoices(), AS_OF)
    m = report.metrics
    assert m["gross_invoiced_sar"] == 1150
    assert m["net_sales_sar"] == 1000
    assert m["vat_sar"] == 150
    assert m["recorded_collections_sar"] == 575
    assert m["outstanding_sar"] == 575
    assert m["overdue_sar"] == 230
    assert m["collection_ratio"] == .5
    assert m["matured_collection_ratio"] == pytest.approx(115 / 690)
    assert m["on_time_paid_ratio"] == .5
    assert m["top_customer_share"] == .4
    assert report.aging.outstanding_sar.sum() == 575
    assert report.aging.set_index("aging_bucket").loc["1-30 days", "outstanding_sar"] == 230
    assert report.monthly.recorded_collections_sar.sum() == 575
    assert report.monthly.gross_invoiced_sar.sum() == 1150


def test_all_paid_and_all_unpaid_edge_cases():
    data = fixture_invoices()
    all_paid = data.copy()
    all_paid["is_paid"] = True
    all_paid["payment_date"] = pd.Timestamp("2026-09-20")
    all_paid["status"] = "Paid"
    result = analyze_invoices(all_paid, AS_OF)
    assert result.metrics["outstanding_sar"] == 0
    assert result.metrics["overdue_share_of_outstanding"] is None
    assert result.aging.outstanding_sar.sum() == 0
    all_open = data.copy()
    all_open["is_paid"] = False
    all_open["payment_date"] = pd.NaT
    all_open["status"] = "Open - within terms"
    all_open.loc[all_open.due_date < pd.Timestamp(AS_OF), "status"] = "Overdue"
    result = analyze_invoices(all_open, AS_OF)
    assert result.metrics["recorded_collections_sar"] == 0
    assert result.metrics["on_time_paid_ratio"] is None


def test_aging_boundaries():
    data = fixture_invoices().iloc[[0]].copy()
    rows = []
    for days in [0, 1, 30, 31, 60, 61, 90, 91]:
        row = data.copy()
        row["is_paid"] = False
        row["payment_date"] = pd.NaT
        row["days_past_due"] = days
        row["due_date"] = pd.Timestamp(AS_OF) - pd.Timedelta(days=days)
        row["status"] = "Overdue" if days else "Open - within terms"
        rows.append(row)
    result = analyze_invoices(pd.concat(rows), AS_OF)
    assert list(result.aging.invoice_count) == [1, 2, 2, 2, 1]


def test_sample_totals_reconcile_and_summary_is_explicit():
    result = analyze_invoices(validate_invoices(generate_invoices(), AS_OF).data, AS_OF)
    m = result.metrics
    assert m["gross_invoiced_sar"] == pytest.approx(m["recorded_collections_sar"] + m["outstanding_sar"])
    assert m["gross_invoiced_sar"] == pytest.approx(m["net_sales_sar"] + m["vat_sar"])
    assert m["overdue_sar"] <= m["outstanding_sar"]
    assert result.monthly.gross_invoiced_sar.sum() == pytest.approx(m["gross_invoiced_sar"])
    assert "not bank verified" in reviewer_summary(result, AS_OF)
    assert "does not approve or reject" in reviewer_summary(result, AS_OF)

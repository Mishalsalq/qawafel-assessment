from datetime import date
from io import BytesIO

import pandas as pd
import pytest

from src.data_generation import AS_OF, generate_invoices
from src.validation import read_invoices, safe_csv, validate_invoices


@pytest.fixture
def raw():
    return pd.DataFrame([{
        "invoice_id": "A", "customer_id": "C1", "customer_name": "Synthetic Shop",
        "invoice_date": "2026-09-01", "due_date": "2026-09-30", "payment_date": "",
        "net_amount_sar": "100.00", "vat_amount_sar": "15.00", "invoice_amount_sar": "115.00", "currency": "SAR",
    }])


def test_generated_data_is_valid_and_reproducible():
    raw = generate_invoices()
    assert raw.equals(generate_invoices())
    result = validate_invoices(raw, AS_OF)
    assert result.valid, result.errors.to_dict("records")
    assert len(result.data.invoice_date.dt.to_period("M").unique()) == 12
    assert set(result.data.status) == {"Paid", "Overdue", "Open - within terms"}


@pytest.mark.parametrize("field,value", [
    ("invoice_id", ""), ("invoice_date", "2026-02-30"), ("invoice_date", "2026-10-01"),
    ("invoice_date", "0001-01-01"), ("due_date", "9999-12-31"),
    ("invoice_date", "2025-09-30"), ("due_date", "2026-08-01"),
    ("payment_date", "2026-08-31"), ("payment_date", "2026-10-01"),
    ("invoice_amount_sar", "NaN"), ("invoice_amount_sar", "inf"),
    ("invoice_amount_sar", "-1"), ("invoice_amount_sar", "0"),
    ("invoice_amount_sar", "115.001"), ("invoice_amount_sar", "1e4"),
    ("invoice_amount_sar", "116.00"), ("currency", "USD"),
])
def test_bad_upload_is_blocked_atomically(raw, field, value):
    raw.loc[0, field] = value
    result = validate_invoices(raw, AS_OF)
    assert not result.valid
    assert result.data is None
    assert field in set(result.errors.field)


def test_duplicates_are_not_silently_deduplicated(raw):
    result = validate_invoices(pd.concat([raw, raw], ignore_index=True), AS_OF)
    assert not result.valid
    assert (result.errors.field == "invoice_id").sum() == 2


def test_due_today_is_open_not_overdue(raw):
    assert validate_invoices(raw, AS_OF).data.iloc[0].status == "Open - within terms"
    raw.loc[0, "due_date"] = "2026-09-29"
    assert validate_invoices(raw, AS_OF).data.iloc[0].status == "Overdue"


def test_missing_months_warn_without_inventing_data(raw):
    result = validate_invoices(raw, AS_OF)
    assert result.valid
    assert any("Only 1 of 12" in warning for warning in result.warnings)


def test_csv_excel_equivalence(raw):
    csv = read_invoices(raw.to_csv(index=False).encode(), "test.csv")
    workbook = BytesIO()
    raw.to_excel(workbook, index=False)
    excel = read_invoices(workbook.getvalue(), "test.xlsx")
    assert csv.equals(excel)


def test_schema_and_unsupported_payments_block(raw):
    assert not validate_invoices(raw.drop(columns="payment_date"), AS_OF).valid
    raw["payment_amount_sar"] = "50.00"
    assert not validate_invoices(raw, AS_OF).valid


def test_customer_id_cannot_have_conflicting_names(raw):
    second = raw.copy()
    second.loc[0, ["invoice_id", "customer_name"]] = ["B", "Another Shop"]
    assert not validate_invoices(pd.concat([raw, second]), AS_OF).valid


def test_reader_rejects_duplicate_headers_and_wrong_format():
    with pytest.raises(ValueError, match="Duplicate"):
        read_invoices(b"invoice_id,invoice_id\nA,B\n", "test.csv")
    with pytest.raises(ValueError, match="CSV"):
        read_invoices(b"", "test.pdf")


def test_excel_duplicate_headers_are_rejected():
    workbook = BytesIO()
    pd.DataFrame([["A", "B"]], columns=["invoice_id", "invoice_id"]).to_excel(workbook, index=False)
    with pytest.raises(ValueError, match="Duplicate"):
        read_invoices(workbook.getvalue(), "duplicate.xlsx")


def test_exports_escape_formulas():
    result = safe_csv(pd.DataFrame({"name": ["=HYPERLINK(1)", " @SUM(A1)", "Normal"]})).decode("utf-8-sig")
    assert "'=HYPERLINK" in result
    assert "' @SUM" in result

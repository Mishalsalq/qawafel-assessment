import numpy as np
import pandas as pd

from src.anomalies import review_anomalies
from src.data_generation import AS_OF, generate_invoices
from src.validation import validate_invoices


def test_ai_is_reproducible_and_does_not_change_financial_data():
    data = validate_invoices(generate_invoices(), AS_OF).data
    original = data.copy(deep=True)
    a, b = review_anomalies(data, AS_OF), review_anomalies(data, AS_OF)
    assert a.fitted
    assert a.invoices.equals(b.invoices)
    assert data.equals(original)
    assert 0 < a.invoices.needs_review.sum() < len(data) / 5
    assert np.isfinite(a.invoices.anomaly_score).all()
    assert "not probabilities" in a.explanation


def test_extreme_synthetic_invoice_enters_review_queue():
    data = validate_invoices(generate_invoices(), AS_OF).data
    # A sensitivity check only, not an accuracy claim against labeled fraud data.
    data.loc[0, "gross_cents"] = 100_000_000
    data.loc[0, "invoice_amount_sar"] = 1_000_000
    invoice_id = data.loc[0, "invoice_id"]
    review = review_anomalies(data, AS_OF)
    assert bool(review.invoices.set_index("invoice_id").loc[invoice_id, "needs_review"])


def test_tiny_cohort_skips_model_without_blocking_analysis():
    data = validate_invoices(generate_invoices().head(5), AS_OF).data
    result = review_anomalies(data, AS_OF)
    assert not result.fitted
    assert not result.invoices.needs_review.any()

"""Small unsupervised AI feature, isolated from financial arithmetic and decisions."""

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


@dataclass
class AnomalyReview:
    invoices: pd.DataFrame
    explanation: str
    fitted: bool


def review_anomalies(data: pd.DataFrame, as_of: date) -> AnomalyReview:
    """Fit an illustrative model to this cohort; scores are relative, not probabilities."""
    view = data[["invoice_id", "customer_id", "customer_name", "invoice_amount_sar"]].copy()
    view["terms_days"] = (data["due_date"] - data["invoice_date"]).dt.days
    observed_end = data["payment_date"].fillna(pd.Timestamp(as_of))
    view["observed_lateness_days"] = (observed_end - data["due_date"]).dt.days.clip(lower=0)
    customer_medians = data.groupby("customer_id")["gross_cents"].transform("median")
    view["amount_vs_customer_median"] = data["gross_cents"] / customer_medians
    features = pd.DataFrame({
        "log_gross_amount": np.log1p(data["gross_cents"] / 100),
        "log_relative_amount": np.log1p(view["amount_vs_customer_median"]),
        "terms_days": view["terms_days"],
        "observed_lateness_days": view["observed_lateness_days"],
    }, index=data.index)
    view["context"] = [
        f"Amount {ratio:.2f}x customer median; terms {terms}d; observed lateness {late}d"
        for ratio, terms, late in zip(view["amount_vs_customer_median"], view["terms_days"], view["observed_lateness_days"])
    ]
    if len(data) < 30 or len(features.drop_duplicates()) < 3:
        view["anomaly_score"] = np.nan
        view["needs_review"] = False
        return AnomalyReview(view, "AI review skipped: at least 30 invoices and 3 distinct feature profiles are needed for this demonstration. Financial analysis remains available.", False)
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42, n_jobs=1)
    predictions = model.fit_predict(features)
    view["anomaly_score"] = -model.score_samples(features)
    view["needs_review"] = predictions == -1
    view = view.sort_values(["anomaly_score", "invoice_id"], ascending=[False, True]).reset_index(drop=True)
    explanation = (
        "Isolation Forest is fitted to this invoice cohort using gross amount, amount relative to the customer's median, "
        "payment terms, and observed lateness. The illustrative 5% contamination setting targets a small review queue; "
        "it is not an estimate of fraud or credit risk. Higher scores mean more unusual relative to this cohort and are not probabilities. "
        "Context hints describe record values, not causal explanations of the model. Human verification is required."
    )
    return AnomalyReview(view, explanation, True)

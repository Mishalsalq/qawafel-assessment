"""Generate reproducible fictional sales invoices; no external data is used."""

from __future__ import annotations

import json
import random
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd

AS_OF = date(2026, 9, 30)
SEED = 42
PERIOD_START = date(2025, 10, 1)
PERIOD_END = AS_OF


def generate_invoices(seed: int = SEED) -> pd.DataFrame:
    """Create a fixed historical snapshot, including ordinary and unusual invoices."""
    rng = random.Random(seed)
    rows = []
    customer_weights = [20, 12, 9, 7, 5, 4] + [2] * 18
    categories = ["Dry groceries", "Beverages", "Household supplies"]
    # Illustrative trading patterns, not fitted to real Qawafel business data.
    seasonality = [1.00, 1.04, 1.08, 1.04, 1.20, 1.28, 1.05, 1.10, 1.15, 0.93, 0.98, 1.13]
    for offset, factor in enumerate(seasonality):
        month_index = 2025 * 12 + 9 + offset
        year, month0 = divmod(month_index, 12)
        month = month0 + 1
        for _ in range(rng.randint(48, 62)):
            customer = rng.choices(range(1, 25), weights=customer_weights, k=1)[0]
            issued = date(year, month, rng.randint(1, monthrange(year, month)[1]))
            terms = rng.choices([15, 30, 45, 60], weights=[1, 5, 3, 1], k=1)[0]
            size = 1.6 if customer <= 3 else 1.0
            net_cents = max(50_000, round(rng.lognormvariate(8.1, 0.65) * factor * size * 100))
            # Two deliberately unusual but valid records; no fraud labels.
            if len(rows) in (125, 420):
                net_cents *= 8
                terms = 120
            net = Decimal(net_cents) / 100
            vat = (net * Decimal("0.15")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            gross = net + vat
            due = issued + timedelta(days=terms)
            delay = rng.choices([-5, 0, 5, 15, 35, 75], weights=[2, 5, 4, 2, 1, 1], k=1)[0]
            scheduled_payment = due + timedelta(days=delay)
            payment = scheduled_payment if rng.random() > 0.055 and scheduled_payment <= AS_OF else None
            rows.append({
                "invoice_id": f"INV-{len(rows) + 1:05d}",
                "customer_id": f"CUS-{customer:03d}",
                "customer_name": f"Synthetic Retailer {customer:03d}",
                "invoice_date": issued.isoformat(),
                "due_date": due.isoformat(),
                "payment_date": payment.isoformat() if payment else "",
                "net_amount_sar": f"{net:.2f}",
                "vat_amount_sar": f"{vat:.2f}",
                "invoice_amount_sar": f"{gross:.2f}",
                "currency": "SAR",
                "category": rng.choice(categories),
            })
    return pd.DataFrame(rows).sort_values(["invoice_date", "invoice_id"]).reset_index(drop=True)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    target = root / "data"
    target.mkdir(exist_ok=True)
    invoices = generate_invoices()
    invoices.to_csv(target / "synthetic_invoices.csv", index=False)
    invoices.to_excel(target / "synthetic_invoices.xlsx", index=False, sheet_name="Invoices")
    manifest = {
        "business": "Demo Wholesale Co. (Synthetic)",
        "synthetic": True,
        "seed": SEED,
        "as_of_date": AS_OF.isoformat(),
        "period_start": PERIOD_START.isoformat(),
        "period_end": PERIOD_END.isoformat(),
        "invoice_count": len(invoices),
        "customer_count": invoices["customer_id"].nunique(),
        "data_source": "Python standard-library random generator; no real records",
        "assumptions_document": "docs/assumptions.md",
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

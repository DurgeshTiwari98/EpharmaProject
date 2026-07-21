"""Data quality summaries and referential integrity checks."""

from __future__ import annotations

import pandas as pd


def profile_table(name: str, frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in frame.columns:
        series = frame[column]
        rows.append(
            {
                "table": name,
                "column": column,
                "dtype": str(series.dtype),
                "rows": len(frame),
                "missing": int(series.isna().sum()),
                "missing_pct": float(series.isna().mean() * 100),
                "unique_values": int(series.nunique(dropna=True)),
            }
        )
    return pd.DataFrame(rows)


def validate_foreign_keys(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    checks = [
        ("orders", "patient_id", "patients", "patient_id"),
        ("orders", "pharmacy_id", "pharmacies", "pharmacy_id"),
        ("order_items", "order_id", "orders", "order_id"),
        ("order_items", "medicine_id", "medicines", "medicine_id"),
        ("appointments", "patient_id", "patients", "patient_id"),
        ("appointments", "doctor_id", "doctors", "doctor_id"),
        ("inventory_movements", "pharmacy_id", "pharmacies", "pharmacy_id"),
        ("inventory_movements", "medicine_id", "medicines", "medicine_id"),
        ("payments", "order_id", "orders", "order_id"),
    ]
    rows = []
    for child_table, child_key, parent_table, parent_key in checks:
        if child_table not in tables or parent_table not in tables:
            continue
        child = tables[child_table][child_key].dropna()
        parent = set(tables[parent_table][parent_key].dropna())
        invalid = ~child.isin(parent)
        rows.append(
            {
                "child_table": child_table,
                "child_key": child_key,
                "parent_table": parent_table,
                "parent_key": parent_key,
                "checked_rows": int(len(child)),
                "invalid_rows": int(invalid.sum()),
                "passed": bool(invalid.sum() == 0),
            }
        )
    return pd.DataFrame(rows)

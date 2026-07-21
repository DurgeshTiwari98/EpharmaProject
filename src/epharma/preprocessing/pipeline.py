"""End-to-end preprocessing pipeline for all canonical E-Pharma tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from epharma.data.schema import REQUIRED_TABLES, TABLE_PRIMARY_KEYS
from epharma.preprocessing.cleaning import (
    add_age_group,
    cap_outliers_iqr,
    fill_missing_values,
    normalize_string_columns,
    parse_datetime_columns,
    remove_duplicate_primary_keys,
)
from epharma.preprocessing.quality import profile_table, validate_foreign_keys
from epharma.utils.config import load_config
from epharma.utils.io import ensure_dir, read_table, table_exists, write_table

DATE_COLUMNS = {
    "patients": ["registered_at", "created_at"],
    "doctors": ["created_at"],
    "pharmacies": ["created_at"],
    "medicines": ["created_at"],
    "orders": ["ordered_at", "delivered_at"],
    "appointments": ["booked_at", "scheduled_at"],
    "inventory_movements": ["movement_at"],
    "payments": ["paid_at"],
}
NUMERIC_OUTLIER_COLUMNS = {
    "patients": ["age"],
    "doctors": ["experience_years", "consultation_fee", "rating"],
    "pharmacies": ["rating", "fulfillment_capacity_per_day"],
    "medicines": ["unit_price"],
    "orders": ["delivery_fee", "discount_amount", "order_total"],
    "order_items": ["quantity", "unit_price", "line_total"],
    "appointments": ["duration_minutes", "consultation_fee"],
    "inventory_movements": ["quantity"],
    "payments": ["amount"],
}


def load_raw_tables(raw_dir: str | Path) -> dict[str, pd.DataFrame]:
    tables = {}
    for table in REQUIRED_TABLES:
        base = Path(raw_dir) / table
        if not table_exists(base):
            raise FileNotFoundError(f"Missing raw table: {base}.parquet or {base}.csv")
        tables[table] = read_table(base)
    return tables


def clean_table(name: str, frame: pd.DataFrame) -> pd.DataFrame:
    primary_key = TABLE_PRIMARY_KEYS[name]
    cleaned = normalize_string_columns(frame)
    cleaned = parse_datetime_columns(cleaned, DATE_COLUMNS.get(name, []))
    cleaned = remove_duplicate_primary_keys(cleaned, primary_key)
    cleaned = fill_missing_values(cleaned)
    cleaned = cap_outliers_iqr(cleaned, NUMERIC_OUTLIER_COLUMNS.get(name, []))
    if name == "patients":
        cleaned = add_age_group(cleaned)
    return cleaned


def preprocess(raw_dir: str | Path, processed_dir: str | Path, report_dir: str | Path) -> dict[str, pd.DataFrame]:
    raw_tables = load_raw_tables(raw_dir)
    profile_before = pd.concat(
        [profile_table(name, frame) for name, frame in raw_tables.items()],
        ignore_index=True,
    )
    processed = {name: clean_table(name, frame) for name, frame in raw_tables.items()}
    integrity = validate_foreign_keys(processed)
    profile_after = pd.concat(
        [profile_table(name, frame) for name, frame in processed.items()],
        ignore_index=True,
    )
    ensure_dir(report_dir)
    profile_before.to_csv(Path(report_dir) / "data_profile_before.csv", index=False)
    profile_after.to_csv(Path(report_dir) / "data_profile_after.csv", index=False)
    integrity.to_csv(Path(report_dir) / "referential_integrity.csv", index=False)
    for name, frame in processed.items():
        write_table(frame, Path(processed_dir) / name)
    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean and validate E-Pharma raw datasets.")
    parser.add_argument("--config", default="config/settings.yaml")
    parser.add_argument("--raw-dir", default=None)
    parser.add_argument("--processed-dir", default=None)
    parser.add_argument("--report-dir", default=None)
    args = parser.parse_args()
    settings = load_config(args.config)
    preprocess(
        raw_dir=args.raw_dir or settings["data"]["raw_dir"],
        processed_dir=args.processed_dir or settings["data"]["processed_dir"],
        report_dir=args.report_dir or settings["data"]["report_dir"],
    )
    print("preprocessing complete")


if __name__ == "__main__":
    main()

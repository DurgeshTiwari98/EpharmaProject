"""EDA summary generation for Phase 3."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from epharma.data.schema import REQUIRED_TABLES
from epharma.utils.config import load_config
from epharma.utils.io import ensure_dir, read_table


def load_processed_tables(processed_dir: str | Path) -> dict[str, pd.DataFrame]:
    return {table: read_table(Path(processed_dir) / table) for table in REQUIRED_TABLES}


def patient_registration_trends(patients: pd.DataFrame) -> pd.DataFrame:
    frame = patients.copy()
    frame["registered_at"] = pd.to_datetime(frame["registered_at"])
    return (
        frame.assign(month=frame["registered_at"].dt.to_period("M").astype(str))
        .groupby(["month", "city", "age_group"], dropna=False)
        .agg(registrations=("patient_id", "count"))
        .reset_index()
        .sort_values(["month", "registrations"], ascending=[True, False])
    )


def medicine_sales_summary(orders: pd.DataFrame, order_items: pd.DataFrame, medicines: pd.DataFrame) -> pd.DataFrame:
    frame = order_items.merge(orders[["order_id", "ordered_at", "order_status"]], on="order_id", how="left")
    frame = frame.merge(medicines[["medicine_id", "category", "medicine_name"]], on="medicine_id", how="left")
    frame["ordered_at"] = pd.to_datetime(frame["ordered_at"])
    frame["month"] = frame["ordered_at"].dt.to_period("M").astype(str)
    return (
        frame[frame["order_status"].ne("cancelled")]
        .groupby(["month", "category"], dropna=False)
        .agg(units=("quantity", "sum"), revenue=("line_total", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .sort_values(["month", "revenue"], ascending=[True, False])
    )


def consultation_summary(appointments: pd.DataFrame) -> pd.DataFrame:
    frame = appointments.copy()
    frame["scheduled_at"] = pd.to_datetime(frame["scheduled_at"])
    frame["weekday"] = frame["scheduled_at"].dt.day_name()
    frame["hour"] = frame["scheduled_at"].dt.hour
    return (
        frame.groupby(["specialty", "weekday", "hour", "appointment_status"], dropna=False)
        .agg(appointments=("appointment_id", "count"), revenue=("consultation_fee", "sum"))
        .reset_index()
    )


def pharmacy_performance(orders: pd.DataFrame, pharmacies: pd.DataFrame) -> pd.DataFrame:
    frame = orders.copy()
    frame["ordered_at"] = pd.to_datetime(frame["ordered_at"])
    frame["delivered_at"] = pd.to_datetime(frame["delivered_at"])
    frame["fulfillment_hours"] = (frame["delivered_at"] - frame["ordered_at"]).dt.total_seconds() / 3600
    summary = (
        frame.groupby("pharmacy_id")
        .agg(
            orders=("order_id", "count"),
            delivered=("order_status", lambda s: int((s == "delivered").sum())),
            cancelled=("order_status", lambda s: int((s == "cancelled").sum())),
            average_fulfillment_hours=("fulfillment_hours", "mean"),
            revenue=("order_total", "sum"),
        )
        .reset_index()
    )
    summary["cancellation_rate"] = summary["cancelled"] / summary["orders"]
    return summary.merge(pharmacies[["pharmacy_id", "city", "rating"]], on="pharmacy_id", how="left")


def build_eda_outputs(processed_dir: str | Path, report_dir: str | Path) -> dict[str, pd.DataFrame]:
    tables = load_processed_tables(processed_dir)
    outputs = {
        "patient_registration_trends": patient_registration_trends(tables["patients"]),
        "medicine_sales_summary": medicine_sales_summary(tables["orders"], tables["order_items"], tables["medicines"]),
        "consultation_summary": consultation_summary(tables["appointments"]),
        "pharmacy_performance": pharmacy_performance(tables["orders"], tables["pharmacies"]),
    }
    output_dir = ensure_dir(Path(report_dir) / "eda")
    for name, frame in outputs.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Build EDA summary tables.")
    parser.add_argument("--config", default="config/settings.yaml")
    parser.add_argument("--processed-dir", default=None)
    parser.add_argument("--report-dir", default=None)
    args = parser.parse_args()
    settings = load_config(args.config)
    build_eda_outputs(
        args.processed_dir or settings["data"]["processed_dir"],
        args.report_dir or settings["data"]["report_dir"],
    )
    print("eda outputs complete")


if __name__ == "__main__":
    main()

"""Utilities for the Durgesh healthcare phase datasets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

import pandas as pd

from epharma.utils.io import ensure_dir

DATASET_FILES = {
    "business_kpi": "phase10_business_kpi.csv",
    "patient_registration": "phase1_patient_registration.csv",
    "raw_patient_data": "phase2_raw_patient_data.csv",
    "doctor_consultation": "phase3_doctor_consultation.csv",
    "inventory": "phase3_inventory.csv",
    "medicine_sales": "phase3_medicine_sales.csv",
    "ml_training": "phase4_ml_training.csv",
    "pharmacy_analytics": "phase5_pharmacy_analytics.csv",
    "recommendation": "phase5_recommendation.csv",
    "feature_engineering": "phase6_feature_engineering.csv",
    "api_prediction": "phase7_api_prediction.csv",
    "model_performance": "phase8_model_performance.csv",
    "production_deployment": "phase9_production_deployment.csv",
}


def _clean_columns(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output.columns = (
        output.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return output


def _percent_to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace("%", "", regex=False), errors="coerce")


def _parse_dates(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    for column in output.columns:
        if column == "date" or column.endswith("_date"):
            output[column] = pd.to_datetime(output[column], errors="coerce", dayfirst=True)
    return output


def load_datasets(dataset_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Load all expected Durgesh healthcare CSV files with normalized column names."""
    base = Path(dataset_dir)
    tables: dict[str, pd.DataFrame] = {}
    missing: list[Path] = []

    for name, filename in DATASET_FILES.items():
        path = base / filename
        if not path.exists():
            missing.append(path)
            continue
        tables[name] = _parse_dates(_clean_columns(pd.read_csv(path)))

    if missing:
        missing_files = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing Durgesh healthcare dataset file(s): {missing_files}")
    return tables


def build_summary_outputs(dataset_dir: str | Path, report_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Build analysis-ready summaries from the phase CSV dataset."""
    tables = load_datasets(dataset_dir)
    output_dir = ensure_dir(report_dir)

    patient_reg = tables["patient_registration"]
    patient_summary = (
        patient_reg.groupby(["city", "disease", "insurance"], dropna=False)
        .agg(patients=("patient_id", "count"), average_age=("age", "mean"))
        .reset_index()
        .sort_values("patients", ascending=False)
    )

    sales = tables["medicine_sales"].copy()
    sales["month"] = sales["date"].dt.to_period("M").astype(str)
    sales_summary = (
        sales.groupby(["month", "category"], dropna=False)
        .agg(units_sold=("units_sold", "sum"), revenue_usd=("revenue_usd", "sum"))
        .reset_index()
        .sort_values(["month", "revenue_usd"], ascending=[True, False])
    )

    doctors = tables["doctor_consultation"]
    doctor_summary = (
        doctors.groupby("department", dropna=False)
        .agg(
            doctors=("doctor_id", "count"),
            patients=("patients", "sum"),
            avg_consultation_minutes=("avg_consultation_time_mins", "mean"),
            avg_rating=("rating", "mean"),
        )
        .reset_index()
        .sort_values("patients", ascending=False)
    )

    inventory = tables["inventory"].copy()
    inventory["needs_reorder"] = inventory["stock"] <= inventory["reorder_level"]
    inventory_summary = (
        inventory.groupby(["warehouse", "needs_reorder"], dropna=False)
        .agg(medicines=("medicine", "count"), stock=("stock", "sum"))
        .reset_index()
        .sort_values(["warehouse", "needs_reorder"])
    )

    kpis = tables["business_kpi"].copy()
    for column in [
        "medicine_prediction_accuracy",
        "readmission_prediction_accuracy",
        "recommendation_accuracy",
        "inventory_forecast_accuracy",
    ]:
        kpis[column] = _percent_to_float(kpis[column])
    kpi_summary = pd.DataFrame(
        [
            {
                "days": len(kpis),
                "total_registered_patients": int(kpis["patients_registered"].sum()),
                "total_online_orders": int(kpis["online_orders"].sum()),
                "total_revenue_usd": float(kpis["revenue_usd"].sum()),
                "avg_customer_satisfaction": float(kpis["customer_satisfaction"].mean()),
                "avg_medicine_prediction_accuracy": float(kpis["medicine_prediction_accuracy"].mean()),
            }
        ]
    )

    outputs = {
        "patient_summary": patient_summary,
        "medicine_sales_summary": sales_summary,
        "doctor_summary": doctor_summary,
        "inventory_summary": inventory_summary,
        "kpi_summary": kpi_summary,
    }
    for name, frame in outputs.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reports from Durgesh healthcare phase CSVs.")
    parser.add_argument("--dataset-dir", default="durgesh_healthcare_datasets")
    parser.add_argument("--report-dir", default="reports/durgesh_healthcare")
    args = parser.parse_args()

    outputs = build_summary_outputs(args.dataset_dir, args.report_dir)
    for name, frame in outputs.items():
        print(f"{name}: {len(frame)} rows")


if __name__ == "__main__":
    main()

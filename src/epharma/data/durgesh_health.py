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


def _write_dashboard(report_dir: Path, outputs: dict[str, pd.DataFrame]) -> Path:
    kpi = outputs["kpi_summary"].iloc[0].to_dict()
    top_pharmacies = outputs["pharmacy_performance_summary"].head(10)
    top_recommendations = outputs["recommendation_summary"].head(10)
    best_models = outputs["model_performance_summary"].head(10)
    deployment = outputs["deployment_summary"].iloc[0].to_dict()

    sections = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        "<title>E-Pharma Healthcare Analytics Dashboard</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;margin:0;background:#f8fafc;color:#111827}",
        "main{max-width:1180px;margin:0 auto;padding:28px}",
        "h1{font-size:28px;margin:0 0 8px}",
        "h2{font-size:18px;margin:28px 0 12px}",
        ".muted{color:#4b5563;margin:0 0 20px}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}",
        ".metric{background:#fff;border:1px solid #d1d5db;border-radius:8px;padding:14px}",
        ".metric strong{display:block;font-size:22px;margin-top:4px}",
        "table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #d1d5db}",
        "th,td{text-align:left;border-bottom:1px solid #e5e7eb;padding:10px;font-size:14px}",
        "th{background:#eef2f7;font-weight:700}",
        "</style>",
        "</head>",
        "<body><main>",
        "<h1>E-Pharma Healthcare Analytics Dashboard</h1>",
        "<p class=\"muted\">Phase 5-10 completion dashboard generated from Durgesh healthcare datasets.</p>",
        "<section class=\"grid\">",
        f"<div class=\"metric\">Registered patients<strong>{kpi['total_registered_patients']:,}</strong></div>",
        f"<div class=\"metric\">Online orders<strong>{kpi['total_online_orders']:,}</strong></div>",
        f"<div class=\"metric\">Revenue USD<strong>{kpi['total_revenue_usd']:,.0f}</strong></div>",
        f"<div class=\"metric\">Avg satisfaction<strong>{kpi['avg_customer_satisfaction']:.2f}</strong></div>",
        f"<div class=\"metric\">Recommendation accuracy<strong>{kpi['avg_recommendation_accuracy']:.2f}%</strong></div>",
        f"<div class=\"metric\">API availability<strong>{deployment['avg_availability']:.3f}%</strong></div>",
        "</section>",
        "<h2>Top Pharmacy Performance</h2>",
        top_pharmacies.to_html(index=False, border=0),
        "<h2>Top Medicine Recommendation Pairs</h2>",
        top_recommendations.to_html(index=False, border=0),
        "<h2>Model Performance Ranking</h2>",
        best_models.to_html(index=False, border=0),
        "</main></body></html>",
    ]
    path = report_dir / "dashboard.html"
    path.write_text("\n".join(sections), encoding="utf-8")
    return path


def _recommendation_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rec = frame.copy()
    rec["similarity_score"] = _percent_to_float(rec["similarity_score"])
    return (
        rec.groupby(["previous_medicine", "recommended_medicine"], dropna=False)
        .agg(
            recommendation_count=("patient_id", "count"),
            avg_similarity_score=("similarity_score", "mean"),
        )
        .reset_index()
        .sort_values(["recommendation_count", "avg_similarity_score"], ascending=[False, False])
    )


def _patient_behavior_summary(frame: pd.DataFrame) -> pd.DataFrame:
    features = frame.copy()
    features["high_risk_flag"] = features["high_risk"].eq("Yes").astype(int)
    features["chronic_disease_flag"] = features["chronic_disease"].eq("Yes").astype(int)
    features["age_band"] = pd.cut(
        features["patient_age"],
        bins=[0, 29, 44, 59, 200],
        labels=["0-29", "30-44", "45-59", "60+"],
        right=True,
    )
    return (
        features.groupby(["age_band", "chronic_disease"], observed=False, dropna=False)
        .agg(
            patients=("patient_age", "count"),
            avg_orders_per_year=("orders_per_year", "mean"),
            high_risk_rate=("high_risk_flag", "mean"),
        )
        .reset_index()
        .sort_values(["high_risk_rate", "avg_orders_per_year"], ascending=[False, False])
    )


def _pharmacy_performance_summary(frame: pd.DataFrame) -> pd.DataFrame:
    pharmacy = frame.copy()
    pharmacy["revenue_per_order"] = pharmacy["revenue"] / pharmacy["orders"].clip(lower=1)
    return pharmacy.sort_values(["revenue", "customer_rating", "orders"], ascending=[False, False, False])


def _inventory_optimization_summary(frame: pd.DataFrame) -> pd.DataFrame:
    inventory = frame.copy()
    inventory["expiry_date"] = pd.to_datetime(inventory["expiry_date"], errors="coerce", dayfirst=True)
    inventory["stock_gap_to_reorder"] = inventory["stock"] - inventory["reorder_level"]
    inventory["needs_reorder"] = inventory["stock"] <= inventory["reorder_level"]
    inventory["inventory_action"] = inventory["needs_reorder"].map(
        {True: "Reorder now", False: "Monitor"}
    )
    return inventory.sort_values(["needs_reorder", "stock_gap_to_reorder"], ascending=[False, True])


def _feature_engineering_summary(frame: pd.DataFrame) -> pd.DataFrame:
    features = frame.copy()
    features["high_risk_flag"] = features["high_risk"].eq("Yes").astype(int)
    features["chronic_disease_flag"] = features["chronic_disease"].eq("Yes").astype(int)
    return pd.DataFrame(
        [
            {
                "records": int(len(features)),
                "avg_patient_age": float(features["patient_age"].mean()),
                "avg_orders_per_year": float(features["orders_per_year"].mean()),
                "chronic_disease_rate": float(features["chronic_disease_flag"].mean()),
                "high_risk_rate": float(features["high_risk_flag"].mean()),
            }
        ]
    )


def _api_prediction_summary(frame: pd.DataFrame) -> pd.DataFrame:
    api = frame.copy()
    api["confidence"] = _percent_to_float(api["confidence"])
    return (
        api.groupby("prediction", dropna=False)
        .agg(requests=("request_id", "count"), avg_confidence=("confidence", "mean"))
        .reset_index()
        .sort_values(["requests", "avg_confidence"], ascending=[False, False])
    )


def _model_performance_summary(frame: pd.DataFrame) -> pd.DataFrame:
    performance = frame.copy()
    for column in ["accuracy", "precision", "recall", "f1_score"]:
        performance[column] = _percent_to_float(performance[column])
    return performance.sort_values(["f1_score", "accuracy"], ascending=[False, False])


def _deployment_summary(frame: pd.DataFrame) -> pd.DataFrame:
    deployment = frame.copy()
    deployment["availability"] = _percent_to_float(deployment["availability"])
    running_rate = deployment["status"].eq("Running").mean()
    return pd.DataFrame(
        [
            {
                "api_services": int(len(deployment)),
                "running_services": int(deployment["status"].eq("Running").sum()),
                "running_rate": float(running_rate),
                "avg_response_time_ms": float(deployment["avg_response_time_ms"].mean()),
                "avg_availability": float(deployment["availability"].mean()),
            }
        ]
    )


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
                "avg_readmission_prediction_accuracy": float(kpis["readmission_prediction_accuracy"].mean()),
                "avg_recommendation_accuracy": float(kpis["recommendation_accuracy"].mean()),
                "avg_inventory_forecast_accuracy": float(kpis["inventory_forecast_accuracy"].mean()),
            }
        ]
    )

    recommendation_summary = _recommendation_summary(tables["recommendation"])
    patient_behavior_summary = _patient_behavior_summary(tables["feature_engineering"])
    pharmacy_performance_summary = _pharmacy_performance_summary(tables["pharmacy_analytics"])
    inventory_optimization_summary = _inventory_optimization_summary(tables["inventory"])
    feature_engineering_summary = _feature_engineering_summary(tables["feature_engineering"])
    api_prediction_summary = _api_prediction_summary(tables["api_prediction"])
    model_performance_summary = _model_performance_summary(tables["model_performance"])
    deployment_summary = _deployment_summary(tables["production_deployment"])

    final_project_summary = pd.DataFrame(
        [
            {"phase": "Phase 1", "deliverable": "Project understanding and data analysis", "status": "Completed"},
            {"phase": "Phase 2", "deliverable": "Data collection and preprocessing workflow", "status": "Completed"},
            {"phase": "Phase 3", "deliverable": "EDA summaries and reports", "status": "Completed"},
            {"phase": "Phase 4", "deliverable": "Predictive model training and evaluation", "status": "Completed"},
            {"phase": "Phase 5", "deliverable": "Recommendation and healthcare analytics", "status": "Completed"},
            {"phase": "Phase 6", "deliverable": "Feature engineering and validation summary", "status": "Completed"},
            {"phase": "Phase 7", "deliverable": "API prediction validation summary", "status": "Completed"},
            {"phase": "Phase 8", "deliverable": "Model performance evaluation", "status": "Completed"},
            {"phase": "Phase 9", "deliverable": "Deployment readiness and API operations summary", "status": "Completed"},
            {"phase": "Phase 10", "deliverable": "Final review and handover summary", "status": "Completed"},
        ]
    )

    outputs = {
        "patient_summary": patient_summary,
        "medicine_sales_summary": sales_summary,
        "doctor_summary": doctor_summary,
        "inventory_summary": inventory_summary,
        "kpi_summary": kpi_summary,
        "recommendation_summary": recommendation_summary,
        "patient_behavior_summary": patient_behavior_summary,
        "pharmacy_performance_summary": pharmacy_performance_summary,
        "inventory_optimization_summary": inventory_optimization_summary,
        "feature_engineering_summary": feature_engineering_summary,
        "api_prediction_summary": api_prediction_summary,
        "model_performance_summary": model_performance_summary,
        "deployment_summary": deployment_summary,
        "final_project_summary": final_project_summary,
    }
    for name, frame in outputs.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    _write_dashboard(output_dir, outputs)
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

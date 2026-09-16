from pathlib import Path

import pandas as pd

from epharma.data.durgesh_health import build_summary_outputs


def _write_required_phase_files(base: Path) -> None:
    pd.DataFrame(
        {
            "Patient ID": ["PT1", "PT2"],
            "Name": ["A", "B"],
            "Age": [30, 65],
            "Gender": ["F", "M"],
            "City": ["Pune", "Mumbai"],
            "Disease": ["Diabetes", "Asthma"],
            "Registration Date": ["01-Jan-2026", "02-Jan-2026"],
            "Doctor ID": ["D1", "D2"],
            "Insurance": ["Yes", "No"],
        }
    ).to_csv(base / "phase1_patient_registration.csv", index=False)
    pd.DataFrame(
        {"Patient ID": ["PT1"], "Age": [30], "Disease": ["Diabetes"], "Medicine": ["Metformin"], "Quantity": [2]}
    ).to_csv(base / "phase2_raw_patient_data.csv", index=False)
    pd.DataFrame(
        {
            "Doctor ID": ["D1"],
            "Department": ["Cardiology"],
            "Patients": [12],
            "Avg Consultation Time (mins)": [18],
            "Rating": [4.6],
        }
    ).to_csv(base / "phase3_doctor_consultation.csv", index=False)
    pd.DataFrame(
        {
            "Medicine": ["Metformin", "Insulin"],
            "Stock": [5, 30],
            "Reorder Level": [10, 12],
            "Expiry Date": ["31-Dec-2026", "31-Dec-2026"],
            "Warehouse": ["W1", "W1"],
        }
    ).to_csv(base / "phase3_inventory.csv", index=False)
    pd.DataFrame(
        {
            "Date": ["01-Jan-2026"],
            "Medicine": ["Metformin"],
            "Category": ["Diabetes"],
            "Units Sold": [20],
            "Revenue (USD)": [200],
        }
    ).to_csv(base / "phase3_medicine_sales.csv", index=False)
    pd.DataFrame(
        {"Date": ["01-Jan-2026"], "Orders": [10], "Patients": [8], "Revenue": [1000], "Medicine Demand": [50]}
    ).to_csv(base / "phase4_ml_training.csv", index=False)
    pd.DataFrame(
        {"Pharmacy": ["Cure"], "Orders": [100], "Revenue": [5000], "Customer Rating": [4.8]}
    ).to_csv(base / "phase5_pharmacy_analytics.csv", index=False)
    pd.DataFrame(
        {
            "Patient ID": ["PT1", "PT2"],
            "Previous Medicine": ["Metformin", "Metformin"],
            "Recommended Medicine": ["Insulin", "Insulin"],
            "Similarity Score": ["96%", "90%"],
        }
    ).to_csv(base / "phase5_recommendation.csv", index=False)
    pd.DataFrame(
        {
            "Patient Age": [30, 65],
            "Chronic Disease": ["Yes", "No"],
            "Orders per Year": [20, 5],
            "High Risk": ["Yes", "No"],
        }
    ).to_csv(base / "phase6_feature_engineering.csv", index=False)
    pd.DataFrame(
        {
            "Request ID": ["API1", "API2"],
            "Patient ID": ["PT1", "PT2"],
            "Prediction": ["High Medicine Demand", "Low Risk"],
            "Confidence": ["91%", "87%"],
        }
    ).to_csv(base / "phase7_api_prediction.csv", index=False)
    pd.DataFrame(
        {
            "Model": ["Random Forest", "Logistic Regression"],
            "Accuracy": ["92%", "88%"],
            "Precision": ["91%", "86%"],
            "Recall": ["90%", "84%"],
            "F1 Score": ["90.5%", "85%"],
        }
    ).to_csv(base / "phase8_model_performance.csv", index=False)
    pd.DataFrame(
        {
            "API Service": ["Prediction API", "Alert API"],
            "Status": ["Running", "Running"],
            "Avg Response Time (ms)": [120, 140],
            "Availability": ["99.9%", "99.8%"],
        }
    ).to_csv(base / "phase9_production_deployment.csv", index=False)
    pd.DataFrame(
        {
            "Date": ["01-Jan-2026"],
            "Patients Registered": [10],
            "Active Doctors": [5],
            "Online Orders": [25],
            "Revenue (USD)": [1200],
            "Daily Appointments": [11],
            "Customer Satisfaction": [4.7],
            "Medicine Prediction Accuracy": ["95%"],
            "Readmission Prediction Accuracy": ["93%"],
            "Recommendation Accuracy": ["94%"],
            "Inventory Forecast Accuracy": ["92%"],
        }
    ).to_csv(base / "phase10_business_kpi.csv", index=False)


def test_build_summary_outputs_includes_phase_5_to_10_reports(tmp_path):
    dataset_dir = tmp_path / "datasets"
    report_dir = tmp_path / "reports"
    dataset_dir.mkdir()
    _write_required_phase_files(dataset_dir)

    outputs = build_summary_outputs(dataset_dir, report_dir)

    assert outputs["recommendation_summary"].iloc[0]["recommendation_count"] == 2
    assert outputs["inventory_optimization_summary"].iloc[0]["inventory_action"] == "Reorder now"
    assert outputs["deployment_summary"].iloc[0]["running_services"] == 2
    assert outputs["final_project_summary"]["status"].eq("Completed").all()
    assert (report_dir / "dashboard.html").exists()

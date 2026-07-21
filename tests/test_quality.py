import pandas as pd

from epharma.preprocessing.quality import validate_foreign_keys


def test_validate_foreign_keys_reports_invalid_rows():
    tables = {
        "patients": pd.DataFrame({"patient_id": ["P1"]}),
        "pharmacies": pd.DataFrame({"pharmacy_id": ["PH1"]}),
        "orders": pd.DataFrame({"order_id": ["O1", "O2"], "patient_id": ["P1", "P2"], "pharmacy_id": ["PH1", "PHX"]}),
    }
    result = validate_foreign_keys(tables)
    order_patient = result[(result["child_table"] == "orders") & (result["child_key"] == "patient_id")].iloc[0]
    order_pharmacy = result[(result["child_table"] == "orders") & (result["child_key"] == "pharmacy_id")].iloc[0]
    assert order_patient["invalid_rows"] == 1
    assert order_pharmacy["invalid_rows"] == 1

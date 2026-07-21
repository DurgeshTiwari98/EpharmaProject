import pandas as pd

from epharma.preprocessing.cleaning import add_age_group, cap_outliers_iqr, remove_duplicate_primary_keys


def test_remove_duplicate_primary_keys_keeps_last_record():
    frame = pd.DataFrame({"patient_id": ["PAT1", "PAT1", "PAT2"], "age": [20, 21, 40]})
    result = remove_duplicate_primary_keys(frame, "patient_id")
    assert result.to_dict("records") == [
        {"patient_id": "PAT1", "age": 21},
        {"patient_id": "PAT2", "age": 40},
    ]


def test_add_age_group_creates_expected_band():
    frame = pd.DataFrame({"age": [17, 18, 44, 60]})
    result = add_age_group(frame)
    assert result["age_group"].astype(str).tolist() == ["0-17", "18-29", "30-44", "60+"]


def test_cap_outliers_iqr_adds_flag_and_caps_values():
    frame = pd.DataFrame({"order_total": [100, 110, 120, 130, 10000]})
    result = cap_outliers_iqr(frame, ["order_total"])
    assert result["order_total_was_outlier"].sum() == 1
    assert result["order_total"].max() < 10000

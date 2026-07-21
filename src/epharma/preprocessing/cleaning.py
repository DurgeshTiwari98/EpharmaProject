"""Cleaning primitives for E-Pharma source tables."""

from __future__ import annotations

import numpy as np
import pandas as pd


def normalize_string_columns(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    for column in output.select_dtypes(include=["object", "string"]).columns:
        output[column] = output[column].astype("string").str.strip()
    return output


def parse_datetime_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    output = frame.copy()
    for column in columns:
        if column in output.columns:
            output[column] = pd.to_datetime(output[column], errors="coerce")
    return output


def cap_outliers_iqr(frame: pd.DataFrame, columns: list[str], factor: float = 1.5) -> pd.DataFrame:
    output = frame.copy()
    for column in columns:
        if column not in output.columns:
            continue
        series = pd.to_numeric(output[column], errors="coerce")
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            continue
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        output[f"{column}_was_outlier"] = (series < lower) | (series > upper)
        output[column] = series.clip(lower, upper)
    return output


def add_age_group(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    if "age" not in output.columns:
        return output
    bins = [0, 17, 29, 44, 59, np.inf]
    labels = ["0-17", "18-29", "30-44", "45-59", "60+"]
    output["age_group"] = pd.cut(output["age"], bins=bins, labels=labels, right=True)
    return output


def fill_missing_values(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    for column in output.columns:
        if output[column].isna().sum() == 0:
            continue
        if pd.api.types.is_numeric_dtype(output[column]):
            output[f"{column}_was_missing"] = output[column].isna()
            output[column] = output[column].fillna(output[column].median())
        elif pd.api.types.is_datetime64_any_dtype(output[column]):
            continue
        else:
            output[f"{column}_was_missing"] = output[column].isna()
            mode = output[column].mode(dropna=True)
            output[column] = output[column].fillna(mode.iloc[0] if not mode.empty else "unknown")
    return output


def remove_duplicate_primary_keys(frame: pd.DataFrame, primary_key: str) -> pd.DataFrame:
    if primary_key not in frame.columns:
        return frame.drop_duplicates().reset_index(drop=True)
    return frame.drop_duplicates(subset=[primary_key], keep="last").reset_index(drop=True)

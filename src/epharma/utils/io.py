"""Shared IO helpers for tabular artifacts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def ensure_dir(path: str | Path) -> Path:
    output = Path(path)
    output.mkdir(parents=True, exist_ok=True)
    return output


def write_table(frame: pd.DataFrame, path_without_suffix: str | Path) -> Path:
    """Write a dataframe as Parquet when possible, falling back to CSV."""
    base = Path(path_without_suffix)
    ensure_dir(base.parent)
    try:
        path = base.with_suffix(".parquet")
        frame.to_parquet(path, index=False)
        return path
    except Exception:
        path = base.with_suffix(".csv")
        frame.to_csv(path, index=False)
        return path


def read_table(path_without_suffix: str | Path) -> pd.DataFrame:
    """Read a table written by `write_table`."""
    base = Path(path_without_suffix)
    parquet_path = base.with_suffix(".parquet")
    csv_path = base.with_suffix(".csv")
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if csv_path.exists():
        return pd.read_csv(csv_path)
    raise FileNotFoundError(f"No table found for {base} with .parquet or .csv suffix")


def table_exists(path_without_suffix: str | Path) -> bool:
    base = Path(path_without_suffix)
    return base.with_suffix(".parquet").exists() or base.with_suffix(".csv").exists()

"""Training harness for Phase 4 baseline and candidate models."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    f1_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from epharma.data.schema import REQUIRED_TABLES
from epharma.models.features import (
    appointment_trend_frame,
    demand_forecasting_frame,
    order_demand_frame,
    readmission_frame,
)
from epharma.utils.config import load_config
from epharma.utils.io import ensure_dir, read_table


@dataclass(frozen=True)
class TrainResult:
    problem: str
    model_name: str
    metrics: dict[str, float]
    artifact_path: str | None


def stringify_values(values):
    return values.astype(str)


def _load_tables(processed_dir: str | Path) -> dict[str, pd.DataFrame]:
    return {table: read_table(Path(processed_dir) / table) for table in REQUIRED_TABLES}


def _regression_pipeline(model) -> Pipeline:
    return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", model)])


def _mixed_pipeline(numeric: list[str], categorical: list[str], model) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
            (
                "cat",
                Pipeline(
                    [
                        ("stringify", FunctionTransformer(stringify_values, feature_names_out="one-to-one")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
        ]
    )
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def _time_split(frame: pd.DataFrame, date_column: str, test_days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    sorted_frame = frame.sort_values(date_column)
    cutoff = pd.to_datetime(sorted_frame[date_column]).max() - pd.Timedelta(days=test_days)
    train = sorted_frame[pd.to_datetime(sorted_frame[date_column]) <= cutoff]
    test = sorted_frame[pd.to_datetime(sorted_frame[date_column]) > cutoff]
    if train.empty or test.empty:
        split = int(len(sorted_frame) * 0.8)
        train = sorted_frame.iloc[:split]
        test = sorted_frame.iloc[split:]
    return train, test


def _save_model(model, model_dir: Path, name: str) -> str:
    ensure_dir(model_dir)
    path = model_dir / f"{name}.joblib"
    joblib.dump(model, path)
    return str(path)


def _regression_metrics(y_true, y_pred) -> dict[str, float]:
    mse = mean_squared_error(y_true, y_pred)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mse)),
        "mape": float(mean_absolute_percentage_error(y_true, np.maximum(y_pred, 1e-6))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def train_medicine_demand(tables: dict[str, pd.DataFrame], model_dir: Path, test_days: int) -> list[TrainResult]:
    frame = demand_forecasting_frame(tables["orders"], tables["order_items"], tables["medicines"])
    train, test = _time_split(frame, "week_start", max(test_days, 28))
    features = ["lag_1", "lag_2", "rolling_4", "revenue", "day_of_week", "month", "weekofyear", "is_weekend"]
    target = "units"
    results = []
    naive_pred = test["lag_1"].to_numpy()
    results.append(TrainResult("medicine_demand_forecasting", "naive_last_week", _regression_metrics(test[target], naive_pred), None))
    for name, estimator in {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(n_estimators=120, min_samples_leaf=3, random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
    }.items():
        model = _regression_pipeline(estimator)
        model.fit(train[features], train[target])
        pred = model.predict(test[features])
        artifact = _save_model(model, model_dir, f"medicine_demand_{name}")
        results.append(TrainResult("medicine_demand_forecasting", name, _regression_metrics(test[target], pred), artifact))
    return results


def train_order_demand(tables: dict[str, pd.DataFrame], model_dir: Path, test_days: int) -> list[TrainResult]:
    frame = order_demand_frame(tables["orders"])
    train, test = _time_split(frame, "order_date", test_days)
    features = ["lag_1", "lag_7", "rolling_7", "revenue", "day_of_week", "month", "weekofyear", "is_weekend"]
    target = "order_count"
    results = [TrainResult("order_demand_prediction", "naive_yesterday", _regression_metrics(test[target], test["lag_1"]), None)]
    for name, estimator in {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(n_estimators=100, min_samples_leaf=2, random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
    }.items():
        model = _regression_pipeline(estimator)
        model.fit(train[features], train[target])
        pred = model.predict(test[features])
        results.append(TrainResult("order_demand_prediction", name, _regression_metrics(test[target], pred), _save_model(model, model_dir, f"order_demand_{name}")))
    return results


def train_appointment_trends(tables: dict[str, pd.DataFrame], model_dir: Path, test_days: int) -> list[TrainResult]:
    frame = appointment_trend_frame(tables["appointments"])
    train, test = _time_split(frame, "appointment_date", test_days)
    features = ["lag_1", "lag_7", "rolling_7", "completed", "day_of_week", "month", "weekofyear", "is_weekend"]
    target = "bookings"
    results = [TrainResult("appointment_trend_prediction", "naive_yesterday", _regression_metrics(test[target], test["lag_1"]), None)]
    for name, estimator in {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(n_estimators=100, min_samples_leaf=2, random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
    }.items():
        model = _regression_pipeline(estimator)
        model.fit(train[features], train[target])
        pred = model.predict(test[features])
        results.append(TrainResult("appointment_trend_prediction", name, _regression_metrics(test[target], pred), _save_model(model, model_dir, f"appointment_trend_{name}")))
    return results


def _classification_metrics(y_true, y_pred, y_score) -> dict[str, float]:
    return {
        "roc_auc": float(roc_auc_score(y_true, y_score)) if len(set(y_true)) > 1 else float("nan"),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def train_readmission(tables: dict[str, pd.DataFrame], model_dir: Path, test_days: int) -> list[TrainResult]:
    frame = readmission_frame(tables["patients"], tables["orders"], tables["appointments"])
    train, test = _time_split(frame, "scheduled_at", test_days)
    numeric = ["age", "lifetime_orders", "lifetime_spend", "days_since_last_order", "duration_minutes", "consultation_fee"]
    categorical = ["gender", "city", "acquisition_channel", "has_chronic_condition", "specialty", "appointment_type"]
    target = "readmission_30d"
    results = []
    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(train[numeric + categorical], train[target])
    dummy_pred = dummy.predict(test[numeric + categorical])
    dummy_score = np.full(len(test), train[target].mean())
    results.append(TrainResult("patient_readmission_prediction", "most_frequent_baseline", _classification_metrics(test[target], dummy_pred, dummy_score), None))
    for name, estimator in {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=160, min_samples_leaf=3, class_weight="balanced", random_state=42, n_jobs=-1),
    }.items():
        model = _mixed_pipeline(numeric, categorical, estimator)
        model.fit(train[numeric + categorical], train[target])
        pred = model.predict(test[numeric + categorical])
        score = model.predict_proba(test[numeric + categorical])[:, 1]
        results.append(TrainResult("patient_readmission_prediction", name, _classification_metrics(test[target], pred, score), _save_model(model, model_dir, f"readmission_{name}")))
    return results


def train_all(processed_dir: str | Path, model_dir: str | Path, report_dir: str | Path, test_days: int) -> pd.DataFrame:
    tables = _load_tables(processed_dir)
    model_path = Path(model_dir)
    results = []
    results.extend(train_medicine_demand(tables, model_path, test_days))
    results.extend(train_readmission(tables, model_path, test_days))
    results.extend(train_order_demand(tables, model_path, test_days))
    results.extend(train_appointment_trends(tables, model_path, test_days))
    rows = []
    for result in results:
        row = {"problem": result.problem, "model": result.model_name, "artifact_path": result.artifact_path}
        row.update(result.metrics)
        rows.append(row)
    metrics = pd.DataFrame(rows)
    ensure_dir(report_dir)
    metrics.to_csv(Path(report_dir) / "model_comparison.csv", index=False)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Phase 4 baseline and candidate models.")
    parser.add_argument("--config", default="config/settings.yaml")
    parser.add_argument("--processed-dir", default=None)
    parser.add_argument("--model-dir", default=None)
    parser.add_argument("--report-dir", default=None)
    args = parser.parse_args()
    settings = load_config(args.config)
    metrics = train_all(
        processed_dir=args.processed_dir or settings["data"]["processed_dir"],
        model_dir=args.model_dir or settings["data"]["model_dir"],
        report_dir=args.report_dir or settings["data"]["report_dir"],
        test_days=settings["models"]["test_days"],
    )
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()

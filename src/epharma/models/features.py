"""Feature builders for Phase 4 model development."""

from __future__ import annotations

import pandas as pd


def calendar_features(frame: pd.DataFrame, date_column: str) -> pd.DataFrame:
    output = frame.copy()
    dates = pd.to_datetime(output[date_column])
    output["day_of_week"] = dates.dt.dayofweek
    output["day_of_month"] = dates.dt.day
    output["month"] = dates.dt.month
    output["weekofyear"] = dates.dt.isocalendar().week.astype(int)
    output["is_weekend"] = dates.dt.dayofweek.isin([5, 6]).astype(int)
    return output


def demand_forecasting_frame(orders: pd.DataFrame, order_items: pd.DataFrame, medicines: pd.DataFrame) -> pd.DataFrame:
    frame = order_items.merge(orders[["order_id", "ordered_at", "order_status"]], on="order_id", how="left")
    frame = frame.merge(medicines[["medicine_id", "category"]], on="medicine_id", how="left")
    frame = frame[frame["order_status"].eq("delivered")].copy()
    frame["week_start"] = pd.to_datetime(frame["ordered_at"]).dt.to_period("W").dt.start_time
    weekly = (
        frame.groupby(["medicine_id", "category", "week_start"], dropna=False)
        .agg(units=("quantity", "sum"), revenue=("line_total", "sum"))
        .reset_index()
        .sort_values(["medicine_id", "week_start"])
    )
    weekly["lag_1"] = weekly.groupby("medicine_id")["units"].shift(1)
    weekly["lag_2"] = weekly.groupby("medicine_id")["units"].shift(2)
    weekly["rolling_4"] = weekly.groupby("medicine_id")["units"].transform(
        lambda values: values.shift(1).rolling(4).mean()
    )
    weekly = calendar_features(weekly, "week_start")
    return weekly.dropna(subset=["lag_1", "lag_2", "rolling_4"]).reset_index(drop=True)


def order_demand_frame(orders: pd.DataFrame) -> pd.DataFrame:
    frame = orders.copy()
    frame["order_date"] = pd.to_datetime(frame["ordered_at"]).dt.floor("D")
    daily = (
        frame.groupby(["city", "order_date"], dropna=False)
        .agg(order_count=("order_id", "count"), revenue=("order_total", "sum"))
        .reset_index()
        .sort_values(["city", "order_date"])
    )
    daily["lag_1"] = daily.groupby("city")["order_count"].shift(1)
    daily["lag_7"] = daily.groupby("city")["order_count"].shift(7)
    daily["rolling_7"] = daily.groupby("city")["order_count"].transform(
        lambda values: values.shift(1).rolling(7).mean()
    )
    daily = calendar_features(daily, "order_date")
    return daily.dropna(subset=["lag_1", "lag_7", "rolling_7"]).reset_index(drop=True)


def appointment_trend_frame(appointments: pd.DataFrame) -> pd.DataFrame:
    frame = appointments.copy()
    frame["appointment_date"] = pd.to_datetime(frame["scheduled_at"]).dt.floor("D")
    daily = (
        frame.groupby(["specialty", "appointment_date"], dropna=False)
        .agg(bookings=("appointment_id", "count"), completed=("appointment_status", lambda s: int((s == "completed").sum())))
        .reset_index()
        .sort_values(["specialty", "appointment_date"])
    )
    daily["lag_1"] = daily.groupby("specialty")["bookings"].shift(1)
    daily["lag_7"] = daily.groupby("specialty")["bookings"].shift(7)
    daily["rolling_7"] = daily.groupby("specialty")["bookings"].transform(
        lambda values: values.shift(1).rolling(7).mean()
    )
    daily = calendar_features(daily, "appointment_date")
    return daily.dropna(subset=["lag_1", "lag_7", "rolling_7"]).reset_index(drop=True)


def readmission_frame(patients: pd.DataFrame, orders: pd.DataFrame, appointments: pd.DataFrame) -> pd.DataFrame:
    appts = appointments.copy()
    appts["scheduled_at"] = pd.to_datetime(appts["scheduled_at"])
    appts = appts.sort_values(["patient_id", "scheduled_at"])
    appts["next_scheduled_at"] = appts.groupby("patient_id")["scheduled_at"].shift(-1)
    appts["readmission_30d"] = (
        (appts["next_scheduled_at"] - appts["scheduled_at"]).dt.days.between(0, 30).fillna(False).astype(int)
    )
    order_features = orders.copy()
    order_features["ordered_at"] = pd.to_datetime(order_features["ordered_at"])
    agg_orders = (
        order_features.groupby("patient_id")
        .agg(
            lifetime_orders=("order_id", "count"),
            lifetime_spend=("order_total", "sum"),
            last_order_at=("ordered_at", "max"),
        )
        .reset_index()
    )
    base = appts.merge(patients, on="patient_id", how="left").merge(agg_orders, on="patient_id", how="left")
    base["lifetime_orders"] = base["lifetime_orders"].fillna(0)
    base["lifetime_spend"] = base["lifetime_spend"].fillna(0)
    base["days_since_last_order"] = (base["scheduled_at"] - base["last_order_at"]).dt.days
    base["days_since_last_order"] = base["days_since_last_order"].fillna(999).clip(lower=0, upper=999)
    return base.reset_index(drop=True)

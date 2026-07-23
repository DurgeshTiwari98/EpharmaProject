"""Synthetic data generation for the E-Pharma analytics workflow."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from epharma.utils.config import load_config
from epharma.utils.io import write_table


SPECIALTIES = [
    "General Medicine",
    "Cardiology",
    "Dermatology",
    "Endocrinology",
    "Pediatrics",
    "Psychiatry",
    "Orthopedics",
    "Pulmonology",
]
MEDICINE_CATEGORIES = [
    "Analgesic",
    "Antibiotic",
    "Antidiabetic",
    "Antihypertensive",
    "Dermatology",
    "Respiratory",
    "Vitamin",
    "Gastrointestinal",
]
CITIES = ["Pune", "Mumbai", "Nashik", "Nagpur", "Indore", "Bhopal", "Hyderabad", "Bengaluru"]
CHANNELS = ["organic", "doctor_referral", "pharmacy_referral", "paid_search", "social"]


@dataclass(frozen=True)
class GenerationConfig:
    seed: int
    start_date: str
    end_date: str
    patients: int
    doctors: int
    pharmacies: int
    medicines: int
    orders: int
    appointments: int


def _ids(prefix: str, count: int) -> list[str]:
    return [f"{prefix}{idx:06d}" for idx in range(1, count + 1)]


def _dates(rng: np.random.Generator, start: str, end: str, count: int) -> pd.Series:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    days = (end_ts - start_ts).days
    offsets = rng.integers(0, max(days, 1), size=count)
    seconds = rng.integers(0, 24 * 3600, size=count)
    return pd.Series(start_ts + pd.to_timedelta(offsets, unit="D") + pd.to_timedelta(seconds, unit="s"))


def build_patients(cfg: GenerationConfig, rng: np.random.Generator) -> pd.DataFrame:
    patient_ids = _ids("PAT", cfg.patients)
    ages = np.clip(rng.normal(39, 15, cfg.patients).round(), 1, 92).astype(int)
    chronic_probability = np.where(ages >= 55, 0.42, np.where(ages >= 35, 0.22, 0.09))
    return pd.DataFrame(
        {
            "patient_id": patient_ids,
            "full_name": [f"Patient {idx:05d}" for idx in range(1, cfg.patients + 1)],
            "age": ages,
            "gender": rng.choice(["female", "male", "other"], cfg.patients, p=[0.48, 0.50, 0.02]),
            "city": rng.choice(CITIES, cfg.patients),
            "acquisition_channel": rng.choice(CHANNELS, cfg.patients, p=[0.34, 0.22, 0.16, 0.18, 0.10]),
            "has_chronic_condition": rng.random(cfg.patients) < chronic_probability,
            "registered_at": _dates(rng, cfg.start_date, cfg.end_date, cfg.patients),
        }
    )


def build_doctors(cfg: GenerationConfig, rng: np.random.Generator) -> pd.DataFrame:
    doctors = cfg.doctors
    return pd.DataFrame(
        {
            "doctor_id": _ids("DOC", doctors),
            "full_name": [f"Dr. Clinician {idx:04d}" for idx in range(1, doctors + 1)],
            "specialty": rng.choice(SPECIALTIES, doctors),
            "city": rng.choice(CITIES, doctors),
            "experience_years": rng.integers(1, 35, doctors),
            "consultation_fee": rng.choice([299, 399, 499, 699, 899, 1199], doctors),
            "rating": np.round(rng.uniform(3.4, 5.0, doctors), 2),
            "is_active": rng.random(doctors) > 0.05,
            "created_at": _dates(rng, cfg.start_date, cfg.end_date, doctors),
        }
    )


def build_pharmacies(cfg: GenerationConfig, rng: np.random.Generator) -> pd.DataFrame:
    pharmacies = cfg.pharmacies
    return pd.DataFrame(
        {
            "pharmacy_id": _ids("PHA", pharmacies),
            "pharmacy_name": [f"CarePlus Pharmacy {idx:03d}" for idx in range(1, pharmacies + 1)],
            "city": rng.choice(CITIES, pharmacies),
            "rating": np.round(rng.uniform(3.2, 5.0, pharmacies), 2),
            "fulfillment_capacity_per_day": rng.integers(35, 240, pharmacies),
            "is_verified": rng.random(pharmacies) > 0.03,
            "created_at": _dates(rng, cfg.start_date, cfg.end_date, pharmacies),
        }
    )


def build_medicines(cfg: GenerationConfig, rng: np.random.Generator) -> pd.DataFrame:
    medicines = cfg.medicines
    categories = rng.choice(MEDICINE_CATEGORIES, medicines)
    prescription_required = np.isin(categories, ["Antibiotic", "Antidiabetic", "Antihypertensive"])
    base_prices = rng.lognormal(mean=4.1, sigma=0.55, size=medicines)
    return pd.DataFrame(
        {
            "medicine_id": _ids("MED", medicines),
            "sku": [f"SKU-{idx:06d}" for idx in range(1, medicines + 1)],
            "medicine_name": [f"{cat} Medicine {idx:04d}" for idx, cat in enumerate(categories, 1)],
            "category": categories,
            "brand": rng.choice(["Cipla", "Sun", "DrReddy", "Lupin", "Glenmark", "Generic"], medicines),
            "unit_price": np.round(np.clip(base_prices, 12, 2200), 2),
            "prescription_required": prescription_required,
            "is_active": rng.random(medicines) > 0.02,
            "created_at": _dates(rng, cfg.start_date, cfg.end_date, medicines),
        }
    )


def build_orders(
    cfg: GenerationConfig,
    rng: np.random.Generator,
    patients: pd.DataFrame,
    pharmacies: pd.DataFrame,
    medicines: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    order_count = cfg.orders
    order_ids = _ids("ORD", order_count)
    ordered_at = _dates(rng, cfg.start_date, cfg.end_date, order_count).sort_values(ignore_index=True)
    city_weights = patients["city"].value_counts(normalize=True)
    patient_by_city = {city: group["patient_id"].to_numpy() for city, group in patients.groupby("city")}
    pharmacy_by_city = {city: group["pharmacy_id"].to_numpy() for city, group in pharmacies.groupby("city")}
    cities = rng.choice(city_weights.index.to_numpy(), order_count, p=city_weights.to_numpy())
    patient_ids = [rng.choice(patient_by_city[city]) for city in cities]
    pharmacy_ids = [rng.choice(pharmacy_by_city.get(city, pharmacies["pharmacy_id"].to_numpy())) for city in cities]
    statuses = rng.choice(
        ["delivered", "cancelled", "refunded"],
        order_count,
        p=[0.88, 0.09, 0.03],
    )
    order_items: list[dict[str, object]] = []
    medicine_prices = medicines.set_index("medicine_id")["unit_price"]
    popular_meds = medicines.sample(frac=0.2, random_state=cfg.seed)["medicine_id"].to_numpy()
    all_meds = medicines["medicine_id"].to_numpy()
    totals = np.zeros(order_count)
    for idx, order_id in enumerate(order_ids):
        item_count = int(rng.choice([1, 2, 3, 4, 5], p=[0.52, 0.25, 0.13, 0.07, 0.03]))
        chosen_pool = popular_meds if rng.random() < 0.65 else all_meds
        for line in range(1, item_count + 1):
            medicine_id = str(rng.choice(chosen_pool))
            quantity = int(rng.choice([1, 1, 1, 2, 2, 3, 4]))
            unit_price = float(medicine_prices.loc[medicine_id])
            line_total = round(quantity * unit_price, 2)
            totals[idx] += line_total
            order_items.append(
                {
                    "order_item_id": f"ORI{len(order_items) + 1:08d}",
                    "order_id": order_id,
                    "medicine_id": medicine_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_total": line_total,
                }
            )
    delivery_fee = rng.choice([0, 29, 49, 79], order_count, p=[0.28, 0.34, 0.28, 0.10])
    orders = pd.DataFrame(
        {
            "order_id": order_ids,
            "patient_id": patient_ids,
            "pharmacy_id": pharmacy_ids,
            "order_status": statuses,
            "ordered_at": ordered_at,
            "delivered_at": ordered_at + pd.to_timedelta(rng.integers(4, 96, order_count), unit="h"),
            "city": cities,
            "delivery_fee": delivery_fee,
            "discount_amount": np.round(totals * rng.choice([0, 0.05, 0.10, 0.15], order_count, p=[0.62, 0.2, 0.14, 0.04]), 2),
            "order_total": np.round(totals + delivery_fee, 2),
            "payment_method": rng.choice(["upi", "card", "wallet", "cod"], order_count, p=[0.46, 0.24, 0.18, 0.12]),
        }
    )
    orders.loc[orders["order_status"].isin(["cancelled", "refunded"]), "delivered_at"] = pd.NaT
    payments = pd.DataFrame(
        {
            "payment_id": _ids("PAY", order_count),
            "order_id": order_ids,
            "payment_method": orders["payment_method"],
            "payment_status": np.where(orders["order_status"].eq("cancelled"), "failed", "success"),
            "amount": orders["order_total"] - orders["discount_amount"],
            "paid_at": ordered_at + pd.to_timedelta(rng.integers(1, 30, order_count), unit="m"),
        }
    )
    return orders, pd.DataFrame(order_items), payments


def build_appointments(
    cfg: GenerationConfig,
    rng: np.random.Generator,
    patients: pd.DataFrame,
    doctors: pd.DataFrame,
) -> pd.DataFrame:
    count = cfg.appointments
    booked_at = _dates(rng, cfg.start_date, cfg.end_date, count).sort_values(ignore_index=True)
    scheduled_at = booked_at + pd.to_timedelta(rng.integers(1, 14 * 24, count), unit="h")
    doctor_lookup = doctors.set_index("doctor_id")
    doctor_ids = rng.choice(doctors["doctor_id"].to_numpy(), count)
    return pd.DataFrame(
        {
            "appointment_id": _ids("APT", count),
            "patient_id": rng.choice(patients["patient_id"].to_numpy(), count),
            "doctor_id": doctor_ids,
            "specialty": doctor_lookup.loc[doctor_ids, "specialty"].to_numpy(),
            "appointment_type": rng.choice(["video", "chat"], count, p=[0.62, 0.38]),
            "appointment_status": rng.choice(
                ["completed", "cancelled", "no_show"],
                count,
                p=[0.81, 0.12, 0.07],
            ),
            "booked_at": booked_at,
            "scheduled_at": scheduled_at,
            "duration_minutes": rng.choice([10, 15, 20, 30, 45], count, p=[0.13, 0.36, 0.27, 0.19, 0.05]),
            "consultation_fee": doctor_lookup.loc[doctor_ids, "consultation_fee"].to_numpy(),
        }
    )


def build_inventory_movements(
    cfg: GenerationConfig,
    rng: np.random.Generator,
    pharmacies: pd.DataFrame,
    medicines: pd.DataFrame,
    order_items: pd.DataFrame,
    orders: pd.DataFrame,
) -> pd.DataFrame:
    order_pharmacy = orders.set_index("order_id")["pharmacy_id"]
    movement_rows = []
    for idx, item in order_items.sample(min(len(order_items), cfg.orders * 2), random_state=cfg.seed).iterrows():
        movement_rows.append(
            {
                "inventory_movement_id": f"INV{len(movement_rows) + 1:08d}",
                "pharmacy_id": order_pharmacy.loc[item["order_id"]],
                "medicine_id": item["medicine_id"],
                "movement_type": "sale",
                "quantity": -int(item["quantity"]),
                "movement_at": orders.loc[orders["order_id"].eq(item["order_id"]), "ordered_at"].iloc[0],
            }
        )
    replenishments = max(cfg.pharmacies * 20, cfg.medicines * 2)
    for _ in range(replenishments):
        movement_rows.append(
            {
                "inventory_movement_id": f"INV{len(movement_rows) + 1:08d}",
                "pharmacy_id": rng.choice(pharmacies["pharmacy_id"].to_numpy()),
                "medicine_id": rng.choice(medicines["medicine_id"].to_numpy()),
                "movement_type": "purchase",
                "quantity": int(rng.integers(20, 400)),
                "movement_at": _dates(rng, cfg.start_date, cfg.end_date, 1).iloc[0],
            }
        )
    return pd.DataFrame(movement_rows)


def generate(cfg: GenerationConfig) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(cfg.seed)
    patients = build_patients(cfg, rng)
    doctors = build_doctors(cfg, rng)
    pharmacies = build_pharmacies(cfg, rng)
    medicines = build_medicines(cfg, rng)
    orders, order_items, payments = build_orders(cfg, rng, patients, pharmacies, medicines)
    appointments = build_appointments(cfg, rng, patients, doctors)
    inventory_movements = build_inventory_movements(cfg, rng, pharmacies, medicines, order_items, orders)
    return {
        "patients": patients,
        "doctors": doctors,
        "pharmacies": pharmacies,
        "medicines": medicines,
        "orders": orders,
        "order_items": order_items,
        "appointments": appointments,
        "inventory_movements": inventory_movements,
        "payments": payments,
    }


def from_settings(settings: dict, scale: str) -> GenerationConfig:
    synthetic = settings["synthetic"].copy()
    if scale == "small":
        synthetic.update({"patients": 500, "doctors": 40, "pharmacies": 25, "medicines": 200, "orders": 2500, "appointments": 1200})
    elif scale == "medium":
        synthetic.update({"patients": 2000, "doctors": 120, "pharmacies": 60, "medicines": 700, "orders": 12000, "appointments": 6000})
    return GenerationConfig(seed=settings["data"]["seed"], **synthetic)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic E-Pharma source datasets.")
    parser.add_argument("--config", default="config/settings.yaml")
    parser.add_argument("--scale", choices=["small", "medium", "full"], default="full")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    settings = load_config(args.config)
    cfg = from_settings(settings, args.scale)
    output_dir = Path(args.output_dir or settings["data"]["raw_dir"])
    for name, frame in generate(cfg).items():
        path = write_table(frame, output_dir / name)
        print(f"wrote {name}: {len(frame):,} rows -> {path}")


if __name__ == "__main__":
    main()

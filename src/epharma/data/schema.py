"""Canonical table schemas used across generation, preprocessing, and modeling."""

from __future__ import annotations

TABLE_PRIMARY_KEYS = {
    "patients": "patient_id",
    "doctors": "doctor_id",
    "pharmacies": "pharmacy_id",
    "medicines": "medicine_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "appointments": "appointment_id",
    "inventory_movements": "inventory_movement_id",
    "payments": "payment_id",
}

REQUIRED_TABLES = tuple(TABLE_PRIMARY_KEYS.keys())

ALLOWED_ORDER_STATUSES = ("created", "paid", "packed", "dispatched", "delivered", "cancelled")
ALLOWED_APPOINTMENT_STATUSES = ("booked", "accepted", "completed", "cancelled", "no_show")
ALLOWED_PAYMENT_STATUSES = ("initiated", "success", "failed", "refunded")

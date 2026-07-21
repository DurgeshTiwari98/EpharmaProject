# Exploratory Data Analysis Report

**Phase dates:** 27 July 2026 to 02 August 2026

## 1. Executive Summary

The EDA pipeline creates repeatable summary tables for patient registration trends, medicine sales, consultation patterns, pharmacy performance, and inventory/order implications.

Run:

```bash
epharma-run-eda
```

Outputs are written to `reports/eda/`.

## 2. Patient Registration Trends

Implemented output: `reports/eda/patient_registration_trends.csv`

Dimensions:

- Month
- City
- Age group
- Registration count

Use this table for growth-rate analysis and cohort input features.

## 3. Medicine Sales Analysis

Implemented output: `reports/eda/medicine_sales_summary.csv`

Metrics:

- Units sold
- Revenue
- Distinct orders
- Month and medicine category

This identifies high-volume categories, seasonality, and candidate targets for medicine demand forecasting.

## 4. Doctor Consultation Trends

Implemented output: `reports/eda/consultation_summary.csv`

Dimensions and metrics:

- Specialty
- Weekday
- Hour
- Appointment status
- Appointment count
- Consultation revenue

## 5. Pharmacy Performance and Inventory Utilization

Implemented output: `reports/eda/pharmacy_performance.csv`

Metrics:

- Orders per pharmacy
- Delivered orders
- Cancelled orders
- Cancellation rate
- Average fulfillment hours
- Revenue

## 6. Appointment Statistics

Appointment trends are available by specialty, status, weekday, and hour. These outputs support no-show/cancellation analysis, utilization planning, and forecasting.

## 7. Cross-Module Correlations and Modeling Implications

Important derived modeling features:

- Order demand: lag order counts, rolling seven-day order counts, calendar fields.
- Medicine demand: lag weekly units, four-week rolling demand, category and revenue context.
- Appointment trends: lag bookings, rolling bookings, completed consultations, calendar fields.
- Readmission: patient demographics, chronic condition flag, spend history, order recency, specialty, and appointment type.

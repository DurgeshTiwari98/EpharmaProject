# Recommendation & Healthcare Analytics Document

**Project:** E-Pharma Management System  
**Owner:** Durgesh Tiwari  
**Phase dates:** 10 August 2026 to 16 August 2026

## 1. Objective

Phase 5 extends the predictive analytics work into recommendation and healthcare business analytics. The goal is to support medicine recommendations, patient behavior review, pharmacy performance analysis, inventory planning, and business KPI reporting.

## 2. Recommendation Analysis

The recommendation dataset is loaded from `durgesh_healthcare_datasets/phase5_recommendation.csv`.

Implemented output:

- `reports/durgesh_healthcare/recommendation_summary.csv`

The summary ranks medicine recommendation pairs by recommendation count and average similarity score. The current recommendation logic uses previous medicine, recommended medicine, and similarity score as the decision evidence.

## 3. Patient Behavior Analysis

Patient behavior is summarized from engineered patient-level signals:

- Patient age
- Chronic disease flag
- Orders per year
- High-risk flag

Implemented output:

- `reports/durgesh_healthcare/patient_behavior_summary.csv`

This supports patient segmentation, repeat purchasing analysis, and risk-based healthcare engagement.

## 4. Pharmacy Analytics

Pharmacy performance is evaluated using order volume, revenue, customer rating, and revenue per order.

Implemented output:

- `reports/durgesh_healthcare/pharmacy_performance_summary.csv`

This helps identify high-performing pharmacies and operational improvement opportunities.

## 5. Inventory Optimization

Inventory optimization reviews stock against reorder level and marks medicines that need immediate restocking.

Implemented output:

- `reports/durgesh_healthcare/inventory_optimization_summary.csv`

Business rule:

- `stock <= reorder_level` means `Reorder now`
- otherwise the item is marked `Monitor`

## 6. Dashboard

A static HTML analytics dashboard is generated at:

- `reports/durgesh_healthcare/dashboard.html`

It includes KPI cards, top pharmacy performance, top recommendation pairs, model performance ranking, and deployment availability.

## 7. Status

Phase 5 deliverables are completed for submission.

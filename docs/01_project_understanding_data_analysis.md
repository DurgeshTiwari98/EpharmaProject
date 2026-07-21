# Project Understanding & Data Analysis Document

**Project:** E-Pharma Management System  
**Owner:** Durgesh Tiwari  
**Coordinator:** Vaishali Pujari  
**Phase dates:** 13 July 2026 to 19 July 2026

## 1. Project Overview and Business Objectives

The E-Pharma Management System supports online healthcare commerce and consultation workflows across four roles:

- Patient: registration, authentication, medicine search, cart, order placement, appointment booking, consultation, e-prescription access, payments, and order tracking.
- Doctor: profile management, availability, appointment acceptance, consultation handling, e-prescription creation, and earnings review.
- Pharmacy: medicine catalog, inventory management, order fulfillment, delivery coordination, and revenue tracking.
- Admin: user management, pharmacy and doctor verification, catalog oversight, reports, disputes, payments, and system monitoring.

Business objectives for analytics are demand prediction, operational efficiency, patient retention, inventory planning, and personalized medicine recommendations.

## 2. System Architecture and Module Descriptions

The nine working modules assumed for analytics are:

1. Landing Page and Discovery: captures acquisition channel and product/service interest.
2. Registration and Login: creates authenticated patient, doctor, pharmacy, and admin identities.
3. Patient Dashboard: reads catalog, orders, appointments, prescriptions, payments, and profile data.
4. Doctor Dashboard: reads appointment queue and patient context; writes consultation and prescription data.
5. Pharmacy Dashboard: reads orders and catalog; writes stock, fulfillment, cancellation, and dispatch data.
6. Order Management: search, cart, checkout, payment, fulfillment, delivery, cancellation, and refund events.
7. Appointment Management: booking, acceptance, scheduling, video/chat consultation, no-show, and cancellation events.
8. Inventory Management: medicine SKU stock, purchase movements, sales movements, stockouts, reorder points.
9. Payment and Admin Reporting: payment initiation, success/failure/refund, payouts, audit views, and performance reports.

## 3. Data Architecture

Canonical tables implemented in `src/epharma/data/schema.py`:

| Table | Primary key | Important fields | Analytics purpose |
|---|---|---|---|
| patients | patient_id | age, gender, city, acquisition_channel, has_chronic_condition, registered_at | registration trends, cohort features, readmission prediction |
| doctors | doctor_id | specialty, city, experience_years, consultation_fee, rating | appointment trend features, doctor performance |
| pharmacies | pharmacy_id | city, rating, capacity, verified status | pharmacy performance, order demand |
| medicines | medicine_id | sku, category, brand, unit_price, prescription_required | demand forecasting, recommendations |
| orders | order_id | patient_id, pharmacy_id, status, ordered_at, delivered_at, total | order demand, fulfillment metrics |
| order_items | order_item_id | order_id, medicine_id, quantity, unit_price, line_total | medicine demand and basket analysis |
| appointments | appointment_id | patient_id, doctor_id, specialty, status, booked_at, scheduled_at | consultation trends, readmission target |
| inventory_movements | inventory_movement_id | pharmacy_id, medicine_id, movement_type, quantity, movement_at | stock turnover and stockout risk |
| payments | payment_id | order_id, method, status, amount, paid_at | payment success and revenue reporting |

Foreign key checks are implemented in `src/epharma/preprocessing/quality.py`.

## 4. Analytics Requirements

| Use case | Business question | Target | Candidate features | Success metric |
|---|---|---|---|---|
| Medicine demand forecasting | How many units of a medicine will sell next week? | weekly units by medicine | lag demand, rolling demand, category, calendar, revenue | MAE, RMSE, MAPE |
| Patient readmission prediction | Which patients will consult again within 30 days? | readmission_30d | age, chronic flag, prior orders, spend, specialty, appointment type | ROC-AUC, recall, F1 |
| Order demand prediction | How many orders will a city or pharmacy receive per day? | daily order count | lag demand, rolling demand, calendar, revenue | RMSE, R2 |
| Appointment trend prediction | How many appointments will each specialty receive? | specialty bookings per day | lag bookings, rolling bookings, calendar, completed consults | MAE, MAPE |
| Medicine recommendation | Which medicines are commonly purchased together or refilled? | next likely medicine/category | basket co-occurrence, patient history, prescription context | precision@k, recall@k |

## 5. Data Availability and Synthetic Data Plan

No production exports exist in the workspace. The default path is synthetic generation with realistic cardinalities, timestamps, prices, order status distributions, appointment outcomes, and inventory movement types.

Implemented generator: `src/epharma/data/synthetic.py`

Default full scale:

- 5,000+ patients
- 200+ doctors
- 100+ pharmacies
- 1,000+ medicine SKUs
- 12+ months of orders, appointments, payments, and inventory movements

## 6. Assumptions, Risks, and Open Questions

Assumptions:

- Appointment readmission is defined as another consultation by the same patient within 30 days.
- Order demand can initially be modeled by city; pharmacy-level modeling can be enabled after enough pharmacy-level history exists.
- Synthetic data is acceptable until real database exports arrive.

Risks:

- Synthetic behavior may understate real-world missingness, cancellations, payment failures, and seasonality.
- Real data may have PII and must be masked before analytics use.
- Recommender quality depends heavily on real basket and prescription history.

Open questions for Vaishali:

- Which database or export format will be available first?
- Are prescriptions stored as structured medicine IDs or free text?
- Should readmission mean repeat consultation, repeat order, or either event?
- Are promotion, campaign, and delivery geography data available?

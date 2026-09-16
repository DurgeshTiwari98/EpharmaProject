# Model Optimization & Validation Document

**Project:** E-Pharma Management System  
**Owner:** Durgesh Tiwari  
**Phase dates:** 17 August 2026 to 23 August 2026

## 1. Objective

Phase 6 focuses on improving model readiness through feature engineering, validation, and performance review.

## 2. Feature Engineering

Feature engineering uses the dataset:

- `durgesh_healthcare_datasets/phase6_feature_engineering.csv`

Core features:

- Patient age
- Chronic disease
- Orders per year
- High-risk label

Implemented output:

- `reports/durgesh_healthcare/feature_engineering_summary.csv`

## 3. Validation Method

The existing model training workflow uses time-based holdout validation for forecasting and classification tasks. Phase 6 adds aggregate feature validation so the model input population can be reviewed before API or deployment use.

Validation checks include:

- Record count
- Average patient age
- Average yearly orders
- Chronic disease rate
- High-risk patient rate

## 4. Optimization Results

Model candidates and metrics are available in:

- `reports/model_comparison.csv`
- `reports/durgesh_healthcare/model_performance_summary.csv`

The selected candidate should prioritize business use case:

- Forecasting: lowest RMSE and acceptable MAPE
- Readmission and risk scoring: balanced recall and F1
- Recommendation: highest similarity and recommendation accuracy

## 5. Status

Phase 6 deliverables are completed for project handover.

# Model Development Document

**Phase dates:** 03 August 2026 to 09 August 2026

## 1. Problem Formulation

Four Phase 4 model families are implemented in `src/epharma/models/training.py`.

| Problem | Target | Split strategy |
|---|---|---|
| Medicine Demand Forecasting | weekly units per medicine | time-based holdout |
| Patient Readmission Prediction | patient has another consultation within 30 days | time-based holdout by scheduled appointment |
| Order Demand Prediction | daily order count by city | time-based holdout |
| Appointment Trend Prediction | daily bookings by specialty | time-based holdout |

## 2. Feature Engineering

Implemented in `src/epharma/models/features.py`.

- Calendar fields: day of week, day of month, month, ISO week, weekend flag.
- Demand lags: previous period demand and rolling averages.
- Readmission features: demographics, chronic condition flag, lifetime orders, lifetime spend, days since last order, consultation duration, fee, specialty, and appointment type.

## 3. Algorithms Compared

Regression and forecasting tasks:

- Naive lag baseline
- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor

Classification task:

- Most-frequent baseline
- Logistic Regression with balanced class weights
- Random Forest Classifier with balanced class weights

The code keeps optional dependencies such as XGBoost, LightGBM, Prophet, and MLflow in `requirements.txt` extras, but the default implementation uses scikit-learn models so the workflow remains portable.

## 4. Evaluation Metrics and Results Table

Run:

```bash
epharma-train-models
```

Output:

- `reports/model_comparison.csv`
- `models/*.joblib`

Regression metrics:

- MAE
- RMSE
- MAPE
- R2

Classification metrics:

- ROC-AUC
- Precision
- Recall
- F1

## 5. Selected Candidate Model

Selection rule:

- Forecasting/regression: choose the lowest validation RMSE, using MAPE as a business readability check.
- Readmission: choose the highest recall/F1 balance when outreach or intervention capacity is limited; choose ROC-AUC for ranking-only workflows.

After running on real or generated data, the selected model per problem should be recorded from `reports/model_comparison.csv`.

## 6. Reproducibility

Recommended end-to-end sequence:

```bash
epharma-generate-data --scale full
epharma-preprocess
epharma-run-eda
epharma-train-models
```

All model artifacts are saved with deterministic seeds where supported. The table-level generation seed is configured in `config/settings.yaml`.

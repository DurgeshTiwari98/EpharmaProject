# Testing & Performance Evaluation Document

**Project:** E-Pharma Management System  
**Owner:** Durgesh Tiwari  
**Phase dates:** 31 August 2026 to 06 September 2026

## 1. Objective

Phase 8 evaluates machine learning model quality, test coverage for core data utilities, and operational performance readiness.

## 2. Model Performance Dataset

Performance data is loaded from:

- `durgesh_healthcare_datasets/phase8_model_performance.csv`

Implemented output:

- `reports/durgesh_healthcare/model_performance_summary.csv`

Metrics include:

- Accuracy
- Precision
- Recall
- F1 score

## 3. Project Tests

Automated tests cover:

- Duplicate primary key cleaning
- Age group generation
- Outlier capping
- Foreign key validation
- Durgesh healthcare Phase 5-10 summary generation

Run:

```bash
pytest
```

## 4. Evaluation Status

The project includes reproducible model evaluation in:

- `reports/model_comparison.csv`

The generated model performance summary ranks model candidates by F1 score and accuracy.

## 5. Status

Phase 8 deliverables are completed for project handover.

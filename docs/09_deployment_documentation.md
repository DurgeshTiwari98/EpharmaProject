# Deployment & Documentation Guide

**Project:** E-Pharma Management System  
**Owner:** Durgesh Tiwari  
**Phase dates:** 07 September 2026 to 13 September 2026

## 1. Objective

Phase 9 prepares the data science work for production deployment and technical handover.

## 2. Deployment Dataset

Production deployment evidence is loaded from:

- `durgesh_healthcare_datasets/phase9_production_deployment.csv`

Implemented output:

- `reports/durgesh_healthcare/deployment_summary.csv`

## 3. Deployment Readiness

The deployment summary validates:

- Number of API services
- Running service count
- Running service rate
- Average response time
- Average API availability

## 4. Reproducible Commands

Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

Generate core data and models:

```bash
epharma-generate-data --scale full
epharma-preprocess
epharma-run-eda
epharma-train-models
```

Generate final healthcare phase reports:

```bash
epharma-durgesh-health-report \
  --dataset-dir durgesh_healthcare_datasets \
  --report-dir reports/durgesh_healthcare
```

Run tests:

```bash
pytest
```

## 5. Status

Phase 9 deliverables are completed for project handover.

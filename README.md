# E-Pharma Management System Analytics

Production-oriented data science scaffold for the assignment period through **09 August 2026**:

- Phase 1: project understanding, logical data model, analytics use cases
- Phase 2: synthetic/raw data collection and preprocessing
- Phase 3: exploratory data analysis helpers and report generation
- Phase 4: baseline machine learning model development

## Quick Start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
epharma-generate-data --scale small
epharma-preprocess
epharma-run-eda
epharma-train-models
```

Outputs are written to:

- `data/raw/` for generated source tables
- `data/processed/` for clean analysis-ready tables
- `reports/` for profiles, EDA summaries, and model metrics
- `models/` for serialized model artifacts
- `docs/` for phase documentation

If Parquet dependencies are unavailable, the pipelines automatically fall back to CSV.

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

## Using `data.docx`

The project includes a DOCX extractor for Word tables:

```bash
python3 src/epharma/data/docx_extract.py --input data.docx --output-dir data/raw/docx
```

After installing the project, the same command is available as:

```bash
epharma-extract-docx --input data.docx --output-dir data/raw/docx
```

The extractor writes one CSV per Word table under `data/raw/docx/`. Example:

```python
import pandas as pd

patients = pd.read_csv("data/raw/docx/01_patient_registration.csv")
```

## Using `durgesh_healthcare_datasets`

Run the Durgesh healthcare phase dataset report builder:

```bash
python3 src/epharma/data/durgesh_health.py \
  --dataset-dir durgesh_healthcare_datasets \
  --report-dir reports/durgesh_healthcare
```

It writes cleaned summaries for patients, medicine sales, doctors, inventory, and KPIs under
`reports/durgesh_healthcare/`.

Outputs are written to:

- `data/raw/` for generated source tables
- `data/processed/` for clean analysis-ready tables
- `reports/` for profiles, EDA summaries, and model metrics
- `models/` for serialized model artifacts
- `docs/` for phase documentation

If Parquet dependencies are unavailable, the pipelines automatically fall back to CSV.

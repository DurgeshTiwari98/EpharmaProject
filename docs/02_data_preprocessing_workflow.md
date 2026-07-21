# Data Preprocessing Workflow Document

**Phase dates:** 20 July 2026 to 26 July 2026

## 1. Data Sources and Collection Method

The repository supports generated synthetic source data by default:

```bash
epharma-generate-data --scale full
```

Raw datasets are written to `data/raw/` and are never edited in place. If production exports are later provided, place matching table files in `data/raw/` with the canonical table names.

## 2. Data Dictionary

The canonical schema is documented in `docs/01_project_understanding_data_analysis.md` and implemented in `src/epharma/data/schema.py`. Processed tables preserve primary and foreign keys and add derived fields such as `age_group` and outlier/missingness indicator columns where needed.

## 3. Data Quality Findings

Run:

```bash
epharma-preprocess
```

Generated quality outputs:

- `reports/data_profile_before.csv`
- `reports/data_profile_after.csv`
- `reports/referential_integrity.csv`

Each profile records row count, dtype, missing count, missing percentage, and unique count by column.

## 4. Cleaning Decisions

- Duplicate records: exact duplicate primary keys keep the latest observed record.
- String categories: whitespace is trimmed consistently.
- Date fields: parsed with `pandas.to_datetime` and invalid values become missing timestamps.
- Numeric missing values: median imputation plus a `{column}_was_missing` flag.
- Categorical missing values: mode imputation plus a `{column}_was_missing` flag.
- Outliers: IQR capping for order amounts, quantities, fees, stock movements, ratings, and age, plus `{column}_was_outlier` flags.
- Referential integrity: orders, items, appointments, inventory movements, and payments are validated against their parent tables.

## 5. Transformation and Normalization

Current transformations are conservative and model-ready:

- Patient `age_group` bands: `0-17`, `18-29`, `30-44`, `45-59`, `60+`.
- Date normalization for registration, appointment, order, delivery, payment, and movement timestamps.
- Model-specific lag, rolling, and calendar features are created in `src/epharma/models/features.py`.

## 6. Pipeline Architecture

One-command preprocessing:

```bash
epharma-preprocess --raw-dir data/raw --processed-dir data/processed --report-dir reports
```

Main modules:

- `src/epharma/preprocessing/cleaning.py`: reusable cleaning primitives
- `src/epharma/preprocessing/quality.py`: profiling and foreign key checks
- `src/epharma/preprocessing/pipeline.py`: end-to-end orchestration

Processed outputs are written as Parquet when possible, with CSV fallback.

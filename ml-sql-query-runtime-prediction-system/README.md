# Machine Learning SQL Query Runtime Prediction System

This project predicts SQL query runtime using machine learning features extracted from:

- Query structure (joins, filters, aggregations, etc.)
- Query execution plans
- Historical runtime measurements

The system is designed to run on DuckDB with a TPC-H style workload and produce a training dataset for regression models.

## Project Structure

```text
ml-sql-query-runtime-prediction-system/
	api/                  # FastAPI service for serving predictions
	data/                 # DuckDB file and generated CSV artifacts
	features/             # SQL and plan feature extraction logic
	models/               # Trained model artifacts
	notebooks/            # Experimentation and analysis notebooks
	pipeline/             # Dataset construction and orchestration scripts
	runner/               # Query loading/execution utilities
	requirements.txt
	README.md
```

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the API:

```bash
uvicorn api.app:app --reload
```

4. Verify service health:

```text
GET http://127.0.0.1:8000/health
```

## Current Status

Phase 1 scaffolding is in place:

- Base project structure
- Core dependency installation via `requirements.txt`
- Starter modules in `runner/`, `features/`, `pipeline/`, and `api/`

Later phases will add workload generation, runtime collection, execution plan parsing, model training, and SHAP-based explainability.

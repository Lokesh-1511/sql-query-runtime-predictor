from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import duckdb
import joblib
import numpy as np
import pandas as pd
import sqlglot
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlglot import expressions as exp

from features.feature_extractor import extract_structural_features
from features.plan_parser import extract_plan_features


DEFAULT_DB_PATH = Path("data") / "tpch.db"
MODEL_PATH = Path("models") / "best_runtime_model.joblib"
METADATA_PATH = Path("models") / "training_metadata.json"


class PredictionRequest(BaseModel):
	"""Request payload for runtime prediction."""

	sql_query: str = Field(..., description="SQL query text to analyze and score")
	include_explain_analyze: bool = Field(
		default=False,
		description="If true, use EXPLAIN ANALYZE (runs query). If false, use EXPLAIN only.",
	)


class PredictionResponse(BaseModel):
	"""Response payload for runtime prediction."""

	predicted_runtime_seconds: float
	predicted_log_runtime: float
	model_name: str
	target_transform: str
	query_category: str
	tables_used: list[str]
	explain_mode: str
	top_feature_values: dict[str, float | int]


app = FastAPI(
	title="SQL Query Runtime Predictor API",
	description="API for ML-based SQL runtime prediction.",
	version="0.2.0",
)


@lru_cache(maxsize=1)
def load_model_bundle() -> tuple[Any, dict[str, Any]]:
	"""Load persisted model and metadata once per process."""
	if not MODEL_PATH.exists():
		raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
	if not METADATA_PATH.exists():
		raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")

	model = joblib.load(MODEL_PATH)
	metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
	return model, metadata


def infer_query_category(structural_features: dict[str, Any]) -> str:
	"""Infer one of the trained query categories from structural features."""
	if int(structural_features.get("subquery_depth", 0)) > 0:
		return "analytical_query"
	if int(structural_features.get("number_of_joins", 0)) > 0:
		return "join_query"
	if int(structural_features.get("group_by_present", 0)) == 1:
		return "group_by_query"
	if int(structural_features.get("aggregation_count", 0)) > 0:
		return "aggregation_query"
	if int(structural_features.get("number_of_filters", 0)) > 0:
		return "filter_query"
	return "single_table"


def extract_tables_used(sql_query: str) -> list[str]:
	"""Extract referenced tables from SQL text."""
	tree = sqlglot.parse_one(sql_query)
	tables = sorted({table.name for table in tree.find_all(exp.Table) if table.name})
	return tables


def build_plan_text(conn: duckdb.DuckDBPyConnection, sql_query: str, include_analyze: bool) -> str:
	"""Build EXPLAIN text blob in the same section format used in training."""

	def explain(prefix: str) -> str:
		rows = conn.execute(f"{prefix} {sql_query}").fetchall()
		parts: list[str] = []
		for row in rows:
			if len(row) == 1:
				parts.append(str(row[0]))
			else:
				parts.append(" | ".join(str(cell) for cell in row))
		return "\n".join(parts)

	explain_text = explain("EXPLAIN")
	analyze_text = explain("EXPLAIN ANALYZE") if include_analyze else ""
	return "[EXPLAIN]\n" + explain_text + "\n\n[EXPLAIN ANALYZE]\n" + analyze_text


def build_feature_row(sql_query: str, include_explain_analyze: bool) -> tuple[pd.DataFrame, str, list[str], dict[str, float | int]]:
	"""Create one model-ready feature row aligned to training metadata feature order."""
	model, metadata = load_model_bundle()
	feature_names = metadata["feature_names"]

	structural = extract_structural_features(sql_query)
	query_category = infer_query_category(structural)
	tables_used = extract_tables_used(sql_query)

	conn = duckdb.connect(str(DEFAULT_DB_PATH))
	try:
		plan_text = build_plan_text(conn, sql_query, include_analyze=include_explain_analyze)
	except Exception as exc:
		raise HTTPException(status_code=400, detail=f"Failed to explain query: {exc}") from exc
	finally:
		conn.close()

	plan_features = extract_plan_features(plan_text)

	features: dict[str, float | int] = {
		**{k: int(v) if isinstance(v, bool) else v for k, v in structural.items()},
		**plan_features,
	}

	features["join_filter_complexity"] = float(features["number_of_joins"]) * float(features["number_of_filters"])
	features["join_table_ratio"] = float(features["number_of_joins"]) / (float(features["number_of_tables"]) + 1.0)
	features["aggregation_density"] = float(features["aggregation_count"]) / (float(features["number_of_tables"]) + 1.0)
	features["scan_join_interaction"] = float(features["scan_count"]) * float(features["number_of_joins"])

	category_columns = [
		"query_category_aggregation_query",
		"query_category_analytical_query",
		"query_category_filter_query",
		"query_category_group_by_query",
		"query_category_join_query",
		"query_category_single_table",
	]
	for col in category_columns:
		features[col] = 1 if col == f"query_category_{query_category}" else 0

	row = {name: float(features.get(name, 0.0)) for name in feature_names}
	feature_df = pd.DataFrame([row], columns=feature_names)

	top_feature_values = {
		key: row[key]
		for key in [
			"rows_scanned",
			"operator_count",
			"number_of_filters",
			"subquery_depth",
			"query_length",
			"token_count",
			"join_filter_complexity",
			"scan_count",
		]
		if key in row
	}

	return feature_df, query_category, tables_used, top_feature_values


@app.get("/")
def root() -> dict[str, str]:
	"""Project metadata endpoint."""
	return {
		"name": "sql-query-runtime-predictor",
		"status": "ready",
		"phase": "phase-11",
	}


@app.get("/health")
def health() -> dict[str, str]:
	"""Simple health check endpoint."""
	return {"status": "ok"}


@app.get("/model-info")
def model_info() -> dict[str, Any]:
	"""Return active model metadata and evaluation values."""
	try:
		_, metadata = load_model_bundle()
	except FileNotFoundError as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc

	return {
		"best_model_name": metadata.get("best_model_name"),
		"target_column": metadata.get("target_column"),
		"target_transform": metadata.get("target_transform"),
		"feature_count": len(metadata.get("feature_names", [])),
		"metrics": metadata.get("metrics", {}),
	}


@app.post("/predict", response_model=PredictionResponse)
def predict_runtime(payload: PredictionRequest) -> PredictionResponse:
	"""Predict SQL runtime (seconds) from query text using the persisted model."""
	sql_query = payload.sql_query.strip()
	if not sql_query:
		raise HTTPException(status_code=400, detail="sql_query must not be empty")

	try:
		model, metadata = load_model_bundle()
	except FileNotFoundError as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc

	feature_df, query_category, tables_used, top_feature_values = build_feature_row(
		sql_query,
		include_explain_analyze=payload.include_explain_analyze,
	)

	predicted_log_runtime = float(model.predict(feature_df)[0])
	if metadata.get("target_transform") == "log1p":
		predicted_runtime = float(np.expm1(predicted_log_runtime))
	else:
		predicted_runtime = predicted_log_runtime

	return PredictionResponse(
		predicted_runtime_seconds=max(predicted_runtime, 0.0),
		predicted_log_runtime=predicted_log_runtime,
		model_name=str(metadata.get("best_model_name", "unknown")),
		target_transform=str(metadata.get("target_transform", "none")),
		query_category=query_category,
		tables_used=tables_used,
		explain_mode="EXPLAIN ANALYZE" if payload.include_explain_analyze else "EXPLAIN",
		top_feature_values=top_feature_values,
	)

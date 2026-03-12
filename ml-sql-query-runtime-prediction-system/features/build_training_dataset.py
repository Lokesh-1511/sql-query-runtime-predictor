"""Phase 8: Final ML Training Dataset.

Combine structural features, execution-plan metrics, and runtime metadata into
one training-ready dataset.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_EXPANDED_FEATURES_PATH = Path(__file__).parent.parent / "data" / "features_expanded_4000.csv"
DEFAULT_PLAN_METRICS_PATH = Path(__file__).parent.parent / "data" / "plan_metrics_100.csv"
DEFAULT_TRAINING_DATASET_PATH = Path(__file__).parent.parent / "data" / "ml_training_dataset.csv"
DEFAULT_RUNTIME_LOGS_PATH = Path(__file__).parent.parent / "data" / "query_runtime_logs.csv"


def load_expanded_features(
    path: Path = DEFAULT_EXPANDED_FEATURES_PATH,
) -> pd.DataFrame:
    """Load expanded feature rows aligned to runtime logs."""
    return pd.read_csv(path)


def load_plan_metrics(
    path: Path = DEFAULT_PLAN_METRICS_PATH,
) -> pd.DataFrame:
    """Load per-query plan metrics."""
    return pd.read_csv(path)


def add_interaction_features(training_df: pd.DataFrame) -> pd.DataFrame:
    """Create derived interaction features for model improvement."""
    enriched_df = training_df.copy()
    enriched_df["join_filter_complexity"] = enriched_df["number_of_joins"] * enriched_df["number_of_filters"]
    enriched_df["join_table_ratio"] = enriched_df["number_of_joins"] / (enriched_df["number_of_tables"] + 1)
    enriched_df["aggregation_density"] = enriched_df["aggregation_count"] / (enriched_df["number_of_tables"] + 1)
    enriched_df["scan_join_interaction"] = enriched_df["scan_count"] * enriched_df["number_of_joins"]
    return enriched_df


def build_training_dataset(
    expanded_features_path: Path = DEFAULT_EXPANDED_FEATURES_PATH,
    plan_metrics_path: Path = DEFAULT_PLAN_METRICS_PATH,
) -> pd.DataFrame:
    """Build the final training dataset from expanded features and plan metrics."""
    expanded_df = load_expanded_features(expanded_features_path)
    plan_df = load_plan_metrics(plan_metrics_path)

    metadata_cols = ["query_id", "run_number", "execution_time", "query_category", "tables_used"]
    plan_metric_cols = [column for column in plan_df.columns if column != "query_id"]
    expanded_feature_cols = [
        column
        for column in expanded_df.columns
        if column not in metadata_cols and column not in plan_metric_cols
    ]

    training_df = expanded_df[metadata_cols + expanded_feature_cols].merge(plan_df, on="query_id", how="left")
    training_df = add_interaction_features(training_df)
    return training_df


def save_training_dataset(
    training_df: pd.DataFrame,
    output_path: Path = DEFAULT_TRAINING_DATASET_PATH,
) -> Path:
    """Save final ML training dataset."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    training_df.to_csv(output_path, index=False)
    return output_path


def validate_training_dataset(
    training_df: pd.DataFrame,
    runtime_logs_path: Path = DEFAULT_RUNTIME_LOGS_PATH,
) -> dict[str, Any]:
    """Validate final training dataset before ML modeling."""
    runtime_logs_df = pd.read_csv(runtime_logs_path)
    expected_rows = len(runtime_logs_df)
    unique_queries = training_df["query_id"].nunique()
    validation = {
        "shape": training_df.shape,
        "expected_rows": expected_rows,
        "rows_match": len(training_df) == expected_rows,
        "unique_queries": unique_queries,
        "expected_unique_queries": runtime_logs_df["query_id"].nunique(),
        "runs_per_query": len(training_df) // unique_queries if unique_queries else 0,
        "null_counts": training_df.isnull().sum().to_dict(),
        "columns": list(training_df.columns),
        "column_count": len(training_df.columns),
    }
    return validation

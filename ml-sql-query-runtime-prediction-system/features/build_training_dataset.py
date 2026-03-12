"""Phase 8: Final ML Training Dataset

Combines all features:
- Structural features (from query parsing)
- Execution plan metrics (from EXPLAIN text)
- Runtime metadata (from execution logs)

Creates final 4000-row dataset ready for ML model training.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_EXPANDED_FEATURES_PATH = Path(__file__).parent.parent / "data" / "features_expanded_4000.csv"
DEFAULT_PLAN_METRICS_PATH = Path(__file__).parent.parent / "data" / "plan_metrics_100.csv"
DEFAULT_TRAINING_DATASET_PATH = Path(__file__).parent.parent / "data" / "ml_training_dataset.csv"


def load_expanded_features(
    path: Path = DEFAULT_EXPANDED_FEATURES_PATH,
) -> pd.DataFrame:
    """Load 4000-row expanded features dataset."""
    return pd.read_csv(path)


def load_plan_metrics(
    path: Path = DEFAULT_PLAN_METRICS_PATH,
) -> pd.DataFrame:
    """Load 100-row plan metrics dataset."""
    return pd.read_csv(path)


def build_training_dataset(
    expanded_features_path: Path = DEFAULT_EXPANDED_FEATURES_PATH,
    plan_metrics_path: Path = DEFAULT_PLAN_METRICS_PATH,
) -> pd.DataFrame:
    """
    Build final ML training dataset by combining:
    1. Expanded features (4000 rows with runtime metadata and structural features)
    2. Plan metrics (100 rows with execution plan-based features)
    
    Result: 4000 rows with all features for ML training.
    """
    expanded_df = load_expanded_features(expanded_features_path)
    plan_df = load_plan_metrics(plan_metrics_path)
    
    # Remove duplicate structural features from expanded (we'll use plan metrics instead)
    # Keep columns: query_id, run_number, execution_time, query_category, tables_used
    # Plus: number_of_tables, number_of_joins, number_of_filters, aggregation_count, group_by_present, order_by_present, subquery_depth
    structural_cols = [
        'query_id', 'run_number', 'execution_time', 'query_category', 'tables_used',
        'number_of_tables', 'number_of_joins', 'number_of_filters', 
        'aggregation_count', 'group_by_present', 'order_by_present', 'subquery_depth'
    ]
    
    expanded_df = expanded_df[structural_cols]
    
    # Merge with plan metrics on query_id
    training_df = expanded_df.merge(plan_df, on='query_id', how='left')
    
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
) -> dict[str, Any]:
    """Validate final training dataset before ML modeling."""
    validation = {
        "shape": training_df.shape,
        "expected_rows": 4000,
        "rows_match": len(training_df) == 4000,
        "unique_queries": training_df['query_id'].nunique(),
        "runs_per_query": len(training_df) // training_df['query_id'].nunique(),
        "null_counts": training_df.isnull().sum().to_dict(),
        "columns": list(training_df.columns),
        "column_count": len(training_df.columns),
    }
    
    return validation

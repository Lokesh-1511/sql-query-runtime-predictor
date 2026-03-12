"""Expand Features to Match Runtime Logs

Aligns the 100-query features dataset with the 4000-row runtime logs
(100 queries × 40 runs each) by repeating features for each runtime measurement.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_RUNTIME_LOGS_PATH = Path(__file__).parent.parent / "data" / "query_runtime_logs.csv"
DEFAULT_FEATURES_PATH = Path(__file__).parent.parent / "data" / "features_dataset.csv"
DEFAULT_EXPANDED_PATH = Path(__file__).parent.parent / "data" / "features_expanded_4000.csv"


def expand_features_to_runtime_logs(
    runtime_logs_path: Path = DEFAULT_RUNTIME_LOGS_PATH,
    features_path: Path = DEFAULT_FEATURES_PATH,
) -> pd.DataFrame:
    """
    Load runtime logs (4000 rows) and features (100 rows),
    then join to create expanded features (4000 rows).
    
    Each row in runtime_logs gets all features for its corresponding query_id.
    """
    # Load both datasets
    runtime_logs_df = pd.read_csv(runtime_logs_path)
    features_df = pd.read_csv(features_path)
    
    # Drop the 'runtime' column from features since we'll use 'execution_time' from logs
    features_for_join = features_df.drop(columns=['runtime'])
    
    # Left join on query_id to expand features for each run
    expanded_df = runtime_logs_df.merge(
        features_for_join,
        on='query_id',
        how='left'
    )
    
    return expanded_df


def save_expanded_features(
    expanded_df: pd.DataFrame,
    output_path: Path = DEFAULT_EXPANDED_PATH,
) -> Path:
    """Save expanded (4000-row) features dataset to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    expanded_df.to_csv(output_path, index=False)
    return output_path


def validate_expansion(expanded_df: pd.DataFrame, runtime_logs_path: Path = DEFAULT_RUNTIME_LOGS_PATH) -> dict[str, Any]:
    """Validate that expansion matched all rows correctly."""
    runtime_df = pd.read_csv(runtime_logs_path)
    
    validation = {
        "expected_rows": len(runtime_df),
        "actual_rows": len(expanded_df),
        "rows_match": len(expanded_df) == len(runtime_df),
        "no_nulls": expanded_df.isnull().sum().sum() == 0,
        "columns": list(expanded_df.columns),
    }
    
    return validation
